"""Test IgPgTg."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestIgPgTg(util.ColorAssertsPyTest):
    """Test IgPgTg."""

    COLORS = [
        ('red', 'color(--igpgtg 0.54834 0.15366 0.43674)'),
        ('orange', 'color(--igpgtg 0.73238 0.0397 0.32108)'),
        ('yellow', 'color(--igpgtg 0.94415 -0.1422 0.39035)'),
        ('green', 'color(--igpgtg 0.42594 -0.18386 0.17055)'),
        ('blue', 'color(--igpgtg 0.3076 -0.26988 -0.40879)'),
        ('indigo', 'color(--igpgtg 0.22925 0.08712 -0.20068)'),
        ('violet', 'color(--igpgtg 0.68117 0.22553 -0.17411)'),
        ('white', 'color(--igpgtg 0.97415 0.00139 -0.00404)'),
        ('gray', 'color(--igpgtg 0.50619 0.00072 -0.0021)'),
        ('black', 'color(--igpgtg 0 0 0)'),
        # Test color
        ('color(--igpgtg 0.5 0.1 -0.1)', 'color(--igpgtg 0.5 0.1 -0.1)'),
        ('color(--igpgtg 0.5 0.1 -0.1 / 0.5)', 'color(--igpgtg 0.5 0.1 -0.1 / 0.5)'),
        ('color(--igpgtg 50% 50% -50% / 50%)', 'color(--igpgtg 0.5 0.5 -0.5 / 0.5)'),
        ('color(--igpgtg none none none / none)', 'color(--igpgtg none none none / none)'),
        # Test percent ranges
        ('color(--igpgtg 0% 0% 0%)', 'color(--igpgtg 0 0 0)'),
        ('color(--igpgtg 100% 100% 100%)', 'color(--igpgtg 1 1 1)'),
        ('color(--igpgtg -100% -100% -100%)', 'color(--igpgtg -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_igpgtg_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('igpgtg'), Color(color2))


class TestIgPgTgSerialize(util.ColorAssertsPyTest):
    """Test IgPgTg serialization."""

    COLORS = [
        # Test color
        ('color(--igpgtg 0.75 0.1 -0.1 / 0.5)', {}, 'color(--igpgtg 0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('color(--igpgtg 0.75 0.1 -0.1)', {'alpha': True}, 'color(--igpgtg 0.75 0.1 -0.1 / 1)'),
        ('color(--igpgtg 0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'color(--igpgtg 0.75 0.1 -0.1)'),
        # Test None
        ('color(--igpgtg none 0.1 -0.1)', {}, 'color(--igpgtg 0 0.1 -0.1)'),
        ('color(--igpgtg none 0.1 -0.1)', {'none': True}, 'color(--igpgtg none 0.1 -0.1)'),
        # Test Fit (not bound)
        ('color(--igpgtg 0.75 1.2 -0.1)', {}, 'color(--igpgtg 0.75 1.2 -0.1)'),
        ('color(--igpgtg 0.75 1.2 -0.1)', {'fit': False}, 'color(--igpgtg 0.75 1.2 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestIgPgTgPoperties(util.ColorAsserts, unittest.TestCase):
    """Test IgPgTg."""

    def test_ig(self):
        """Test `ig`."""

        c = Color('color(--igpgtg 0.94415 -0.1422 0.39035)')
        self.assertEqual(c['ig'], 0.94415)
        c['ig'] = 0.2
        self.assertEqual(c['ig'], 0.2)

    def test_pg(self):
        """Test `pg`."""

        c = Color('color(--igpgtg 0.94415 -0.1422 0.39035)')
        self.assertEqual(c['pg'], -0.1422)
        c['pg'] = 0.1
        self.assertEqual(c['pg'], 0.1)

    def test_tg(self):
        """Test `tg`."""

        c = Color('color(--igpgtg 0.94415 -0.1422 0.39035)')
        self.assertEqual(c['tg'], 0.39035)
        c['tg'] = 0.1
        self.assertEqual(c['tg'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--igpgtg 0.94415 -0.1422 0.39035)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
