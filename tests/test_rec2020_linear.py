"""Test Linear Rec. 2020."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestLinearRec2020(util.ColorAssertsPyTest):
    """Test Linear Rec. 2020."""

    COLORS = [
        ('red', 'color(--rec2020-linear 0.6274 0.0691 0.01639)'),
        ('orange', 'color(--rec2020-linear 0.7513 0.41509 0.04951)'),
        ('yellow', 'color(--rec2020-linear 0.95669 0.98864 0.1044)'),
        ('green', 'color(--rec2020-linear 0.07108 0.19849 0.019)'),
        ('blue', 'color(--rec2020-linear 0.04331 0.01136 0.8956)'),
        ('indigo', 'color(--rec2020-linear 0.05381 0.0074 0.20108)'),
        ('violet', 'color(--rec2020-linear 0.64696 0.27406 0.79939)'),
        ('white', 'color(--rec2020-linear 1 1 1)'),
        ('gray', 'color(--rec2020-linear 0.21586 0.21586 0.21586)'),
        ('black', 'color(--rec2020-linear 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rec2020-linear'), Color(color2))


class TestLinearRec2020Poperties(util.ColorAsserts, unittest.TestCase):
    """Test Linear Rec. 2020 properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--rec2020-linear 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--rec2020-linear 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--rec2020-linear 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--rec2020-linear 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
