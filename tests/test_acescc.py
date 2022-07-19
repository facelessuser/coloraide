"""Test ACEScc."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestACEScc(util.ColorAssertsPyTest):
    """Test ACEScc."""

    COLORS = [
        # Tests from S-2014-003 paper
        (
            f'color(--aces2065-1 {2 ** -24} {2 ** -24} {2 ** -24})',
            'color(--acescc -0.35828683 -0.35828683 -0.35828683)'
        ),
        ('color(--aces2065-1 0.18 0.18 0.18)', 'color(--acescc 0.4135884 0.4135884 0.4135884)'),
        ('color(--aces2065-1 65504 65504 65504)', 'color(--acescc 1.4679964 1.4679964 1.4679964)'),
        ('color(--aces2065-1 0.08731 0.07443 0.27274)', 'color(--acescc 0.30893183 0.3139529 0.44770366)'),
        ('color(--aces2065-1 0.15366 0.25692 0.09071)', 'color(--acescc 0.39450577 0.45037976 0.35672173)'),
        ('color(--aces2065-1 0.21743 0.07070 0.05130)', 'color(--acescc 0.45224518 0.32502314 0.31222793)'),
        ('color(--aces2065-1 0.58921 0.53944 0.09157)', 'color(--acescc 0.52635247 0.5099772 0.3592168)'),
        ('color(--aces2065-1 0.30904 0.14818 0.27426)', 'color(--acescc 0.46941227 0.382433 0.44858035)'),
        ('color(--aces2065-1 0.14900 0.23377 0.35939)', 'color(--acescc 0.35056654 0.43295938 0.4702988)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color2).convert('aces2065-1'), Color(color1))


class TestACESccMisc(util.ColorAsserts, unittest.TestCase):
    """Test other assorted ACEScc cases."""

    def test_close_to_black(self):
        """Test close to black."""

        self.assertColorEqual(
            Color('srgb', [0.00001, 0.00001, 0.00001]).convert('acescc'),
            Color('color(--acescc -0.35639 -0.35639 -0.35639)')
        )


class TestACESccProperties(util.ColorAsserts, unittest.TestCase):
    """Test ACEScc."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(--acescc 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(--acescc 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(--acescc 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--acescc 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
