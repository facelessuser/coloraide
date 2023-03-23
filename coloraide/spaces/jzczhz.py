"""
JzCzhz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from __future__ import annotations
from ..spaces import Space, LChish
from ..cat import WHITES
from .jzazbz import xyz_d65_to_jzazbz
from ..channels import Channel, FLG_ANGLE
from .. import util
import math
from ..types import Vector, VectorLike  # noqa: F401
from .achromatic import Achromatic as _Achromatic
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from typing import Any

ACHROMATIC_RESPONSE = [
    (0.0009185262133445958, 2.840443191466584e-06, 216.0885802021336),
    (0.0032449260086909186, 8.875176418290735e-06, 216.0865538095895),
    (0.007045724283550615, 1.742628198531671e-05, 216.08513073729978),
    (0.009865500056099596, 2.317265885648471e-05, 216.08447255685712),
    (0.012214842923825998, 2.7682763639616338e-05, 216.08404287184672),
    (0.015369999849987263, 3.342002187758669e-05, 216.08357072027584),
    (0.026429457971518095, 5.1379582880951015e-05, 216.08241937449768),
    (0.03795335080434383, 6.754453992375505e-05, 216.08162581187318),
    (0.0496126266066084, 8.199630263090859e-05, 216.08102874711298),
    (0.06126031449112626, 9.494644967522632e-05, 216.08055486842582),
    (0.07282655496930118, 0.00010660656866708172, 216.08016488545363),
    (0.08427796718853352, 0.00011716067835114454, 216.0798354347326),
    (0.09559970294921614, 0.00012676275854570153, 216.0795515304612),
    (0.10678676267720202, 0.00013554040219310688, 216.07930302231028),
    (0.11783950641678197, 0.00014359941404136083, 216.07908273274572),
    (0.128761217869841, 0.00015102796116683243, 216.078885416252),
    (0.13955673492972168, 0.0001578999927439067, 216.07870713000503),
    (0.15023166076742123, 0.00016427796836496916, 216.07854484086508),
    (0.16079190286441147, 0.0001702150126800942, 216.0783961640361),
    (0.17124340278282393, 0.00017575661525780106, 216.07825920065824),
    (0.18159197939495234, 0.0001809419766579858, 216.07813240086588),
    (0.19184324072201478, 0.0001858050800739324, 216.07801451440326),
    (0.202002537697924, 0.00019037555077941712, 216.07790446638342),
    (0.212074943655568, 0.00019467934928498842, 216.07780140303458),
    (0.22206524953574297, 0.00019873933566668563, 216.0777045520467),
    (0.23197796856991826, 0.00020257573055322867, 216.07761330139613),
    (0.24181734649813305, 0.0002062064957239789, 216.0775271074707),
    (0.2515873748285007, 0.00020964764951292278, 216.0774454624974),
    (0.26129180556065146, 0.00021291352944234363, 216.07736799235488),
    (0.2709341663811061, 0.000216017013418292, 216.07729432750452),
    (0.28051777571685255, 0.0002189697057799681, 216.07722412744226),
    (0.290045757277825, 0.0002217820949262585, 216.07715714699978),
    (0.29952105387798683, 0.0002244636883549905, 216.0770931087182),
    (0.3089464404271933, 0.0002270231273315339, 216.07703180849134),
    (0.318324536052124, 0.00022946828610769828, 216.07697303732877),
    (0.3276578153459098, 0.0002318063574656088, 216.0769166243739),
    (0.3369486187721122, 0.00023404392655192895, 216.07686240723885),
    (0.34619916226324066, 0.000236187035570456, 216.0768102367525),
    (0.35541154606263237, 0.00023824123982980468, 216.07675997555808),
    (0.3645877628616357, 0.00024021165709839148, 216.07671150261558),
    (0.37372970528478, 0.00024210301076329533, 216.07666473133563),
    (0.3828391727747085, 0.00024391966826672074, 216.07661953313035),
    (0.3919178779258038, 0.0002456656744964799, 216.07657583096483),
    (0.40096745231307596, 0.0002473447819044588, 216.0765335334877),
    (0.40998945185929875, 0.00024896047690368863, 216.07649257414334),
    (0.41898536178028756, 0.0002505160037467973, 216.0764528665608),
    (0.4279566011448586, 0.0002520143854570069, 216.0764143483904),
    (0.436904527082952, 0.00025345844284644823, 216.07637696574648),
    (0.4458304386725309, 0.00025485081154952267, 216.0763406502616),
    (0.45473558053292124, 0.0002561939571477633, 216.07630536182953),
    (0.46362114614988975, 0.00025749018901337296, 216.076271046612),
    (0.4724882809556213, 0.00025874167285922954, 216.0762376414462),
    (0.48133808518405347, 0.0002599504415907072, 216.07620513643784),
    (0.4901716165209132, 0.0002611184059690287, 216.07617346460367),
    (0.4989898925652301, 0.0002622473634499798, 216.07614259956978),
    (0.5077938931183061, 0.00026333900680666604, 216.0761124982918),
    (0.5165845623138925, 0.0002643949317428146, 216.07608312529777),
    (0.5253628106028233, 0.00026541664370761806, 216.07605447424666),
    (0.5341295166035784, 0.0002664055645672449, 216.07602649958457),
    (0.5428855288294885, 0.0002673630382194607, 216.07599917253518),
    (0.5516316673022515, 0.000268290336017799, 216.0759724678456),
    (0.5603687250606968, 0.00026918866170280904, 216.07594635260233),
    (0.5690974695727122, 0.00027005915570308363, 216.07592082145845),
    (0.577818644057799, 0.00027090289970419, 216.07589582847083),
    (0.5865329687269464, 0.0002717209198919205, 216.0758713947664),
    (0.5952411419459632, 0.00027251419112430856, 216.07584745423335),
    (0.6039438413278134, 0.00027328363966826354, 216.07582400851473),
    (0.6126417247594602, 0.0002740301463754527, 216.07580104515094),
    (0.6213354313673709, 0.0002747545495315845, 216.0757785384075),
    (0.6300255824264327, 0.0002754576472788127, 216.07575649442398),
    (0.6387127822161972, 0.0002761402003565629, 216.07573486301123),
    (0.6473976188282312, 0.00027680293389351936, 216.0757136258035),
    (0.6560806649274313, 0.0002774465395262874, 216.07569281536746),
    (0.6647624784710684, 0.00027807167758923647, 216.07567238313288),
    (0.6734436033881548, 0.00027867897881155425, 216.0756523336041),
    (0.6821245702214195, 0.00027926904569367526, 216.0756326518158),
    (0.690805896734986, 0.0002798424544922738, 216.0756133148165),
    (0.6994880884896815, 0.0002803997564164447, 216.07559431135778),
    (0.7081716393877641, 0.0002809414788313494, 216.0755756567117),
    (0.7168570321896396, 0.00028146812703358645, 216.07555731158192),
    (0.7255447390038526, 0.00028198018474468557, 216.0755392792927),
    (0.7342352217521082, 0.00028247811589614984, 216.07552156593712),
    (0.7429289326111091, 0.00028296236534187003, 216.07550410795596),
    (0.7516263144323508, 0.00028343335953108555, 216.07548695771598),
    (0.7603278011412196, 0.0002838915080817255, 216.07547008983803),
    (0.7690338181169624, 0.0002843372041772946, 216.0754534830032),
    (0.7777447825542029, 0.0002847708255904337, 216.07543712872257),
    (0.7864611038074191, 0.0002851927351040769, 216.0754210526465),
    (0.7951831837192964, 0.00028560328191764596, 216.07540518924762),
    (0.8039114169337114, 0.0002860028013948804, 216.07538959279591),
    (0.8126461911946142, 0.0002863916163923197, 216.07537422001636),
    (0.8213878876310632, 0.00028677003762061056, 216.07535909255094),
    (0.8301368810297582, 0.0002871383644753164, 216.07534418061982),
    (0.8388935400954018, 0.0002874968849051483, 216.07532948943617),
    (0.8476582276995501, 0.0002878458767183673, 216.07531500623608),
    (0.8564313011189064, 0.0002881856073368163, 216.07530073169454),
    (0.865213112263103, 0.0002885163350064677, 216.075286652818),
    (0.8740040078932181, 0.00028883830848341153, 216.07527274888812),
    (0.8828043298308796, 0.0002891517676790176, 216.0752590661328),
    (0.8916144151585883, 0.0002894569445330787, 216.0752455737732),
    (0.9004345964124912, 0.00028975406253522584, 216.07523226493686),
    (0.9092652017663436, 0.00029004333800628, 216.07521910990573),
    (0.9181065552091947, 0.0002903249794051363, 216.07520614221542),
    (0.9269589767151265, 0.0002905991882510502, 216.07519334531088),
    (0.9358227824068801, 0.0002908661596042513, 216.07518072883923),
    (0.9446982847132939, 0.00029112608192757156, 216.0751682475839),
    (0.9535857925200474, 0.0002913791373231644, 216.07515593963097),
    (0.9624856113154553, 0.0002916255021248798, 216.07514377514713),
    (0.971398043330407, 0.0002918653467695802, 216.0751317926928)]  # type: list[VectorLike]


def jzazbz_to_jzczhz(jzazbz: Vector) -> Vector:
    """Jzazbz to JzCzhz."""

    jz, az, bz = jzazbz

    cz = math.sqrt(az ** 2 + bz ** 2)
    hz = math.degrees(math.atan2(bz, az))

    return [jz, cz, util.constrain_hue(hz)]


def jzczhz_to_jzazbz(jzczhz: Vector) -> Vector:
    """JzCzhz to Jzazbz."""

    jz, cz, hz = jzczhz

    return [
        jz,
        cz * math.cos(math.radians(hz)),
        cz * math.sin(math.radians(hz))
    ]


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
    MAX_C_BUFFER = 0.0001
    MAX_C_ROUND = 5

    def convert(self, coords: Vector, *args: Any, **kwargs: Any) -> Vector:
        """Convert to the target color space."""

        return jzazbz_to_jzczhz(xyz_d65_to_jzazbz(lin_srgb_to_xyz(lin_srgb(coords))))


class JzCzhz(LChish, Space):
    """
    JzCzhz class.

    https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
    """

    BASE = "jzazbz"
    NAME = "jzczhz"
    SERIALIZE = ("--jzczhz",)
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'
    CHANNEL_ALIASES = {
        "lightness": "jz",
        "chroma": "cz",
        "hue": "hz"
    }
    ACHROMATIC = Achromatic(
        # Precalculated from
        # {
        #     'low': (1, 5, 5, 1000.0),
        #     'mid': (1, 9, 2, 200.0),
        #     'high': (5, 521, 5, 100.0)
        # },
        ACHROMATIC_RESPONSE,
        2.121e-7,
        1.172e-6,
        0.00039,
        'catrom',
    )
    CHANNELS = (
        Channel("jz", 0.0, 1.0, limit=(0.0, None)),
        Channel("cz", 0.0, 0.5, limit=(0.0, None)),
        Channel("hz", 0.0, 360.0, flags=FLG_ANGLE, nans=ACHROMATIC.hue)
    )

    def is_achromatic(self, undefined: list[bool], coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        ldef, cdef, hdef = undefined
        if ldef and cdef:
            return False

        elif cdef:
            return coords[0] == 0.0

        elif ldef:
            return coords[1] < 1e-10

        return (
            coords[0] == 0.0 or
            self.ACHROMATIC.test(coords[0], coords[1], self.ACHROMATIC.hue if hdef else coords[2])
        )

    def achromatic_hue(self) -> float:
        """Ideal hue for conversion."""

        return self.ACHROMATIC.hue

    def hue_name(self) -> str:
        """Hue name."""

        return "hz"

    def to_base(self, coords: Vector) -> Vector:
        """To Jzazbz from JzCzhz."""

        return jzczhz_to_jzazbz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From Jzazbz to JzCzhz."""

        return jzazbz_to_jzczhz(coords)
