"""Test harmonies."""
from coloraide.everything import ColorAll as Color
from . import util
import math
import unittest


class TestWavelenghts(util.ColorAssertsPyTest, unittest.TestCase):
    """Test wavelengths."""

    def test_wavelengths_exact(self):
        """
        Test conversion from a wavelength to a color.

        If we are dealing with exact wavelengths from the CMF, we should get the same value
        when spawning a color from that wavelength and then reading that wavelength data back.
        """

        for w in range(360, 700, 1):
            self.assertEqual(Color.from_wavelength('xyz-d65', w, scale=False).wavelength()[0], w)

    def test_wavelengths_scale(self):
        """
        Test conversion from a wavelength to a color with scaling.

        We should have enough accuracy to scale in a linear RGB space and still get the same wavelength.
        """

        for w in range(360, 700, 1):
            self.assertEqual(Color.from_wavelength('srgb', w, scale_space='srgb-linear').wavelength()[0], w)

    def test_wavelengths_exact_other_whitepoint(self):
        """
        Test conversion from a wavelength to a color with an non-D65 white point.

        Color data should be placed in a color's white point and still yield the same wavelength, assuming, the
        color space transformation doesn't go through another white point or introduce too much error.
        """

        for w in range(360, 700, 1):
            self.assertEqual(Color.from_wavelength('xyz-d50', w, scale=False).wavelength()[0], w)

    def test_wavelengths_exact_in_manual_whitepoint(self):
        """
        Test conversion from a wavelength to a color with a manual white point.

        We should still get reasonable results when testing in another white point.
        """

        for w in range(360, 700, 1):
            self.assertEqual(Color.from_wavelength('xyz-d65', w, scale=False).wavelength(white=(1 / 3, 1 / 3))[0], w)

    def test_wavelength_not_cloeset(self):
        """Test wavelength without snapping to closest wavelength."""

        self.assertEqual(Color('red').wavelength(closest=False)[0], 611.2745348508324)

    def test_scale_rgb(self):
        """Scale color in RGB."""

        c = Color.from_wavelength('srgb', 405)
        self.assertColorEqual(c, Color('rgb(141.26 0 255)'))
        self.assertEqual(c.wavelength()[0], 405)
        c = Color.from_wavelength('srgb', 405, scale_space='rec2020-linear')
        self.assertColorEqual(c, Color('rgb(142.61 -51.963 267.48)'))
        self.assertEqual(c.wavelength()[0], 405)
        c = Color.from_wavelength('hsl', 405)
        self.assertColorEqual(c, Color('hsl(273.24 100 50)'))
        self.assertEqual(c.wavelength()[0], 405)

    def test_wavelengths_approx(self):
        """Wavelengths that are not exactly in the CMFs will should round to nearest."""

        self.assertEqual(Color.from_wavelength('xyy', 420.78, scale=False).wavelength()[0], 421)
        self.assertEqual(Color.from_wavelength('xyy', 633.18, scale=False).wavelength()[0], 633)

    def test_dominant(self):
        """Test dominant wavelength results."""

        wl = Color('cyan').wavelength()
        self.assertEqual(wl[0], 491)
        self.assertEqual(wl[1], [0.038498159153797895, 0.3281622308559494])
        self.assertEqual(wl[2], [0.038498159153797895, 0.3281622308559494])

    def test_dominant_purple_line(self):
        """Test dominant on the purple line."""

        wl = Color('magenta').wavelength()
        self.assertEqual(wl[0], -549)
        self.assertEqual(wl[1], [0.32462146299052036, 0.0746128763440127])
        self.assertEqual(wl[2], [0.2954087822179229, 0.6979700802318552])

    def test_complementary(self):
        """Test complementary wavelength results."""

        wl = Color('cyan').wavelength(complementary=True)
        self.assertEqual(wl[0], 611)
        self.assertEqual(wl[1], [0.6697060045245415, 0.330090760783766])
        self.assertEqual(wl[2], [0.6697060045245415, 0.330090760783766])

    def test_complementary_purple_line(self):
        """Test complementary on the purple line."""

        wl = Color('magenta').wavelength(complementary=True)
        self.assertEqual(wl[0], 549)
        self.assertEqual(wl[1], [0.2954087822179229, 0.6979700802318552])
        self.assertEqual(wl[2], [0.2954087822179229, 0.6979700802318552])

    def test_achromatic_wavelength(self):
        """Test achromatic."""

        wl = Color('white').wavelength()
        self.assertTrue(math.isnan(wl[0]))
        self.assertTrue(all(math.isnan(x) for x in wl[1]))
        self.assertTrue(all(math.isnan(x) for x in wl[2]))

    def test_bad_range(self):
        """Test achromatic."""

        with self.assertRaises(ValueError):
            Color.from_wavelength('srgb', 300)
