"""Test contrast."""
import unittest
from coloraide.everything import ColorAll as Color
from . import util


class TestLuminance(util.ColorAsserts, unittest.TestCase):
    """Test luminance cases."""

    def test_luminance(self):
        """Test luminance."""

        c1 = Color('orange')
        c2 = c1.convert('xyz-d65')
        self.assertEqual(c1.luminance(), c2.get('y'))

    def test_luminance_auto(self):
        """Test luminance auto white point."""

        c1 = Color('orange').convert('prophoto-rgb')
        self.assertCompare(c1.luminance(), c1.convert('xyz-d65').get('y'))
        self.assertCompare(c1.luminance(white=None), c1.convert('xyz-d50').get('y'))


class TestContrast(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous API features."""

    def test_bad_indirect_input(self):
        """Test bad input when it is done indirectly through a method."""

        with self.assertRaises(TypeError):
            Color("red").contrast(3)

    def test_contrast_dict(self):
        """Test contrast with a dictionary mapping."""

        self.assertEqual(
            Color('white').contrast('blue'),
            Color('white').contrast({"space": "srgb", "coords": [0, 0, 1]})
        )

    def test_bad_method(self):
        """Test bad contrast method."""

        with self.assertRaises(ValueError):
            Color('white').contrast('blue', method='bad')


class TestContrastWCAG21(util.ColorAsserts, unittest.TestCase):
    """Test WCAG 2.1 contrast ration specifics."""

    def test_contrast_one_wcag21(self):
        """Test contrast of one."""

        self.assertEqual(Color('blue').contrast('blue', method='wcag21'), 1)

    def test_contrast_bigger_wcag21(self):
        """Test greater contrast."""

        self.assertCompare(Color('white').contrast('blue', method='wcag21'), 8.59301)

    def test_symmetry(self):
        """Test symmetry."""

        self.assertEqual(
            Color('white').contrast('blue', method='wcag21'),
            Color('blue').contrast('white', method='wcag21'),
        )


class TestContrastLstar(util.ColorAsserts, unittest.TestCase):
    """Test L* contrast difference."""

    def test_contrast_same(self):
        """Test contrast of to same colors."""

        self.assertEqual(Color('blue').contrast('blue', method='lstar'), 0)

    def test_contrast_bigger(self):
        """Test greater contrast."""

        self.assertCompare(Color('orange').contrast('blue', method='lstar'), 42.63303)

    def test_symmetry(self):
        """Test symmetry."""

        self.assertEqual(
            Color('orange').contrast('blue', method='lstar'),
            Color('blue').contrast('orange', method='lstar')
        )
