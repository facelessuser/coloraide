"""Test Lab library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestLab(util.ColorAssertsPyTest):
    """Test Lab."""

    COLORS = [
        ('red', 'color(--lab 54.291 80.805 69.891)'),
        ('orange', 'color(--lab 75.59 27.516 79.121)'),
        ('yellow', 'color(--lab 97.607 -15.75 93.394)'),
        ('green', 'color(--lab 46.278 -47.552 48.586)'),
        ('blue', 'color(--lab 29.568 68.287 -112.03)'),
        ('indigo', 'color(--lab 19.715 47.029 -54.278)'),
        ('violet', 'color(--lab 69.618 53.295 -36.538)'),
        ('white', 'color(--lab 100 0 0)'),
        ('gray', 'color(--lab 53.585 0 0)'),
        ('black', 'color(--lab 0 0 0)'),
        # Test CSS
        ('lab(100 10 -10)', 'color(--lab 100 10 -10)'),
        ('lab(100 10 -10 / 0.5)', 'color(--lab 100 10 -10 / 0.5)'),
        ('lab(50% 10 -10)', 'color(--lab 50 10 -10)'),
        ('lab(50% 50% -50% / 50%)', 'color(--lab 50 62.5 -62.5 / 0.5)'),
        ('lab(none none none / none)', 'color(--lab none none none / none)'),
        ('lab(1, 10, -10)', None),
        # Test color
        ('color(--lab 100 10 -10)', 'color(--lab 100 10 -10)'),
        ('color(--lab 100 10 -10 / 0.5)', 'color(--lab 100 10 -10 / 0.5)'),
        ('color(--lab 50% 50% -50% / 50%)', 'color(--lab 50 62.5 -62.5 / 0.5)'),
        ('color(--lab none none none / none)', 'color(--lab none none none / none)'),
        # Test percent ranges
        ('color(--lab 0% 0% 0%)', 'color(--lab 0 0 0)'),
        ('color(--lab 100% 100% 100%)', 'color(--lab 100 125 125)'),
        ('color(--lab -100% -100% -100%)', 'color(--lab -100 -125 -125)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('lab'), Color(color2), color=True)


class TestLabSerialize(util.ColorAssertsPyTest):
    """Test Lab serialization."""

    COLORS = [
        # Test hex no options
        ('lab(75 10 -10)', {}, 'lab(75 10 -10)'),
        # Test alpha
        ('lab(75 10 -10 / 0.5)', {}, 'lab(75 10 -10 / 0.5)'),
        ('lab(75 10 -10)', {'alpha': True}, 'lab(75 10 -10 / 1)'),
        ('lab(75 10 -10 / 0.5)', {'alpha': False}, 'lab(75 10 -10)'),
        # Test percent
        ('lab(50 62.5 -62.5)', {'percent': True}, 'lab(50% 50% -50%)'),
        ('lab(50 62.5 -62.5 / 0.5)', {'percent': True, 'alpha': True}, 'lab(50% 50% -50% / 0.5)'),
        # Test None
        ('lab(none 10 -10)', {}, 'lab(0 10 -10)'),
        ('lab(none 10 -10)', {'none': True}, 'lab(none 10 -10)'),
        # Test fit (not bound)
        ('lab(20 130 0)', {}, 'lab(20 130 0)'),
        ('lab(20 130 0)', {'fit': False}, 'lab(20 130 0)'),
        # Test color
        ('lab(none 10 -10 / 0.5)', {'color': True}, 'color(--lab 0 10 -10 / 0.5)'),
        ('lab(none 10 -10)', {'color': True, 'none': True}, 'color(--lab none 10 -10)'),
        ('lab(0 10 -10)', {'color': True, 'alpha': True}, 'color(--lab 0 10 -10 / 1)'),
        ('lab(0 10 -10 / 0.5)', {'color': True, 'alpha': False}, 'color(--lab 0 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestLabProperties(util.ColorAsserts, unittest.TestCase):
    """Test Lab."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['a'], 50)
        c['a'] = 40
        self.assertEqual(c['a'], 40)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['b'], -20)
        c['b'] = -10
        self.assertEqual(c['b'], -10)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
