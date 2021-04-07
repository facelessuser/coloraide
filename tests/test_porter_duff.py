"""Test Porter Duff composition modes."""
import unittest
from coloraide import Color
from . import util


class TestPorterDuffModes(util.ColorAsserts, unittest.TestCase):
    """Test Porter Duff modes."""

    def test_clear(self):
        """Test clear."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='clear'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='clear'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='clear'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='clear'),
            Color('transparent')
        )

    def test_copy(self):
        """Test copy."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='copy'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='copy'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='copy'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='copy'),
            Color('transparent')
        )

    def test_destination(self):
        """Test destination."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='destination'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='destination'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='destination'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='destination'),
            Color('transparent')
        )

    def test_source_over(self):
        """Test source over."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='source-over'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='source-over'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='source-over'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='source-over'),
            Color('transparent')
        )

    def test_destination_over(self):
        """Test destination over."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='destination-over'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='destination-over'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='destination-over'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='destination-over'),
            Color('transparent')
        )

    def test_source_in(self):
        """Test source in."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='source-in'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='source-in'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='source-in'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='source-in'),
            Color('transparent')
        )

    def test_destination_in(self):
        """Test destination in."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='destination-in'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='destination-in'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='destination-in'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='destination-in'),
            Color('transparent')
        )

    def test_source_out(self):
        """Test source out."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='source-out'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='source-out'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='source-out'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='source-out'),
            Color('transparent')
        )

    def test_destination_out(self):
        """Test destination out."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='destination-out'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='destination-out'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='destination-out'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='destination-out'),
            Color('transparent')
        )

    def test_source_atop(self):
        """Test source atop."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='source-atop'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='source-atop'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='source-atop'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='source-atop'),
            Color('transparent')
        )

    def test_destination_atop(self):
        """Test destination atop."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='destination-atop'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='destination-atop'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='destination-atop'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='destination-atop'),
            Color('transparent')
        )

    def test_xor(self):
        """Test XOR."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='xor'),
            Color('transparent')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='xor'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='xor'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='xor'),
            Color('transparent')
        )

    def test_lighter(self):
        """Test lighter."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('color(srgb 0 0 1 / 1)', operator='lighter'),
            Color('rgb(255 0 255)')
        )
        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 1)').compose('transparent', operator='lighter'),
            Color('color(srgb 1 0 0 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('color(srgb 0 0 1 / 1)', operator='lighter'),
            Color('color(srgb 0 0 1 / 1)')
        )
        self.assertColorEqual(
            Color('transparent').compose('transparent', operator='lighter'),
            Color('transparent')
        )
