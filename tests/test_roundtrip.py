"""Sanity check that ensures all colors round trip back."""
from coloraide.everything import ColorAll as Base
from coloraide.spaces import Cylindrical
from coloraide import algebra as alg
import pytest


class TestRoundTrip:
    """
    Test round trip conversions for non-achromatic colors.

    A color that does not round trip back likely has a broken conversion.
    It may be possible that some color spaces degrade through conversion.
    Only lower precision for spaces that do not have a high degree of accuracy,
    but they should round trip for their lower precision.
    """

    class Color(Base):
        """Local color object."""

    Color.deregister('space:hpluv')

    SPACES = {k: 5 for k in Color.CS_MAP.keys()}
    SPACES['hct'] = 3
    SPACES['cam16-jmh'] = 3
    SPACES['okhsl'] = 4
    SPACES['okhsv'] = 4
    SPACES['jzczhz'] = 4

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

    def assert_round_trip(self, color, space):
        """Cycle through all the other colors and convert to them and back and check the results."""

        c1 = self.Color(color)
        name = c1.to_string(names=True)
        c1.convert(space, in_place=True)
        p1 = self.SPACES[space]
        for space, p2 in self.SPACES.items():
            p = min(p1, p2)
            # Print the color space to easily identify which color space broke.
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            # Catch cases where we are really close to 360 which should wrap to 0
            if isinstance(c2._space, Cylindrical):
                if alg.round_half_up(alg.no_nan(c2['hue']), p) == 360:
                    c2.set('hue', 0)
            # Run rounded string back through parsing in case we hit something like a hue that needs normalization.
            str1 = self.Color(c1.to_string(color=True, fit=False)).to_string(color=True, fit=False, precision=p)
            str2 = self.Color(c2.to_string(color=True, fit=False)).to_string(color=True, fit=False, precision=p)
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


# class TestAchromaticRoundTrip(TestRoundTrip):
#     """
#     Test achromatic round trip.

#     For convienance, we determine achromatic colors and set hues to `NaN`.
#     This can cause a slight drop in precision.
#     """

#     class Color(Base):
#         """Local color object."""

#     Color.deregister('space:hpluv')

#     SPACES = {k: 5 for k in Color.CS_MAP.keys()}
#     SPACES['hct'] = 3
#     SPACES['cam16-jmh'] = 3
#     SPACES['okhsl'] = 4
#     SPACES['okhsv'] = 4
#     SPACES['jzczhz'] = 4

#     COLORS = [
#         Color('darkgrey'),
#         Color('lightgrey'),
#         Color('gray'),
#         Color('black'),
#         Color('white')
#     ]

#     @pytest.mark.parametrize('space', SPACES)
#     def test_round_trip(self, space):
#         """Test round trip."""

#         for c in self.COLORS:
#             self.assert_round_trip(c, space)
