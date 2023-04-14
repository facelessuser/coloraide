"""Test Averaging."""
import unittest
from coloraide.everything import ColorAll as Color
from . import util


class TestAverage(util.ColorAsserts, unittest.TestCase):
    """Test averaging."""

    def test_no_colors(self):
        """Test averaging no colors."""

        with self.assertRaises(ValueError):
            Color.average([])

    def test_one_colors(self):
        """Test averaging one color."""

        self.assertColorEqual(Color.average(['red']), Color('oklab(0.62796 0.22486 0.12585)'))

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
            ['color(srgb 0 0.29804 0.33333 / 0.66667)',
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
            ['color(--hsl 150 1 0.34804 / 0.66667)',
             'color(--hsl 150 1 0.33725 / 0.75)',
             'color(--hsl 150 1 0.32863 / 0.83333)',
             'color(--hsl 150 1 0.32157 / 0.91667)',
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
            ['color(--hsl 150 1 0.31569 / 0.66667)',
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

    def test_average_ignore_undefined_alpha_premultiplied(self):
        """Test averaging ignores undefined."""

        colors = [Color('darkgreen'), Color('color(srgb 0 0.50196 0 / none)'), Color('color(srgb 0 0 1)')]
        self.assertEqual(Color.average(colors, space='srgb').to_string(color=True), 'color(srgb 0 0.29804 0.33333)')
