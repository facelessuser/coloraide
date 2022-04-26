"""Test harmonies."""
from coloraide import Color
from . import util
import pytest
from itertools import zip_longest as zipl
import unittest


class TestHarmonies(util.ColorAssertsPyTest):
    """Test harmonies."""

    @pytest.mark.parametrize(
        'color,name,colors,space',
        [
            (
                'red',
                'mono',
                ['rgb(128.04 0 0)',
                 'rgb(189.52 0 0)',
                 'rgb(255 0 0)',
                 'rgb(263.47 106.88 88.846)',
                 'rgb(266.95 161.01 145.22)'],
                None
            ),
            (
                'white',
                'mono',
                ['rgb(128.04 128.04 128.04)',
                 'rgb(158.23 158.23 158.23)',
                 'rgb(189.52 189.52 189.52)',
                 'rgb(221.8 221.8 221.8)',
                 'rgb(255 255 255)'],
                None
            ),
            (
                'black',
                'mono',
                ['rgb(0 0 0)',
                 'rgb(3.2946 3.2946 3.2946)',
                 'rgb(21.957 21.957 21.957)',
                 'rgb(45.705 45.705 45.705)',
                 'rgb(71.554 71.554 71.554)'],
                None
            ),
            (
                'red',
                'complement',
                ['rgb(255 0 0)',
                 'rgb(-144.41 169.17 218.81)'],
                None
            ),
            (
                'red',
                'split',
                ['rgb(255 0 0)',
                 'rgb(-108.26 144.11 271.69)',
                 'rgb(-142.25 179.87 140.26)'],
                None
            ),
            (
                'red',
                'analogous',
                ['rgb(255 0 0)',
                 'rgb(239.47 70.306 -85.526)',
                 'rgb(245.33 -9.3969 132.34)'],
                None
            ),
            (
                'red',
                'triad',
                ['rgb(255 0 0)',
                 'rgb(-90.834 173.97 -5.7495)',
                 'rgb(78.547 111.49 288.59)'],
                None
            ),
            (
                'red',
                'square',
                ['rgb(255 0 0)',
                 'rgb(122.96 152.52 -89.834)',
                 'rgb(-144.41 169.17 218.81)',
                 'rgb(162.78 79.238 265.73)'],
                None
            ),
            (
                'red',
                'rectangle',
                ['rgb(255 0 0)',
                 'rgb(239.47 70.306 -85.526)',
                 'rgb(-144.41 169.17 218.81)',
                 'rgb(-108.26 144.11 271.69)'],
                None
            ),
            (
                'red',
                'complement',
                ['rgb(255 0 0)',
                 'rgb(0 255 255)'],
                'hsl'
            ),
            (
                'red',
                'mono',
                ['rgb(153 0 0)',
                 'rgb(204 0 0)',
                 'rgb(255 0 0)',
                 'rgb(255 63.75 63.75)',
                 'rgb(255 127.5 127.5)'],
                'srgb'  # monochromatic doesn't restrict space
            )
        ]
    )
    def test_harmonies(self, color, name, colors, space):
        """Test color harmonies."""

        results = Color(color).harmony(name, space=space)
        for c1, c2 in zipl(results, [Color(c) for c in colors]):
            self.assertColorEqual(c1, c2)


class TestHarmonyError(util.ColorAsserts, unittest.TestCase):
    """Test filter miscellaneous cases."""

    def test_bad_space(self):
        """Test using a harmony with sRGB."""

        with self.assertRaises(ValueError):
            Color('red').harmony('complement', space='srgb')

        with self.assertRaises(ValueError):
            Color('red').harmony('split', space='srgb')

        with self.assertRaises(ValueError):
            Color('red').harmony('analogous', space='srgb')

        with self.assertRaises(ValueError):
            Color('red').harmony('triad', space='srgb')

        with self.assertRaises(ValueError):
            Color('red').harmony('square', space='srgb')

        with self.assertRaises(ValueError):
            Color('red').harmony('rectangle', space='srgb')

    def test_bad_harmony(self):
        """Test bad harmony."""

        with self.assertRaises(ValueError):
            Color('red').harmony('bad')
