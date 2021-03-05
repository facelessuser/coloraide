"""Sanity check that ensures all colors round trip back."""
import unittest
from coloraide.css import Color


class TestRoundTrip(unittest.TestCase):
    """
    Test round trip conversions of all color spaces.

    A color that does not round trip back likely has a broken conversion.
    It may be possible that some color spaces degrade through conversion,
    but the currently supported spaces have enough integrity when performing
    a round trip to meet the required value at the default precision.
    """

    def assert_round_trip(self, color):
        """Test sRGB to HSL."""

        print('----- Color -----')
        print(color)
        c1 = Color(color)
        for space in c1.CS_MAP.keys():
            # Print the color space to easily identify which color space broke.
            print('>>> Convert to: {}'.format(space))
            c2 = c1.convert(space)
            c2.convert(c1.space(), in_place=True)
            self.assertEqual(c1.to_string(color=True), c2.to_string(color=True))

    def test_srgb(self):
        """Test sRGB."""

        self.assert_round_trip("rgb(10% 100% 50%)")

    def test_srgb_linear(self):
        """Test sRGB Linear."""

        self.assert_round_trip("color(srgb-linear 10% 100% 50%)")

    def test_hsl(self):
        """Test HSL."""

        self.assert_round_trip("hsl(128 50% 75%)")

    def test_hsv(self):
        """Test HSV."""

        self.assert_round_trip("color(hsv 300 70 50)")

    def test_hwb(self):
        """Test HWB."""

        self.assert_round_trip("hwb(90 25% 10%)")

    def test_lab(self):
        """Test Lab."""

        self.assert_round_trip("lab(50% -40 10)")

    def test_lch(self):
        """Test LCH."""

        self.assert_round_trip("lch(80% 50 270)")

    def test_xyz(self):
        """Test XYZ."""

        self.assert_round_trip("color(xyz 0.3 0.7 0.7)")

    def test_display_p3(self):
        """Test Display P3."""

        self.assert_round_trip("color(display-p3 0.3 0.4 0.9)")

    def test_rec_2020(self):
        """Test Rec 2020."""

        self.assert_round_trip("color(rec2020 0.9 0.2 0.4)")

    def test_prophoto_rgb(self):
        """Test ProPhoto RGB."""

        self.assert_round_trip("color(prophoto-rgb 0.2 0.8 0.0)")

    def test_a98_rgb(self):
        """Test A98 RGB."""

        self.assert_round_trip("color(a98-rgb 0.6 0.4 0.2)")
