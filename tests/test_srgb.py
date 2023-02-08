"""Test sRGB library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestsRGB(util.ColorAssertsPyTest):
    """Test sRGB."""

    COLORS = [
        # Test general conversion
        ('red', 'color(srgb 1 0 0)'),
        ('orange', 'color(srgb 1 0.64706 0)'),
        ('yellow', 'color(srgb 1 1 0)'),
        ('green', 'color(srgb 0 0.50196 0)'),
        ('blue', 'color(srgb 0 0 1)'),
        ('indigo', 'color(srgb 0.29412 0 0.5098)'),
        ('violet', 'color(srgb 0.93333 0.5098 0.93333)'),
        ('white', 'color(srgb 1 1 1)'),
        ('gray', 'color(srgb 0.50196 0.50196 0.50196)'),
        ('black', 'color(srgb 0 0 0)'),
        # Test Hex
        ('#ee82ee', 'color(srgb 0.93333 0.5098 0.93333)'),
        ('#ee82ee80', 'color(srgb 0.93333 0.5098 0.93333 / 0.50196)'),
        ('#383', 'color(srgb 0.2 0.53333 0.2)'),
        ('#3838', 'color(srgb 0.2 0.53333 0.2 / 0.53333)'),
        # Test legacy CSS
        ('rgb(0, 128, 0)', 'color(srgb 0 0.50196 0)'),
        ('rgb(0%, 50%, 0%)', 'color(srgb 0 0.5 0)'),
        ('rgb(0, 128, 0, 0.5)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgb(0, 128, 0, 50%)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgba(0, 128, 0)', 'color(srgb 0 0.50196 0)'),
        ('rgba(0%, 50%, 0%)', 'color(srgb 0 0.5 0)'),
        ('rgba(0, 128, 0, 0.5)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgba(0, 128, 0, 50%)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgb(none, 128, 0)', None),
        ('rgb(50%, 128, 0)', None),
        ('rgba(none, 128, 0)', None),
        ('rgba(50%, 128, 0)', None),
        # Test CSS
        ('rgb(0 128 0)', 'color(srgb 0 0.50196 0)'),
        ('rgb(0% 50% 0%)', 'color(srgb 0 0.5 0)'),
        ('rgb(0 128 0 / 0.5)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgb(0 128 0 / 50%)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgb(none none none / none)', 'color(srgb none none none / none)'),
        ('rgba(0 128 0)', 'color(srgb 0 0.50196 0)'),
        ('rgba(0% 50% 0%)', 'color(srgb 0 0.5 0)'),
        ('rgba(0 128 0 / 0.5)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgba(0 128 0 / 50%)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('rgba(none none none / none)', 'color(srgb none none none / none)'),
        ('rgb(50% 128 0)', None),
        ('rgba(50% 128 0)', None),
        # Test CSS color
        ('color(srgb 0 0.50196 0)', 'color(srgb 0 0.50196 0)'),
        ('color(srgb 0 0.50196 0 / 0.5)', 'color(srgb 0 0.50196 0 / 0.5)'),
        ('color(srgb 50% 50% 50% / 50%)', 'color(srgb 0.5 0.5 0.5 / 0.5)'),
        ('color(srgb none none none / none)', 'color(srgb none none none / none)'),
        # Test range
        ('color(srgb 0% 0% 0%)', 'color(srgb 0 0 0)'),
        ('color(srgb 100% 100% 100%)', 'color(srgb 1 1 1)'),
        ('color(srgb -100% -100% -100%)', 'color(srgb -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('srgb'), Color(color2), color=True)


class TestsRGBSerialize(util.ColorAssertsPyTest):
    """Test sRGB serialization."""

    COLORS = [
        # Test hex no options
        ('rgb(255 0 0)', {}, 'rgb(255 0 0)'),
        # Test CSS names
        ('rgb(255 0 0)', {'names': True}, 'red'),
        # Test hex
        ('rgb(255 0 0)', {'hex': True}, '#ff0000'),
        ('rgb(255 0 0)', {'hex': True, 'compress': True}, '#f00'),
        ('rgb(255 0 0 / 0.53333)', {'hex': True}, '#ff000088'),
        ('rgb(255 0 0 / 0.53333)', {'hex': True, 'compress': True}, '#f008'),
        ('rgb(255 0 0 / 0.53333)', {'hex': True, 'upper': True}, '#FF000088'),
        # Test alpha
        ('rgb(255 0 0 / 0.5)', {}, 'rgb(255 0 0 / 0.5)'),
        ('rgb(255 0 0)', {'alpha': True}, 'rgb(255 0 0 / 1)'),
        ('rgb(255 0 0 / 0.5)', {'alpha': False}, 'rgb(255 0 0)'),
        # Test percent
        ('rgb(255 0 0)', {'percent': True}, 'rgb(100% 0% 0%)'),
        ('rgb(255 0 0)', {'percent': True, 'alpha': True}, 'rgb(100% 0% 0% / 1)'),
        # Test None
        ('rgb(none 128 10)', {}, 'rgb(0 128 10)'),
        ('rgb(none 128 10)', {'none': True}, 'rgb(none 128 10)'),
        # Test fit
        ('rgb(260 0 0 )', {}, 'rgb(255 0 0)'),
        ('rgb(260 0 0 )', {'fit': False}, 'rgb(260 0 0)'),
        ('rgb(260 0 0 )', {'hex': True}, '#ff0000'),
        # Test legacy
        ('rgb(255 0 0)', {'comma': True}, 'rgb(255, 0, 0)'),
        # Test legacy alpha
        ('rgb(255 0 0 / 0.5)', {'comma': True}, 'rgba(255, 0, 0, 0.5)'),
        ('rgb(255 0 0)', {'comma': True, 'alpha': True}, 'rgba(255, 0, 0, 1)'),
        ('rgb(255 0 0 / 0.5)', {'comma': True, 'alpha': False}, 'rgb(255, 0, 0)'),
        # Test legacy None
        ('rgb(none 128 10)', {'comma': True}, 'rgb(0, 128, 10)'),
        ('rgb(none 128 10)', {'comma': True, 'none': True}, 'rgb(0, 128, 10)'),
        # Test color
        ('rgb(none 255 25.5 / 0.5)', {'color': True}, 'color(srgb 0 1 0.1 / 0.5)'),
        ('rgb(none 255 25.5)', {'color': True, 'none': True}, 'color(srgb none 1 0.1)'),
        ('rgb(0 255 25.5)', {'color': True, 'alpha': True}, 'color(srgb 0 1 0.1 / 1)'),
        ('rgb(0 255 25.5 / 0.5)', {'color': True, 'alpha': False}, 'color(srgb 0 1 0.1)'),
        # Test Fit
        ('color(srgb 1.2 0.2 0)', {'color': True}, 'color(srgb 1 0.42121 0.26413)'),
        ('color(srgb 1.2 0.2 0)', {'color': True, 'fit': False}, 'color(srgb 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestsRGBProperties(util.ColorAsserts, unittest.TestCase):
    """Test sRGB."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
