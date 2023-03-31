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
                 'rgb(262.16 94.255 76.67)',
                 'rgb(266.2 140.53 123.15)'],
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
                'lightyellow',
                'mono',
                ['rgb(148.04 148.04 129.36)',
                 'rgb(182.47 182.47 159.83)',
                 'rgb(218.17 218.17 191.41)',
                 'rgb(255 255 224)',
                 'rgb(254.96 255.07 239.68)'],
                None
            ),
            (
                '#000011',
                'mono',
                ['rgb(0 0 2.3084)',
                 'rgb(0 0 17)',
                 'rgb(6.8796 16.788 39.776)',
                 'rgb(31.005 41.641 63.598)',
                 'rgb(58.097 68.188 88.434)'],
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
                 'rgb(245.33 -9.3968 132.34)'],
                None
            ),
            (
                'red',
                'triad',
                ['rgb(255 0 0)',
                 'rgb(-90.834 173.97 -5.7497)',
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
            )
        ]
    )
    def test_harmonies(self, color, name, colors, space):
        """Test color harmonies."""

        results = Color(color).harmony(name, space=space, out_space='srgb')
        for c1, c2 in zipl(results, [Color(c) for c in colors]):
            self.assertColorEqual(c1, c2)


class TestHarmonyError(util.ColorAsserts, unittest.TestCase):
    """Test harmony errors."""

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

        with self.assertRaises(ValueError):
            Color('red').harmony('mono', space='srgb')

    def test_bad_harmony(self):
        """Test bad harmony."""

        with self.assertRaises(ValueError):
            Color('red').harmony('bad')
