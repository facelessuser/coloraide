"""Sanity check that ensures all colors round trip back."""
from coloraide.everything import ColorAll as Color
from coloraide.spaces import Cylindrical
from coloraide import algebra as alg
import pytest

SPACES = {k: 5 for k in Color.CS_MAP.keys()}

# This color's gamut is less than the sRGB gamut we use to round trip, so we cannot test it.
del SPACES['hpluv']
SPACES['hct'] = 3


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

    # Except for black, it can be very difficult to get perfect round tripping
    # on achromatic colors unless we do absolutely no hue adjustments near achromatic.
    # Many algorithms do not exactly land on what is expected for achromatic. For
    # instance CIELab rarely resolves to `a = b = 0` except in the case of black.
    # For cylindrical spaces that pass through a Lab-like spaces during conversion,
    # you can often get wild hues near achromatic values because the saturation or
    # chroma never quite gets to zero. In these case, we often set hue as undefined when
    # chroma or saturation is very close to zero. But, when we pass through multiple
    # spaces that do this, we can get a compounding error near achromatic colors making
    # it difficult to get perfect round tripping with achromatic values.
    COLORS = [
        Color('red'),
        Color('orange'),
        Color('yellow'),
        Color('green'),
        Color('blue'),
        Color('indigo'),
        Color('violet'),
        Color('darkgrey'),
        Color('lightgrey'),
        Color('gray'),
        Color('black'),
        Color('white')
    ]

    # Ignore non-black achromatic cases for spaces who's algorithm isn't precise enough
    IGNORE_ACHROMA = ['okhsl', 'okhsv']

    # Ignore gray cases. Spaces that don't offer enough precision near grey.
    IGNORE_GREY = ['jzczhz', 'cam16-jmh', 'hct']

    ACHROMA = {'grey', 'white', 'darkgrey', 'lightgrey'}
    GREY = {'grey', 'darkgrey', 'lightgrey'}

    def assert_round_trip(self, color, space):
        """Cycle through all the other colors and convert to them and back and check the results."""

        c1 = Color(color)
        name = c1.to_string(names=True)
        c1.convert(space, in_place=True)
        p1 = SPACES[space]
        for space, p2 in SPACES.items():
            p = min(p1, p2)
            if ((c1.space() in self.IGNORE_ACHROMA or space in self.IGNORE_ACHROMA) and name in self.ACHROMA):
                continue
            if ((c1.space() in self.IGNORE_GREY or space in self.IGNORE_GREY) and name in self.GREY):
                continue
            # Print the color space to easily identify which color space broke.
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            # Catch cases where we are really close to 360 which should wrap to 0
            if isinstance(c2._space, Cylindrical):
                if alg.round_half_up(alg.no_nan(c2['hue']), p) == 360:
                    c2.set('hue', 0)
            # Run rounded string back through parsing in case we hit something like a hue that needs normalization.
            str1 = Color(c1.to_string(color=True, fit=False)).to_string(color=True, fit=False, precision=p)
            str2 = Color(c2.to_string(color=True, fit=False)).to_string(color=True, fit=False, precision=p)
            # Print failing results for debug purposes
            if str1 != str2:
                print('----- Convert: {} <=> {} -----'.format(c1.space(), space))
                print('Name: ', name)
                print('Original: ', color.to_string(color=True, fit=False, precision=p))
                print(c1.space() + ': ', str1, c1[:])
                print(space + ': ', str2, c2[:])
                assert str1 == str2

    @pytest.mark.parametrize('space', SPACES)
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)
