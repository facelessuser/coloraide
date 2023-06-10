"""Everything and the kitchen sink."""
from __future__ import annotations
from .color import Color as Base
from .spaces.rec2100_pq import Rec2100PQ
from .spaces.rec2100_hlg import Rec2100HLG
from .spaces.jzazbz import Jzazbz
from .spaces.jzczhz import JzCzhz
from .spaces.ictcp import ICtCp
from .spaces.din99o import DIN99o
from .spaces.lch99o import LCh99o
from .spaces.luv import Luv
from .spaces.lchuv import LChuv
from .spaces.hsluv import HSLuv
from .spaces.hpluv import HPLuv
from .spaces.okhsl import Okhsl
from .spaces.okhsv import Okhsv
from .spaces.hsi import HSI
from .spaces.ipt import IPT
from .spaces.igpgtg import IgPgTg
from .spaces.cmy import CMY
from .spaces.cmyk import CMYK
from .spaces.xyy import xyY
from .spaces.xyb import XYB
from .spaces.hunter_lab import HunterLab
from .spaces.prismatic import Prismatic
from .spaces.rlab import RLAB
from .spaces.orgb import oRGB
from .spaces.aces2065_1 import ACES20651
from .spaces.acescg import ACEScg
from .spaces.acescc import ACEScc
from .spaces.acescct import ACEScct
from .spaces.cam16 import CAM16
from .spaces.cam16_jmh import CAM16JMh
from .spaces.cam16_ucs import CAM16UCS, CAM16LCD, CAM16SCD
from .spaces.hct import HCT
from .spaces.ucs import UCS
from .spaces.rec709 import Rec709
from .distance.delta_e_itp import DEITP
from .distance.delta_e_99o import DE99o
from .distance.delta_e_z import DEZ
from .distance.delta_e_cam16 import DECAM16
from .distance.delta_e_hct import DEHCT
from .gamut.fit_hct_chroma import HCTChroma
from .interpolate.catmull_rom import CatmullRom
from .contrast.lstar import LstarContrast
from .cat import VonKries, XYZScaling, CAT02, CMCCAT97, Sharp, CMCCAT2000, CAT16
from .color import ColorMatch
from .interpolate import stop, hint
from .algebra import NaN

__all__ = ('ColorAll', 'ColorMatch', 'stop', 'hint', 'NaN')


class ColorAll(Base):
    """Color with all plugins."""


ColorAll.register(
    [
        # Spaces
        Rec709(),
        Rec2100PQ(),
        Rec2100HLG(),
        Jzazbz(),
        JzCzhz(),
        ICtCp(),
        DIN99o(),
        LCh99o(),
        Luv(),
        LChuv(),
        Okhsl(),
        Okhsv(),
        HSLuv(),
        HPLuv(),
        HSI(),
        IPT(),
        IgPgTg(),
        CMY(),
        CMYK(),
        xyY(),
        XYB(),
        HunterLab(),
        Prismatic(),
        RLAB(),
        oRGB(),
        ACES20651(),
        ACEScg(),
        ACEScc(),
        ACEScct(),
        CAM16(),
        CAM16JMh(),
        CAM16UCS(),
        CAM16SCD(),
        CAM16LCD(),
        HCT(),
        UCS(),

        # Delta E
        DEITP(),
        DE99o(),
        DEZ(),
        DECAM16(),
        DEHCT(),

        # Gamut Mapping
        HCTChroma(),

        # CAT
        VonKries(),
        XYZScaling(),
        CAT02(),
        CMCCAT97(),
        Sharp(),
        CMCCAT2000(),
        CAT16(),

        # Interpolation
        CatmullRom(),

        # Contrast
        LstarContrast()
    ]
)
