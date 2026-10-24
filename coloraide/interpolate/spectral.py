"""
Approach based off of Spectral.js library.

https://github.com/rvanwijnen/spectral.js
---
MIT License

 Copyright (c) 2023 Ronald van Wijnen

 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
---
Modified by Isaac Muse
- Recalculated D65 illuminated CMFs and R, G, and B curves with higher precision
  and generated them with our exact RGB matrix, white point, and CMF calculations.
- Added sane handling for colors beyond the sRGB gamut. Limit the curves to be below
  1 and calculate residual XYZ difference between what the concentration can produce
  and actual value. Add the interpolated residual back in after blending the reflectance
  curves.
"""
from __future__ import annotations
import math
import itertools as it
from .. import algebra as alg
from ..types import Vector, AnyColor, ColorInput
from . import Interpolator, Interpolate, Sentinel
from .linear import InterpolatorLinear
from .continuous import InterpolatorContinuous
from ..spaces.srgb_linear import XYZ_TO_RGB
from typing import Any, Mapping, Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .. import Color

EPSILON = alg.EPS

SPACE = 'xyz-d65'

# X, Y, and Z bar using a D65 illuminant and adapted such that sRGB white is flat and treated
# as a perfect reflector.
X_BAR = [
    6.4765443328975870e-05, 2.1965921863900288e-04, 1.1218495701418130e-03, 3.7709077850641360e-03,
    1.1894125472762583e-02, 2.3313065852836500e-02, 3.4598892069622564e-02, 3.7266235991980190e-02,
    3.2455116386009834e-02, 2.1256028912422780e-02, 1.0498727463182988e-02, 3.2915323998510305e-03,
    4.9285362540128340e-04, 9.2469550186137960e-04, 6.2432723686117830e-03, 1.6832890374744260e-02,
    2.8663248905918180e-02, 4.2656823918907440e-02, 5.6248743727935310e-02, 6.9477945953588140e-02,
    8.3074819223137340e-02, 8.6157833305662860e-02, 9.0506071101758860e-02, 8.5045373835735920e-02,
    7.0943303788413110e-02, 5.0655907934555350e-02, 3.5493284255175075e-02, 2.1480048693506407e-02,
    1.2523406569359068e-02, 6.8083730078566660e-03, 3.4665008463892226e-03, 1.4984475805421141e-03,
    7.7013130317381130e-04, 4.0759607307458727e-04, 1.6910500286726530e-04, 9.5277814775238820e-05,
    4.9058431269132036e-05, 2.0007341609267430e-05
]

Y_BAR = [
    1.8814452711296273e-06, 6.3314061008429530e-06, 3.1654185112952360e-05, 1.0691640272239762e-04,
    3.6047483572904885e-04, 9.6476796584806130e-04, 2.3016408715357418e-03, 4.2274866395607350e-03,
    6.7050985515775400e-03, 9.8966219118005600e-03, 1.5248665150656173e-02, 2.1410071671732686e-02,
    3.3406919900283610e-02, 5.1285057386464630e-02, 7.0370120171585710e-02, 8.7803323812575650e-02,
    9.4216423210304610e-02, 9.7929264004674780e-02, 9.4133573708589420e-02, 8.6772813940900010e-02,
    7.8859192278672880e-02, 6.3538603224853800e-02, 5.3760424866176890e-02, 4.2667858514245750e-02,
    3.1637511604749430e-02, 2.0900449222636230e-02, 1.3871178206739193e-02, 8.1094813433280600e-03,
    4.6341378691998400e-03, 2.4935868871856360e-03, 1.2604316103900520e-03, 5.4213557784198790e-04,
    2.7820445783924910e-04, 1.4724120992211030e-04, 6.1087985975207750e-05, 3.4418445746402460e-05,
    1.7722011096611667e-05, 7.2275103743479910e-06
]

Z_BAR = [
    3.0532669456856035e-04, 1.0378588328003280e-03, 5.3185279648379740e-03, 1.7972610017619628e-02,
    5.7135479496946820e-02, 1.1376679820364824e-01, 1.7353409074608858e-01, 1.9640441686864682e-01,
    1.8626897617472300e-01, 1.4008919736420150e-01, 8.9260240449878500e-02, 4.7938524074247056e-02,
    2.8164875747515875e-02, 1.6140356683993670e-02, 7.7490713608331450e-03, 4.2792922968061500e-03,
    1.9860155518430806e-03, 8.4142607319717330e-04, 3.5101091646138650e-04, 1.7662400927460388e-04,
    1.3829440231932083e-04, 8.5348094843855710e-05, 6.4192563360195540e-05, 2.7142423874658860e-05,
    1.5390056986897080e-05, 4.1065878438994570e-06, 1.9016388577533820e-06, 2.6595115553882350e-07,
    1.7964511291122375e-07, 1.0441329008350976e-07, 5.5567597652118840e-08, 2.4728357674356180e-08,
    1.2821197288505172e-08, 6.7856796831650190e-09, 2.8152697973324540e-09, 1.5861881245769394e-09,
    8.1672761779498350e-10, 3.3308343545695520e-10
]

# Reflectance curves for RGB which sum up to the white (with a reflectance of all ones).
# Since these were all solved together and add up to our perfect reflector, we can derive
# any curve within the sRGB gamut.
REF_R = [
    0.016897380848290185, 0.01689768966475472 , 0.016899064551474847, 0.01690601699724202 ,
    0.016932557626287592, 0.01702541241938885 , 0.017271835199589417, 0.017813206989478417,
    0.018789792562283796, 0.020180186090602473, 0.02083816509763065 , 0.016463478883260434,
    0.008684863990914615, 0.004754439789462918, 0.003390120364929663, 0.00315108805507146 ,
    0.003725686129944587, 0.005510477774775622, 0.01041635007123168 , 0.026612320853074693,
    0.10111873479035514 , 0.4768680015201364  , 0.8530277051769866  , 0.9430722284287628  ,
    0.9675126399418936  , 0.9764249335676783  , 0.9803841774223934  , 0.9822562193942365  ,
    0.983179007934218   , 0.9836295011271525  , 0.9838436013201767  , 0.9839419293432011  ,
    0.9839909995284102  , 0.9840149821320566  , 0.9840257562304665  , 0.9840310625076246  ,
    0.9840332917400199  , 0.9840339374369889
]

REF_G = [
    0.014613689609343882, 0.014616531398556894, 0.014629039037471817, 0.014691258428763041,
    0.014924205711561193, 0.01573217281188403 , 0.017908984198824363, 0.023228692834070305,
    0.03616316065287483 , 0.07167753632370133 , 0.18327935216927618 , 0.48245708265838383 ,
    0.7936598803055227  , 0.9188959178726537  , 0.9600992407959915  , 0.9751544064791383  ,
    0.9806963719510872  , 0.9812941965870734  , 0.9763765946122539  , 0.9574726936055697  ,
    0.8753265405810503  , 0.4912162313551131  , 0.12788626652361054 , 0.04589161994703497 ,
    0.024711069776853948, 0.01725382347909218 , 0.014014796520588032, 0.012503952572789986,
    0.011764857462193634, 0.011405503659073753, 0.011235066030786571, 0.011156866857667893,
    0.011117860273305774, 0.011098800704292242, 0.011090239236439411, 0.011086022908038085,
    0.011084251619981285, 0.011083738571320719
]

REF_B = [
    0.9684889295423659   , 0.9684857789366885   , 0.9684718964110532   , 0.968402724573995    ,
    0.9681432366621513   , 0.9672424147687272   , 0.9648191806015862   , 0.9589581001764513   ,
    0.9450470467848414   , 0.9081422775856963   , 0.7958824827330933   , 0.5010794384583558   ,
    0.19765525570356277  , 0.07634964233788341  , 0.03651063883907881  , 0.02169450546579016  ,
    0.015577941918968207 , 0.01319532563815096  , 0.013207055316514326 , 0.015914985541355748 ,
    0.02355472462859446  , 0.03191576712475044  , 0.019086028299402886 , 0.011036151624202156 ,
    0.00777629028125245  , 0.0063212429532295885, 0.005601026057018491 , 0.005239828032973596 ,
    0.005056134603588532 , 0.004964995213773781 , 0.004921332649036723 , 0.0049012037991308715,
    0.004891140198283912 , 0.004886217163650973 , 0.004884004533094174 , 0.004882914584337175 ,
    0.004882456639998865 , 0.004882323991690284
]

SIZE = len(X_BAR)
REFLECTANCE = [REF_R, REF_G, REF_B]


def calculate_mixing_concentration(t: float, l1: float, l2: float) -> tuple[float, float]:
    """Calculate the concentrations of the colors based on the interpolation progress and luminance."""

    # Get luminance but use a very small lightness if lightness is zero
    if l1 <= 0.0:
        l1 = EPSILON
    if l2 <= 0.0:
        l2 = EPSILON

    # Calculate the concentration of each reflectance curve.
    # This applies an easing function to the interpolation progress
    # that biases the color mixing towards the more luminous color.
    c1 = (1 - t) ** 2 * l1
    c2 = t ** 2 * l2
    total = c1 + c2
    c1 /= total
    c2 /= total

    return c1, c2


def km_to_ks(r: float) -> float:
    """Kubelka-Munk function that convert the reflectance to the KS coefficients that can be linearly mixed."""

    return (1 - r) ** 2 / (2 * r)


def km_to_r(ks: float) -> float:
    """Kubelka-Munk function that converts the absorption/scattering (KS) back to reflectance values."""

    return 1 + ks - alg.nth_root(ks ** 2 + 2 * ks, 2)


def xyz_to_concentration(xyz: Vector) -> Vector:
    """
    Convert XYZ to concentrations of the spectral curves of our palette.

    Concentrations should be constrained to [0, 1].
    """

    return [alg.clamp(c, 0.0, 1.0) for c in alg.matmul_x3(XYZ_TO_RGB, xyz, dims=alg.D2_D1)]


def single_constant_xyz_to_reflectance(xyz: Vector) -> tuple[Vector, Vector]:
    """
    Linear sRGB to a reflectance.

    For out of gamut colors, our concentrations are clipped to 0 - 1. Lastly, we ensure the
    final reflectance result is never zero with a small epsilon.

    Because out of gamut colors may be attenuated due to constraints on concentrations, we must
    also calculate the residual, left over weights of our XYZ value and return them as well. We can
    use the residual later to better approximate colors out of gamut by adding them back in.

    Returns the reflectance curve along with any residual.
    """

    c = xyz_to_concentration(xyz)
    r = [alg.clamp(sum([c[j] * p[i] for j, p in enumerate(REFLECTANCE)]), EPSILON, 1.0) for i in range(SIZE)]
    xyz2 = reflectance_to_xyz(r)
    return r, [xyz[0] - xyz2[0], xyz[1] - xyz2[1], xyz[2] - xyz2[2]]


def reflectance_to_xyz(r: Vector) -> Vector:
    """Convert the reflectance value to an XYZ value."""

    return [alg.vdot(r, X_BAR), alg.vdot(r, Y_BAR), alg.vdot(r, Z_BAR)]


def spectral_mix(xyz1: Vector, xyz2: Vector, t: float) -> Vector:
    """Interpolate two colors applying Kubelka-Munk theory."""

    # Convert the colors into a reflectance curve
    r1, res1 = single_constant_xyz_to_reflectance(xyz1)
    r2, res2 = single_constant_xyz_to_reflectance(xyz2)
    # Calculate weighting for the given interpolation factor using luminance.
    # This gives more weight to high luminance colors.
    c1, c2 = calculate_mixing_concentration(t, xyz1[1], xyz2[1])

    # Apply the Kubelka-Munk mixing.
    r = [km_to_r(km_to_ks(r1[i]) * c1 + km_to_ks(r2[i]) * c2) for i in range(SIZE)]

    # Convert the reflection back to XYZ and add back in any residual
    xyz1 = reflectance_to_xyz(r)
    xyz2 = [alg.lerp(r1, r2, t) for r1, r2 in zip(res1, res2)]
    return [xyz1[0] + xyz2[0], xyz1[1] + xyz2[1], xyz1[2] + xyz2[2]]


class InterpolatorSpectralContinuous(InterpolatorContinuous[AnyColor]):
    """Interpolate with continuous piecewise."""

    def interpolate(
        self,
        point: float,
        index: int
    ) -> Vector:
        """Interpolate."""

        # Interpolate between the values of the two colors for each channel.
        channels = []
        idx = index - 2 if index == self.length else index - 1

        # Handle spectral interpolation
        c1, c2 = self.coordinates[idx:idx + 2]
        channels = spectral_mix(
            [0.0 if math.isnan(i) else i for i in c1[:-1]],
            [0.0 if math.isnan(i) else i for i in c2[:-1]],
            self.ease(point, 0)
        )
        channels.append(alg.lerp(c1[-1], c2[-1], self.ease(point, len(c1) - 1)))
        return channels

    def ease(self, t: float, channel_index: int) -> float:
        """Provide a progression time and channel index."""

        progress = None
        if self.current_easing is not None:
            # Do we have an easing function, or mapping with a channel easing function?
            name = self.channel_names[channel_index]
            if isinstance(self.current_easing, Mapping):
                progress = self.current_easing.get(name) if name == 'alpha' else None
                if progress is None:
                    progress = self.current_easing.get('all')
            else:
                progress = self.current_easing

        return progress(t) if progress is not None else t


class InterpolatorSpectralLinear(InterpolatorLinear[AnyColor]):
    """Interpolate multiple ranges of colors using linear, Piecewise interpolation."""

    def interpolate(
            self,
            point: float,
            index: int
        ) -> Vector:
            """Interpolate."""

            i = (index - 1) * 2

            # Apply spectral interpolation
            c1, c2 = self.coordinates[i:i + 2]
            aidx = len(c1) - 1
            for i in range(len(c1)):
                a, b = c1[i], c2[i]
                if math.isnan(a) and math.isnan(b):
                    if i != aidx:
                        c1[i], c2[i] = 0.0, 0.0
                elif math.isnan(a):
                    c1[i] = b
                elif math.isnan(b):
                    c2[i] = a
            coords = spectral_mix(c1[:-1], c2[:-1], self.ease(point, 0))
            coords.append(alg.lerp(c1[aidx], c2[aidx], self.ease(point, aidx)))
            return coords

    def ease(self, t: float, channel_index: int) -> float:
        """Provide a progression time and channel index."""

        progress = None
        if self.current_easing is not None:
            # Do we have an easing function, or mapping with a channel easing function?
            name = self.channel_names[channel_index]
            if isinstance(self.current_easing, Mapping):
                progress = self.current_easing.get(name) if name == 'alpha' else None
                if progress is None:
                    progress = self.current_easing.get('all')
            else:
                progress = self.current_easing

        return progress(t) if progress is not None else t


class Spectral(Interpolate):
    """Linear interpolation plugin."""

    NAME = "spectral"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:
        """Return the linear interpolator."""

        return InterpolatorSpectralLinear(*args, **kwargs)

    def get_space(self, space: str | None, color_cls: type[Color]) -> str:
        """Filter specified spaces."""

        return SPACE

    def weighted_mix(
        self,
        color_cls: type[AnyColor],
        colors: Iterable[ColorInput],
        weights: Iterable[float] | None,
        space: str | None,
        premultiplied: bool = True,
        carryforward: bool = False,
        powerless: bool = False,
        hue: str = 'shorter',
        **kwargs: Any
    ) -> AnyColor:
        """Mix a list of colors together with weights."""

        space = self.get_space(space, color_cls)

        # Get channel information
        obj = color_cls(space, [])
        avgs = [0.0] * SIZE
        res_avgs = [0.0] * 4
        counts = [0] * SIZE
        res_counts = [0] * 4
        wavg = 0.0
        cavg = 0.0
        no_weights = not weights
        if no_weights:
            weights = ()
        mx = 0.0

        # Sum channel values using a rolling average. Apply premultiplication and additional weighting as required.
        count = 0
        sentinel = Sentinel()
        fill = 1 if no_weights else sentinel
        for c, w in it.zip_longest(colors, [] if no_weights else weights, fillvalue=fill):  # type: ignore[arg-type]

            # Handle explicit weighted cases
            if not no_weights:
                # If there are more weights than colors, ignore additional weights
                if c is sentinel:
                    break

                # If there are less weights than colors, assume full weight for colors without weights
                if w is sentinel:
                    w = mx

                # Negative weights are considered as zero weight
                if w < 0.0:
                    w = 0.0

                # Track the largest weight so we can populate colors with no weights
                elif w > mx:
                    mx = w

            obj.update(c)  # type: ignore[arg-type]

            coords = obj.coords(nans=False)

            count += 1

            # Include alpha in average if it is defined. If not defined, skip, but assume color is opaque.
            alpha = obj.alpha()
            if math.isnan(alpha):
                alpha = 1.0
            else:
                res_counts[-1] += 1
                res_avgs[-1] += ((alpha *  w) - res_avgs[-1]) / res_counts[-1]

            # Premultiply alpha
            if premultiplied:
                coords = [x * alpha for x in coords]

            # Calculate the reflectance and residual XYZ value
            r, res = single_constant_xyz_to_reflectance(coords)

            # Adjust the weight for the spectral mixing based on the luminance
            lfactor = w ** 2 * coords[1]
            # Average of weights
            wavg += (w - wavg) / count
            # Average of concentration
            cavg += (lfactor - cavg) / count

            # Apply mixing
            ks = 0.0
            for i in range(SIZE):
                # Mix the scattering and absorption coefficients
                ks = (1 - r[i]) ** 2 / (2 * r[i])
                counts[i] += 1
                n = counts[i]
                avgs[i] += (ks * lfactor - avgs[i]) / n

                # Mix the residual
                if i < 3:
                    coord = res[i]
                    res_counts[i] += 1
                    n = res_counts[i]
                    res_avgs[i] += (coord * w - res_avgs[i]) / n

        if not count:
            raise ValueError('At least one color must be provided in order to average colors')

        # Convert back to reflectance
        xyz1 = reflectance_to_xyz([km_to_r(ks / (cavg or 1)) for ks in avgs])

        # Add in residual and undo premultiplication to get the final color.
        if not wavg:
            wavg = math.nan
        res_avgs[-1] = alpha = math.nan if not res_counts[-1] else res_avgs[-1] / wavg
        factor = 1 if not premultiplied or not alpha or (math.isnan(alpha) and not math.isnan(wavg)) else alpha
        xyz = [(xyz1[0] + res_avgs[0]) / factor, (xyz1[1] + res_avgs[1]) / factor, (xyz1[2] + res_avgs[2]) / factor]

        # Create the color.
        color = obj.update(space, xyz, res_avgs[-1])
        return color


class SpectralContinuous(Spectral):
    """Linear interpolation plugin."""

    NAME = "spectral-continuous"

    def interpolator(self, *args: Any, **kwargs: Any) -> Interpolator[AnyColor]:
        """Return the linear interpolator."""

        return InterpolatorSpectralContinuous(*args, **kwargs)
