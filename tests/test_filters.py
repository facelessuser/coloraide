"""Test filter method."""
from coloraide import Color
from . import util
import pytest
import unittest


class TestFilters(util.ColorAssertsPyTest):
    """Test filters."""

    @pytest.mark.parametrize(
        'color1,color2,name,amount',
        [
            ('red', 'rgb(168.28 159.48 142.36)', 'sepia', 1),
            ('red', 'rgb(217.36 115.95 103.13)', 'sepia', 0.5),
            ('red', 'rgb(255 0 0)', 'sepia', 0),
            ('red', 'rgb(255 0 0)', 'sepia', -1),
            ('red', 'rgb(168.28 159.48 142.36)', 'sepia', 2),

            ('orange', 'rgb(184.41 184.41 184.41)', 'grayscale', 1),
            ('orange', 'rgb(223.39 175.05 134.63)', 'grayscale', 0.5),
            ('orange', 'rgb(255 165 0)', 'grayscale', 0),
            ('orange', 'rgb(255 165 0)', 'grayscale', -1),
            ('orange', 'rgb(184.41 184.41 184.41)', 'grayscale', 2),

            ('yellow', 'rgb(255 255 0)', 'saturate', 1),
            ('yellow', 'rgb(250.92 250.92 181.34)', 'saturate', 0.5),
            ('yellow', 'rgb(246.75 246.75 246.75)', 'saturate', 0),
            ('yellow', 'rgb(246.75 246.75 246.75)', 'saturate', -1),
            ('yellow', 'rgb(262.91 262.91 -246.75)', 'saturate', 2),

            ('green', 'rgb(255 229.08 255)', 'invert', 1),
            ('green', 'rgb(187.52 187.52 187.52)', 'invert', 0.5),
            ('green', 'rgb(0 128 0)', 'invert', 0),
            ('green', 'rgb(0 128 0)', 'invert', -1),
            ('green', 'rgb(255 229.08 255)', 'invert', 2),

            ('blue', 'rgb(0 0 255)', 'brightness', 1),
            ('blue', 'rgb(0 0 187.52)', 'brightness', 0.5),
            ('blue', 'rgb(0 0 0)', 'brightness', 0),
            ('blue', 'rgb(0 0 0)', 'brightness', -1),
            ('blue', 'rgb(0 0 345.08)', 'brightness', 2),

            ('indigo', 'rgb(75 0 130)', 'contrast', 1),
            ('indigo', 'rgb(145.47 136.96 162.06)', 'contrast', 0.5),
            ('indigo', 'rgb(187.52 187.52 187.52)', 'contrast', 0),
            ('indigo', 'rgb(187.52 187.52 187.52)', 'contrast', -1),
            ('indigo', 'rgb(-161.59 -187.52 -65.424)', 'contrast', 2),

            ('violet', 'rgb(238 130 238)', 'hue-rotate', 0),
            ('violet', 'rgb(238 152.19 -62.17)', 'hue-rotate', 90),
            ('violet', 'rgb(-62.17 200.89 -62.17)', 'hue-rotate', 180),
            ('violet', 'rgb(-62.17 186.12 238)', 'hue-rotate', 270),
            ('violet', 'rgb(238 130 238)', 'hue-rotate', 360),
            ('violet', 'rgb(238 152.19 -62.17)', 'hue-rotate', 450),
            ('violet', 'rgb(-62.17 186.12 238)', 'hue-rotate', -90),

            ('black', 'rgb(0 0 0)', 'opacity', 1),
            ('black', 'rgb(0 0 0 / 0.5)', 'opacity', 0.5),
            ('black', 'rgb(0 0 0 / 0)', 'opacity', 0),
            ('black', 'rgb(0 0 0 / 0)', 'opacity', -1),
            ('black', 'rgb(0 0 0)', 'opacity', 2)
        ]
    )
    def test_filter(self, color1, color2, name, amount):
        """Test filter."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertColorEqual(
            Color(color1).filter(name, amount, out_space='srgb'),
            Color(color2) if isinstance(color2, str) else color2
        )


class TestFilterMisc(util.ColorAsserts, unittest.TestCase):
    """Test filter miscellaneous cases."""

    def test_srgb(self):
        """Test using a filter with sRGB."""

        self.assertColorEqual(Color('red').filter('sepia', space='srgb'), Color('rgb(100.22 88.995 69.36)'))
        self.assertColorNotEqual(Color('red').filter('sepia'), Color('red').filter('sepia', space='srgb'))

    def test_bad_space(self):
        """Test a bad input space."""

        with self.assertRaises(ValueError):
            Color('red').filter('sepia', space='display-p3', out_space='srgb')

    def test_bad_filter(self):
        """Test bad filter."""

        with self.assertRaises(ValueError):
            Color('red').filter('bad')
