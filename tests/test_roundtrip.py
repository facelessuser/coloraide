"""Sanity check that ensures all colors round trip back."""
from coloraide import Color
import pytest


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
        # Color('red'),
        Color('orange'),
        Color('yellow'),
        Color('green'),
        Color('blue'),
        Color('indigo'),
        Color('violet'),
        # Color('white'),
        # Color('black')
    ]

    def assert_round_trip(self, color, space):
        """Cycle through all the other colors and convert to them and back and check the results."""

        c1 = Color(color).convert(space)
        for space in c1.CS_MAP.keys():
            # Print the color space to easily identify which color space broke.
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            str1 = c1.to_string(color=True)
            str2 = c2.to_string(color=True)
            if str1 != str2:
                print('----- Color Space {} -----'.format(color.space()))
                print(color)
                print('>>> Convert to: {}'.format(space))
                assert str1 == str2

    @pytest.mark.parametrize('space', list(Color.CS_MAP.keys()))
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)
