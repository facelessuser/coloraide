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

    # Some color space have not too great round tripping.
    PRECISION_EXCEPTIONS = {
        # Okhsv: On the edge of red. Force a rounding of 3.
        # ```
        # Original:  color(srgb 1 0 0)
        # okhsv:  color(--okhsv 29.234 99.952% 100%) [29.23388519234263, 99.9521969225699, 100.00000001685628]
        # srgb:  color(--okhsv 29.234 100% 100%) [29.233890258729758, 100.00004917796078, 100.0000000337129]
        # ```
        'okhsv'
    }

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
        for space in c1.CS_MAP.keys():
            # Print the color space to easily identify which color space broke.
            precision = 5
            if c1.space() in self.PRECISION_EXCEPTIONS:
                precision = 3
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            str1 = c1.to_string(color=True, precision=precision)
            # Run back through parsing in case we hit something like a hue that needs normalization.
            str2 = Color(c2.to_string(color=True)).to_string(color=True, precision=precision)
            if str1 != str2:
                print('----- Convert: {} <=> {} -----'.format(c1.space(), space))
                print('Original: ', color.to_string(color=True))
                print(c1.space() + ': ', str1, c1.coords())
                print(space + ': ', str2, c2.coords())
                assert str1 == str2

    @pytest.mark.parametrize('space', list(Color.CS_MAP.keys()))
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)
