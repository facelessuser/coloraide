"""Test Averaging."""
import unittest
from coloraide.everything import ColorAll as Color
from . import util
import math


class TestAverage(util.ColorAsserts, unittest.TestCase):
    """Test averaging."""

    def test_average_achromatic(self):
        """Test that we force achromatic hues to undefined."""

        self.assertEqual(
            Color.average(['hsl(30 0 100)', 'color(srgb 0 0 1)'], space='hsl').to_string(),
            'hsl(240 50% 75%)'
        )

    def test_no_colors(self):
        """Test averaging no colors."""

        with self.assertRaises(ValueError):
            Color.average([])

    def test_one_colors(self):
        """Test averaging one color."""

        self.assertColorEqual(Color.average(['red']), Color('color(srgb-linear 1 0 0)'))

    def test_average_premultiplied(self):
        """Test averaging with premultiplication."""

        colors = [Color('darkgreen'), Color('color(srgb 0 0.50196 0 / 1)'), Color('color(srgb 0 0 1)')]
        results = []
        for i in range(5):
            colors[1].set('alpha', i / 4)
            results.append(Color.average(colors, space='srgb').to_string(color=True))
        self.assertEqual(
            results,
            ['color(srgb 0 0.19608 0.5 / 0.66667)',
             'color(srgb 0 0.23007 0.44444 / 0.75)',
             'color(srgb 0 0.25725 0.4 / 0.83333)',
             'color(srgb 0 0.2795 0.36364 / 0.91667)',
             'color(srgb 0 0.29804 0.33333)']
        )

    def test_average_no_premultiplied(self):
        """Test averaging without premultiplication."""

        colors = [Color('darkgreen'), Color('color(srgb 0 0.50196 0 / 1)'), Color('color(srgb 0 0 1)')]
        results = []
        for i in range(5):
            colors[1].set('alpha', i / 4)
            results.append(Color.average(colors, space='srgb', premultiplied=False).to_string(color=True))
        self.assertEqual(
            results,
            ['color(srgb 0 0.19608 0.5 / 0.66667)',
             'color(srgb 0 0.29804 0.33333 / 0.75)',
             'color(srgb 0 0.29804 0.33333 / 0.83333)',
             'color(srgb 0 0.29804 0.33333 / 0.91667)',
             'color(srgb 0 0.29804 0.33333)']
        )

    def test_average_cylindrical_premultiplied(self):
        """Test cylindrical averaging without premultiplication."""

        colors = [Color('darkgreen'), Color('color(srgb 0 0.50196 0 / 1)'), Color('color(srgb 0 0 1)')]
        results = []
        for i in range(5):
            colors[1].set('alpha', i / 4)
            results.append(Color.average(colors, space='hsl').to_string(color=True))
        self.assertEqual(
            results,
            ['color(--hsl 180 1 0.34804 / 0.66667)',
             'color(--hsl 169.11 1 0.33725 / 0.75)',
             'color(--hsl 160.89 1 0.32863 / 0.83333)',
             'color(--hsl 154.72 1 0.32157 / 0.91667)',
             'color(--hsl 150 1 0.31569)']
        )

    def test_average_cylindrical_no_premultiplied(self):
        """Test cylindrical averaging without premultiplication."""

        colors = [Color('darkgreen'), Color('color(srgb 0 0.50196 0 / 1)'), Color('color(srgb 0 0 1)')]
        results = []
        for i in range(5):
            colors[1].set('alpha', i / 4)
            results.append(Color.average(colors, space='hsl', premultiplied=False).to_string(color=True))
        self.assertEqual(
            results,
            ['color(--hsl 180 1 0.34804 / 0.66667)',
             'color(--hsl 150 1 0.31569 / 0.75)',
             'color(--hsl 150 1 0.31569 / 0.83333)',
             'color(--hsl 150 1 0.31569 / 0.91667)',
             'color(--hsl 150 1 0.31569)']
        )

    def test_average_ignore_undefined(self):
        """Test averaging ignores undefined."""

        colors = [Color('darkgreen'), Color('color(srgb 0 none 0 / 1)'), Color('color(srgb 0 0 1)')]
        results = []
        for i in range(5):
            colors[1].set('alpha', i / 4)
            results.append(Color.average(colors, space='srgb').to_string(color=True))
        self.assertEqual(
            results,
            ['color(srgb 0 0.29412 0.5 / 0.66667)',
             'color(srgb 0 0.26144 0.44444 / 0.75)',
             'color(srgb 0 0.23529 0.4 / 0.83333)',
             'color(srgb 0 0.2139 0.36364 / 0.91667)',
             'color(srgb 0 0.19608 0.33333)']
        )

    def test_average_with_undefined_alpha_result(self):
        """Test average when the resulting alpha is undefined."""

        colors = [
            Color('color(srgb 1 1 0 / none)'),
            Color('color(srgb 0 0.50196 0 / none)'),
            Color('color(srgb 0 0 1 / none)')
        ]
        self.assertEqual(
            Color.average(colors, space='srgb').to_string(color=True, none=True),
            'color(srgb 0.33333 0.50065 0.33333 / none)'
        )

    def test_average_ignore_undefined_alpha_premultiplied(self):
        """Test averaging ignores undefined."""

        colors = [Color('darkgreen'), Color('color(srgb 0 0.50196 0 / none)'), Color('color(srgb 0 0 1)')]
        self.assertEqual(Color.average(colors, space='srgb').to_string(color=True), 'color(srgb 0 0.29804 0.33333)')

    def test_evenly_distributed(self):
        """Test evenly distributed colors."""

        colors = ['red', 'green', 'blue']
        self.assertEqual(
            Color.average(colors, space='hsl').to_string(color=True, none=True),
            'color(--hsl none 0 0.41699)'
        )

    def test_hwb_handling(self):
        """Test HWB handling."""

        colors = ['red', 'green', 'blue']
        self.assertEqual(
            Color.average(colors, space='hwb').to_string(color=True, none=True),
            'color(--hwb none 0.83399 0.16601)'
        )

        self.assertEqual(
            Color.average(['orange', 'purple', 'darkgreen'], space='hwb').to_string(color=True),
            'color(--hwb 38.824 0 0.36863)'
        )

    def test_all_undefined_hue(self):
        """Test all hues undefined."""

        a = Color.average(['white', 'gray', 'black'], space='hsl')
        self.assertColorEqual(a, Color('hsl(none 0% 50.065%)'))
        self.assertTrue(math.isnan(a[0]))

    def test_all_undefined_non_hue(self):
        """Test all non hue undefined."""

        a = Color.average(['color(srgb 1 none 0)', 'color(srgb 0.1 none 0.3)', 'color(srgb 0.7 none 0)'], space='srgb')
        self.assertColorEqual(a, Color('rgb(153 none 25.5)'))
        self.assertTrue(math.isnan(a[1]))

    def test_weighted_colors(self):
        """Test weighted colors."""

        a = Color.average(['red', 'green', 'yellow', 'blue'], space='srgb')
        a = self.assertColorEqual(a, Color('color(srgb 0.5 0.37549 0.25 / 1)'))
        a = Color.average(['red', 'green', 'yellow', 'blue'], [1, 1, 1, 0], space='srgb')
        a = self.assertColorEqual(a, Color('rgb(170 127.67 0)'))
        a = Color.average(['red', 'green', 'yellow', 'blue'], [1, 4, 2, 3], space='srgb')
        a = self.assertColorEqual(a, Color('rgb(76.5 102.2 76.5)'))

    def test_weighted_polar_colors(self):
        """Test weighted colors."""

        a = Color.average(['red', 'orange', 'white'], space='hsl')
        a = self.assertColorEqual(a, Color('hsl(19.412 66.667% 66.667%)'))
        a = Color.average(['red', 'orange', 'white'], [1, 1, 4], space='hsl')
        a = self.assertColorEqual(a, Color('hsl(19.412 33.333% 83.333%)'))

    def test_weighted_colors_mismatch(self):
        """Test weighted colors."""

        a = Color.average(['red', 'green', 'yellow', 'blue'], [1, 4, 2], space='srgb')
        a = self.assertColorEqual(a, Color('rgb(69.545 92.909 92.727)'))
        a = Color.average(['red', 'green', 'yellow', 'blue'], [1, 4, 2, 3, 5, 6], space='srgb')
        a = self.assertColorEqual(a, Color('rgb(76.5 102.2 76.5)'))

    def test_weighted_negative(self):
        """Test weighted with negative weights."""

        a = Color.average(['red', 'green', 'yellow', 'blue'], [1, 1, 1, -1], space='srgb')
        a = self.assertColorEqual(a, Color('rgb(170 127.67 0)'))
