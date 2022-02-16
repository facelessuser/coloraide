"""Sanity check that ensures all colors round trip back."""
from coloraide import Color
from coloraide.spaces import Cylindrical
from coloraide import util
import pytest

SPACES = Color.CS_MAP.keys()


class TestRoundTrip:
    """
    Test round trip conversions of all color spaces.

    A color that does not round trip back likely has a broken conversion.
    It may be possible that some color spaces degrade through conversion,
    but the currently supported spaces have enough integrity when performing
    a round trip to meet the required value at the default precision.

    There are certain values they may not round trip exactly. Hues may become
    null, etc. But we are picking general colors that should round trip well
    enough.
    """

    # Skip colors with null hues or hues that can wrap.
    COLORS = [
        Color('red'),
        Color('orange'),
        Color('yellow'),
        Color('green'),
        Color('blue'),
        Color('indigo'),
        Color('violet'),
        # Color('white'),  # General: this is difficult as not everything lands exactly
        Color('black')
    ]

    def assert_round_trip(self, color, space):
        """Cycle through all the other colors and convert to them and back and check the results."""

        c1 = Color(color).convert(space)
        for space in SPACES:
            # Print the color space to easily identify which color space broke.
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            # Catch cases where we are really close to 360 which should wrap to 0
            for c in (c1, c2):
                if isinstance(c._space, Cylindrical):
                    if util.round_half_up(util.no_nan(c.hue), c.PRECISION) == 360:
                        c.hue = 0
            # Run rounded string back through parsing in case we hit something like a hue that needs normalization.
            str1 = Color(c1.to_string(color=True, fit=False)).to_string(color=True, fit=False)
            str2 = Color(c2.to_string(color=True, fit=False)).to_string(color=True, fit=False)
            # Print failing results for debug purposes
            if str1 != str2:
                print('----- Convert: {} <=> {} -----'.format(c1.space(), space))
                print('Original: ', color.to_string(color=True, fit=False))
                print(c1.space() + ': ', str1, c1.coords())
                print(space + ': ', str2, c2.coords())
                assert str1 == str2

    @pytest.mark.parametrize('space', SPACES)
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)
