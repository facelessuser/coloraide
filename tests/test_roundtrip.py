"""Sanity check that ensures all colors round trip back."""
from coloraide.everything import ColorAll as Base
from coloraide.spaces import HSLish, HSVish
from coloraide import algebra as alg
import math
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

    SPACES = dict.fromkeys(Color.CS_MAP, 10)
    # HCT will actually provide good conversion at about 11 decimal precision,
    # but certain spaces have a gamma power function that is less accurate with RGB channels near zero
    # (not necessarily near black): Rec. 2020, Rec. 709, etc. HCT, which approximates its inverse transform,
    # can emphasizes these cases and fall a little below our target of 6. This is expected.
    # To handle this in testing, we can specify more nuanced conditions. Provide the default precision,
    # and optional lower precision, and spaces that would trigger this lower precision.
    SPACES['hct'] = (10, 4, {'rec709', 'rec2020', 'a98-rgb'})

    COLORS = [
        Color('red'),
        Color('orange'),
        Color('yellow'),
        Color('green'),
        Color('blue'),
        Color('indigo'),
        Color('violet')
    ]

    def assert_round_trip(self, color, space):
        """Cycle through all the other colors and convert to them and back and check the results."""

        c1 = self.Color(color)
        name = c1.to_string(names=True)
        c1.convert(space, in_place=True)
        p1 = self.SPACES[space]
        original_space = space
        # Is this a value or a tuple for conditional precision
        conditional = isinstance(p1, tuple)
        for space, p2 in self.SPACES.items():
            pa = (p1[1] if space in p1[2] else p1[0]) if conditional else p1
            pb = (p2[1] if original_space in p2[2] else p2[0]) if isinstance(p2, tuple) else p2
            p = min(pa, pb)
            # Print the color space to easily identify which color space broke.
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            # Catch cases where we are really close to 360 which should wrap to 0
            if c2._space.is_polar():
                if alg.round_half_up(c2.get('hue', nans=False), p) == 360:
                    c2.set('hue', 0)
            # In HSL and HSV spaces particularly, we can get nonsense saturation if lightness
            # is not exactly within 0 - 1 range. Ignore saturation in achromatic cases.
            if isinstance(c2._space, (HSLish, HSVish)) and math.isnan(c2['hue']):
                c2[c2._space.indexes()[1]] = 0.0
            if isinstance(c1._space, (HSLish, HSVish)) and math.isnan(c1['hue']):
                c1[c1._space.indexes()[1]] = 0.0
            # Run rounded string back through parsing in case we hit something like a hue that needs normalization.
            str1 = self.Color(c1.to_string(color=True, fit=False)).to_string(color=True, fit=False, precision=p)
            str2 = self.Color(c2.to_string(color=True, fit=False)).to_string(color=True, fit=False, precision=p)
            # Print failing results for debug purposes
            if str1 != str2:
                print(f'----- Convert: {c1.space()} <=> {space} -----')
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


class TestAchromaticRoundTrip(TestRoundTrip):
    """
    Test achromatic round trip.

    For convenience, we determine achromatic colors and set hues to `NaN`.
    This can cause a slight drop in precision.
    """

    class Color(Base):
        """Local color object."""

    Color.deregister('space:hpluv')
    Color.deregister('space:ryb')
    Color.deregister('space:ryb-biased')

    SPACES = dict.fromkeys(Color.CS_MAP, 10)

    COLORS = [
        Color('darkgrey'),
        Color('lightgrey'),
        Color('gray'),
        Color('black'),
        Color('white')
    ]

    @pytest.mark.parametrize('space', SPACES)
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)
            if c._space.is_polar():
                hue = c._space.hue_name()
                assert math.isnan(c[hue]) is True


class TestRYBRoundTrip(TestRoundTrip):
    """
    Test RYB round trip.

    We are only interested in testing this against sRGB.
    """

    class Color(Base):
        """Local color object."""

    SPACES = {'srgb': 8}

    COLORS = [
        Color('ryb', [1, 1, 1]),
        Color('ryb', [1, 0, 0]),
        Color('ryb', [1, 0, 0]),
        Color('ryb', [0, 1, 0]),
        Color('ryb', [0, 0, 1]),
        Color('ryb', [1, 1, 0]),
        Color('ryb', [0, 1, 1]),
        Color('ryb', [1, 0, 1]),
        Color('ryb', [0, 0, 0]),
        Color('ryb', [0.2, 5, 0.7]),
        Color('ryb', [0.8, 0.65, 0.21]),
        Color('ryb', [0.8, 0.65, 0.21]),
        Color('ryb', [0.8, 0.65, 0.21]),
        Color('ryb', [0.9, 0.8, 0.21]),
        Color('ryb', [0.1, 0.3, 0.05])
    ]

    @pytest.mark.parametrize('space', SPACES)
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)


class TestRYBBiasedRoundTrip(TestRoundTrip):
    """
    Test RYB round trip.

    We are only interested in testing this against sRGB.
    """

    class Color(Base):
        """Local color object."""

    SPACES = {'srgb': 8}

    COLORS = [
        Color('ryb-biased', [1, 1, 1]),
        Color('ryb-biased', [1, 0, 0]),
        Color('ryb-biased', [1, 0, 0]),
        Color('ryb-biased', [0, 1, 0]),
        Color('ryb-biased', [0, 0, 1]),
        Color('ryb-biased', [1, 1, 0]),
        Color('ryb-biased', [0, 1, 1]),
        Color('ryb-biased', [1, 0, 1]),
        Color('ryb-biased', [0, 0, 0]),
        Color('ryb-biased', [0.2, 5, 0.7]),
        Color('ryb-biased', [0.8, 0.65, 0.21]),
        Color('ryb-biased', [0.8, 0.65, 0.21]),
        Color('ryb-biased', [0.8, 0.65, 0.21]),
        Color('ryb-biased', [0.9, 0.8, 0.21]),
        Color('ryb-biased', [0.1, 0.3, 0.05])
    ]

    @pytest.mark.parametrize('space', SPACES)
    def test_round_trip(self, space):
        """Test round trip."""

        for c in self.COLORS:
            self.assert_round_trip(c, space)
