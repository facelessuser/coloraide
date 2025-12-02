"""Test Msh library."""
import math
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestMsh(util.ColorAssertsPyTest):
    """Test Msh."""

    COLORS = [
        ('red', 'color(--msh 117.32 1.0998 0.69813rad)'),
        ('orange', 'color(--msh 111.45 0.83341 1.2765rad)'),
        ('yellow', 'color(--msh 137.21 0.78423 1.7951rad)'),
        ('green', 'color(--msh 85.439 0.9991 2.3739rad)'),
        ('blue', 'color(--msh 137.65 1.3339 5.3457rad)'),
        ('indigo', 'color(--msh 77.026 1.3018 5.4823rad)'),
        ('violet', 'color(--msh 96.895 0.76803 5.7046rad)'),
        ('white', 'color(--msh 100 0 0rad)'),
        ('gray', 'color(--msh 53.585 0 0rad)'),
        ('black', 'color(--msh 0 0 0rad)'),
        # Test color
        ('color(--msh 100 0.1 0.1rad)', 'color(--msh 100 0.1 0.1rad)'),
        ('color(--msh 100 0.1 0.1rad / 0.5)', 'color(--msh 100 0.1 0.1rad / 0.5)'),
        ('color(--msh 50% 50% 0.1rad / 50%)', 'color(--msh 89.975 0.8 0.1rad / 0.5)'),
        ('color(--msh none none none / none)', 'color(--msh none none none / none)'),
        # Test percent ranges
        ('color(--msh 0% 0% 0rad)', 'color(--msh 0 0 0rad)'),
        ('color(--msh 100% 100% 0rad)', 'color(--msh 179.95 1.6 0rad)'),
        ('color(--msh -100% -100% 0rad)', 'color(--msh -179.95 -1.6 0rad)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('msh'), Color(color2))


class TestMshSerialize(util.ColorAssertsPyTest):
    """Test Msh serialization."""

    COLORS = [
        # Test color
        ('color(--msh 80 1.08 1.88rad / 0.5)', {}, 'color(--msh 80 1.08 1.88rad / 0.5)'),
        # Test alpha
        ('color(--msh 80 1.08 1.88rad)', {'alpha': True}, 'color(--msh 80 1.08 1.88rad / 1)'),
        ('color(--msh 80 1.08 1.88rad / 0.5)', {'alpha': False}, 'color(--msh 80 1.08 1.88rad)'),
        # Test None
        ('color(--msh none 1.08 1.88rad)', {}, 'color(--msh 0 1.08 1.88rad)'),
        ('color(--msh none 1.08 1.88rad)', {'none': True}, 'color(--msh none 1.08 1.88rad)'),
        # Test Fit (not bound)
        ('color(--msh 80 2 1.88rad)', {}, 'color(--msh 80 2 1.88rad)'),
        ('color(--msh 80 2 1.88rad)', {'fit': False}, 'color(--msh 80 2 1.88rad)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestMshProperties(util.ColorAsserts, unittest.TestCase):
    """Test Msh."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--msh 80 1.08 1.88rad / 1)')
        self.assertEqual(c._space.names(), ('m', 's', 'h'))
        self.assertEqual(c._space.lightness_name(), 'm')
        self.assertEqual(c._space.radial_name(), 's')

    def test_indexes(self):
        """Test LCh-ish indexes."""

        self.assertEqual(Color('color(--msh 80 1.08 1.88rad / 1)')._space.indexes(), [0, 1, 2])

    def test_magnitude(self):
        """Test `magnitude`."""

        c = Color('color(--msh 80 1.08 1.88rad / 1)')
        self.assertEqual(c['magnitude'], 80)
        c['magnitude'] = 60
        self.assertEqual(c['magnitude'], 60)

    def test_s(self):
        """Test `s`."""

        c = Color('color(--msh 80 1.08 1.88rad / 1)')
        self.assertEqual(c['s'], 1.08)
        c['s'] = 1.0
        self.assertEqual(c['s'], 1.0)

    def test_h(self):
        """Test `h`."""

        c = Color('color(--msh 80 1.08 1.88rad / 1)')
        self.assertEqual(c['h'], 1.88)
        c['h'] = 2.0
        self.assertEqual(c['h'], 2.0)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--msh 80 1.08 1.88rad / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chroma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to lab."""

        self.assertColorEqual(
            Color('color(--msh 80 -1.08 1.8rad / 1)').normalize(),
            Color(f'color(--msh 80 1.08 {1.8 + math.pi}rad / 1)')
        )


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('msh', [NaN, 0.00001, 1.88]).is_achromatic(), True)
        self.assertEqual(Color('msh', [0, NaN, 1.88]).is_achromatic(), True)
        self.assertEqual(Color('msh', [0, 0.5, 1.88]).is_achromatic(), False)
        self.assertEqual(Color('msh', [NaN, 0.5, 1.88]).is_achromatic(), False)
        self.assertEqual(Color('msh', [20, NaN, 1.88]).is_achromatic(), True)
        self.assertEqual(Color('msh', [NaN, NaN, 1.88]).is_achromatic(), True)
        self.assertEqual(Color('msh', [20, -1.3, 1.88]).is_achromatic(), False)
