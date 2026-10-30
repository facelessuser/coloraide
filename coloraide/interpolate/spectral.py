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
- Use only 3 curves: R, G, and B.
- Provided adaptation for CSS white to the perfect reflector white in our CMFs.
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

# X, Y, and Z bar using a D65 illuminant. We also fold in the Bradford adaptation matrix to
# adapt CSS white to the ideal, perfect reflector white.
X_BAR = [
    6.4736947826811400e-05, 2.1956264007550312e-04, 1.1213566733160700e-03, 3.7692552397073065e-03,
    1.1888944903221505e-02, 2.3303133733586997e-02, 3.4584846035689250e-02, 3.7252504948711510e-02,
    3.2445525794260540e-02, 2.1253660509254035e-02, 1.0504341954355083e-02, 3.3036740740067542e-03,
    5.1289379262680400e-04, 9.5422815137015560e-04, 6.2799553757071650e-03, 1.6872541854411744e-02,
    2.8698776832701510e-02, 4.2685313996378710e-02, 5.6266170763064960e-02, 6.9482511149091490e-02,
    8.3065970839552300e-02, 8.6138169882277750e-02, 9.0477953538710340e-02, 8.5014441623895920e-02,
    7.0915227839520210e-02, 5.0634889569258275e-02, 3.5478112917933020e-02, 2.1470703324347393e-02,
    1.2517904037996158e-02, 6.8053667397941440e-03, 3.4649649200587823e-03, 1.4977820988416597e-03,
    7.6978903130333020e-04, 4.0741492388864440e-04, 1.6902984700390314e-04, 9.5235470164408430e-05,
    4.9036628077573460e-05, 1.9998449683952883e-05
]

Y_BAR = [
    1.8617051900832975e-06, 6.2644749109438730e-06, 3.1312399291295340e-05, 1.0576926058516144e-04,
    3.5687194204443983e-04, 9.5782608252555450e-04, 2.2917216880374053e-03, 4.2175740672645250e-03,
    6.6977803149861640e-03, 9.8940681485782960e-03, 1.5251393239089125e-02, 2.1417133408224244e-02,
    3.3419003991751090e-02, 5.1303107477263965e-02, 7.0392712060947040e-02, 8.7827891946908110e-02,
    9.4238601068612600e-02, 9.7947268898618570e-02, 9.4144915491072890e-02, 8.6776377593200280e-02,
    7.8854640615538220e-02, 6.3527423181966400e-02, 5.3744084221697160e-02, 4.2649725148111840e-02,
    3.1620985018261600e-02, 2.0888050473096238e-02, 1.3862217026915463e-02, 8.1039572125423400e-03,
    4.6308839298031040e-03, 2.4918087556972870e-03, 1.2595230192715412e-03, 5.4174186809321510e-04,
    2.7800195826154525e-04, 1.4713403595693311e-04, 6.1043521232771520e-05, 3.4393393247233040e-05,
    1.7709111593449580e-05, 7.2222496115619380e-06
]

Z_BAR = [
    3.0528841114314006e-04, 1.0377287245403855e-03, 5.3178613507298385e-03, 1.7970358832144803e-02,
    5.7128333720099370e-02, 1.1375264401073360e-01, 1.7351272960862366e-01, 1.9638068898284697e-01,
    1.8624719905185550e-01, 1.4007397650710518e-01, 8.9252471336068800e-02, 4.7937045129877230e-02,
    2.8168084564841756e-02, 1.6148277476228190e-02, 7.7611720114444910e-03, 4.2943243250882215e-03,
    2.0016557287951480e-03, 8.5687303991080070e-04, 3.6478973831377375e-04, 1.8804642104684360e-04,
    1.4721285959615142e-04, 9.1124299712303060e-05, 6.7786938145781300e-05, 2.9026849261459415e-05,
    1.6208563778221368e-05, 4.3695537780151650e-06, 1.9385489124105125e-06, 2.3400670117110803e-07,
    1.4311289016519172e-07, 7.9637345282367350e-08, 4.1201111745673100e-08, 1.8002292387894766e-08,
    9.2827570966138650e-09, 4.9129465016869470e-09, 2.0383022105031880e-09, 1.1484277023466018e-09,
    5.9132437783611940e-10, 2.4115792470975265e-10
]

# Reflectance curves for RGB which sum up to white with a perfect reflectance of all ones.
# Since these were all solved together and add up to our perfect reflector, we can derive
# any curve within the sRGB gamut.
REF_R = [
    0.028234536033744817 , 0.02823052270005566  , 0.028212949614484728 , 0.028126471431092037 ,
    0.02781169124983962  , 0.026799952467841615 , 0.024546999291522487 , 0.020714681656291423 ,
    0.015605440484912914 , 0.010647862990977752 , 0.007188556637466925 , 0.0051026604607462   ,
    0.003883951888940196 , 0.003227162936649375 , 0.002992351303220009 , 0.0031643788045365717,
    0.003922020755887601 , 0.005869727206960218 , 0.011249651245967218 , 0.029894307705677026 ,
    0.11445162456032115  , 0.48515305921988927  , 0.8445014244266669   , 0.9365826507700583   ,
    0.9623523666994167   , 0.9719023844794688   , 0.9761961207078744   , 0.9782437028093232   ,
    0.9792583074832387   , 0.9797550944945298   , 0.9799915921457957   , 0.9801003025387628   ,
    0.9801545726974805   , 0.9801811002032583   , 0.9801930183420842   , 0.9801988882297552   ,
    0.9802013542742258   , 0.9802020685672341
]

REF_G = [
    0.00879984465166267 , 0.008802348439640006, 0.008813363197139934, 0.008868155583432624,
    0.009073885398365122, 0.009797061544155439, 0.011818544670339381, 0.017127175704826747,
    0.031147100632307134, 0.0710835920148532  , 0.19915705039104414 , 0.528573565982872   ,
    0.8177143803782764  , 0.9235318185769124  , 0.9583284182200668  , 0.9710504238684192  ,
    0.9752589317346498  , 0.9746773553940316  , 0.9686415151258687  , 0.9490461599888047  ,
    0.8657609519775569  , 0.49796867981851456 , 0.141491675876031   , 0.05167199391801741 ,
    0.027467642231140343, 0.018899304975187714, 0.015191625522440855, 0.01346982761293275 ,
    0.012630068496716162, 0.01222247545968247 , 0.012029317299614428, 0.011940727439864296,
    0.011896547785383071, 0.011874963455554277, 0.011865268523777728, 0.01186049412740764 ,
    0.011858488419550117, 0.011857907474398077
]

REF_B = [
    0.9629656193145923  , 0.9629671288603043  , 0.9629736871883753  , 0.9630053729854753  ,
    0.9631144233517952  , 0.963402985988003   , 0.9636344560381381  , 0.9621581426388817  ,
    0.95324745888278    , 0.918268544994169   , 0.7936543929714891  , 0.46632377355638205 ,
    0.17840166773278338 , 0.07324101848643833 , 0.03867923047671329 , 0.025785197327044262,
    0.020819047509462674, 0.01945291739900812 , 0.02010883362816407 , 0.02105953230551827 ,
    0.019787423462122034, 0.01687826096159617 , 0.014006899697302122, 0.011745355311924388,
    0.010179991069443117, 0.009198310545343535, 0.008612253769684719, 0.008286469577744038,
    0.008111624020044894, 0.00802243004578762 , 0.007979090554590007, 0.007958970021372858,
    0.007948879517136409, 0.007943936341187452, 0.007941713134138162, 0.007940617642837045,
    0.00794015730622405 , 0.007940023958367959
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
