"""Test Blend modes."""
import unittest
from coloraide import Color
from . import util


class TestBlendModes(util.ColorAsserts, unittest.TestCase):
    """Test blend modes."""

    def test_transparent(self):
        """Test blending with transparent colors."""

        self.assertColorEqual(Color.layer(['blue', 'transparent'], blend='normal'), Color('blue'))
        self.assertColorEqual(Color.layer(['transparent', 'blue'], blend='normal'), Color('blue'))

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

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='normal', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='normal', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='normal', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='normal', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='normal', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='normal', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='normal', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(7 199 237)'))
        self.assertColorEqual(r5, Color('rgb(252 61 153)'))
        self.assertColorEqual(r6, Color('rgb(7 199 237)'))
        self.assertColorEqual(r7, Color('rgb(7 199 237)'))

    def test_multiply(self):
        """Test multiply."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='multiply', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='multiply', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='multiply', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='multiply', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='multiply', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='multiply', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='multiply', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(6.9176 47.604 142.2)'))
        self.assertColorEqual(r5, Color('rgb(242.12 50.475 10.2)'))
        self.assertColorEqual(r6, Color('rgb(6.7255 164.66 15.8)'))
        self.assertColorEqual(r7, Color('rgb(6.6464 39.39 9.48)'))

    def test_screen(self):
        """Test screen."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='screen', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='screen', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='screen', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='screen', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='screen', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='screen', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='screen', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(252.08 212.4 247.8)'))
        self.assertColorEqual(r5, Color('rgb(254.88 221.53 159.8)'))
        self.assertColorEqual(r6, Color('rgb(245.27 245.34 238.2)'))
        self.assertColorEqual(r7, Color('rgb(254.89 247.65 248.28)'))

    def test_overlay(self):
        """Test overlay."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='overlay', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='overlay', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='overlay', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='overlay', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='overlay', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='overlay', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='overlay', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(249.16 95.208 240.6)'))
        self.assertColorEqual(r5, Color('rgb(254.76 188.05 20.4)'))
        self.assertColorEqual(r6, Color('rgb(235.55 235.67 31.6)'))
        self.assertColorEqual(r7, Color('rgb(254.54 225.59 37.92)'))

    def test_darken(self):
        """Test darken."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='darken', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='darken', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='darken', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='darken', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='darken', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='darken', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='darken', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(7 61 153)'))
        self.assertColorEqual(r5, Color('rgb(245 61 17)'))
        self.assertColorEqual(r6, Color('rgb(7 199 17)'))
        self.assertColorEqual(r7, Color('rgb(7 61 17)'))

    def test_lighten(self):
        """Test lighten."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='lighten', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='lighten', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='lighten', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='lighten', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='lighten', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='lighten', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='lighten', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(252 199 237)'))
        self.assertColorEqual(r5, Color('rgb(252 211 153)'))
        self.assertColorEqual(r6, Color('rgb(245 211 237)'))
        self.assertColorEqual(r7, Color('rgb(252 211 237)'))

    def test_color_dodge(self):
        """Test color dodge."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='color-dodge', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='color-dodge', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='color-dodge', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='color-dodge', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='color-dodge', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='color-dodge', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='color-dodge', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(255 255 255)'))
        self.assertColorEqual(r5, Color('rgb(255 255 42.5)'))
        self.assertColorEqual(r6, Color('rgb(251.92 255 240.83)'))
        self.assertColorEqual(r7, Color('rgb(255 255 255)'))

        # If source channel is 1 resultant channel will be 1
        self.assertColorEqual(Color.layer(['#fc3d99', 'black'], blend='color-dodge'), Color('black'))

        self.assertColorEqual(Color.layer(['#fc3d99', 'white'], blend='color-dodge'), Color('white'))
        self.assertColorEqual(Color.layer(['white', '#fc3d99'], blend='color-dodge'), Color('white'))

    def test_color_burn(self):
        """Test color burn."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='color-burn', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='color-burn', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='color-burn', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='color-burn', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='color-burn', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='color-burn', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='color-burn', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(145.71 6.407 145.25)'))
        self.assertColorEqual(r5, Color('rgb(244.88 71.066 0)'))
        self.assertColorEqual(r6, Color('rgb(0 198.62 0)'))
        self.assertColorEqual(r7, Color('rgb(0 19.305 0)'))

        # If source is  channel is 0, resultant channel will be 0
        self.assertColorEqual(Color.layer(['black', '#fc3d99'], blend='color-burn'), Color('black'))

        self.assertColorEqual(Color.layer(['#fc3d99', 'black'], blend='color-burn'), Color('black'))
        self.assertColorEqual(Color.layer(['#fc3d99', 'white'], blend='color-burn'), Color('white'))

    def test_difference(self):
        """Test difference."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='difference', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='difference', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='difference', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='difference', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='difference', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='difference', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='difference', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(245 138 84)'))
        self.assertColorEqual(r5, Color('rgb(7 150 136)'))
        self.assertColorEqual(r6, Color('rgb(238 12 220)'))
        self.assertColorEqual(r7, Color('rgb(0 49 101)'))

    def test_exclusion(self):
        """Test exclusion."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='exclusion', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='exclusion', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='exclusion', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='exclusion', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='exclusion', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='exclusion', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='exclusion', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(245.16 164.79 105.6)'))
        self.assertColorEqual(r5, Color('rgb(12.765 171.05 149.6)'))
        self.assertColorEqual(r6, Color('rgb(238.55 80.675 222.4)'))
        self.assertColorEqual(r7, Color('rgb(19.064 103.08 108.52)'))

    def test_color_hard_light(self):
        """Test hard light."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='hard-light', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='hard-light', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='hard-light', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='hard-light', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='hard-light', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='hard-light', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='hard-light', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(13.835 169.79 240.6)'))
        self.assertColorEqual(r5, Color('rgb(254.76 100.95 64.6)'))
        self.assertColorEqual(r6, Color('rgb(13.451 235.67 221.4)'))
        self.assertColorEqual(r7, Color('rgb(13.987 187.34 228.12)'))

    def test_color_soft_light(self):
        """Test soft light."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='soft-light', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='soft-light', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='soft-light', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='soft-light', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='soft-light', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='soft-light', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='soft-light', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(249.2 96.747 191.24)'))
        self.assertColorEqual(r5, Color('rgb(249.83 192.01 24.722)'))
        self.assertColorEqual(r6, Color('rgb(235.92 222.75 50.158)'))
        self.assertColorEqual(r7, Color('rgb(245.05 208.42 66.909)'))

    def test_hue(self):
        """Test hue."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='hue', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='hue', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='hue', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='hue', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='hue', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='hue', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='hue', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(13.23 172.67 204.23)'))
        self.assertColorEqual(r5, Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(r6, Color('rgb(113.71 231.66 255)'))
        self.assertColorEqual(r7, Color('rgb(146.74 219.03 233.34)'))

    def test_saturation(self):
        """Test hue."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='saturation', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='saturation', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='saturation', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='saturation', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='saturation', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='saturation', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='saturation', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(255 59.357 153.59)'))
        self.assertColorEqual(r5, Color('rgb(237.54 209.06 46.543)'))
        self.assertColorEqual(r6, Color('rgb(245.4 211.1 15.403)'))
        self.assertColorEqual(r7, Color('rgb(245.4 211.1 15.403)'))

        self.assertColorEqual(Color.layer(['#fc3d99', 'black'], blend='saturation'), Color('black'))
        self.assertColorEqual(Color.layer(['#fc3d99', 'white'], blend='saturation'), Color('white'))

    def test_luminosity(self):
        """Test luminosity."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='luminosity', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='luminosity', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='luminosity', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='luminosity', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='luminosity', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='luminosity', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='luminosity', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(255 86.175 167.49)'))
        self.assertColorEqual(r5, Color('rgb(161.06 137.04 0)'))
        self.assertColorEqual(r6, Color('rgb(182.76 155.5 0)'))
        self.assertColorEqual(r7, Color('rgb(178.38 154.37 17.327)'))

    def test_color(self):
        """Test color."""

        c1 = Color('#07c7ed')
        c2 = Color('#fc3d99')
        c3 = Color('#f5d311')

        r1 = Color.layer([c1, 'transparent', 'transparent'], blend='color', space='srgb')
        r2 = Color.layer(['transparent', c2, 'transparent'], blend='color', space='srgb')
        r3 = Color.layer(['transparent', 'transparent', c3], blend='color', space='srgb')
        r4 = Color.layer([c1, c2, 'transparent'], blend='color', space='srgb')
        r5 = Color.layer(['transparent', c2, c3], blend='color', space='srgb')
        r6 = Color.layer([c1, 'transparent', c3], blend='color', space='srgb')
        r7 = Color.layer([c1, c2, c3], blend='color', space='srgb')

        self.assertColorEqual(r1, Color('rgb(7 199 237)'))
        self.assertColorEqual(r2, Color('rgb(252 61 153)'))
        self.assertColorEqual(r3, Color('rgb(245 211 17)'))
        self.assertColorEqual(r4, Color('rgb(0 177.73 212.9)'))
        self.assertColorEqual(r5, Color('rgb(255 168.4 210.11)'))
        self.assertColorEqual(r6, Color('rgb(113.71 231.66 255)'))
        self.assertColorEqual(r7, Color('rgb(113.71 231.66 255)'))


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
