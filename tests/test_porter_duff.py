"""Test Porter Duff composition modes."""
import unittest
from coloraide import Color
from . import util


class TestPorterDuffModes(util.ColorAsserts, unittest.TestCase):
    """Test Porter Duff modes."""

    def test_clear(self):
        """Test clear."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='clear', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='clear', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='clear', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='clear', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='clear', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='clear', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='clear', space='srgb')

        self.assertColorEqual(r1, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r7, Color('rgb(0 0 0 / 0)'))

    def test_copy(self):
        """Test copy."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='copy', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='copy', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='copy', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='copy', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='copy', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='copy', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='copy', space='srgb')

        self.assertColorEqual(r1, Color('#07c7ed'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r4, Color('#07c7ed'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('#07c7ed'))
        self.assertColorEqual(r7, Color('#07c7ed'))

    def test_destination(self):
        """Test destination."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='destination', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='destination', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='destination', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='destination', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='destination', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='destination', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='destination', space='srgb')

        self.assertColorEqual(r1, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('#f5d311'))
        self.assertColorEqual(r6, Color('#f5d311'))
        self.assertColorEqual(r7, Color('#f5d311'))

    def test_source_over(self):
        """Test source over."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='source-over', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='source-over', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='source-over', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='source-over', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='source-over', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='source-over', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='source-over', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(7 199 237)'))
        self.assertColorEqual(r5, Color('rgb(252 61 153)'))
        self.assertColorEqual(r6, Color('rgb(7 199 237)'))
        self.assertColorEqual(r7, Color('rgb(7 199 237)'))

    def test_destination_over(self):
        """Test destination over."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='destination-over', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='destination-over', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='destination-over', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='destination-over', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='destination-over', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='destination-over', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='destination-over', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(252 61 153)'))
        self.assertColorEqual(r5, Color('rgb(245 211 17)'))
        self.assertColorEqual(r6, Color('rgb(245 211 17)'))
        self.assertColorEqual(r7, Color('rgb(245 211 17)'))

    def test_source_in(self):
        """Test source in."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='source-in', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='source-in', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='source-in', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='source-in', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='source-in', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='source-in', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='source-in', space='srgb')

        self.assertColorEqual(r1, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r7, Color('#07c7ed'))

    def test_destination_in(self):
        """Test destination in."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='destination-in', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='destination-in', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='destination-in', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='destination-in', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='destination-in', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='destination-in', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='destination-in', space='srgb')

        self.assertColorEqual(r1, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r7, Color('#f5d311'))

    def test_source_out(self):
        """Test source out."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='source-out', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='source-out', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='source-out', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='source-out', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='source-out', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='source-out', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='source-out', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(7 199 237)'))
        self.assertColorEqual(r7, Color('rgb(7 199 237)'))

    def test_destination_out(self):
        """Test destination out."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='destination-out', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='destination-out', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='destination-out', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='destination-out', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='destination-out', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='destination-out', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='destination-out', space='srgb')

        self.assertColorEqual(r1, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r7, Color('rgb(0 0 0 / 0)'))

    def test_source_atop(self):
        """Test source atop."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='source-atop', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='source-atop', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='source-atop', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='source-atop', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='source-atop', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='source-atop', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='source-atop', space='srgb')

        self.assertColorEqual(r1, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(252 61 153)'))
        self.assertColorEqual(r6, Color('rgb(7 199 237)'))
        self.assertColorEqual(r7, Color('rgb(7 199 237)'))

    def test_destination_atop(self):
        """Test destination atop."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='destination-atop', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='destination-atop', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='destination-atop', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='destination-atop', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='destination-atop', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='destination-atop', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='destination-atop', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r3, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r4, Color('rgb(252 61 153)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(7 199 237)'))
        self.assertColorEqual(r7, Color('rgb(245 211 17)'))

    def test_xor(self):
        """Test XOR."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='xor', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='xor', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='xor', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='xor', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='xor', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='xor', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='xor', space='srgb')

        self.assertColorEqual(r1, Color('#07c7ed'))
        self.assertColorEqual(r2, Color('#fc3d99'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r5, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r6, Color('rgb(0 0 0 / 0)'))
        self.assertColorEqual(r7, Color('rgb(7 199 237)'))

    def test_lighter(self):
        """Test lighter."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='lighter', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='lighter', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='lighter', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='lighter', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='lighter', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='lighter', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='plus-lighter', space='srgb')

        self.assertColorEqual(r1, Color('#07c7ed'))
        self.assertColorEqual(r2, Color('#fc3d99'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(259 260 390)'))
        self.assertColorEqual(r5, Color('rgb(497 272 170)'))
        self.assertColorEqual(r6, Color('rgb(252 410 254)'))
        self.assertColorEqual(r7, Color('rgb(255 255 255)'))

    def test_plus_lighter(self):
        """Test plus lighter."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='plus-lighter', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='plus-lighter', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='plus-lighter', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='plus-lighter', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='plus-lighter', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='plus-lighter', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='plus-lighter', space='srgb')

        self.assertColorEqual(r1, Color('#07c7ed'))
        self.assertColorEqual(r2, Color('#fc3d99'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(255 255 255)'))
        self.assertColorEqual(r5, Color('rgb(255 255 170)'))
        self.assertColorEqual(r6, Color('rgb(252 255 254)'))
        self.assertColorEqual(r7, Color('rgb(255 255 255)'))

    def test_plus_darker(self):
        """Test plus darker."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], operator='plus-darker', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], operator='plus-darker', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], operator='plus-darker', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], operator='plus-darker', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], operator='plus-darker', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], operator='plus-darker', space='srgb')
        r7 = Color.layer([c1, c2, c3], operator='plus-darker', space='srgb')

        self.assertColorEqual(r1, Color('#07c7ed'))
        self.assertColorEqual(r2, Color('#fc3d99'))
        self.assertColorEqual(r3, Color('#f5d311'))
        self.assertColorEqual(r4, Color('rgb(4 5 135)'))
        self.assertColorEqual(r5, Color('rgb(242 17 0)'))
        self.assertColorEqual(r6, Color('rgb(0 155 0)'))
        self.assertColorEqual(r7, Color('rgb(0 0 0)'))
