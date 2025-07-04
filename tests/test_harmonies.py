"""Test harmonies."""
from coloraide.everything import ColorAll as Color
from . import util
import pytest
from itertools import zip_longest as zipl
import unittest


class TestHarmonies(util.ColorAssertsPyTest):
    """Test harmonies."""

    @pytest.mark.parametrize(
        'color,name,colors,space,kwargs',
        [
            (
                'red',
                'mono',
                ['rgb(54.113 0 0)',
                 'rgb(148.04 0 0)',
                 'rgb(255 0 0)',
                 'rgb(265.22 126.15 108.17)',
                 'rgb(266.09 193.38 181.63)'],
                None,
                {"count": 5}
            ),
            (
                'white',
                'mono',
                ['rgb(0 0 0)',
                 'rgb(33.532 33.532 33.532)',
                 'rgb(99.086 99.086 99.086)',
                 'rgb(173.74 173.74 173.74)',
                 'rgb(255 255 255)'],
                None,
                {"count": 5}
            ),
            (
                'black',
                'mono',
                ['rgb(0 0 0)',
                 'rgb(33.532 33.532 33.532)',
                 'rgb(99.086 99.086 99.086)',
                 'rgb(173.74 173.74 173.74)',
                 'rgb(255 255 255)'],
                None,
                {"count": 5}
            ),
            (
                'lightyellow',
                'mono',
                ['rgb(71.554 71.554 61.693)',
                 'rgb(128.04 128.04 111.67)',
                 'rgb(189.52 189.52 166.06)',
                 'rgb(255 255 224)',
                 'rgb(254.96 255.07 239.68)'],
                None,
                {"count": 5}
            ),
            (
                '#000011',
                'mono',
                ['rgb(0 0 2.3084)',
                 'rgb(0 0 17)',
                 'rgb(25.879 36.536 58.751)',
                 'rgb(75.376 84.884 103.79)',
                 'rgb(130.95 137.97 151.75)'],
                None,
                {"count": 5}
            ),
            (
                'oklab(1.05 0.01 270)',
                'mono',
                ['rgb(-53411 64818 -127820)',
                 'rgb(-88672 107610 -212190)',
                 'rgb(-127050 154180 -304030)',
                 'rgb(-167930 203790 -401840)',
                 'rgb(-210920 255960 -504700)'],
                'oklab',
                {"count": 5}
            ),
            (
                'red',
                'mono',
                ['rgb(255 0 0)'],
                None,
                {"count": 1}
            ),
            (
                'red',
                'complement',
                ['rgb(255 0 0)',
                 'rgb(-144.41 169.17 218.81)'],
                None,
                {}
            ),
            (
                'gray',
                'complement',
                ['rgb(128 128 128)',
                 'rgb(128 128 128)'],
                'srgb',
                {}
            ),
            (
                'red',
                'split',
                ['rgb(-108.26 144.11 271.69)',
                 'rgb(255 0 0)',
                 'rgb(-142.25 179.87 140.26)'],
                None,
                {}
            ),
            (
                'red',
                'analogous',
                ['rgb(245.33 -9.3968 132.34)',
                 'rgb(255 0 0)',
                 'rgb(239.47 70.306 -85.526)'],
                None,
                {}
            ),
            (
                'red',
                'triad',
                ['rgb(255 0 0)',
                 'rgb(-90.834 173.97 -5.7497)',
                 'rgb(78.547 111.49 288.59)'],
                None,
                {}
            ),
            (
                'red',
                'square',
                ['rgb(255 0 0)',
                 'rgb(122.96 152.52 -89.834)',
                 'rgb(-144.41 169.17 218.81)',
                 'rgb(162.78 79.238 265.73)'],
                None,
                {}
            ),
            (
                'red',
                'rectangle',
                ['rgb(255 0 0)',
                 'rgb(239.47 70.306 -85.526)',
                 'rgb(-144.41 169.17 218.81)',
                 'rgb(-108.26 144.11 271.69)'],
                None,
                {}
            ),
            (
                'red',
                'complement',
                ['rgb(255 0 0)',
                 'rgb(0 255 255)'],
                'hsl',
                {}
            ),
            (
                'red',
                'wheel',
                ['rgb(255 0 0)',
                 'rgb(255 127.5 0)',
                 'rgb(255 255 0)',
                 'rgb(127.5 255 0)',
                 'rgb(0 255 0)',
                 'rgb(0 255 127.5)',
                 'rgb(0 255 255)',
                 'rgb(0 127.5 255)',
                 'rgb(0 0 255)',
                 'rgb(127.5 0 255)',
                 'rgb(255 0 255)',
                 'rgb(255 0 127.5)'],
                'srgb',
                {}
            ),
            (
                'red',
                'triad',
                ['rgb(255 0 0)',
                 'rgb(-90.834 173.97 -5.7497)',
                 'rgb(78.547 111.49 288.59)'],
                'oklab',
                {}
            ),
            (
                'red',
                'split',
                ['rgb(-108.26 144.11 271.69)',
                 'rgb(255 0 0)',
                 'rgb(-142.25 179.87 140.26)'],
                'oklab',
                {}
            ),
            (
                'red',
                'analogous',
                ['rgb(245.33 -9.3968 132.34)',
                 'rgb(255 0 0)',
                 'rgb(239.47 70.306 -85.526)'],
                'oklab',
                {}
            ),
            (
                'red',
                'rectangle',
                ['rgb(255 0 0)',
                 'rgb(239.47 70.306 -85.526)',
                 'rgb(-144.41 169.17 218.81)',
                 'rgb(-108.26 144.11 271.69)'],
                'oklab',
                {}
            )
        ]
    )
    def test_harmonies(self, color, name, colors, space, kwargs):
        """Test color harmonies."""

        results = Color(color).harmony(name, space=space, out_space='srgb', **kwargs)
        for c1, c2 in zipl(results, [Color(c) for c in colors]):
            self.assertColorEqual(c1, c2)


class TestHarmonyError(util.ColorAsserts, unittest.TestCase):
    """Test harmony errors."""

    def test_bad_space(self):
        """Test using a harmony with sRGB."""

        with self.assertRaises(ValueError):
            Color('red').harmony('complement', space='cmyk')

        with self.assertRaises(ValueError):
            Color('red').harmony('split', space='cmyk')

        with self.assertRaises(ValueError):
            Color('red').harmony('analogous', space='cmyk')

        with self.assertRaises(ValueError):
            Color('red').harmony('triad', space='cmyk')

        with self.assertRaises(ValueError):
            Color('red').harmony('square', space='cmyk')

        with self.assertRaises(ValueError):
            Color('red').harmony('rectangle', space='cmyk')

        with self.assertRaises(ValueError):
            Color('red').harmony('mono', space='cmyk')

    def test_bad_harmony(self):
        """Test bad harmony."""

        with self.assertRaises(ValueError):
            Color('red').harmony('bad')

    def test_too_few_mono(self):
        """Test failure when too few colors are specified for monochromatic."""

        with self.assertRaises(ValueError):
            Color('red').harmony('mono', count=0)
