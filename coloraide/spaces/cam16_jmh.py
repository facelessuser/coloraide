"""
CAM16 class (JMh).

https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import math
import bisect
from .. import util
from .. import algebra as alg
from ..spaces import Space, LChish
from ..cat import WHITES, CAT16
from ..channels import Channel, FLG_ANGLE
from .achromatic import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from ..types import Vector, VectorLike, Matrix
from typing import Any

# CAT16
M16 = CAT16.MATRIX
MI6_INV = alg.inv(M16)

M1 = [
    [460.0, 451.0, 288.0],
    [460.0, -891.0, -261.0],
    [460.0, -220.0, -6300.0]
]

ADAPTED_COEF = 0.42
ADAPTED_COEF_INV = 1 / ADAPTED_COEF

SURROUND = {
    'dark': (0.8, 0.525, 0.8),
    'dim': (0.9, 0.59, 0.9),
    'average': (1, 0.69, 1)
}

HUE_QUADRATURE = {
    # Red, Yellow, Green, Blue, Red
    "h": (20.14, 90.00, 164.25, 237.53, 380.14),
    "e": (0.8, 0.7, 1.0, 1.2, 0.8),
    "H": (0.0, 100.0, 200.0, 300.0, 400.0)
}

ACHROMATIC_RESPONSE = [
    [0.5197637353103578, 0.10742101902546781, 209.53702017876432],
    [0.7653410752577902, 0.14285252204838345, 209.53699586564701],
    [0.9597225272459006, 0.1674639325209385, 209.5369779985614],
    [1.1268800051398011, 0.18685008110835863, 209.5369633468102],
    [1.2763267654963262, 0.2030639541700499, 209.53695070009815],
    [1.8790377054651906, 0.26061543207726645, 209.53690294574977],
    [2.3559753209404573, 0.2998668559412108, 209.53686786031403],
    [2.7660324716814633, 0.3305058430743193, 209.536839093849],
    [3.1325805945142164, 0.3559891904115732, 209.53681426762876],
    [3.4678031173571573, 0.3779903818931045, 209.5367921887862],
    [3.7790286254197216, 0.397459500662546, 209.53677216077287],
    [4.071081036208187, 0.41499276041595823, 209.53675373607373],
    [4.35987940988476, 0.4317047383578854, 209.53673583657556],
    [4.653923368359191, 0.44814375233486375, 209.53671791170922],
    [7.833618587426542, 0.5996289140723937, 209.53653852944092],
    [11.379933581738413, 0.7341977581705729, 209.53635903741286],
    [15.226965773377026, 0.857259036676519, 209.53617955384075],
    [19.331425543357224, 0.9717687075452716, 209.53600014936998],
    [23.662223781347393, 1.0795574256327514, 209.5358208710024],
    [28.195712492409086, 1.181856050998015, 209.5356417521982],
    [32.91316356733729, 1.2795417603936137, 209.53546281794857],
    [37.799294675334956, 1.3732674055098613, 209.53528408756415],
    [42.841343691205466, 1.4635354939944947, 209.5351055763844],
    [48.028455187972774, 1.5507433232034882, 209.53492729681835],
    [53.35125605180922, 1.6352119585004592, 209.53474925909882],
    [58.80155160494701, 1.7172056265103606, 209.53457147176655],
    [64.37210171522501, 1.7969451471063127, 209.53439394202456],
    [70.05645182832635, 1.8746175094579138, 209.53421667601953],
    [75.8488028092011, 1.95038286970608, 209.53403967901312],
    [81.74390888832981, 2.0243797747219405, 209.5338629555596],
    [87.73699639870503, 2.096729134902292, 209.53368650960735],
    [93.82369818202439, 2.1675372954936383, 209.53351034459058],
    [100.0, 2.2368984457705743, 209.53333446353417],
    [106.26219627903436, 2.304896533525034, 209.53315886906827],
    [112.60685320678104, 2.37160680430044, 209.5329835635175],
    [119.03077768851209, 2.4370970520495017, 209.53280854892373],
    [125.53099102420309, 2.501428645093027, 209.53263382708093],
    [132.1047064258276, 2.5646573751376196, 209.532459399577],
    [138.74930968646498, 2.626834165511834, 209.53228526779787],
    [145.46234245739691, 2.6880056663241145, 209.5321114329661],
    [152.24148769946316, 2.748214758003532, 209.5319378961533],
    [159.08455695969053, 2.807500980008346, 209.53176465830455],
    [165.98947919010237, 2.865900897958051, 209.53159172021918],
    [172.95429087732893, 2.92344841973748, 209.53141908260915],
    [179.9771272925688, 2.980175069050048, 209.53124674607443],
    [187.05621470411134, 3.0361102232687336, 209.5310747111302],
    [194.18986342088985, 3.0912813211607015, 209.53090297820904],
    [201.3764615567875, 3.145714045061113, 209.5307315476577],
    [208.6144694227416, 3.199432481261756, 209.53056041976922],
    [215.90241446789472, 3.252459261745779, 209.5303895947692],
    [223.23888670275286, 3.304815689873112, 209.53021907281482],
    [230.62253454702395, 3.3565218522006455, 209.53004885402189],
    [238.05206105290907, 3.4075967182791853, 209.5298789384579],
    [245.52622046139462, 3.458058229985187, 209.52970932613115],
    [253.04381505480683, 3.507923381705505, 209.52954001701696],
    [260.6036922737095, 3.5572082925096393, 209.52937101105175],
    [268.20474207032214, 3.605928271271525, 209.52920230813686],
    [275.8458944741247, 3.654097875574637, 209.52903390813748],
    [283.52611734829725, 3.7017309651178785, 209.52886581088453],
    [291.2444143182101, 3.7488407502396903, 209.52869801618388],
    [298.9998228553806, 3.795439836103318, 209.52853052381926],
    [306.7914125022303, 3.841540263013781, 209.52836333353144],
    [314.61828322461565, 3.8871535432701356, 209.52819644505152],
    [322.479563880563, 3.9322906949207233, 209.52802985809194],
    [330.37441079487513, 3.9769622727358835, 209.52786357233052],
    [338.30200643038665, 4.021178396670769, 209.52769758743355],
    [346.2615581476034, 4.064948778071774, 209.527531903052],
    [354.2522970453064, 4.108282743840221, 209.52736651881136],
    [362.2734768754491, 4.151189258746347, 209.52720143432805],
    [370.32437302633326, 4.193676946068329, 209.52703664919864],
    [378.40428156863675, 4.235754106704258, 209.52687216301322],
    [386.5125183593773, 4.2774287369029045, 209.52670797533614],
    [394.648418199364, 4.318708544722146, 209.5265440857335],
    [402.8113340400954, 4.359600965341976, 209.52638049373465],
    [411.00063623642933, 4.400113175309797, 209.52621719889768],
    [419.2157118416773, 4.440252105831943, 209.52605420073294],
    [427.45596394207547, 4.480024455165197, 209.52589149876238],
    [435.7208110278373, 4.519436700202084, 209.52572909248678],
    [444.00968639824373, 4.558495107300929, 209.52556698141063],
    [452.32203759843054, 4.597205742430075, 209.52540516500954],
    [460.65732588572826, 4.635574480668486, 209.52524364277534],
    [469.01502572358646, 4.67360701512636, 209.52508241417655],
    [477.39462430127537, 4.711308865315819, 209.52492147868603],
    [485.79562107768834, 4.7486853850221635, 209.5247608357571],
    [494.2175273477135, 4.78574176970701, 209.5246004848463],
    [502.65986582975273, 4.822483063478878, 209.52444042540557],
    [511.12217027307815, 4.858914165665327, 209.52428065686505],
    [519.603985083808, 4.895039837005332, 209.52412117867837],
    [528.1048649683819, 4.930864705501955, 209.52396199027478],
    [536.6243745934894, 4.966393271948785, 209.52380309107085],
    [545.1620882614892, 5.00162991514904, 209.52364448050218],
    [553.7175896004151, 5.036578896863506, 209.52348615798303],
    [562.2904712677357, 5.071244366487241, 209.52332812293528],
    [570.8803346670916, 5.105630365484719, 209.52317037476547],
    [579.4867896772784, 5.139740831594337, 209.5230129128839],
    [588.1094543928118, 5.173579602815829, 209.5228557367024],
    [596.7479548754266, 5.207150421200013, 209.52269884562236],
    [605.4019249159434, 5.240456936444621, 209.52254223903395],
    [614.0710058059254, 5.2735027093139655, 209.5223859163477],
    [622.7548461186354, 5.306291214893902, 209.52222987695998],
    [631.4531014987923, 5.338825845688801, 209.52207412025294],
    [640.1654344606808, 5.371109914568736, 209.52191864562857],
    [648.8915141941957, 5.403146657580616, 209.5217634524664],
    [657.6310163784137, 5.434939236625219, 209.52160854017026],
    [666.3836230023236, 5.466490742017722, 209.52145390811216],
    [675.1490221923619, 5.497804194921784, 209.5212995556808],
    [683.9269080464271, 5.528882549682189, 209.52114548225762],
    [692.7169804740557, 5.559728696047723, 209.52099168723132],
    [701.5189450424705, 5.590345461302892, 209.5208381699748],
    [710.3325128282281, 5.620735612298451, 209.52068492987357],
    [719.1574002741951, 5.6509018574012, 209.52053196630135],
    [727.9933290516212, 5.6808468483554915, 209.52037927864566],
    [736.8400259270659, 5.710573182071535, 209.52022686627654],
    [745.6972226339658, 5.7400834023332274, 209.5200747285655],
    [754.5646557486314, 5.769380001437249, 209.51992286490193],
    [763.4420665704857, 5.79846542176912, 209.51977127465065],
    [772.3292010063437, 5.827342057308235, 209.519619957194]
]  # type: Matrix

INV_ACHROMATIC_RESPONSE = [
    [-745.6972226339658, 3.9058442577310335, 29.520074728565508],
    [-735.069838051441, 3.8819263653809566, 29.520257326754717],
    [-724.4576501804336, 3.8577985580981653, 29.520440320639388],
    [-713.8611251494627, 3.833457877370439, 29.52062371129394],
    [-703.2807394924491, 3.808901290613594, 29.520807499801364],
    [-692.7169804740557, 3.784125688308396, 29.520991687231326],
    [-682.1703464292635, 3.7591278809827804, 29.521176274649854],
    [-671.6413471180169, 3.7339045960347192, 29.52136126314039],
    [-661.1305040957991, 3.708452474389241, 29.52154665374936],
    [-650.6383511010857, 3.6827680669597007, 29.52173244755951],
    [-640.1654344606808, 3.6568478309274903, 29.521918645628578],
    [-629.7123135140142, 3.630688125805234, 29.522105249012025],
    [-619.2795610575735, 3.6042852092759383, 29.522292258760274],
    [-608.867763810707, 3.5776352327921503, 29.522479675925247],
    [-598.4775229041638, 3.5507342369185246, 29.522667501562207],
    [-588.1094543928114, 3.52357814639877, 29.52285573670506],
    [-577.7641897941089, 3.4961627649222966, 29.52304438238462],
    [-567.4423766540311, 3.4684837695697692, 29.52323343964739],
    [-557.1446791422768, 3.4405367049209086, 29.523422909501317],
    [-546.8717786787527, 3.4123169767805006, 29.523612792968613],
    [-536.6243745934894, 3.3838198455090045, 29.523803091070853],
    [-526.4031848223244, 3.3550404189212553, 29.523993804799613],
    [-516.2089466409072, 3.3259736447087915, 29.524184935147293],
    [-506.04241743978673, 3.296614302357983, 29.524376483108842],
    [-495.90437554360454, 3.266956994517464, 29.524568449660666],
    [-485.79562107768817, 3.2369961377639362, 29.52476083575679],
    [-475.7169768856457, 3.2067259527154626, 29.52495364236188],
    [-465.66928950189845, 3.1761404534389444, 29.52514687041382],
    [-455.6534301834797, 3.1452334360790952, 29.525340520846825],
    [-445.6702960058343, 3.1139984666461693, 29.52553459456717],
    [-435.7208110278373, 3.082428867874411, 29.5257290924868],
    [-425.8059275317766, 3.0505177050718344, 29.525924015485998],
    [-415.92662734463676, 3.0182577708558007, 29.52611936443042],
    [-406.083923247684, 2.9856415686663307, 29.52631514016902],
    [-396.27886048211604, 2.952661294934431, 29.52651134353625],
    [-386.51251835937717, 2.9193088197676564, 29.526707975334507],
    [-376.7860119857034, 2.8855756659908245, 29.526905036355817],
    [-367.10049411155643, 2.851452986376106, 29.52710252735586],
    [-357.45715711784163, 2.8169315388520286, 29.52730044906793],
    [-347.8572351522114, 2.782001659474689, 29.527498802198505],
    [-338.30200643038665, 2.7466532328995963, 29.52769758743247],
    [-328.7927957192639, 2.7108756600670354, 29.52789680540236],
    [-319.33097702071825, 2.6746578227614957, 29.52809645671388],
    [-309.9179764774579, 2.6379880446668658, 29.52829654193727],
    [-300.5552755251352, 2.6008540484792033, 29.528497061598884],
    [-291.24441431821003, 2.563242908568836, 29.528698016188653],
    [-281.98699546090495, 2.5251409986089803, 29.52889940612333],
    [-272.7846880790835, 2.486533933485875, 29.529101231797068],
    [-263.639232274142, 2.447406504709738, 29.529303493528808],
    [-254.5524440062237, 2.4077426083931366, 29.529506191571432],
    [-245.52622046139462, 2.367525164712573, 29.529709326130295],
    [-236.56254596615122, 2.326736027580904, 29.5299128973098],
    [-227.6634985230424, 2.2853558830037684, 29.53011690515518],
    [-218.83125705368175, 2.2433641343318333, 29.530321349611842],
    [-210.0681094504913, 2.2007387722434517, 29.530526230530054],
    [-201.3764615567875, 2.1574562268776667, 29.530731547657684],
    [-192.75884721709647, 2.1134911989870173, 29.53093730061302],
    [-184.21793956692375, 2.0688164663097193, 29.531143488887402],
    [-175.7565637649753, 2.023402660514716, 29.53135011183324],
    [-167.37771141282732, 1.9772180089969948, 29.531557168641637],
    [-159.08455695969053, 1.9302280344282914, 29.531764658304553],
    [-150.88047645641842, 1.8823952031949056, 29.531972579634196],
    [-142.76906910766013, 1.8336785115639005, 29.532180931194063],
    [-134.75418218006106, 1.7840329953780394, 29.532389711302343],
    [-126.8399399660233, 1.7334091450861648, 29.532598917989905],
    [-119.03077768851209, 1.6817522025123908, 29.532808548921828],
    [-111.3314814795425, 1.6290013084445116, 29.533018601410397],
    [-103.74723589766963, 1.5750884600392587, 29.533229072305296],
    [-96.28368090402213, 1.5199372229123853, 29.533439957935965],
    [-88.94698084625801, 1.4634611227411158, 29.53365125402588],
    [-81.74390888832978, 1.405561612204716, 29.533862955558845],
    [-74.68195160155422, 1.3461254663212219, 29.534075056667046],
    [-67.76944030933414, 1.2850213948099434, 29.534287550419478],
    [-61.01571860238462, 1.222095560637958, 29.534500428593944],
    [-54.431359810175515, 1.1571655361895847, 29.53471368135187],
    [-48.028455187972774, 1.0900119706792142, 29.53492729681837],
    [-41.821005124247854, 1.0203668063332338, 29.5351412604527],
    [-35.82546562518518, 0.9478961141166822, 29.535355554197068],
    [-30.061538624119837, 0.8721742118508005, 29.53557015516213],
    [-24.553364919057078, 0.7926430161985776, 29.535785033575767],
    [-19.331425543357224, 0.7085451025202562, 29.536000149370004],
    [-14.435797393047228, 0.6188075378862801, 29.536215446052257],
    [-9.922309454243656, 0.5218316998784264, 29.536430838352594],
    [-5.876049367374544, 0.4151475361300732, 29.536646182976344],
    [-1.8790377054651906, 0.27254960955258617, 29.536902945749794],
    [-0.5197637353103578, 0.2703043894853694, 29.537020178764333]
]  # type: Matrix


class Achromatic(_Achromatic):
    """
    Test if color is achromatic.

    Should work quite well through the SDR range. Can reasonably handle HDR range out to 3
    which is far enough for anything practical.
    We use a spline mainly to quickly fit the line in a way we do not have to analyze and tune.
    """

    L_IDX = 0
    C_IDX = 1
    H_IDX = 2

    def __init__(
        self,
        data: Matrix | None = None,
        threshold_upper: float = 0.0,
        threshold_lower: float = 0.0,
        threshold_cutoff: float = math.inf,
        spline: str = 'linear',
        mirror: bool = False,
        *,
        env: Environment,
        **kwargs: Any
    ) -> None:
        """Initialize."""

        super().__init__(data, threshold_upper, threshold_lower, threshold_cutoff, spline, mirror, env=env, **kwargs)

    def calc_achromatic_response(  # type: ignore[override]
        self,
        parameters: list[tuple[int, int, int, float]],
        *,
        env: Environment,
        **kwargs: Any
    ) -> None:  # pragma: no cover
        """Precalculate the achromatic response."""

        super().calc_achromatic_response(parameters, env=env, **kwargs)

    def convert(self, coords: Vector, *, env: Environment, **kwargs: Any) -> Vector:  # type: ignore[override]
        """Convert to the target color space."""

        return xyz_d65_to_cam16_jmh(lin_srgb_to_xyz(lin_srgb(coords)), env)


def hue_quadrature(h: float) -> float:
    """
    Hue to hue quadrature.

    https://onlinelibrary.wiley.com/doi/pdf/10.1002/col.22324
    """

    hp = util.constrain_hue(h)
    if hp <= HUE_QUADRATURE['h'][0]:
        hp += 360

    i = bisect.bisect_left(HUE_QUADRATURE['h'], hp) - 1
    hi, hii = HUE_QUADRATURE['h'][i:i + 2]
    ei, eii = HUE_QUADRATURE['e'][i:i + 2]
    Hi = HUE_QUADRATURE['H'][i]

    t = (hp - hi) / ei
    return Hi + (100 * t) / (t + (hii - hp) / eii)


def inv_hue_quadrature(H: float) -> float:
    """Hue quadrature to hue."""

    Hp = (H % 400 + 400) % 400
    i = math.floor(0.01 * Hp)
    Hp = Hp % 100
    hi, hii = HUE_QUADRATURE['h'][i:i + 2]
    ei, eii = HUE_QUADRATURE['e'][i:i + 2]

    return util.constrain_hue((Hp * (eii * hi - ei * hii) - 100 * hi * eii) / (Hp * (eii - ei) - 100 * eii))


def adapt(coords: Vector, fl: float) -> Vector:
    """Adapt the coordinates."""

    adapted = []
    for c in coords:
        x = (fl * abs(c) * 0.01) ** ADAPTED_COEF
        adapted.append(400 * math.copysign(x, c) / (x + 27.13))
    return adapted


def unadapt(adapted: Vector, fl: float) -> Vector:
    """Remove adaptation from coordinates."""

    coords = []
    constant = 100 / fl * (27.13 ** ADAPTED_COEF_INV)
    for c in adapted:
        cabs = abs(c)
        coords.append(math.copysign(constant * alg.npow(cabs / (400 - cabs), ADAPTED_COEF_INV), c))
    return coords


class Environment:
    """
    Class to calculate and contain any required environmental data (viewing conditions included).

    Usage Guidelines for CIECAM97s (Nathan Moroney)
    https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf

    ref_white: The reference white XYZ. We assume XYZ is in the range 0 - 1 as that is how ColorAide
        handles XYZ everywhere else. It will be scaled up to 0 - 100.

    adapting_luminance: This is the the luminance of the adapting field. The units are in cd/m2.
        The equation is `L = (E * R) / π`, where `E` is the illuminance in lux, `R` is the reflectance,
        and `L` is the luminance. If we assume a perfectly reflecting diffuser, `R` is assumed as 1.
        For the "gray world" assumption, we must also divide by 5 (or multiply by 0.2 - 20%).
        This results in `La = E / π * 0.2`.

    background_luminance: The background is the region immediately surrounding the stimulus and
        for images is the neighboring portion of the image. Generally, this value is set to a value of 20.
        This implicitly assumes a gray world assumption.

    surround: The surround is categorical and is defined based on the relationship between the relative
        luminance of the surround and the luminance of the scene or image white. While there are 4 defined
        surrounds, usually just `average`, `dim`, and `dark` are used.

        Dark    | 0%        | Viewing film projected in a dark room
        Dim     | 0% to 20% | Viewing television
        Average | > 20%     | Viewing surface colors

    discounting: Whether we are discounting the illuminance. Done when eye is assumed to be fully adapted.
    """

    def __init__(
        self,
        ref_white: VectorLike,
        adapting_luminance: float,
        background_luminance: float,
        surround: str,
        discounting: bool
    ):
        """
        Initialize environmental viewing conditions.

        Using the specified viewing conditions, and general environmental data,
        initialize anything that we can ahead of time to speed up the process.
        """

        self.discounting = discounting
        self.ref_white = util.xy_to_xyz(ref_white)
        self.surround = surround
        xyz_w = alg.multiply(self.ref_white, 100, dims=alg.D1_SC)

        # The average luminance of the environment in `cd/m^2cd/m` (a.k.a. nits)
        self.la = adapting_luminance
        # The relative luminance of the nearby background
        self.yb = background_luminance
        # Absolute luminance of the reference white.
        yw = xyz_w[1]

        # Cone response for reference white
        rgb_w = alg.matmul(M16, xyz_w, dims=alg.D2_D1)

        # Surround: dark, dim, and average
        f, self.c, self.nc = SURROUND[self.surround]

        k = 1 / (5 * self.la + 1)
        k4 = k ** 4

        # Factor of luminance level adaptation
        self.fl = (k4 * self.la + 0.1 * (1 - k4) * (1 - k4) * math.pow(5 * self.la, 1 / 3))
        self.fl_root = math.pow(self.fl, 0.25)

        self.n = self.yb / yw
        self.z = 1.48 + math.sqrt(self.n)
        self.nbb = 0.725 * math.pow(self.n, -0.2)
        self.ncb = self.nbb

        # Degree of adaptation calculating if not discounting illuminant (assumed eye is fully adapted)
        d = alg.clamp(f * (1 - 1 / 3.6 * math.exp((-self.la - 42) / 92)), 0, 1) if not discounting else 1
        self.d_rgb = [alg.lerp(1, yw / coord, d) for coord in rgb_w]
        self.d_rgb_inv = [1 / coord for coord in self.d_rgb]

        # Achromatic response
        rgb_cw = alg.multiply(rgb_w, self.d_rgb, dims=alg.D1)
        rgb_aw = adapt(rgb_cw, self.fl)
        self.a_w = self.nbb * (2 * rgb_aw[0] + rgb_aw[1] + 0.05 * rgb_aw[2])


def cam16_to_xyz_d65(
    J: float | None = None,
    C: float | None = None,
    h: float | None = None,
    s: float | None = None,
    Q: float | None = None,
    M: float | None = None,
    H: float | None = None,
    env: Environment | None = None
) -> Vector:
    """
    From CAM16 to XYZ.

    Reverse calculation can actually be obtained from a small subset of the CAM16 components
    Really, only one suitable value is needed for each type of attribute: (lightness/brightness),
    (chroma/colorfulness/saturation), (hue/hue quadrature). If more than one for a given
    category is given, we will fail as we have no idea which is the right one to use. Also,
    if none are given, we must fail as well as there is nothing to calculate with.
    """

    # These check ensure one, and only one attribute for a given category is provided.
    if not ((J is not None) ^ (Q is not None)):
        raise ValueError("Conversion requires one and only one: 'J' or 'Q'")

    if not ((C is not None) ^ (M is not None) ^ (s is not None)):
        raise ValueError("Conversion requires one and only one: 'C', 'M' or 's'")

    # Hue is absolutely required
    if not ((h is not None) ^ (H is not None)):
        raise ValueError("Conversion requires one and only one: 'h' or 'H'")

    # We need viewing conditions
    if env is None:
        raise ValueError("No viewing conditions/environment provided")

    # Black
    if J == 0.0 or Q == 0.0:
        return [0.0, 0.0, 0.0]

    # Break hue into Cartesian components
    h_rad = 0.0
    if h is not None:
        h_rad = math.radians(h % 360)
    elif H is not None:
        h_rad = math.radians(inv_hue_quadrature(H))
    cos_h = math.cos(h_rad)
    sin_h = math.sin(h_rad)

    # Calculate `J_root` from one of the lightness derived coordinates.
    J_root = 0.0
    if J is not None:
        J_root = alg.nth_root(J, 2) * 0.1
    elif Q is not None:
        J_root = 0.25 * env.c * Q / ((env.a_w + 4) * env.fl_root)

    # Calculate the `t` value from one of the chroma derived coordinates
    alpha = 0.0
    if C is not None:
        alpha = C / J_root
    elif M is not None:
        alpha = (M / env.fl_root) / J_root
    elif s is not None:
        alpha = 0.0004 * (s ** 2) * (env.a_w + 4) / env.c
    t = alg.npow(alpha * math.pow(1.64 - math.pow(0.29, env.n), -0.73), 10 / 9)

    # Eccentricity
    et = 0.25 * (math.cos(h_rad + 2) + 3.8)

    # Achromatic response
    A = env.a_w * alg.npow(J_root, 2 / env.c / env.z)

    # Calculate red-green and yellow-blue components
    p1 = 5e4 / 13 * env.nc * env.ncb * et
    p2 = A / env.nbb
    r = 23 * (p2 + 0.305) * alg.zdiv(t, 23 * p1 + t * (11 * cos_h + 108 * sin_h))
    a = r * cos_h
    b = r * sin_h

    # Calculate back from cone response to XYZ
    rgb_c = unadapt(alg.multiply(alg.matmul(M1, [p2, a, b], dims=alg.D2_D1), 1 / 1403, dims=alg.D1_SC), env.fl)
    return alg.divide(
        alg.matmul(MI6_INV, alg.multiply(rgb_c, env.d_rgb_inv, dims=alg.D1), dims=alg.D2_D1),
        100,
        dims=alg.D1_SC
    )


def xyz_d65_to_cam16(xyzd65: Vector, env: Environment) -> Vector:
    """From XYZ to CAM16."""

    # Cone response
    rgb_a = adapt(
        alg.multiply(
            alg.matmul(M16, alg.multiply(xyzd65, 100, dims=alg.D1_SC), dims=alg.D2_D1),
            env.d_rgb,
            dims=alg.D1
        ),
        env.fl
    )

    # Calculate hue from red-green and yellow-blue components
    a = rgb_a[0] + (-12 * rgb_a[1] + rgb_a[2]) / 11
    b = (rgb_a[0] + rgb_a[1] - 2 * rgb_a[2]) / 9
    h_rad = math.atan2(b, a) % math.tau

    # Eccentricity
    et = 0.25 * (math.cos(h_rad + 2) + 3.8)

    t = (
        5e4 / 13 * env.nc * env.ncb *
        alg.zdiv(et * math.sqrt(a ** 2 + b ** 2), rgb_a[0] + rgb_a[1] + 1.05 * rgb_a[2] + 0.305)
    )
    alpha = alg.npow(t, 0.9) * math.pow(1.64 - math.pow(0.29, env.n), 0.73)

    # Achromatic response
    A = env.nbb * (2 * rgb_a[0] + rgb_a[1] + 0.05 * rgb_a[2])

    J_root = alg.npow(A / env.a_w, 0.5 * env.c * env.z)

    # Lightness
    J = 100 * alg.npow(J_root, 2)

    # Brightness
    Q = (4 / env.c * J_root * (env.a_w + 4) * env.fl_root)

    # Chroma
    C = alpha * J_root

    # Colorfulness
    M = C * env.fl_root

    # Hue
    h = util.constrain_hue(math.degrees(h_rad))

    # Hue quadrature
    H = hue_quadrature(h)

    # Saturation
    s = 50 * alg.nth_root(env.c * alpha / (env.a_w + 4), 2)

    return [J, C, h, s, Q, M, H]


def xyz_d65_to_cam16_jmh(xyzd65: Vector, env: Environment) -> Vector:
    """XYZ to CAM16 JMh."""

    cam16 = xyz_d65_to_cam16(xyzd65, env)
    J, M, h = cam16[0], cam16[5], cam16[2]
    return [J, M, h]


def cam16_jmh_to_xyz_d65(jmh: Vector, env: Environment) -> Vector:
    """CAM16 JMh to XYZ."""

    J, M, h = jmh
    return cam16_to_xyz_d65(J=J, M=M, h=h, env=env)


class CAM16JMh(LChish, Space):
    """CAM16 class (JMh)."""

    BASE = "xyz-d65"
    NAME = "cam16-jmh"
    SERIALIZE = ("--cam16-jmh",)
    CHANNEL_ALIASES = {
        "lightness": "j",
        "colorfulness": 'm',
        "hue": 'h'
    }
    WHITE = WHITES['2deg']['D65']
    # Assuming sRGB which has a lux of 64
    ENV = Environment(WHITE, 64 / math.pi * 0.2, 20, 'average', False)
    # If discounting were True, we could remove the dynamic achromatic response
    ACHROMATIC = Achromatic(
        # Precalculated from:
        # [
        #     (1, 5, 1, 1000.0),
        #     (1, 10, 1, 200.0),
        #     (5, 521, 5, 100.0)
        # ],
        ACHROMATIC_RESPONSE,
        0.0012,
        0.0141,
        6.7,
        'catrom',
        env=ENV
    )
    INV_ACHROMATIC = Achromatic(
        # Precalculated from:
        # [
        #     [1, 5, 10, 1000],
        #     [1, 511, 6, 100]
        # ],
        INV_ACHROMATIC_RESPONSE,
        0.0295,
        0.01508,
        4.8,
        'catrom',
        env=ENV,
        negative=True
    )
    CHANNELS = (
        Channel("j", 0.0, 100.0),
        Channel("m", 0, 105.0),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE, nans=ACHROMATIC.hue)
    )

    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resolve channels."""

        # Assume black if J is below zero
        J = coords[0]
        achromatic = self.ACHROMATIC if J >= 0 else self.INV_ACHROMATIC

        if index == 2:
            h = coords[2]
            return achromatic.get_ideal_hue(J, coords[1]) if math.isnan(h) else h

        elif index == 1:
            c = coords[1]
            return achromatic.get_ideal_chroma(J) if math.isnan(c) else c

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[1] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[2] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        if coords[0] == 0:
            return True

        if coords[0] < 0:
            return self.INV_ACHROMATIC.test(*self.normalize(coords))

        return self.ACHROMATIC.test(*self.normalize(coords))

    def to_base(self, coords: Vector) -> Vector:
        """From CAM16 JMh to XYZ."""

        return cam16_jmh_to_xyz_d65(coords, self.ENV)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16 JMh."""

        return xyz_d65_to_cam16_jmh(coords, self.ENV)
