"""Test RYB."""
import itertools
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestRYB(util.ColorAssertsPyTest):
    """Test RYB."""

    COLORS = [
        ('color(srgb 1.0 1.0 1.0)', 'color(--ryb 0 0 0)'),
        ('color(srgb 1.0 0.0 0.0)', 'color(--ryb 1 0 0)'),
        ('color(srgb 1.0 1.0 0.0)', 'color(--ryb 0 1 0)'),
        ('color(srgb 1.0 0.5 0.0)', 'color(--ryb 1 1 0)'),
        ('color(srgb 0.163 0.373 0.6)', 'color(--ryb 0 0 1)'),
        ('color(srgb 0.5 0.0 0.5)', 'color(--ryb 1 0 1)'),
        ('color(srgb 0.0 0.66 0.2)', 'color(--ryb 0 1 1)'),
        ('color(srgb 0.2 0.094 0.0)', 'color(--ryb 1 1 1)'),
        # # Test CSS color
        ('color(--ryb 0 0.50196 0)', 'color(--ryb 0 0.50196 0)'),
        ('color(--ryb 0 0.50196 0 / 0.5)', 'color(--ryb 0 0.50196 0 / 0.5)'),
        ('color(--ryb 50% 50% 50% / 50%)', 'color(--ryb 0.5 0.5 0.5 / 0.5)'),
        ('color(--ryb none none none / none)', 'color(--ryb none none none / none)'),
        # # Test range
        ('color(--ryb 0% 0% 0%)', 'color(--ryb 0 0 0)'),
        ('color(--ryb 100% 100% 100%)', 'color(--ryb 1 1 1)'),
        ('color(--ryb -100% -100% -100%)', 'color(--ryb -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ryb'), Color(color2))


class TestRYBBiased(util.ColorAssertsPyTest):
    """Test RYB biased."""

    COLORS = [
        ('color(srgb 1.0 1.0 1.0)', 'color(--ryb-biased 0 0 0)'),
        ('color(srgb 1.0 0.0 0.0)', 'color(--ryb-biased 1 0 0)'),
        ('color(srgb 1.0 1.0 0.0)', 'color(--ryb-biased 0 1 0)'),
        ('color(srgb 1.0 0.5 0.0)', 'color(--ryb-biased 1 1 0)'),
        ('color(srgb 0.163 0.373 0.6)', 'color(--ryb-biased 0 0 1)'),
        ('color(srgb 0.5 0.0 0.5)', 'color(--ryb-biased 1 0 1)'),
        ('color(srgb 0.0 0.66 0.2)', 'color(--ryb-biased 0 1 1)'),
        ('color(srgb 0.2 0.094 0.0)', 'color(--ryb-biased 1 1 1)'),
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ryb-biased'), Color(color2))


class TestRYBSerialize(util.ColorAssertsPyTest):
    """Test RYB serialization."""

    COLORS = [
        # Test color
        ('color(--ryb 0 0.3 0.75 / 0.5)', {}, 'color(--ryb 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--ryb 0 0.3 0.75)', {'alpha': True}, 'color(--ryb 0 0.3 0.75 / 1)'),
        ('color(--ryb 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--ryb 0 0.3 0.75)'),
        # Test None
        ('color(--ryb none 0.3 0.75)', {}, 'color(--ryb 0 0.3 0.75)'),
        ('color(--ryb none 0.3 0.75)', {'none': True}, 'color(--ryb none 0.3 0.75)'),
        # Test Fit
        ('color(--ryb 1.2 0.2 0)', {}, 'color(--ryb 1 0.45367 0.10497)'),
        ('color(--ryb 1.2 0.2 0)', {'fit': False}, 'color(--ryb 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestRYBRoundTrip:
    """
    Test round tripping within the RYB gamut.

    Converting to RYB requires inverting a trilinear interpolation, so these tests ensure we can accurately get back
    the colors we started with.
    """

    # Include some values very close to the vertices as they are the most poorly conditioned
    VALUES = [i / 10 for i in range(11)] + [0.001, 0.999]
    GRID = list(itertools.product(VALUES, repeat=3))

    @pytest.mark.parametrize('space', ['ryb', 'ryb-biased'])
    def test_srgb_precision(self, space):
        """Test that the inverse is precise by converting back to sRGB, which is well conditioned for both spaces."""

        for coords in self.GRID:
            srgb = Color(space, list(coords)).convert('srgb')
            result = srgb.convert(space).convert('srgb')
            for a, b in zip(result[:-1], srgb[:-1]):
                assert abs(a - b) < 1e-12, f'{space} {coords}: {result} != {srgb}'

    def test_ryb_round_trip(self):
        """Test RYB to sRGB and back."""

        for coords in self.GRID:
            result = Color('ryb', list(coords)).convert('srgb').convert('ryb')
            for a, b in zip(result[:-1], coords):
                assert abs(a - b) < 1e-10, f'{coords}: {result}'

    def test_ryb_biased_round_trip(self):
        """
        Test RYB biased to sRGB and back.

        The bias is a smoothstep, which is flat at 0 and 1, so removing it near the vertices is poorly conditioned,
        and the error of a root finder near a flat region scales with the square root of the machine epsilon.
        """

        for coords in self.GRID:
            result = Color('ryb-biased', list(coords)).convert('srgb').convert('ryb-biased')
            for a, b in zip(result[:-1], coords):
                assert abs(a - b) < 1e-4, f'{coords}: {result}'

        # Away from the vertices, we can expect much better
        for coords in itertools.product([0.2, 0.35, 0.5, 0.65, 0.8], repeat=3):
            result = Color('ryb-biased', list(coords)).convert('srgb').convert('ryb-biased')
            for a, b in zip(result[:-1], coords):
                assert abs(a - b) < 1e-12, f'{coords}: {result}'


class TestRYBPoperties(util.ColorAsserts, unittest.TestCase):
    """Test RYB."""

    def test_c(self):
        """Test `c`."""

        c = Color('color(--ryb 0 0 1)')
        self.assertEqual(c['r'], 0)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_m(self):
        """Test `m`."""

        c = Color('color(--ryb 0 0 1)')
        self.assertEqual(c['y'], 0)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_y(self):
        """Test `y`."""

        c = Color('color(--ryb 0 0 1)')
        self.assertEqual(c['b'], 1)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--ryb 0 0 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('srgb', [0.3, 0.3, 0.3]).convert('ryb').is_achromatic(), True)
        self.assertEqual(Color('srgb', [0.3, 0.3, 0.30000001]).convert('ryb').is_achromatic(), True)
        self.assertEqual(Color('srgb', [0.3, 0.4, 0.3]).convert('ryb').is_achromatic(), False)
        self.assertEqual(Color('ryb', [1.0, 1.0, NaN]).convert('ryb').is_achromatic(), False)
