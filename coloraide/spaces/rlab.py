"""
RLAB.

https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=1153&context=article
Compared against http://markfairchild.org/files/AppModEx.xls
"""
from __future__ import annotations
from ..cat import WHITES
from .. import util
from ..spaces.lab import Lab
from .. import algebra as alg
from ..types import Vector, VectorLike, Matrix
from ..channels import Channel, FLG_MIRROR_PERCENT

R = [
    [1.9569, -1.1882, 0.2313],
    [0.3612, 0.6388, 0.0],
    [0.0, 0.0, 1.0000]
]

# Equal energy Hunt-Pointer-Estevez
M = [
    [0.38971, 0.68898, -0.07868],
    [-0.22981, 1.18340, 0.04641],
    [0.00000, 0.00000, 1.00000]
]

# Defaults
YN = 318.0  # `318 cd / m^2`

# Sigma is usually defined as 1 / x, but we are using x due to the way we use them
SURROUND = {
    "average": 2.3,
    "dim": 2.9,
    "dark": 3.5
}

D = {
    # Full discounting
    "hard-copy": 1.0,
    # When no visual data are available and an intermediate value is
    # necessary, a value of 0.5 should be chosen and refined with experience.
    # An intermediate value is often needed for projected transparencies in completely darkened rooms.
    "projected-transparency": 0.5,
    # No discounting
    "soft-copy": 0.0
}


class Environment:
    """RLAB environment."""

    def __init__(self, white: VectorLike, adapting_luminance: float, surround: float, discounting: float) -> None:
        """Initialize."""

        self.xyz_w = util.xy_to_xyz(white)
        self.surround = surround
        self.yn = adapting_luminance
        self.d = discounting
        self.ram = self.calc_ram()
        self.iram = alg.inv(self.ram)

    def calc_ram(self) -> Matrix:
        """Calculate RAM."""

        lms = alg.matmul(M, self.xyz_w)
        a = []  # type: Vector
        s = sum(lms)
        for c in lms:
            l = (3.0 * c) / s
            p = (1.0 + alg.nth_root(self.yn, 3) + l) / (1.0 + alg.nth_root(self.yn, 3) + 1.0 / l)
            a.append((p + self.d * (1.0 - p)) / c)
        A = alg.diag(a)
        return alg.multi_dot([R, A, M])  # type: ignore[no-any-return]


def rlab_to_xyz(rlab: Vector, env: Environment) -> Vector:
    """RLAB to XYZ."""

    LR, aR, bR = rlab
    yr = LR / 100
    xr = alg.npow((aR / 430) + yr, env.surround)
    zr = alg.npow(yr - (bR / 170), env.surround)
    return alg.matmul(env.iram, [xr, alg.npow(yr, env.surround), zr], dims=alg.D2_D1)


def xyz_to_rlab(xyz: Vector, env: Environment) -> Vector:
    """XYZ to RLAB."""

    xyz_ref = alg.matmul(env.ram, xyz, dims=alg.D2_D1)
    xr, yr, zr = [alg.nth_root(c, env.surround) for c in xyz_ref]
    LR = 100 * yr
    aR = 430 * (xr - yr)
    bR = 170 * (yr - zr)
    return [LR, aR, bR]


class RLAB(Lab):
    """RLAB class."""

    BASE = 'xyz-d65'
    NAME = "rlab"
    SERIALIZE = ("--rlab",)
    WHITE = WHITES['2deg']['D65']
    CHANNELS = (
        Channel("l", 0.0, 100.0),
        Channel("a", -125.0, 125.0, flags=FLG_MIRROR_PERCENT),
        Channel("b", -125.0, 125.0, flags=FLG_MIRROR_PERCENT)
    )
    # Using less than full discounting would require special achromatic handling
    # to identify achromatic colors as `a == b == 0.0` would no longer be true.
    ENV = Environment(WHITE, YN, SURROUND['average'], D['hard-copy'])

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Hunter Lab."""

        return rlab_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Hunter Lab."""

        return xyz_to_rlab(coords, self.ENV)
