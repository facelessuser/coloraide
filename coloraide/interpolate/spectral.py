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

X_BAR = [
    6.4691998957636e-05, 0.00021940989981324543, 0.0011205743509342526, 0.003766613411711093,
    0.011880553603799004, 0.023286442419177128, 0.034559418196974744, 0.03722379011620067,
    0.03241837610914861, 0.021233205609381033, 0.01049099076854208, 0.003295837579793109,
    0.0005070351633801336, 0.0009486742057141478, 0.006273718099831793, 0.0168646241897775,
    0.028689649025980982, 0.04267481246917313, 0.05625474813113776, 0.06947039726771581,
    0.08305315169982916, 0.08612609630022569, 0.09046613768477696, 0.08500386505912774,
    0.0709066691074488, 0.050628891637364504, 0.03547396188526398, 0.021468210259706556,
    0.012516456761911689, 0.006804581639016529, 0.0034645657946526308, 0.0014976097506959416,
    0.000769700480928044, 0.00040736805813154517, 0.0001690104031613905, 9.5224515036545e-05,
    4.903098729584765e-05, 1.999614922216866e-05
]

Y_BAR = [
    1.8442894439676924e-06, 6.205323586516486e-06, 3.100960467994158e-05, 0.00010474838492692305,
    0.00035364052995383256, 0.0009514714056444336, 0.0022822631748317997, 0.004207329043473007,
    0.006688798371901364, 0.009888396019356503, 0.015249451449631114, 0.02141831094497228,
    0.033422930157506775, 0.05131001349185122, 0.070402083939949, 0.0878387072603517,
    0.0942490536184086, 0.09795667027189314, 0.09415218568626084, 0.08678102374867531,
    0.07885653386320132, 0.06352670262035551, 0.05374141675682006, 0.042646064357411986,
    0.03161734927927079, 0.020885205921391023, 0.01386011013601517, 0.008102640203839865,
    0.004630102258802989, 0.0024913800051319097, 0.0012593033677377537, 0.0005416465221680035,
    0.00027795289200670086, 0.00014710806738544828, 6.103274729272546e-05, 3.43873229523396e-05,
    1.7705986005253943e-05, 7.220974912993785e-06
]

Z_BAR = [
    0.00030501714763797594, 0.0010368066663574284, 0.0053131363323992, 0.01795439258995359,
    0.05707758153454857, 0.11365161893628682, 0.17335872618354975, 0.19620657555865664,
    0.18608237070629596, 0.13995047538320737, 0.08917452942686492, 0.04789621135170755,
    0.02814562539579518, 0.01613766229505142, 0.0077591019215213644, 0.00429614837366175,
    0.002005509212215613, 0.0008614711098801786, 0.0003690387177652434, 0.000191428728857372,
    0.00014955558589748968, 9.231092851042412e-05, 6.813491823368628e-05, 2.8826365569622417e-05,
    1.5767182055279397e-05, 3.940604102707517e-06, 1.5840125869731628e-06, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0
]

REF_R = [
    0.031560573775605893, 0.03155207183104386, 0.03151482154968238, 0.031331804497015225,
    0.03067298577184263, 0.028648047698799695, 0.02464504070475776, 0.019296075366599053,
    0.014206661222182781, 0.010294260887878548, 0.007619146052136205, 0.005898041083471917,
    0.004823324778097049, 0.004229874834993319, 0.004059917129869861, 0.004353369559408238,
    0.005343442596964287, 0.007691720100996724, 0.013596979573625545, 0.03169754426617544,
    0.10786119635570235, 0.46381260316918005, 0.8470554052715022, 0.9431854093936334,
    0.9688621506964221, 0.978030667473553, 0.9820436438543185, 0.9839236237187765,
    0.9848454841545076, 0.9852942758147769, 0.9855072952200589, 0.9856050715401196,
    0.985653849933904, 0.9856776850342464, 0.9856883918065151, 0.9856936646904471,
    0.9856958798486362, 0.9856965214642008
]

REF_G = [
    0.009556074754410449, 0.00955815801112031, 0.009567324543584887, 0.009612912628991555,
    0.009783709039599076, 0.010378622705444651, 0.012002645237574217, 0.01609777214724728,
    0.02670619022321924, 0.0595555440190878, 0.18603982653435341, 0.5705798201163349,
    0.8614677683992376, 0.945879089766979, 0.9704654864738727, 0.9784136302841248,
    0.9795890314109317, 0.9755335369083287, 0.9622887553974709, 0.9231215745128396,
    0.7934340189439301, 0.45927013590622906, 0.18557410366813132, 0.08817749599543823,
    0.05436302287555966, 0.04062884470419337, 0.03422152042906518, 0.03111857909223853,
    0.029570889829271474, 0.028810873929642933, 0.02844862712632218, 0.028282030165508287,
    0.028198837641326635, 0.028158165525883294, 0.028139891012812057, 0.028130890157372412,
    0.02812710867111673, 0.028126013351616186
]

REF_B = [
    0.9794047525027293, 0.9794007068438306, 0.9793829034709327, 0.9792943649462249,
    0.9789630146091524, 0.9778144666945839, 0.9747243211343526, 0.9671984823444855,
    0.9490796575310576, 0.9008501289411428, 0.7631504454607034, 0.4659221716451323,
    0.20126328044854624, 0.08775244134130433, 0.045717679329214, 0.0284706050524961,
    0.020527176757419385, 0.01653027923153466, 0.014513510721861633, 0.013600350864389432,
    0.013360425877586513, 0.013548894315131066, 0.013959435637084183, 0.014443425575408897,
    0.014885444061693232, 0.015225429698892456, 0.015459284816230268, 0.015601802646075802,
    0.015682487124966893, 0.01572487643217746, 0.01574581087393412, 0.015755612330020707,
    0.015760544391039022, 0.01576296374570002, 0.015764052556781927, 0.01576458922659668,
    0.015764814770760138, 0.015764880108381563
]

REF_C = [
    0.9705850013236135, 0.970592498144049, 0.9706253487304599, 0.9707868061194989,
    0.9713686732286088, 0.9731632306214547, 0.9767402231588058, 0.9815876054913082,
    0.986280265652838, 0.9899491476890221, 0.992492701538321, 0.9941456804051705,
    0.995183975033137, 0.9957567501107486, 0.9959128182866417, 0.9956061578344543,
    0.9945976009617659, 0.9922157154922507, 0.9862364527830636, 0.9679433372642177,
    0.8912850042445518, 0.5362024778642942, 0.15410811900323895, 0.057457509322873246,
    0.03153498731012505, 0.022263392007673855, 0.018202284147909364, 0.016299055971509935,
    0.015365623931250794, 0.014911156870711872, 0.014695433986668727, 0.014596414668177127,
    0.014547015665979879, 0.0145228771856305, 0.014512034107306337, 0.014506694089188088,
    0.014504450726515294, 0.014503800941462253
]

REF_M = [
    0.9906735573200153, 0.9906715249620033, 0.9906625823534385, 0.9906181076448026,
    0.990451480878705, 0.9898710814001851, 0.9882866087596054, 0.9842906927974489,
    0.9739349056252178, 0.9418178384600091, 0.8173903261951432, 0.4324728050666193,
    0.13845397825928085, 0.05373472169407012, 0.029217499667296976, 0.02131365175080624,
    0.020134953018049795, 0.02413230962799845, 0.03722361452230161, 0.07605065527064236,
    0.2053754719424571, 0.5412689034601018, 0.8158416850861612, 0.9128177041239232,
    0.9463398301670932, 0.9599276963322717, 0.9662605952307386, 0.9693259700590107,
    0.9708545367221553, 0.9716050665290574, 0.9719627697584916, 0.9721272722757663,
    0.9722094177472096, 0.9722495776799405, 0.972267622000355, 0.9722765094638359,
    0.9722802433086088, 0.9722813248283197
]

REF_Y = [
    0.021052337176682534, 0.021056462749591276, 0.02107461786754744, 0.02116490584319808,
    0.021502795725913126, 0.02267387990316372, 0.02582356496868543, 0.03348793856360477,
    0.05190696637404363, 0.10074901483425852, 0.23912989970912618, 0.5348043122750332,
    0.7978075786433301, 0.9114498940670794, 0.9537979630041813, 0.9712416154651606,
    0.9793031238073717, 0.9833801195073975, 0.9854612465676097, 0.9864350469764908,
    0.9867382506700643, 0.9866178824450031, 0.9862777767586757, 0.985860592444166,
    0.9854749276764108, 0.9851769347658557, 0.9849715740145766, 0.9848463034162018,
    0.984775351811776, 0.9847380666259202, 0.9847196483124904, 0.9847110233927254,
    0.984706683301515, 0.984704554393973, 0.9847035963102866, 0.9847031240784958,
    0.9847029256160507, 0.984702868123764
]

REF_W = [
    1.0011609380945206, 1.0011608623718085, 1.0011605295297332, 1.0011588809895395,
    1.0011527996370448, 1.0011327038479474, 1.0010851344696379, 1.0009969223979824,
    1.000865191602915, 1.0006961357507411, 1.000504750049934, 1.0003078659509828,
    1.000119494451461, 0.9999526742333059, 0.9998218359182679, 0.9997386813870067,
    0.999709657158615, 0.999732027037823, 0.9997994926837177, 0.9999003348396848,
    1.0000203680490436, 1.000144727840223, 1.0002599198116873, 1.0003557541640735,
    1.0004275168049208, 1.0004762320514617, 1.0005072228582503, 1.0005252140962848,
    1.000535124149449, 1.0005402521608604, 1.000542761051987, 1.0005439295178398,
    1.0005445165353923, 1.0005448043949652, 1.0005449339234573, 1.0005449977629202,
    1.0005450245916068, 1.0005450323634841
]

SIZE = len(X_BAR)
REFLECTANCE = [REF_W, REF_C, REF_M, REF_Y, REF_R, REF_G, REF_B]


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

    lrgb = alg.matmul_x3(XYZ_TO_RGB, xyz, dims=alg.D2_D1)
    w = max(min(lrgb), 0.0)
    r, g, b = lrgb[0] - w, lrgb[1] - w, lrgb[2] - w
    cy = max(min(g, b), 0.0)
    ma = max(min(r, b - cy), 0.0)
    ye = max(min(r - ma, g - cy), 0.0)
    r -= ma + ye
    g -= cy + ye
    b -= cy + ma
    return [
        min(w, 1.0),
        min(cy, 1.0),
        min(ma, 1.0),
        min(ye, 1.0),
        alg.clamp(r, 0.0, 1.0),
        alg.clamp(g, 0.0, 1.0),
        alg.clamp(b, 0.0, 1.0)
    ]


def single_constant_xyz_to_reflectance(xyz: Vector) -> tuple[Vector, Vector]:
    """
    Linear sRGB to a reflectance.

    For out of gamut colors, our concentration concentration are clipped to 0 - 1. Lastly, we ensure the
    final reflectance result is never zero with a small epsilon.

    Because out of gamut colors may be attenuated due to constraints on concentrations, we must
    also calculate the residual, left over weights of our XYZ value and return them as well. We can
    use the residual later to better approximate colors out of gamut by adding them back in.
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
    # Calculate weighting for for the given interpolation factor using luminance.
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
