"""Test CAM02 UCS."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestCAM02UCS(util.ColorAssertsPyTest):
    """Test CAM02 UCS."""

    COLORS = [
        ('red', 'color(--cam02-ucs 60.054 38.679 24.316)'),
        ('orange', 'color(--cam02-ucs 79.041 9.9159 31.18)'),
        ('yellow', 'color(--cam02-ucs 97.411 -10.31 35.608)'),
        ('green', 'color(--cam02-ucs 46.973 -24.251 22.833)'),
        ('blue', 'color(--cam02-ucs 31.215 -8.3885 -39.158)'),
        ('indigo', 'color(--cam02-ucs 23.261 13.398 -25.33)'),
        ('violet', 'color(--cam02-ucs 74.347 25.207 -16.775)'),
        ('white', 'color(--cam02-ucs 100 -1.9179 -1.1405)'),
        ('gray', 'color(--cam02-ucs 56.23 -1.2687 -0.75454)'),
        ('black', 'color(--cam02-ucs 0 0 0)'),
        # Test color
        ('color(--cam02-ucs 50 10 -10)', 'color(--cam02-ucs 50 10 -10)'),
        ('color(--cam02-ucs 50 10 -10 / 0.5)', 'color(--cam02-ucs 50 10 -10 / 0.5)'),
        ('color(--cam02-ucs none none none / none)', 'color(--cam02-ucs none none none / none)'),
        # Test percent ranges
        ('color(--cam02-ucs 0% 0% 0%)', 'color(--cam02-ucs 0 0 0)'),
        ('color(--cam02-ucs 50% 50% -50% / 50%)', 'color(--cam02-ucs 50 25 -25 / 0.5)'),
        ('color(--cam02-ucs 100% 100% 100%)', 'color(--cam02-ucs 100 50 50)'),
        ('color(--cam02-ucs -100% -100% -100%)', 'color(--cam02-ucs -100 -50 -50)'),
        # Miscellaneous cases
        ('color(--cam02-jmh -10 30 270)', 'color(--cam02-ucs -15.888 0 -22.858)'),
        ('color(--cam02-jmh 10 -20 90)', 'color(--cam02-ucs 15.888 0 -23.466)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam02-ucs'), Color(color2))


class TestCAM02UCSSerialize(util.ColorAssertsPyTest):
    """Test CAM02 UCS serialization."""

    COLORS = [
        # Test color
        ('color(--cam02-ucs 75 10 -10 / 0.5)', {}, 'color(--cam02-ucs 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam02-ucs 75 10 -10)', {'alpha': True}, 'color(--cam02-ucs 75 10 -10 / 1)'),
        ('color(--cam02-ucs 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam02-ucs 75 10 -10)'),
        # Test None
        ('color(--cam02-ucs none 10 -10)', {}, 'color(--cam02-ucs 0 10 -10)'),
        ('color(--cam02-ucs none 10 -10)', {'none': True}, 'color(--cam02-ucs none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam02-ucs 120 10 -10)', {}, 'color(--cam02-ucs 120 10 -10)'),
        ('color(--cam02-ucs 120 10 -10)', {'fit': False}, 'color(--cam02-ucs 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM02UCSPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM02 UCS."""

    def test_names(self):
        """Test Lab-ish names."""

        c = Color('color(--cam02-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c._space.names(), ('j', 'a', 'b'))
        self.assertEqual(c._space.lightness_name(), 'j')

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam02-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam02-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam02-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam02-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestCAM02SCD(util.ColorAssertsPyTest):
    """Test CAM02 SCD."""

    COLORS = [
        ('red', 'color(--cam02-scd 60.054 31.859 20.029)'),
        ('orange', 'color(--cam02-scd 79.041 8.4908 26.699)'),
        ('yellow', 'color(--cam02-scd 97.411 -8.7055 30.066)'),
        ('green', 'color(--cam02-scd 46.973 -20.725 19.513)'),
        ('blue', 'color(--cam02-scd  31.215 -7.0198 -32.768)'),
        ('indigo', 'color(--cam02-scd 23.261 11.636 -21.998)'),
        ('violet', 'color(--cam02-scd 74.347 21.765 -14.485)'),
        ('white', 'color(--cam02-scd 100 -1.89 -1.124)'),
        ('gray', 'color(--cam02-scd 56.23 -1.2564 -0.7472)'),
        ('black', 'color(--cam02-scd 0 0 0)'),
        # Test color
        ('color(--cam02-scd 50 10 -10)', 'color(--cam02-scd 50 10 -10)'),
        ('color(--cam02-scd 50 10 -10 / 0.5)', 'color(--cam02-scd 50 10 -10 / 0.5)'),
        ('color(--cam02-scd 50% 50% -50% / 50%)', 'color(--cam02-scd 50 20 -20 / 0.5)'),
        ('color(--cam02-scd none none none / none)', 'color(--cam02-scd none none none / none)'),
        # Test percent ranges
        ('color(--cam02-scd 0% 0% 0%)', 'color(--cam02-scd 0 0 0)'),
        ('color(--cam02-scd 100% 100% 100%)', 'color(--cam02-scd 100 40 40)'),
        ('color(--cam02-scd -100% -100% -100%)', 'color(--cam02-scd -100 -40 -40)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam02-scd'), Color(color2))


class TestCAM02SCDSerialize(util.ColorAssertsPyTest):
    """Test CAM02 SCD serialization."""

    COLORS = [
        # Test color
        ('color(--cam02-scd 75 10 -10 / 0.5)', {}, 'color(--cam02-scd 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam02-scd 75 10 -10)', {'alpha': True}, 'color(--cam02-scd 75 10 -10 / 1)'),
        ('color(--cam02-scd 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam02-scd 75 10 -10)'),
        # Test None
        ('color(--cam02-scd none 10 -10)', {}, 'color(--cam02-scd 0 10 -10)'),
        ('color(--cam02-scd none 10 -10)', {'none': True}, 'color(--cam02-scd none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam02-scd 120 10 -10)', {}, 'color(--cam02-scd 120 10 -10)'),
        ('color(--cam02-scd 120 10 -10)', {'fit': False}, 'color(--cam02-scd 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM02SCDPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM02 SCD."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam02-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam02-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam02-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam02-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestCAM02LCD(util.ColorAssertsPyTest):
    """Test CAM02 LCD."""

    COLORS = [
        ('red', 'color(--cam02-lcd 60.054 56.72 35.659)'),
        ('orange', 'color(--cam02-lcd 79.041 13.11 41.225)'),
        ('yellow', 'color(--cam02-lcd 97.411 -14.122 48.773)'),
        ('green', 'color(--cam02-lcd 46.973 -32.219 30.335)'),
        ('blue', 'color(--cam02-lcd 31.215 -11.767 -54.93)'),
        ('indigo', 'color(--cam02-lcd 23.261 17.131 -32.386)'),
        ('violet', 'color(--cam02-lcd 74.347 32.664 -21.738)'),
        ('white', 'color(--cam02-lcd 100 -1.9557 -1.163)'),
        ('gray', 'color(--cam02-lcd 56.23 -1.2852 -0.76434)'),
        ('black', 'color(--cam02-lcd 0 0 0)'),
        # Test color
        ('color(--cam02-lcd 50 10 -10)', 'color(--cam02-lcd 50 10 -10)'),
        ('color(--cam02-lcd 50 10 -10 / 0.5)', 'color(--cam02-lcd 50 10 -10 / 0.5)'),
        ('color(--cam02-lcd 50% 50% -50% / 50%)', 'color(--cam02-lcd 50 35 -35 / 0.5)'),
        ('color(--cam02-lcd none none none / none)', 'color(--cam02-lcd none none none / none)'),
        # Test percent ranges
        ('color(--cam02-lcd 0% 0% 0%)', 'color(--cam02-lcd 0 0 0)'),
        ('color(--cam02-lcd 100% 100% 100%)', 'color(--cam02-lcd 100 70 70)'),
        ('color(--cam02-lcd -100% -100% -100%)', 'color(--cam02-lcd -100 -70 -70)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam02-lcd'), Color(color2))


class TestCAM02LCDSerialize(util.ColorAssertsPyTest):
    """Test CAM02 LCD serialization."""

    COLORS = [
        # Test color
        ('color(--cam02-lcd 75 10 -10 / 0.5)', {}, 'color(--cam02-lcd 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam02-lcd 75 10 -10)', {'alpha': True}, 'color(--cam02-lcd 75 10 -10 / 1)'),
        ('color(--cam02-lcd 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam02-lcd 75 10 -10)'),
        # Test None
        ('color(--cam02-lcd none 10 -10)', {}, 'color(--cam02-lcd 0 10 -10)'),
        ('color(--cam02-lcd none 10 -10)', {'none': True}, 'color(--cam02-lcd none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam02-lcd 120 10 -10)', {}, 'color(--cam02-lcd 120 10 -10)'),
        ('color(--cam02-lcd 120 10 -10)', {'fit': False}, 'color(--cam02-lcd 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM02LCDPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM02 LCD."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam02-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam02-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam02-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam02-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestSpecialCases(util.ColorAsserts, unittest.TestCase):
    """Test special cases."""

    def test_zero_lightness_high_chroma(self):
        """Test cases of zero lightness and high chroma."""

        c = Color('color(--cam02-ucs 0 20 30)')
        c2 = c.convert('srgb')
        self.assertEqual(c2.in_gamut(tolerance=0), False)
        self.assertColorEqual(c2, Color('rgb(-0.10218 0.13047 -1.0947)'))

    def test_from_negative_lightness(self):
        """Test conversion from negative lightness."""

        self.assertColorEqual(Color('cam02-ucs', [-10, 20, -10]).convert('srgb'), Color('rgb(16.039 -28.194 -2.7708)'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('srgb', [0.000000001] * 3).convert('cam02-ucs').set('j', NaN).is_achromatic(), True)
        self.assertEqual(Color('cam02-ucs', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('cam02-ucs', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('cam02-ucs', [0, 3, -4]).is_achromatic(), False)
        self.assertEqual(Color('cam02-ucs', [NaN, 0, -3]).is_achromatic(), False)
        self.assertEqual(Color('cam02-ucs', [30, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('cam02-ucs', [NaN, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('cam02-ucs', [-12.625, 0.40666, 0.23042]).is_achromatic(), False)
