"""Test Linear Display P3."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestLinearDisplayP3(util.ColorAssertsPyTest):
    """Test Linear Display P3."""

    COLORS = [
        ('red', 'color(--display-p3-linear 0.82246 0.03319 0.01708)'),
        ('orange', 'color(--display-p3-linear 0.88926 0.39697 0.04432)'),
        ('yellow', 'color(--display-p3-linear 1 1 0.08948)'),
        ('green', 'color(--display-p3-linear 0.03832 0.2087 0.01563)'),
        ('blue', 'color(--display-p3-linear 0 0 0.91052)'),
        ('indigo', 'color(--display-p3-linear 0.05787 0.00234 0.20446)'),
        ('violet', 'color(--display-p3-linear 0.74283 0.2442 0.80925)'),
        ('white', 'color(--display-p3-linear 1 1 1)'),
        ('gray', 'color(--display-p3-linear 0.21586 0.21586 0.21586)'),
        ('black', 'color(--display-p3-linear 0 0 0)'),
        # Test CSS color
        ('color(--display-p3-linear 0 0.50196 0)', 'color(--display-p3-linear 0 0.50196 0)'),
        ('color(--display-p3-linear 0 0.50196 0 / 0.5)', 'color(--display-p3-linear 0 0.50196 0 / 0.5)'),
        ('color(--display-p3-linear 50% 50% 50% / 50%)', 'color(--display-p3-linear 0.5 0.5 0.5 / 0.5)'),
        ('color(--display-p3-linear none none none / none)', 'color(--display-p3-linear none none none / none)'),
        # Test range
        ('color(--display-p3-linear 0% 0% 0%)', 'color(--display-p3-linear 0 0 0)'),
        ('color(--display-p3-linear 100% 100% 100%)', 'color(--display-p3-linear 1 1 1)'),
        ('color(--display-p3-linear -100% -100% -100%)', 'color(--display-p3-linear -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('display-p3-linear'), Color(color2))


class TestLinearDisplayP3Serialize(util.ColorAssertsPyTest):
    """Test Linear Display serialization."""

    COLORS = [
        # Test color
        ('color(--display-p3-linear 0 0.3 0.75 / 0.5)', {}, 'color(--display-p3-linear 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--display-p3-linear 0 0.3 0.75)', {'alpha': True}, 'color(--display-p3-linear 0 0.3 0.75 / 1)'),
        ('color(--display-p3-linear 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--display-p3-linear 0 0.3 0.75)'),
        # Test None
        ('color(--display-p3-linear none 0.3 0.75)', {}, 'color(--display-p3-linear 0 0.3 0.75)'),
        ('color(--display-p3-linear none 0.3 0.75)', {'none': True}, 'color(--display-p3-linear none 0.3 0.75)'),
        # Test Fit
        ('color(--display-p3-linear 1.2 0.2 0)', {}, 'color(--display-p3-linear 1 0.23465 0.01349)'),
        ('color(--display-p3-linear 1.2 0.2 0)', {'fit': False}, 'color(--display-p3-linear 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestLinearDisplayP3Poperties(util.ColorAsserts, unittest.TestCase):
    """Test Linear Display P3 properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--display-p3-linear 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--display-p3-linear 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--display-p3-linear 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--display-p3-linear 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
