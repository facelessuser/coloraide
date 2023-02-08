"""Test CAM16 UCS."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestCAM16CAM16UCS(util.ColorAssertsPyTest):
    """Test CAM16 UCS."""

    COLORS = [
        ('red', 'color(--cam16-ucs 59.178 40.82 21.153)'),
        ('orange', 'color(--cam16-ucs 78.364 9.6945 28.629)'),
        ('yellow', 'color(--cam16-ucs 96.802 -12.779 33.037)'),
        ('green', 'color(--cam16-ucs 46.661 -26.746 20.671)'),
        ('blue', 'color(--cam16-ucs 36.252 8.5723 -37.87)'),
        ('indigo', 'color(--cam16-ucs 24.524 19.714 -22.758)'),
        ('violet', 'color(--cam16-ucs 74.738 27.949 -15.247)'),
        ('white', 'color(--cam16-ucs 100 -1.8983 -1.0754)'),
        ('gray', 'color(--cam16-ucs 56.23 -1.2555 -0.71134)'),
        ('black', 'color(--cam16-ucs 0 0 0)'),
        # Test color
        ('color(--cam16-ucs 50 10 -10)', 'color(--cam16-ucs 50 10 -10)'),
        ('color(--cam16-ucs 50 10 -10 / 0.5)', 'color(--cam16-ucs 50 10 -10 / 0.5)'),
        ('color(--cam16-ucs 50% 50% -50% / 50%)', 'color(--cam16-ucs 50 25 -25 / 0.5)'),
        ('color(--cam16-ucs none none none / none)', 'color(--cam16-ucs none none none / none)'),
        # Test percent ranges
        ('color(--cam16-ucs 0% 0% 0%)', 'color(--cam16-ucs 0 0 0)'),
        ('color(--cam16-ucs 100% 100% 100%)', 'color(--cam16-ucs 100 50 50)'),
        ('color(--cam16-ucs -100% -100% -100%)', 'color(--cam16-ucs -100 -50 -50)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam16-ucs'), Color(color2))


class TestCAM16UCSSerialize(util.ColorAssertsPyTest):
    """Test CAM16 UCS serialization."""

    COLORS = [
        # Test color
        ('color(--cam16-ucs 75 10 -10 / 0.5)', {}, 'color(--cam16-ucs 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam16-ucs 75 10 -10)', {'alpha': True}, 'color(--cam16-ucs 75 10 -10 / 1)'),
        ('color(--cam16-ucs 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam16-ucs 75 10 -10)'),
        # Test None
        ('color(--cam16-ucs none 10 -10)', {}, 'color(--cam16-ucs 0 10 -10)'),
        ('color(--cam16-ucs none 10 -10)', {'none': True}, 'color(--cam16-ucs none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam16-ucs 120 10 -10)', {}, 'color(--cam16-ucs 120 10 -10)'),
        ('color(--cam16-ucs 120 10 -10)', {'fit': False}, 'color(--cam16-ucs 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM16UCSPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 UCS."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestCAM16CAM16SCD(util.ColorAssertsPyTest):
    """Test CAM16 SCD."""

    COLORS = [
        ('red', 'color(--cam16-scd 59.178 33.597 17.41)'),
        ('orange', 'color(--cam16-scd 78.364 8.3723 24.725)'),
        ('yellow', 'color(--cam16-scd 96.802 -10.847 28.041)'),
        ('green', 'color(--cam16-scd 46.661 -22.82 17.637)'),
        ('blue', 'color(--cam16-scd 36.252 7.1995 -31.806)'),
        ('indigo', 'color(--cam16-scd 24.524 17.032 -19.663)'),
        ('violet', 'color(--cam16-scd 74.738 24.003 -13.094)'),
        ('white', 'color(--cam16-scd 100 -1.8713 -1.0602)'),
        ('gray', 'color(--cam16-scd 56.23 -1.2436 -0.70457)'),
        ('black', 'color(--cam16-scd 0 0 0)'),
        # Test color
        ('color(--cam16-scd 50 10 -10)', 'color(--cam16-scd 50 10 -10)'),
        ('color(--cam16-scd 50 10 -10 / 0.5)', 'color(--cam16-scd 50 10 -10 / 0.5)'),
        ('color(--cam16-scd 50% 50% -50% / 50%)', 'color(--cam16-scd 50 20 -20 / 0.5)'),
        ('color(--cam16-scd none none none / none)', 'color(--cam16-scd none none none / none)'),
        # Test percent ranges
        ('color(--cam16-scd 0% 0% 0%)', 'color(--cam16-scd 0 0 0)'),
        ('color(--cam16-scd 100% 100% 100%)', 'color(--cam16-scd 100 40 40)'),
        ('color(--cam16-scd -100% -100% -100%)', 'color(--cam16-scd -100 -40 -40)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam16-scd'), Color(color2))


class TestCAM16SCDSerialize(util.ColorAssertsPyTest):
    """Test CAM16 SCD serialization."""

    COLORS = [
        # Test color
        ('color(--cam16-scd 75 10 -10 / 0.5)', {}, 'color(--cam16-scd 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam16-scd 75 10 -10)', {'alpha': True}, 'color(--cam16-scd 75 10 -10 / 1)'),
        ('color(--cam16-scd 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam16-scd 75 10 -10)'),
        # Test None
        ('color(--cam16-scd none 10 -10)', {}, 'color(--cam16-scd 0 10 -10)'),
        ('color(--cam16-scd none 10 -10)', {'none': True}, 'color(--cam16-scd none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam16-scd 120 10 -10)', {}, 'color(--cam16-scd 120 10 -10)'),
        ('color(--cam16-scd 120 10 -10)', {'fit': False}, 'color(--cam16-scd 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM16SCDPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 SCD."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam16-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam16-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam16-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam16-scd 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestCAM16CAM16LCD(util.ColorAssertsPyTest):
    """Test CAM16 LCD."""

    COLORS = [
        ('red', 'color(--cam16-lcd 59.178 59.994 31.089)'),
        ('orange', 'color(--cam16-lcd 78.364 12.557 37.084)'),
        ('yellow', 'color(--cam16-lcd 96.802 -17.273 44.653)'),
        ('green', 'color(--cam16-lcd 46.661 -35.677 27.573)'),
        ('blue', 'color(--cam16-lcd 36.252 11.909 -52.61)'),
        ('indigo', 'color(--cam16-lcd 24.524 25.511 -29.451)'),
        ('violet', 'color(--cam16-lcd 74.738 36.686 -20.013)'),
        ('white', 'color(--cam16-lcd 100 -1.9348 -1.0961)'),
        ('gray', 'color(--cam16-lcd 56.23 -1.2714 -0.72038)'),
        ('black', 'color(--cam16-lcd 0 0 0)'),
        # Test color
        ('color(--cam16-lcd 50 10 -10)', 'color(--cam16-lcd 50 10 -10)'),
        ('color(--cam16-lcd 50 10 -10 / 0.5)', 'color(--cam16-lcd 50 10 -10 / 0.5)'),
        ('color(--cam16-lcd 50% 50% -50% / 50%)', 'color(--cam16-lcd 50 35 -35 / 0.5)'),
        ('color(--cam16-lcd none none none / none)', 'color(--cam16-lcd none none none / none)'),
        # Test percent ranges
        ('color(--cam16-lcd 0% 0% 0%)', 'color(--cam16-lcd 0 0 0)'),
        ('color(--cam16-lcd 100% 100% 100%)', 'color(--cam16-lcd 100 70 70)'),
        ('color(--cam16-lcd -100% -100% -100%)', 'color(--cam16-lcd -100 -70 -70)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam16-lcd'), Color(color2))


class TestCAM16LCDSerialize(util.ColorAssertsPyTest):
    """Test CAM16 LCD serialization."""

    COLORS = [
        # Test color
        ('color(--cam16-lcd 75 10 -10 / 0.5)', {}, 'color(--cam16-lcd 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam16-lcd 75 10 -10)', {'alpha': True}, 'color(--cam16-lcd 75 10 -10 / 1)'),
        ('color(--cam16-lcd 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam16-lcd 75 10 -10)'),
        # Test None
        ('color(--cam16-lcd none 10 -10)', {}, 'color(--cam16-lcd 0 10 -10)'),
        ('color(--cam16-lcd none 10 -10)', {'none': True}, 'color(--cam16-lcd none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam16-lcd 120 10 -10)', {}, 'color(--cam16-lcd 120 10 -10)'),
        ('color(--cam16-lcd 120 10 -10)', {'fit': False}, 'color(--cam16-lcd 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM16LCDPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 LCD."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam16-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam16-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam16-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam16-lcd 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
