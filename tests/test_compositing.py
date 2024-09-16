"""Test compositing."""
import unittest
from coloraide import Color, NaN
from . import util


class TestCompositing(util.ColorAsserts, unittest.TestCase):
    """Test compositing."""

    def test_disable_compose(self):
        """Test that we can disable either blend or alpha compositing."""

        c1 = Color.layer(
            [Color('#07c7ed').set('alpha', 0.5), '#fc3d99'], blend='multiply', operator=False, space="srgb"
        )
        c2 = Color.layer([c1, '#fc3d99'], blend=False, space="srgb")
        self.assertColorEqual(
            Color.layer([Color('#07c7ed').set('alpha', 0.5), '#fc3d99'], blend='multiply', space="srgb"),
            c2
        )
        self.assertColorEqual(
            Color.layer([Color('#07c7ed').set('alpha', 0.5), '#fc3d99'], blend=False, operator=False, space="srgb"),
            Color('#07c7ed').set('alpha', 0.5)
        )

    def test_compose_no_operator(self):
        """Test compose with no operator."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = Color.layer([c1, c2])
        c4 = Color.layer([c1, c2], operator='source-over')
        self.assertEqual(c3, c4)

    def test_compose(self):
        """Test compose logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = Color.layer([c1, c2])
        self.assertTrue(c1 is not c3)
        self.assertEqual(Color.layer([c1, c2]), Color('color(srgb 0.5 0.5 0.5)'))

    def test_compose_dict(self):
        """Test compositing with a mapping."""

        c1 = Color('blue').set('alpha', 0.5)
        self.assertEqual(
            Color.layer([c1, "yellow"]),
            Color.layer([c1, {"space": "srgb", "coords": [1, 1, 0]}])
        )

    def test_compose_blend_multi(self):
        """Test compose blend with multiple colors."""

        self.assertColorEqual(
            Color.layer([Color('#07c7ed'), '#fc3d99', '#f5d311'], blend='multiply', space="srgb"),
            Color('rgb(6.6464 39.39 9.48)')
        )

    def test_compose_alpha_multi(self):
        """Test layer alpha compositing with multiple colors."""

        self.assertColorEqual(
            Color.layer(
                [
                    Color('#07c7ed').set('alpha', 0.5),
                    Color('#fc3d99').set('alpha', 0.5),
                    Color('#f5d311').set('alpha', 0.5),
                    'white'
                ],
                blend='normal',
                space="srgb"
            ),
            Color('rgb(129 173 190.75)')
        )

    def test_compose_only_one(self):
        """Test layer with only one color."""

        self.assertColorEqual(Color.layer(['green']), Color('green'))

    def test_compose_bad_operator(self):
        """Test layer with bad operator."""

        with self.assertRaises(ValueError):
            Color.layer(['red', 'blue'], operator='bad')

    def test_compose_nan(self):
        """Test layer with `NaN` values."""

        self.assertColorEqual(
            Color.layer([Color('srgb', [NaN, 0.75, 0.75], 0.5), Color('srgb', [1, 0.25, 0.25])]),
            Color('rgb(127.5 127.5 127.5)')
        )
        self.assertColorEqual(
            Color.layer([Color('srgb', [NaN, 0.75, 0.75], 0.5), Color('srgb', [NaN, 0.25, 0.25])]),
            Color('rgb(0 127.5 127.5)')
        )
        self.assertColorEqual(
            Color.layer([Color('srgb', [0.2, 0.75, 0.75], 0.5), Color('srgb', [NaN, 0.25, 0.25])]),
            Color('rgb(25.5 127.5 127.5)')
        )

    def test_compose_bad_space(self):
        """Test layer with bad space."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        with self.assertRaises(KeyError):
            Color.layer([c1, c2], space="bad")

    def test_compose_no_alpha(self):
        """Test layer logic when color has no alpha."""

        c1 = Color('blue')
        c2 = Color('yellow')
        c3 = Color.layer([c1, c2])
        self.assertTrue(c1 is not c3)
        self.assertEqual(Color.layer([c1, c2]), c1)

    def test_compose_nan_alpha(self):
        """Test layer logic with alpha as `NaN`."""

        c1 = Color('blue').set('alpha', NaN)
        c2 = Color('yellow')
        c3 = Color.layer([c1, c2])
        self.assertTrue(c1 is not c3)
        self.assertEqual(c3, Color('color(srgb 1 1 0 / 1)'))

    def test_compose_cyl(self):
        """Test layer logic with non-RGB space."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        with self.assertRaises(ValueError):
            Color.layer([c1, c2], space="hsl")
