"""
HCT color space.

This implements the HCT color space as described. This is not a port of the Material library.
We simply, as described, create a color space with CIELAB L* and CAM16's C and h components.
Environment settings are calculated with the assumption of L* 50.

As ColorAide usually cares about setting powerless hues as NaN, especially for good interpolation,
we've also calculated the cut off for chromatic colors and will properly enforce achromatic, powerless
hues. This is because CAM16 actually resolves colors as achromatic before chroma reaches zero as
lightness increases. In the SDR range, a Tone of 100 will have a cut off as high as ~2.87 chroma.

Generally, the HCT color space is restricted to sRGB and SDR range in the Material library, but we do
not have such restrictions.

Though we did not port HCT from Material Color Utilities, we did test against it, and are pretty
much on point. The only differences are due to matrix precision and white point precision. Material
uses an RGB <-> XYZ matrix that rounds values off significantly more than we do. Also, while we
calculate the XYZ points from the `xy` points without rounding, they have rounded XYZ points. Lastly,
the gamut mapping algorithm we use is likely different even though it arrives at pretty much the same
result, so slightly different values can occur.

Material:

```
> hct.Hct.fromInt(0xff305077)
Hct {
  argb: 4281356407,
  internalHue: 256.8040416857594,
  internalChroma: 31.761442797741243,
  internalTone: 33.34501410942328
}
```

ColorAide:

```
>>> from coloraide_extras.everything import ColorAll as Color
>>> Color('#305077').convert('hct')
color(--hct 256.79 31.766 33.344 / 1)
```

"""
from __future__ import annotations
from .. import algebra as alg
from ..spaces import Space, LChish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .cam16_jmh import Environment, cam16_to_xyz_d65, xyz_d65_to_cam16
from .cam16_jmh import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from .lab import EPSILON, KAPPA, KE
from ..types import Vector, Matrix  # noqa: F401
from typing import Any
import math

ACHROMATIC_RESPONSE = [
    [0.06991457401674239, 0.14894004649491985, 209.54685746644427],
    [0.13982914803348123, 0.19600973408107872, 209.54683151375164],
    [0.20974372205022362, 0.2284758840823509, 209.54681244250116],
    [0.279658296066966, 0.2539510473857674, 209.54679680373425],
    [0.34957287008370486, 0.27520353123076896, 209.54678330540025],
    [0.6991457401674133, 0.3503388633000774, 209.54673233806204],
    [1.0487186102511181, 0.4013845937276958, 209.54669489478562],
    [1.398291480334823, 0.44114839784490845, 209.54666419686697],
    [1.7478643504185314, 0.474176553523894, 209.5466377050236],
    [2.0974372205022362, 0.5026634742613169, 209.54661414586045],
    [2.447010090585941, 0.5278524887931191, 209.5465927758291],
    [2.7965829606696495, 0.5505226723840896, 209.5465731172251],
    [3.1624547958278697, 0.5721193279495548, 209.54655401960312],
    [3.5553195764898433, 0.5933528830664249, 209.5465348955287],
    [3.9752712774319967, 0.6142212187429537, 209.5465157686296],
    [4.422818762249047, 0.6347462660662626, 209.54649663922487],
    [4.89845719045681, 0.6549477974516251, 209.54647750762507],
    [5.40266895987223, 0.6748437111130419, 209.54645837410766],
    [5.93592454797767, 0.6944502696114525, 209.54643923893252],
    [6.4986832666748775, 0.7137823011126716, 209.5464201023271],
    [7.091393942308237, 0.732853370157594, 209.54640096452033],
    [7.714495530830426, 0.7516759233486977, 209.54638182570906],
    [8.362902589291522, 0.7702614142702398, 209.54636268608706],
    [9.010442756551821, 0.7886204111203621, 209.54634354582225],
    [9.653817900540862, 0.8067626898669605, 209.5463244050959],
    [10.29318377392433, 0.8246973152252656, 209.5463052640459],
    [10.928685772528809, 0.8424327113314977, 209.5462861228275],
    [11.56045990779819, 0.8599767236656302, 209.54626698157904],
    [12.188633662809302, 0.8773366735026917, 209.5462478404262],
    [12.813326748632115, 0.8945194059620861, 209.54622869948886],
    [13.434651775012771, 0.9115313325460387, 209.54620955888788],
    [14.0527148470809, 0.9283784689195937, 209.54619041872914],
    [14.667616097925809, 0.9450664685622908, 209.5461712791161],
    [15.279450165363095, 0.9616006528304082, 209.54615214014845],
    [15.888306619956744, 0.9779860378836129, 209.54613300191994],
    [16.494270350320917, 0.9942273588675171, 209.54611386451774],
    [17.097421910858294, 1.0103290916839778, 209.5460947280279],
    [17.697837836366574, 1.026295472637739, 209.5460755925407],
    [18.295590927334914, 1.0421305162064542, 209.54605645811773],
    [18.890750509238096, 1.057838031146838, 209.54603732484748],
    [19.483382668700436, 1.0734216351263122, 209.54601819278727],
    [20.073550469030984, 1.088884768038463, 209.54599906201673],
    [20.661314147315657, 1.1042307041468111, 209.54597993259077],
    [21.24673129498138, 1.1194625631780193, 209.54596080458563],
    [21.829857023514606, 1.1345833204761497, 209.54594167805195],
    [22.41074411681668, 1.1495958163105326, 209.54592255304232],
    [22.989443171504917, 1.164502764423835, 209.54590342962592],
    [23.566002726318594, 1.1793067598944942, 209.5458843078509],
    [24.140469381658278, 1.1940102863793578, 209.54586518776134],
    [24.71288791017345, 1.208615722794075, 209.54584606941722],
    [25.283301359213652, 1.2231253494868157, 209.54582695285913],
    [25.851751145872043, 1.2375413539480247, 209.5458078381372],
    [26.418277145272675, 1.2518658361006216, 209.5457887252938],
    [32.53317505979514, 1.4039207501018756, 209.5455786194677],
    [58.346464585181536, 2.0040978388926978, 209.54462755393828],
    [82.04578167434552, 2.5102950876783927, 209.54368432153106],
    [104.37764532041983, 2.957132646110733, 209.54274979150162],
    [125.71227094822433, 3.3610704881488145, 209.54182435083504],
    [146.26918350453806, 3.731633656682073, 209.5409081799222],
    [166.19277583771807, 4.074995088257203, 209.54000135154777],
    [185.58476265482338, 4.395465139909588, 209.53910387571688],
    [204.52038939834455, 4.696217703676614, 209.53821572300697],
    [223.05740651867518, 4.979684699789179, 209.5373368379916],
    [241.2414278875509, 5.247788076344199, 209.53646714753637],
    [259.10932108008694, 5.502084789195138, 209.53560656613365],
    [276.69145334478924, 5.743861871175241, 209.53475499956414],
    [294.01323625159637, 5.9742012642698965, 209.53391234742955],
    [311.09622156929686, 6.194025494618159, 209.5330785049965],
    [327.9588994483437, 6.404130748156792, 209.5322533645655],
    [344.61729300144975, 6.60521139322382, 209.53143681641436],
    [361.08540993083295, 6.797878536697256, 209.53062874966722],
    [377.375591468867, 6.9826743184757625, 209.5298290527965],
    [393.4987860653063, 7.160083098082503, 209.52903761414294],
    [409.4647669400027, 7.330540332852221, 209.52825432223364]
]  # type: Matrix

INV_ACHROMATIC_RESPONSE = [
    [-44570.454917014395, 4.984058427842426, 29.528254322233643],
    [-39738.74229269304, 4.868992098048034, 29.529037614142972],
    [-35227.22948703891, 4.749243790113306, 29.5298290527965],
    [-31029.54799495578, 4.624521731030067, 29.530628749667212],
    [-27139.129218104852, 4.494501608270974, 29.53143681641436],
    [-23549.186758448897, 4.358820705994274, 29.53225336456548],
    [-20252.696013957233, 4.217070528241072, 29.533078504996485],
    [-17242.37047122224, 4.068787389324386, 29.533912347429574],
    [-14510.633904472961, 3.9134402232209555, 29.534754999564143],
    [-12049.587431138627, 3.7504145097188952, 29.535606566133662],
    [-9850.9700030737, 3.57899065066929, 29.53646714753636],
    [-7906.1103682456205, 3.3983141993252333, 29.537336837991614],
    [-6205.867715825722, 3.2073537531209646, 29.53821572300699],
    [-4740.556934184132, 3.004839469667562, 29.539103875716876],
    [-3499.8523254905363, 2.7891697871907946, 29.54000135154777],
    [-2472.6600640203656, 2.5582631140416034, 29.540908179922234],
    [-1646.9432511982377, 2.309307714994031, 29.54182435083504],
    [-1009.4708758426449, 2.038306399455464, 29.542749791501617],
    [-545.4349987904753, 1.7391570082516687, 29.543684321531057],
    [-237.81389477171723, 1.4014938491794258, 29.54462755393829],
    [-66.15647758957148, 1.0042248527096727, 29.545578619467726],
    [-44.16877329851594, 0.9045142761589678, 29.54578872529381],
    [-42.42258854100067, 0.8951499834879552, 29.54580783813722],
    [-40.71735152221153, 0.885731507008267, 29.545826952859137],
    [-39.05278319774536, 0.8762577488471229, 29.545846069417227],
    [-37.428601621130795, 0.8667275715376151, 29.54586518776134],
    [-35.84452186191744, 0.8571397960298269, 29.545884307850905],
    [-34.300255919939744, 0.8474931995804906, 29.545903429625927],
    [-32.795512635504856, 0.8377865135106229, 29.545922553042335],
    [-31.329997595230186, 0.8280184208260168, 29.54594167805195],
    [-29.90341303323391, 0.8181875536890815, 29.545960804585643],
    [-28.51545772735428, 0.8082924907335349, 29.54597993259078],
    [-27.165826890045, 0.7983317542132449, 29.54599906201674],
    [-25.854212053560502, 0.7883038069759454, 29.546018192787304],
    [-24.580300949008887, 0.7782070492505507, 29.54603732484749],
    [-23.343777378809595, 0.7680398152420924, 29.54605645811775],
    [-22.144321082046854, 0.7578003695232353, 29.5460755925407],
    [-20.981607592159143, 0.7474869032182557, 29.54609472802791],
    [-19.855308086347, 0.7370975299714788, 29.54611386451775],
    [-18.76508922601634, 0.7266302817017825, 29.54613300191993],
    [-17.710612987501253, 0.7160831041421349, 29.546152140148457],
    [-16.69153648222621, 0.7054538521739349, 29.546171279116077],
    [-15.70751176537303, 0.6947402849727958, 29.546190418729164],
    [-14.75818563200937, 0.6839400609923351, 29.54620955888788],
    [-13.843199399511406, 0.6730507328308233, 29.546228699488893],
    [-12.962188674970657, 0.6620697420440577, 29.5462478404262],
    [-12.11478310611083, 0.6509944140004065, 29.546266981579034],
    [-11.300606114050115, 0.6398219529102014, 29.54628612282749],
    [-10.519274606023421, 0.6285494372210045, 29.546305264045923],
    [-9.770398665921691, 0.6171738156416642, 29.546324405095888],
    [-9.053581220203, 0.6056919041652574, 29.54634354582226],
    [-8.36841767637534, 0.5941003846022807, 29.546362686087097],
    [-7.714495530830426, 0.5823958053405168, 29.54638182570907],
    [-7.091393942308239, 0.5705745853224489, 29.54640096452036],
    [-6.4986832666748775, 0.5586330226371172, 29.5464201023271],
    [-5.9359245479776686, 0.5465673096808428, 29.546439238932532],
    [-5.402668959872228, 0.5343735576616648, 29.546458374107672],
    [-4.89845719045681, 0.5220478343999755, 29.546477507625063],
    [-4.422818762249047, 0.5095862211204446, 29.546496639224877],
    [-3.9752712774319967, 0.49698489651743805, 29.546515768629586],
    [-3.555319576489845, 0.4842402602948852, 29.546534895528715],
    [-3.1624547958278697, 0.4713491143947718, 29.54655401960312],
    [-2.7965829606696477, 0.45832488304806807, 29.546573117225094],
    [-2.447010090585943, 0.4447586387623133, 29.546592775829115],
    [-2.0974372205022362, 0.42982773750036296, 29.546614145860463],
    [-1.7478643504185296, 0.4131501637871255, 29.54663770502361],
    [-1.398291480334823, 0.39414263959389384, 29.546664196866974],
    [-1.04871861025112, 0.37184420794844997, 29.546694894785634],
    [-0.6991457401674115, 0.3445030170602825, 29.546732338062064],
    [-0.3495728700837084, 0.30872069573903993, 29.54678330540024],
    [-0.27965829606696424, 0.3002727676037857, 29.546796803734274],
    [-0.20974372205022362, 0.291838255404801, 29.54681244250118],
    [-0.13982914803348123, 0.28544551295072706, 29.546831513751652],
    [-0.06991457401674062, 0.2970033564541394, 29.546857466444255]
]  # type: Matrix


def y_to_lstar(y: float) -> float:
    """Convert XYZ Y to Lab L*."""

    fy = alg.nth_root(y, 3) if y > EPSILON else (KAPPA * y + 16) / 116
    return (116.0 * fy) - 16.0


def lstar_to_y(lstar: float) -> float:
    """Convert Lab L* to XYZ Y."""

    fy = (lstar + 16) / 116
    y = fy ** 3 if lstar > KE else lstar / KAPPA
    return y


def hct_to_xyz(coords: Vector, env: Environment) -> Vector:
    """
    Convert HCT to XYZ.

    Use Newton's method to try and converge as quick as possible or converge as
    close as we can. While the requested precision is achieved most of the time,
    it may not always be achievable. Especially past the visible spectrum, the
    algorithm will likely struggle to get the same precision. If, for whatever
    reason, we cannot achieve the accuracy we seek in the allotted iterations,
    just return the closest we were able to get.
    """

    h, c, t = coords[:]

    # Shortcut out for black
    if t == 0:
        return [0.0, 0.0, 0.0]

    # Calculate the Y we need to target
    y = lstar_to_y(t)

    # Try to start with a reasonable initial guess for J
    # Calculated by curve fitting J vs T.
    if t > 0:
        j = 0.00379058511492914 * t ** 2 + 0.608983189401032 * t + 0.9155088574762233
    else:
        j = 9.514440756550361e-06 * t ** 2 + 0.08693057439788597 * t -21.928975842194614

    # Threshold of how close is close enough, and max number of attempts.
    # More precision and more attempts means more time spent iterating.
    # Higher required precision gives more accuracy but also increases the
    # chance of not hitting the goal. 2e-12 allows us to convert round trip
    # with reasonable accuracy of six decimal places or more.
    threshold = 2e-12
    max_attempt = 15

    attempt = 0
    last = math.inf
    best = j

    # Try to find a J such that the returned y matches the returned y of the L*
    while attempt <= max_attempt:
        xyz = cam16_to_xyz_d65(J=j, C=c, h=h, env=env)

        # If we are within range, return XYZ
        # If we are closer than last time, save the values
        delta = abs(xyz[1] - y)
        if delta < last:
            if delta <= threshold:
                return xyz
            best = j
            last = delta

        # ```
        # f(j_root) = (j ** (1 / 2)) * 0.1
        # f(j) = ((f(j_root) * 100) ** 2) / j - 1 = 0
        # f(j_root) = Y = y / 100
        # f(j) = (y ** 2) / j - 1
        # f'(j) = (2 * y) / j
        # ```
        j = j - (xyz[1] - y) * j / (2 * xyz[1])

        attempt += 1

    # We could not acquire the precision we desired, return our closest attempt.
    return cam16_to_xyz_d65(J=best, C=c, h=h, env=env)  # pragma: no cover


def xyz_to_hct(coords: Vector, env: Environment) -> Vector:
    """Convert XYZ to HCT."""

    t = y_to_lstar(coords[1])
    if t == 0.0:
        return [0.0, 0.0, 0.0]
    c, h = xyz_d65_to_cam16(coords, env)[1:3]
    return [h, c, t]


class Achromatic(_Achromatic):
    """Test HCT achromatic response."""

    # Lightness and chroma (equivalent) index.
    L_IDX = 2
    C_IDX = 1
    H_IDX = 0

    def convert(self, coords: Vector, *, env: Environment, **kwargs: Any) -> Vector:  # type: ignore[override]
        """Convert to the target color space."""

        return xyz_to_hct(lin_srgb_to_xyz(lin_srgb(coords)), env)


class HCT(LChish, Space):
    """HCT class."""

    BASE = "xyz-d65"
    NAME = "hct"
    SERIALIZE = ("--hct",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(
        WHITE,
        200 / math.pi * lstar_to_y(50.0),
        lstar_to_y(50.0) * 100,
        'average',
        False
    )
    CHANNEL_ALIASES = {
        "lightness": "t",
        "tone": "t",
        "chroma": "c",
        "hue": "h"
    }

    # Achromatic detection
    # Precalculated from:
    # [
    #     (1, 5, 1, 1000.0),
    #     (1, 50, 1, 200.0),
    #     (30, 551, 25, 100.0)
    # ]
    ACHROMATIC = Achromatic(
        ACHROMATIC_RESPONSE,
        0.0053,
        0.0395,
        8.1,
        'catrom',
        env=ENV,
    )

    # Precalculated from:
    # [
    #     (1, 5, 1, 1000.0),
    #     (1, 50, 1, 200.0),
    #     (30, 551, 25, 100.0)
    # ]
    INV_ACHROMATIC = Achromatic(
        INV_ACHROMATIC_RESPONSE,
        0.0049,
        0.0646,
        5.8,
        'catrom',
        env=ENV,
        negative=True
    )


    CHANNELS = (
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE),
        Channel("c", 0.0, 145.0),
        Channel("t", 0.0, 100.0)
    )

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        # Treat tone less than zero as black
        t = coords[2]
        achromatic = self.INV_ACHROMATIC if t < 0 else self.ACHROMATIC

        if index == 0:
            h = coords[0]
            return achromatic.get_ideal_hue(t, coords[1]) if math.isnan(h) else h

        elif index == 1:
            c = coords[1]
            return achromatic.get_ideal_chroma(t) if math.isnan(c) else c

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[0] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        if coords[2] == 0:
            return True

        coords = self.normalize(coords)

        if coords[2] < 0:
            return self.INV_ACHROMATIC.test(coords[2], coords[1], coords[0])

        return self.ACHROMATIC.test(coords[2], coords[1], coords[0])

    def names(self) -> tuple[str, ...]:
        """Return LCh-ish names in the order L C h."""

        channels = self.channels
        return channels[2], channels[1], channels[0]

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        return hct_to_xyz(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        return xyz_to_hct(coords, self.ENV)
