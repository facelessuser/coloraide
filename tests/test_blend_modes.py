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

        self.assertColorEqual(Color('blue').compose('color(srgb 1 0 0 / 0.5)', blend='normal'), Color('blue'))
        self.assertColorEqual(
            Color('color(srgb 0 0 1 / 0.5)').compose('color(srgb 1 0 0)', blend='normal'),
            Color('color(srgb 0.5 0 0.5)')
        )
        self.assertColorEqual(
            Color('color(srgb 0 0 1 / 0.5)').compose('color(srgb 1 0 0 / 0.5)', blend='normal'),
            Color('color(srgb 0.333333 0 0.666667 / 0.75)')
        )

    def test_normal(self):
        """Test normal."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='normal'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).compose('white', blend='normal'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='normal'), Color(REDISH))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='normal'), Color(BLUISH))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='normal'), Color(BLUISH))

    def test_multiply(self):
        """Test multiply."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='multiply'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='multiply'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='multiply'), Color('rgb(242.12 50.475 10.2)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='multiply'), Color('rgb(6.9176 47.604 142.2)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='multiply'), Color('rgb(6.7255 164.66 15.8)'))

    def test_screen(self):
        """Test screen."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='screen'), Color(REDISH))
        self.assertColorEqual(Color(REDISH).compose('white', blend='screen'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='screen'), Color('rgb(254.88 221.53 159.8)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='screen'), Color('rgb(252.08 212.4 247.8)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='screen'), Color('rgb(245.27 245.34 238.2)'))

    def test_overlay(self):
        """Test overlay."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='overlay'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='overlay'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='overlay'), Color('rgb(254.76 188.05 20.4)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='overlay'), Color('rgb(249.16 95.208 240.6)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='overlay'), Color('rgb(235.55 235.67 31.6)'))

    def test_darken(self):
        """Test darken."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='darken'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='darken'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='darken'), Color('rgb(245 61 17)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='darken'), Color('rgb(7 61 153)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='darken'), Color('rgb(7 199 17)'))

    def test_lighten(self):
        """Test lighten."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='lighten'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='lighten'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='lighten'), Color('rgb(252 211 153)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='lighten'), Color('rgb(252 199 237)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='lighten'), Color('rgb(245 211 237)'))

    def test_color_dodge(self):
        """Test color dodge."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='color-dodge'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='color-dodge'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='color-dodge'), Color('rgb(255 255 42.5)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='color-dodge'), Color('rgb(255 255 255)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='color-dodge'), Color('rgb(251.92 255 240.83)'))

        # If source channel is 1 resultant channel will be 1
        self.assertColorEqual(Color('white').compose(REDISH, blend='color-dodge'), Color('white'))

    def test_color_burn(self):
        """Test color burn."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='color-burn'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='color-burn'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='color-burn'), Color('rgb(244.88 71.066 0)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='color-burn'), Color('rgb(145.71 6.407 145.25)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='color-burn'), Color('rgb(0 198.62 0)'))

        # If source is  channel is 0, resultant channel will be 0
        self.assertColorEqual(Color('black').compose(REDISH, blend='color-burn'), Color('black'))

    def test_difference(self):
        """Test difference."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='difference'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='difference'), Color('rgb(3 194 102)'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='difference'), Color('rgb(7 150 136)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='difference'), Color('rgb(245 138 84)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='difference'), Color('rgb(238 12 220)'))

    def test_exclusion(self):
        """Test exclusion."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='exclusion'), Color('rgb(252 61 153)'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='exclusion'), Color('rgb(3 194 102)'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='exclusion'), Color('rgb(12.765 171.05 149.6)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='exclusion'), Color('rgb(245.16 164.79 105.6)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='exclusion'), Color('rgb(238.55 80.675 222.4)'))

    def test_color_hard_light(self):
        """Test hard light."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='hard-light'), Color('rgb(249 0 51)'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='hard-light'), Color('rgb(255 122 255)'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='hard-light'), Color('rgb(254.76 100.95 64.6)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='hard-light'), Color('rgb(13.835 169.79 240.6)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='hard-light'), Color('rgb(13.451 235.67 221.4)'))

    def test_color_soft_light(self):
        """Test soft light."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='soft-light'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='soft-light'), Color('white'))
        self.assertColorEqual(
            Color(REDISH).compose(YELLOWISH, blend='soft-light'),
            Color('rgb(249.83 192.01 24.722)')
        )
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='soft-light'), Color('rgb(249.2 96.747 191.24)'))
        self.assertColorEqual(
            Color(BLUISH).compose(YELLOWISH, blend='soft-light'),
            Color('rgb(235.92 222.75 50.158)')
        )

    def test_hue(self):
        """Test hue."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='hue'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='hue'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='hue'), Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='hue'), Color('rgb(13.23 172.67 204.23)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='hue'), Color('rgb(113.71 231.66 255)'))

    def test_saturation(self):
        """Test hue."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='saturation'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='saturation'), Color('white'))
        self.assertColorEqual(
            Color(REDISH).compose(YELLOWISH, blend='saturation'),
            Color('rgb(237.54 209.06 46.543)')
        )
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='saturation'), Color('rgb(255 59.357 153.59)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='saturation'), Color('rgb(245.4 211.1 15.403)'))

    def test_luminosity(self):
        """Test luminosity."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='luminosity'), Color('rgb(128.6 128.6 128.6)'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='luminosity'), Color('rgb(128.6 128.6 128.6)'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='luminosity'), Color('rgb(161.06 137.04 0)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='luminosity'), Color('rgb(255 86.175 167.49)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='luminosity'), Color('rgb(182.76 155.5 0)'))

    def test_color(self):
        """Test color."""

        self.assertColorEqual(Color(REDISH).compose('black', blend='color'), Color('black'))
        self.assertColorEqual(Color(REDISH).compose('white', blend='color'), Color('white'))
        self.assertColorEqual(Color(REDISH).compose(YELLOWISH, blend='color'), Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(Color(BLUISH).compose(REDISH, blend='color'), Color('rgb(0 177.73 212.9)'))
        self.assertColorEqual(Color(BLUISH).compose(YELLOWISH, blend='color'), Color('rgb(113.71 231.66 255)'))


class TestBlend(util.ColorAsserts, unittest.TestCase):
    """Test general blend API."""

    def test_blend_no_mode(self):
        """Test blend with no mode."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertEqual(c1.compose(c2, blend='normal'), c1.compose(c2))

    def test_blend_different_space(self):
        """Test blend logic in different space."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertColorEqual(
            c1.compose(c2, blend='normal', space="display-p3"),
            Color('color(display-p3 0.5 0.5 0.64524)')
        )

    def test_blend_different_space_and_output(self):
        """Test blend logic in different space and different output."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertColorEqual(
            c1.compose(c2, blend='normal', space="display-p3", out_space="srgb"),
            Color('rgb(127.5 127.5 167.63)')
        )

    def test_blend_bad_mode(self):
        """Test blend bad mode."""

        with self.assertRaises(ValueError):
            Color('blue').compose('red', blend='bad')

    def test_blend_in_place(self):
        """Test blend in place modifies original."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = c1.compose(c2, blend='normal', in_place=True)
        self.assertTrue(c1 is c3)
        self.assertEqual(c1, Color('color(srgb 0.5 0.5 0.5)'))
