"""Test Helmlab."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestHelmlaMetric(util.ColorAssertsPyTest):
    """Test Helmlab."""

    COLORS = [
        ('red', 'color(--helmlab-metric 0.9207 0.94084 -0.2063)'),
        ('orange', 'color(--helmlab-metric 1.0056 0.80476 0.71403)'),
        ('yellow', 'color(--helmlab-metric 0.89977 0.17785 0.87596)'),
        ('green', 'color(--helmlab-metric 0.37812 -0.04603 0.55253)'),
        ('blue', 'color(--helmlab-metric 0.76231 -0.12541 -0.20263)'),
        ('indigo', 'color(--helmlab-metric 0.58174 0.15615 -0.23201)'),
        ('violet', 'color(--helmlab-metric 1.0991 0.16562 -0.1134)'),
        ('white', 'color(--helmlab-metric 1.1211 0.10164 0.20041)'),
        ('gray', 'color(--helmlab-metric 0.77788 0.23579 0.16737)'),
        ('black', 'color(--helmlab-metric 0 0 0)'),
        ('color(srgb 1.5 1.5 1.5)', 'color(--helmlab-metric 1.5448 0.01225 0.0711)'),
        ('color(srgb 1e-3 1e-3 1e-3)', 'color(--helmlab-metric 0.02104 0.01541 -0.00171)'),
        # Test color
        ('color(--helmlab-metric 0.5 0.1 -0.1)', 'color(--helmlab-metric 0.5 0.1 -0.1)'),
        ('color(--helmlab-metric 0.5 0.1 -0.1 / 0.5)', 'color(--helmlab-metric 0.5 0.1 -0.1 / 0.5)'),
        ('color(--helmlab-metric 50% 50% -50% / 50%)', 'color(--helmlab-metric 0.8 0.75 -0.75 / 0.5)'),
        ('color(--helmlab-metric none none none / none)', 'color(--helmlab-metric none none none / none)'),
        # Test percent ranges
        ('color(--helmlab-metric 0% 0% 0%)', 'color(--helmlab-metric 0 0 0)'),
        ('color(--helmlab-metric 100% 100% 100%)', 'color(--helmlab-metric 1.6 1.5 1.5)'),
        ('color(--helmlab-metric -100% -100% -100%)', 'color(--helmlab-metric -1.6 -1.5 -1.5)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('helmlab-metric'), Color(color2))


class TestHelmlabMetricSerialize(util.ColorAssertsPyTest):
    """Test Helmlab serialization."""

    COLORS = [
        # Test color
        ('color(--helmlab-metric 0.1 0.75 -0.1 / 0.5)', {}, 'color(--helmlab-metric 0.1 0.75 -0.1 / 0.5)'),
        # Test alpha
        ('color(--helmlab-metric 0.1 0.75 -0.1)', {'alpha': True}, 'color(--helmlab-metric 0.1 0.75 -0.1 / 1)'),
        ('color(--helmlab-metric 0.1 0.75 -0.1 / 0.5)', {'alpha': False}, 'color(--helmlab-metric 0.1 0.75 -0.1)'),
        # Test None
        ('color(--helmlab-metric none 0.75 -0.1)', {}, 'color(--helmlab-metric 0 0.75 -0.1)'),
        ('color(--helmlab-metric none 0.75 -0.1)', {'none': True}, 'color(--helmlab-metric none 0.75 -0.1)'),
        # Test Fit (not bound)
        ('color(--helmlab-metric 1.2 0.75 -0.1)', {}, 'color(--helmlab-metric 1.2 0.75 -0.1)'),
        ('color(--helmlab-metric 1.2 0.75 -0.1)', {'fit': False}, 'color(--helmlab-metric 1.2 0.75 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHelmlabMetricPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Helmlab."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--helmlab-metric -0.02 0.7 0.04)')
        self.assertEqual(c['l'], -0.02)
        c['l'] = 0.1
        self.assertEqual(c['l'], 0.1)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--helmlab-metric -0.02 0.7 0.04)')
        self.assertEqual(c['a'], 0.7)
        c['a'] = 0.2
        self.assertEqual(c['a'], 0.2)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--helmlab-metric -0.02 0.7 0.04)')
        self.assertEqual(c['b'], 0.04)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--helmlab-metric -0.02 0.7 0.04)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('color(--helmlab-metric -0.02 0.7 0.03 / 1)')
        self.assertEqual(c._space.names(), ('l', 'a', 'b'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('helmlab-metric', [0.3, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab-metric', [0.3, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab-metric', [NaN, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab-metric', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('helmlab-metric', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('helmlab-metric', [0, 0.1, -0.2]).is_achromatic(), False)
        self.assertEqual(Color('helmlab-metric', [NaN, 0, -0.1]).is_achromatic(), False)
        self.assertEqual(Color('helmlab-metric', [0.3, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab-metric', [NaN, NaN, 0]).is_achromatic(), True)
