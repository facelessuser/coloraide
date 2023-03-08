# pragma: init

from coloraide import Color as Base
from coloraide.cat import WHITES
from coloraide.spaces import Space
from coloraide import algebra as alg
from coloraide.types import Vector
from coloraide.channels import Channel


class LMS(Space):
    """The LMS class."""

    BASE = "srgb-linear"
    NAME = "lms"
    SERIALIZE = ("--lms",)
    CHANNELS = (
        Channel("l", 0.0, 1.0),
        Channel("m", 0.0, 1.0),
        Channel("s", 0.0, 1.0)
    )
    CHANNEL_ALIASES = {
        "long": "l",
        "medium": "m",
        "short": "s"
    }
    WHITE = WHITES['2deg']['D65']

    LRGB_TO_LMS = [
        [0.178824041258, 0.4351609057000001, 0.04119349692],
        [0.034556423182, 0.27155382458, 0.038671308360000003],
        [0.000299565576, 0.0018430896, 0.01467086136]
    ]

    LMS_TO_LRGB = [
        [8.094435598032371, -13.050431460496926, 11.672058453917323],
        [-1.0248505586646686, 5.401931309674973, -11.361471490598712],
        [-0.03652974715933318, -0.412162807001268, 69.35132423820858]
    ]

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return alg.dot(self.LMS_TO_LRGB, coords, dims=alg.D2_D1)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return alg.dot(self.LRGB_TO_LMS, coords, dims=alg.D2_D1)


class Color(Base):
    ...


Color.register(LMS())


def get_limit(c, channel, upper=False):

    if upper:
        low = c[channel]
        high = 1
    else:
        high = c[channel]
        low = 0

    temp = c.clone()

    while abs(high - low) >= 0.002:
        value = (high + low) * 0.5
        temp[channel] = value
        if temp.in_gamut('srgb', tolerance=0.01):
            if upper:
                low = value
            else:
                high = value
        else:
            if upper:
                high = value
            else:
                low = value

    return temp.clip('srgb')


def confusion_line(c, cone):
    """Generate colors on a line of confusion."""

    lms = c.convert('lms')
    high = get_limit(lms, cone, upper=True)
    low = get_limit(lms, cone)
    return Color.steps([low, high], steps=6, space='lms', out_space='srgb')

# pragma: init
