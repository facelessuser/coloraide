"""Test ACEScct."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestACEScct(util.ColorAssertsPyTest):
    """Test ACEScct."""

    COLORS = [
        # Tests from S-2016-001 paper
        (
            f'color(--aces2065-1 {2 ** -24} {2 ** -24} {2 ** -24})',
            'color(--acescct 0.072906162 0.072906162 0.072906162)'
        ),
        ('color(--aces2065-1 0.18 0.18 0.18)', 'color(--acescct 0.4135884 0.4135884 0.4135884)'),
        ('color(--aces2065-1 65504 65504 65504)', 'color(--acescct 1.4679964 1.4679964 1.4679964)'),
        ('color(--aces2065-1 0.08731 0.07443 0.27274)', 'color(--acescct 0.30893773 0.31394949 0.44770345)'),
        ('color(--aces2065-1 0.15366 0.25692 0.09071)', 'color(--acescct 0.39450300 0.45037864 0.35672542)'),
        ('color(--aces2065-1 0.21743 0.07070 0.05130)', 'color(--acescct 0.45224438 0.32502256 0.31222500)'),
        ('color(--aces2065-1 0.58921 0.53944 0.09157)', 'color(--acescct 0.52635207 0.50997715 0.35921441)'),
        ('color(--aces2065-1 0.30904 0.14818 0.27426)', 'color(--acescct 0.46941309 0.38243160 0.44857958)'),
        ('color(--aces2065-1 0.14900 0.23377 0.35939)', 'color(--acescct 0.35056940 0.43296115 0.47029844)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color2).convert('aces2065-1'), Color(color1))


class TestACEScctProperties(util.ColorAsserts, unittest.TestCase):
    """Test ACEScct."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(--acescct 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(--acescct 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(--acescct 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--acescct 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
