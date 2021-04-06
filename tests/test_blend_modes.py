"""Test Blend modes."""
import unittest
from coloraide import Color
from . import util

# Colors that produce pretty distinct results
REDISH = '#fc3d99'
BLUISH = '#07c7ed'
YELLOWISH = '#f5d311'


class TestBlendModes(util.ColorAsserts, unittest.TestCase):
    """Test blend modes."""

    def test_alpha(self):
        """Test normal blend mode with source alpha."""

        self.assertColorEqual(Color('blue').blend('color(srgb 1 0 0 / 0.5)', 'normal'), Color('blue'))
        self.assertColorEqual(
            Color('color(srgb 0 0 1 / 0.5)').blend('color(srgb 1 0 0)', 'normal'),
            Color('color(srgb 0.5 0 0.5)')
        )
        self.assertColorEqual(
            Color('color(srgb 0 0 1 / 0.5)').blend('color(srgb 1 0 0 / 0.5)', 'normal'),
            Color('color(srgb 0.25 0 0.5 / 0.75)')
        )

    def test_normal(self):
        """Test normal."""

        self.assertColorEqual(Color(REDISH).blend('black', 'normal'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).blend('white', 'normal'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'normal'), Color(REDISH))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'normal'), Color(BLUISH))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'normal'), Color(BLUISH))

    def test_multiply(self):
        """Test multiply."""

        self.assertColorEqual(Color(REDISH).blend('black', 'multiply'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'multiply'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'multiply'), Color('rgb(242.12 50.475 10.2)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'multiply'), Color('rgb(6.9176 47.604 142.2)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'multiply'), Color('rgb(6.7255 164.66 15.8)'))

    def test_screen(self):
        """Test screen."""

        self.assertColorEqual(Color(REDISH).blend('black', 'screen'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).blend('white', 'screen'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'screen'), Color('rgb(254.88 221.53 159.8)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'screen'), Color('rgb(252.08 212.4 247.8)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'screen'), Color('rgb(245.27 245.34 238.2)'))

    def test_overlay(self):
        """Test overlay."""

        self.assertColorEqual(Color(REDISH).blend('black', 'overlay'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'overlay'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'overlay'), Color('rgb(254.76 188.05 20.4)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'overlay'), Color('rgb(249.16 95.208 240.6)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'overlay'), Color('rgb(235.55 235.67 31.6)'))

    def test_darken(self):
        """Test darken."""

        self.assertColorEqual(Color(REDISH).blend('black', 'darken'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'darken'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'darken'), Color('rgb(245 61 17)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'darken'), Color('rgb(7 61 153)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'darken'), Color('rgb(7 199 17)'))

    def test_lighten(self):
        """Test lighten."""

        self.assertColorEqual(Color(REDISH).blend('black', 'lighten'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).blend('white', 'lighten'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'lighten'), Color('rgb(252 211 153)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'lighten'), Color('rgb(252 199 237)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'lighten'), Color('rgb(245 211 237)'))

    def test_color_dodge(self):
        """Test color dodge."""

        self.assertColorEqual(Color(REDISH).blend('black', 'color-dodge'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'color-dodge'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'color-dodge'), Color('rgb(255 255 42.5)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'color-dodge'), Color('rgb(255 255 255)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'color-dodge'), Color('rgb(251.92 255 240.83)'))

        # If source channel is 1 resultant channel will be 1
        self.assertColorEqual(Color('white').blend(REDISH, 'color-dodge'), Color('white'))

    def test_color_burn(self):
        """Test color burn."""

        self.assertColorEqual(Color(REDISH).blend('black', 'color-burn'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'color-burn'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'color-burn'), Color('rgb(244.88 71.066 0)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'color-burn'), Color('rgb(145.71 6.407 145.25)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'color-burn'), Color('rgb(0 198.62 0)'))

        # If source is  channel is 0, resultant channel will be 0
        self.assertColorEqual(Color('black').blend(REDISH, 'color-burn'), Color('black'))

    def test_difference(self):
        """Test difference."""

        self.assertColorEqual(Color(REDISH).blend('black', 'difference'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).blend('white', 'difference'), Color('rgb(3 194 102)'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'difference'), Color('rgb(7 150 136)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'difference'), Color('rgb(245 138 84)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'difference'), Color('rgb(238 12 220)'))

    def test_exclusion(self):
        """Test exclusion."""

        self.assertColorEqual(Color(REDISH).blend('black', 'exclusion'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).blend('white', 'exclusion'), Color('rgb(3 194 102)'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'exclusion'), Color('rgb(12.765 171.05 149.6)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'exclusion'), Color('rgb(245.16 164.79 105.6)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'exclusion'), Color('rgb(238.55 80.675 222.4)'))

    def test_color_hard_light(self):
        """Test hard light."""

        self.assertColorEqual(Color(REDISH).blend('black', 'hard-light'), Color('rgb(249 0 51)'))
        self.assertColorEqual(Color(REDISH).blend('white', 'hard-light'), Color('rgb(255 122 255)'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'hard-light'), Color('rgb(254.76 100.95 64.6)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'hard-light'), Color('rgb(13.835 169.79 240.6)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'hard-light'), Color('rgb(13.451 235.67 221.4)'))

    def test_color_soft_light(self):
        """Test soft light."""

        self.assertColorEqual(Color(REDISH).blend('black', 'soft-light'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'soft-light'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'soft-light'), Color('rgb(249.83 192.01 24.722)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'soft-light'), Color('rgb(249.2 96.747 191.24)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'soft-light'), Color('rgb(235.92 222.75 50.158)'))

    def test_hue(self):
        """Test hue."""

        self.assertColorEqual(Color(REDISH).blend('black', 'hue'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'hue'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'hue'), Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'hue'), Color('rgb(13.23 172.67 204.23)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'hue'), Color('rgb(113.71 231.66 255)'))

        # sRGB must be forced
        self.assertColorEqual(
            Color(BLUISH).blend(YELLOWISH, 'hue', space="display-p3"),
            Color(BLUISH).blend(YELLOWISH, 'hue', space="srgb")
        )

    def test_saturation(self):
        """Test hue."""

        self.assertColorEqual(Color(REDISH).blend('black', 'saturation'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'saturation'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'saturation'), Color('rgb(237.54 209.06 46.543)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'saturation'), Color('rgb(255 59.357 153.59)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'saturation'), Color('rgb(245.4 211.1 15.403)'))

        # sRGB must be forced
        self.assertColorEqual(
            Color(BLUISH).blend(YELLOWISH, 'saturation', space="display-p3"),
            Color(BLUISH).blend(YELLOWISH, 'saturation', space="srgb")
        )

    def test_luminosity(self):
        """Test luminosity."""

        self.assertColorEqual(Color(REDISH).blend('black', 'luminosity'), Color('rgb(128.6 128.6 128.6)'))
        self.assertColorEqual(Color(REDISH).blend('white', 'luminosity'), Color('rgb(128.6 128.6 128.6)'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'luminosity'), Color('rgb(161.06 137.04 0)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'luminosity'), Color('rgb(255 86.175 167.49)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'luminosity'), Color('rgb(182.76 155.5 0)'))

        # sRGB must be forced
        self.assertColorEqual(
            Color(BLUISH).blend(YELLOWISH, 'luminosity', space="display-p3"),
            Color(BLUISH).blend(YELLOWISH, 'luminosity', space="srgb")
        )

    def test_color(self):
        """Test color."""

        self.assertColorEqual(Color(REDISH).blend('black', 'color'), Color('black'))
        self.assertColorEqual(Color(REDISH).blend('white', 'color'), Color('white'))
        self.assertColorEqual(Color(REDISH).blend(YELLOWISH, 'color'), Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(Color(BLUISH).blend(REDISH, 'color'), Color('rgb(0 177.73 212.9)'))
        self.assertColorEqual(Color(BLUISH).blend(YELLOWISH, 'color'), Color('rgb(113.71 231.66 255)'))

        # sRGB must be forced
        self.assertColorEqual(
            Color(BLUISH).blend(YELLOWISH, 'color', space="display-p3"),
            Color(BLUISH).blend(YELLOWISH, 'color', space="srgb")
        )
