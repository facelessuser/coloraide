"""Test ACEScc."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestACEScc(util.ColorAssertsPyTest):
    """Test ACEScc."""

    COLORS = [
        # Test general conversion
        ('red', 'color(--acescc 0.51451 0.33604 0.23515)'),
        ('orange', 'color(--acescc 0.53009 0.48237 0.32561)'),
        ('yellow', 'color(--acescc 0.5508 0.55368 0.38691)'),
        ('green', 'color(--acescc 0.3396 0.42136 0.24647)'),
        ('blue', 'color(--acescc 0.30368 0.2 0.54331)'),
        ('indigo', 'color(--acescc 0.31401 0.1566 0.42044)'),
        ('violet', 'color(--acescc 0.51811 0.44881 0.53494)'),
        ('white', 'color(--acescc 0.55479 0.55479 0.55479)'),
        ('gray', 'color(--acescc 0.42855 0.42855 0.42855)'),
        ('black', 'color(--acescc -0.35845 -0.35845 -0.35845)'),
        # Test CSS color
        ('color(--acescc 0 0.50196 0)', 'color(--acescc 0 0.50196 0)'),
        ('color(--acescc 0 0.50196 0 / 0.5)', 'color(--acescc 0 0.50196 0 / 0.5)'),
        ('color(--acescc 50% 50% 50% / 50%)', 'color(--acescc 0.55477 0.55477 0.55477 / 0.5)'),
        ('color(--acescc none none none / none)', 'color(--acescc none none none / none)'),
        # Test range
        ('color(--acescc 0% 0% 0%)', 'color(--acescc -0.35845 -0.35845 -0.35845)'),
        ('color(--acescc 100% 100% 100%)', 'color(--acescc 1.468 1.468 1.468)'),
        ('color(--acescc -100% -100% -100%)', 'color(--acescc -2.1849 -2.1849 -2.1849)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('acescc'), Color(color2))


class TestACESccSerialize(util.ColorAssertsPyTest):
    """Test ACEScc serialization."""

    COLORS = [
        # Test color
        ('color(--acescc 0 0.3 0.75 / 0.5)', {}, 'color(--acescc 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--acescc 0 0.3 0.75)', {'alpha': True}, 'color(--acescc 0 0.3 0.75 / 1)'),
        ('color(--acescc 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--acescc 0 0.3 0.75)'),
        # Test None
        ('color(--acescc none 0.3 0.75)', {}, 'color(--acescc 0 0.3 0.75)'),
        ('color(--acescc none 0.3 0.75)', {'none': True}, 'color(--acescc none 0.3 0.75)'),
        # Test Fit
        ('color(--acescc 1.5 0.2 0)', {}, 'color(--acescc 1.468 0.2 0)'),
        ('color(--acescc 1.5 0.2 0)', {'fit': False}, 'color(--acescc 1.5 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestACESccToACES2056_1(util.ColorAssertsPyTest):
    """Test ACEScc to ACES 2056-1."""

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
