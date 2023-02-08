"""Test ACEScct."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestACEScct(util.ColorAssertsPyTest):
    """Test ACEScct."""

    COLORS = [
        # Test general conversion
        ('red', 'color(--acescct 0.51451 0.33604 0.23515)'),
        ('orange', 'color(--acescct 0.53009 0.48237 0.32561)'),
        ('yellow', 'color(--acescct 0.5508 0.55368 0.38691)'),
        ('green', 'color(--acescct 0.3396 0.42136 0.24647)'),
        ('blue', 'color(--acescct 0.30368 0.2 0.54331)'),
        ('indigo', 'color(--acescct 0.31401 0.1566 0.42044)'),
        ('violet', 'color(--acescct 0.51811 0.44881 0.53494)'),
        ('white', 'color(--acescct 0.55479 0.55479 0.55479)'),
        ('gray', 'color(--acescct 0.42855 0.42855 0.42855)'),
        ('black', 'color(--acescct 0.07291 0.07291 0.07291)'),
        # Test CSS color
        ('color(--acescct 0 0.50196 0)', 'color(--acescct 0 0.50196 0)'),
        ('color(--acescct 0 0.50196 0 / 0.5)', 'color(--acescct 0 0.50196 0 / 0.5)'),
        ('color(--acescct 50% 50% 50% / 50%)', 'color(--acescct 0.77045 0.77045 0.77045 / 0.5)'),
        ('color(--acescct none none none / none)', 'color(--acescct none none none / none)'),
        # Test range
        ('color(--acescct 0% 0% 0%)', 'color(--acescct 0.07291 0.07291 0.07291)'),
        ('color(--acescct 100% 100% 100%)', 'color(--acescct 1.468 1.468 1.468)'),
        ('color(--acescct -100% -100% -100%)', 'color(--acescct -1.3222 -1.3222 -1.3222)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('acescct'), Color(color2))


class TestACEScctSerialize(util.ColorAssertsPyTest):
    """Test ACEScct serialization."""

    COLORS = [
        # Test color
        ('color(--acescct 0.1 0.3 0.75 / 0.5)', {}, 'color(--acescct 0.1 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--acescct 0.1 0.3 0.75)', {'alpha': True}, 'color(--acescct 0.1 0.3 0.75 / 1)'),
        ('color(--acescct 0.1 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--acescct 0.1 0.3 0.75)'),
        # Test None
        # TODO: In ACEScct, it seems that 0 may or may not be out of gamut? If it is out of gamut,
        # then we might need to rethink zero always being the default replacement for NaN
        # or come up with some other approach.
        ('color(--acescct none 0.3 0.75)', {}, 'color(--acescct 0 0.3 0.75)'),
        ('color(--acescct none 0.3 0.75)', {'none': True}, 'color(--acescct none 0.3 0.75)'),
        # Test Fit
        ('color(--acescct 1.5 0.2 0)', {}, 'color(--acescct 1.468 0.2 0.07291)'),
        ('color(--acescct 1.5 0.2 0)', {'fit': False}, 'color(--acescct 1.5 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestACEScctToACES2065_1(util.ColorAssertsPyTest):
    """Test ACEScct to Aces 2065-1."""

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
