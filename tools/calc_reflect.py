"""
Calculate reflection curves for red, green, and blue jointly, with a chromatic adaptation in the CMFs.

This is a pure Python version of `calc_spectral.py`, solved with the same Newton/KKT approach used in
`calc_reflect.py` instead of SciPy.

Model:
  * `T`: illuminant referenced CMFs, as the illuminant and CMFs yield them (3 x N).
  * `M`: linear sRGB to XYZ D65.
  * `A`: Bradford chromatic adaptation from the white of `M` (`M @ 1`) to the white the CMFs yield (`T @ 1`).
  * Find `B` (N x 3) with `T @ B = A @ M` and `B @ 1 = 1` (the curves sum to a flat reflectance of 1),
    minimizing the sum of squared first differences of `atanh(2 * B - 1)` for all three curves.
  * The adaptation is folded into the CMFs, `T_ADAPTED = A^-1 @ T`, so XYZ produced from the curves is in the
    white point of `M`. The RGB conversion matrix is left alone: XYZ to RGB is just `inv(M)`, concentrations
    are exactly the linear sRGB values, and a flat reflectance of 1 integrates to exactly the white of `M`.

The curves are `(1 + tanh(z)) / 2`, so they always stay strictly between 0 and 1. Red and green are
constrained to their colors, the color of blue is implied by the flat white. The result is a stationary point of
a nonconvex problem, there is no proof that it is the global optimum.
"""
import sys
import os
import math
import plotly.graph_objects as go

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg
from coloraide.cmfs import CIE_1931_2DEG as CMF
from coloraide.illuminants import D65
from coloraide.spaces.srgb_linear import RGB_TO_XYZ
from coloraide.cat import Bradford

START = 380
STEP = 10
END = 750 + STEP
MAX_ITERS = 100
# The joint system is large and has a residual that bottoms out near 1e-15
EPSILON = 1e-12

# Bradford cone response matrix
BRADFORD = Bradford.MATRIX

wavelengths = list(range(START, END, STEP))
size = len(wavelengths)

A = [[CMF[r][i] for r in wavelengths] for i in range(3)]
W = [D65[r] for r in wavelengths]

# Illuminant referenced CMFs
T = alg.divide(alg.matmul(A, alg.diag(W)), alg.vdot(A[1], W))


def chromatic_adaptation(source_white, destination_white):
    """Get the Bradford chromatic adaptation matrix that maps the source white exactly to the destination white."""

    source = alg.dot(BRADFORD, source_white)
    destination = alg.dot(BRADFORD, destination_white)
    return alg.matmul(alg.matmul(alg.inv(BRADFORD), alg.diag(alg.divide(destination, source))), BRADFORD)


# The white the CMFs yield and the white of the color space
white_raw = [math.fsum(row) for row in T]
white_srgb = [math.fsum(row) for row in RGB_TO_XYZ]

# Adaptation from the color space's white to the CMF's white, the primaries as the CMFs see them,
# and the CMFs with the adaptation folded in.
CAT = chromatic_adaptation(white_srgb, white_raw)
PRIMARIES = alg.matmul(CAT, RGB_TO_XYZ)
T_ADAPTED = alg.matmul(alg.inv(CAT), T)
XYZ_TO_RGB = alg.inv(RGB_TO_XYZ)

# Smoothness of a curve is the sum of the squared first differences, as a matrix: `z.L.z`
L = [[0.0] * size for _ in range(size)]
for i in range(size):
    L[i][i] = 1.0 if i in (0, size - 1) else 2.0
    if i:
        L[i][i - 1] = -1.0
    if i < size - 1:
        L[i][i + 1] = -1.0


def _tanh(x):
    """Clamp the results if there is overflow."""

    try:
        return math.tanh(x)
    except OverflowError:
        return 1.0 if x > 0 else -1.0


def _sech2(x):
    """Clamp the results to zero if there is overflow."""

    try:
        return 1 / (math.cosh(x) ** 2)
    except OverflowError:
        return 0.0


def joint_method(l, cmfs, color_r, color_g, max_iterations=MAX_ITERS, tolerance=EPSILON):
    """
    Estimate the red, green, and blue reflectance curves together.

    Approaches comes from Scott Burns.
    http://scottburns.us/matlab-octave-and-python-source-code-for-refl-recon-chrom-adapt/

    This extends `method_3` from Scott Burns to three curves that must sum to 1 at every wavelength.
    Each curve is `(1 + tanh(z)) / 2` and the roughness of the `z` values is minimized subject to:

    - The three curves sum to 1 at every wavelength.
    - The red and green curves reproduce their colors (blue is implied by the above).

    References
    ----------
    [1] Burns SA. Numerical methods for smoothest reflectance
        reconstruction. Color Research & Application, Vol 45,
        No 1, 2020, pp 8-21.
    [2] Generating Reflectance Curves from sRGB Triplets, 2015
        http://scottburns.us/reflectance-curves-from-srgb/#LHTSS

    Parameters
    ----------
    `l`: nxn matrix of the squared first differences.
    `cmfs`: 3xn illuminant referenced CMFs.
    `color_r`: the XYZ of the red curve, as the CMFs see it.
    `color_g`: the XYZ of the green curve, as the CMFs see it.

    Returns
    -------
    Three nx1 vectors of spectral reflectance values for red, green, and blue (or zeros if failure).

    """

    n = len(l)
    m = 3 * n + n + 6
    target = color_r + color_g
    z = [alg.zeros(n), alg.zeros(n), alg.zeros(n)]
    lam = alg.zeros(n + 6)

    def evaluate(z, lam):
        """Evaluate the curves, the KKT residual, and what is needed for the Jacobian."""

        th = [[_tanh(x) for x in zi] for zi in z]
        b = [[(1 + t) / 2 for t in ti] for ti in th]
        s = [[_sech2(x) for x in zi] for zi in z]
        # The multiplier weight each curve's wavelength sees: the sum constraint plus the color constraints
        wt = []
        for i in range(3):
            if i < 2:
                wt.append([lam[j] + math.fsum(lam[n + 3 * i + a] * cmfs[a][j] for a in range(3)) for j in range(n)])
            else:
                wt.append(lam[:n])
        # Gradient of the Lagrangian with respect to z, then the constraints
        grad = []
        for i in range(3):
            grad.extend(alg.add(alg.dot(l, z[i]), [wt[i][j] * s[i][j] / 2 for j in range(n)]))
        g = [b[0][j] + b[1][j] + b[2][j] - 1 for j in range(n)]
        g.extend(alg.subtract(alg.dot(cmfs, b[0]), target[:3]))
        g.extend(alg.subtract(alg.dot(cmfs, b[1]), target[3:]))
        return b, th, s, wt, grad + g

    for _ in range(max_iterations):
        b, th, s, wt, f = evaluate(z, lam)
        magnitude = max(abs(x) for x in f)
        if magnitude < tolerance:
            return b

        # Assemble the Newton/KKT system.
        # The Hessian of the Lagrangian is the smoothness plus a diagonal from the curvature of `b`.
        j = alg.zeros((m, m))
        for i in range(3):
            o = i * n
            for r in range(n):
                for c in range(n):
                    j[o + r][o + c] = l[r][c]
                j[o + r][o + r] += -s[i][r] * th[i][r] * wt[i][r]
        # Jacobian of the constraints (and its transpose)
        for i in range(3):
            o = i * n
            for k in range(n):
                db = s[i][k] / 2
                j[o + k][3 * n + k] = j[3 * n + k][o + k] = db
                if i < 2:
                    for a in range(3):
                        col = 4 * n + 3 * i + a
                        j[o + k][col] = j[col][o + k] = cmfs[a][k] * db

        try:
            try:
                delta = alg.solve(j, alg.multiply(-1, f))
            except Exception:
                delta = alg.dot(alg.pinv(j), alg.multiply(f, -1))
        except Exception:
            print('Ill-conditioned or singular linear system detected.')
            return [alg.zeros(n) for _ in range(3)]

        # Backtrack so the residual always improves
        step = 1.0
        for _ in range(40):
            z_try = [alg.add(z[i], alg.multiply(step, delta[i * n:(i + 1) * n])) for i in range(3)]
            lam_try = alg.add(lam, alg.multiply(step, delta[3 * n:]))
            trial = evaluate(z_try, lam_try)[-1]
            if max(abs(x) for x in trial) < magnitude * (1 - 1e-4 * step):
                z, lam = z_try, lam_try
                break
            step /= 2
        else:
            print('Line search failed.')
            return [alg.zeros(n) for _ in range(3)]

    print('Maximum number of iterations reached.')
    return [alg.zeros(n) for _ in range(3)]


# Red and green are constrained, blue is implied. All other colors are sums of the primaries.
red, green, blue = joint_method(L, T, [row[0] for row in PRIMARIES], [row[1] for row in PRIMARIES])
curves = {
    '#ff0000': red,
    '#00ff00': green,
    '#0000ff': blue,
    '#00ffff': alg.add(green, blue),
    '#ff00ff': alg.add(red, blue),
    '#ffff00': alg.add(red, green),
    '#ffffff': alg.add(alg.add(red, green), blue)
}

print('=== CMFs D65 (adapted) ===')
for name, row in zip(('X', 'Y', 'Z'), T_ADAPTED):
    print(f'==== {name} ====')
    alg.pprint(row)

# Setup plot for results
fig = go.Figure(
    layout={
        'title': 'Primary Color Reflectance Curves',
        'xaxis_title': 'Wavelength',
        'yaxis_title': 'Reflection',
        'width': 800,
        'height': 600
    }
)

print('=== Reflectance Curves ===')
for target, r in curves.items():
    print(f'==== Curve for {target} ====')
    alg.pprint(r)

    fig.add_traces(data=go.Scatter(
        x=wavelengths,
        y=r,
        mode="lines",
        line={'color': target, 'width': 4, 'shape': 'spline'},
        showlegend=False
    ))

fig.show('browser')
