"""Test Rec.2020 library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestRec2020(util.ColorAssertsPyTest):
    """Test Rec. 2020."""

    COLORS = [
        ('red', 'color(rec2020 0.79198 0.23098 0.07376)'),
        ('orange', 'color(rec2020 0.86727 0.64078 0.18496)'),
        ('yellow', 'color(rec2020 0.97831 0.99436 0.29839)'),
        ('green', 'color(rec2020 0.23521 0.43171 0.08543)'),
        ('blue', 'color(rec2020 0.16837 0.05113 0.94678)'),
        ('indigo', 'color(rec2020 0.19583 0.03329 0.43481)'),
        ('violet', 'color(rec2020 0.80438 0.51467 0.89463)'),
        ('white', 'color(rec2020 1 1 1)'),
        ('gray', 'color(rec2020 0.45214 0.45214 0.45214)'),
        ('black', 'color(rec2020 0 0 0)'),
        # Test CSS color
        ('color(rec2020 0 0.50196 0)', 'color(rec2020 0 0.50196 0)'),
        ('color(rec2020 0 0.50196 0 / 0.5)', 'color(rec2020 0 0.50196 0 / 0.5)'),
        ('color(rec2020 50% 50% 50% / 50%)', 'color(rec2020 0.5 0.5 0.5 / 0.5)'),
        ('color(rec2020 none none none / none)', 'color(rec2020 none none none / none)'),
        # Test range
        ('color(rec2020 0% 0% 0%)', 'color(rec2020 0 0 0)'),
        ('color(rec2020 100% 100% 100%)', 'color(rec2020 1 1 1)'),
        ('color(rec2020 -100% -100% -100%)', 'color(rec2020 -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rec2020'), Color(color2))


class TestRec2020Serialize(util.ColorAssertsPyTest):
    """Test Rec. 2020 serialization."""

    COLORS = [
        # Test color
        ('color(rec2020 0 0.3 0.75 / 0.5)', {}, 'color(rec2020 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(rec2020 0 0.3 0.75)', {'alpha': True}, 'color(rec2020 0 0.3 0.75 / 1)'),
        ('color(rec2020 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(rec2020 0 0.3 0.75)'),
        # Test None
        ('color(rec2020 none 0.3 0.75)', {}, 'color(rec2020 0 0.3 0.75)'),
        ('color(rec2020 none 0.3 0.75)', {'none': True}, 'color(rec2020 none 0.3 0.75)'),
        # Test Fit
        ('color(rec2020 1.2 0.2 0)', {}, 'color(rec2020 1 0.41836 0.13834)'),
        ('color(rec2020 1.2 0.2 0)', {'fit': False}, 'color(rec2020 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestRec2020Properties(util.ColorAsserts, unittest.TestCase):
    """Test Rec2020."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
