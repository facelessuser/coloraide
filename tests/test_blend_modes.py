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

        self.assertColorEqual(Color.layer(['blue', 'color(srgb 1 0 0 / 0.5)'], blend='normal'), Color('blue'))
        self.assertColorEqual(
            Color.layer(['color(srgb 0 0 1 / 0.5)', 'color(srgb 1 0 0)'], blend='normal'),
            Color('color(srgb 0.5 0 0.5)')
        )
        self.assertColorEqual(
            Color.layer(['color(srgb 0 0 1 / 0.5)', 'color(srgb 1 0 0 / 0.5)'], blend='normal'),
            Color('color(srgb 0.333333 0 0.666667 / 0.75)')
        )

    def test_normal(self):
        """Test normal."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='normal'), Color(REDISH))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='normal'), Color(REDISH))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='normal'), Color(REDISH))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='normal'), Color(BLUISH))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='normal'), Color(BLUISH))

    def test_multiply(self):
        """Test multiply."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='multiply'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='multiply'), Color(REDISH))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='multiply'), Color('rgb(242.12 50.475 10.2)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='multiply'), Color('rgb(6.9176 47.604 142.2)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='multiply'), Color('rgb(6.7255 164.66 15.8)'))

    def test_screen(self):
        """Test screen."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='screen'), Color(REDISH))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='screen'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='screen'), Color('rgb(254.88 221.53 159.8)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='screen'), Color('rgb(252.08 212.4 247.8)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='screen'), Color('rgb(245.27 245.34 238.2)'))

    def test_overlay(self):
        """Test overlay."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='overlay'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='overlay'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='overlay'), Color('rgb(254.76 188.05 20.4)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='overlay'), Color('rgb(249.16 95.208 240.6)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='overlay'), Color('rgb(235.55 235.67 31.6)'))

    def test_darken(self):
        """Test darken."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='darken'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='darken'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='darken'), Color('rgb(245 61 17)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='darken'), Color('rgb(7 61 153)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='darken'), Color('rgb(7 199 17)'))

    def test_lighten(self):
        """Test lighten."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='lighten'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='lighten'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='lighten'), Color('rgb(252 211 153)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='lighten'), Color('rgb(252 199 237)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='lighten'), Color('rgb(245 211 237)'))

    def test_color_dodge(self):
        """Test color dodge."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='color-dodge'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='color-dodge'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='color-dodge'), Color('rgb(255 255 42.5)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='color-dodge'), Color('rgb(255 255 255)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='color-dodge'), Color('rgb(251.92 255 240.83)'))

        # If source channel is 1 resultant channel will be 1
        self.assertColorEqual(Color.layer(['white', REDISH], blend='color-dodge'), Color('white'))

    def test_color_burn(self):
        """Test color burn."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='color-burn'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='color-burn'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='color-burn'), Color('rgb(244.88 71.066 0)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='color-burn'), Color('rgb(145.71 6.407 145.25)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='color-burn'), Color('rgb(0 198.62 0)'))

        # If source is  channel is 0, resultant channel will be 0
        self.assertColorEqual(Color.layer(['black', REDISH], blend='color-burn'), Color('black'))

    def test_difference(self):
        """Test difference."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='difference'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='difference'), Color('rgb(3 194 102)'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='difference'), Color('rgb(7 150 136)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='difference'), Color('rgb(245 138 84)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='difference'), Color('rgb(238 12 220)'))

    def test_exclusion(self):
        """Test exclusion."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='exclusion'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='exclusion'), Color('rgb(3 194 102)'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='exclusion'), Color('rgb(12.765 171.05 149.6)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='exclusion'), Color('rgb(245.16 164.79 105.6)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='exclusion'), Color('rgb(238.55 80.675 222.4)'))

    def test_color_hard_light(self):
        """Test hard light."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='hard-light'), Color('rgb(249 0 51)'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='hard-light'), Color('rgb(255 122 255)'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='hard-light'), Color('rgb(254.76 100.95 64.6)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='hard-light'), Color('rgb(13.835 169.79 240.6)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='hard-light'), Color('rgb(13.451 235.67 221.4)'))

    def test_color_soft_light(self):
        """Test soft light."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='soft-light'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='soft-light'), Color('white'))
        self.assertColorEqual(
            Color.layer([REDISH, YELLOWISH], blend='soft-light'),
            Color('rgb(249.83 192.01 24.722)')
        )
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='soft-light'), Color('rgb(249.2 96.747 191.24)'))
        self.assertColorEqual(
            Color.layer([BLUISH, YELLOWISH], blend='soft-light'),
            Color('rgb(235.92 222.75 50.158)')
        )

    def test_hue(self):
        """Test hue."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='hue'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='hue'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='hue'), Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='hue'), Color('rgb(13.23 172.67 204.23)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='hue'), Color('rgb(113.71 231.66 255)'))

    def test_saturation(self):
        """Test hue."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='saturation'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='saturation'), Color('white'))
        self.assertColorEqual(
            Color.layer([REDISH, YELLOWISH], blend='saturation'),
            Color('rgb(237.54 209.06 46.543)')
        )
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='saturation'), Color('rgb(255 59.357 153.59)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='saturation'), Color('rgb(245.4 211.1 15.403)'))

    def test_luminosity(self):
        """Test luminosity."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='luminosity'), Color('rgb(128.6 128.6 128.6)'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='luminosity'), Color('rgb(128.6 128.6 128.6)'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='luminosity'), Color('rgb(161.06 137.04 0)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='luminosity'), Color('rgb(255 86.175 167.49)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='luminosity'), Color('rgb(182.76 155.5 0)'))

    def test_color(self):
        """Test color."""

        self.assertColorEqual(Color.layer([REDISH, 'black'], blend='color'), Color('black'))
        self.assertColorEqual(Color.layer([REDISH, 'white'], blend='color'), Color('white'))
        self.assertColorEqual(Color.layer([REDISH, YELLOWISH], blend='color'), Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(Color.layer([BLUISH, REDISH], blend='color'), Color('rgb(0 177.73 212.9)'))
        self.assertColorEqual(Color.layer([BLUISH, YELLOWISH], blend='color'), Color('rgb(113.71 231.66 255)'))


class TestBlend(util.ColorAsserts, unittest.TestCase):
    """Test general blend API."""

    def test_blend_no_mode(self):
        """Test blend with no mode."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertEqual(Color.layer([c1, c2], blend='normal'), Color.layer([c1, c2]))

    def test_blend_different_space(self):
        """Test blend logic in different space."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertColorEqual(
            Color.layer([c1, c2], blend='normal', space="display-p3"),
            Color('color(display-p3 0.5 0.5 0.64524)')
        )

    def test_blend_different_space_and_output(self):
        """Test blend logic in different space and different output."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertColorEqual(
            Color.layer([c1, c2], blend='normal', space="display-p3", out_space="srgb"),
            Color('rgb(127.5 127.5 167.63)')
        )

    def test_blend_bad_mode(self):
        """Test blend bad mode."""

        with self.assertRaises(ValueError):
            Color.layer(['blue', 'red'], blend='bad')
