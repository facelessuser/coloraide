"""Test miscellaneous API features."""
import unittest
from coloraide import Color, NaN
from . import util
import math


class TestMisc(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous API features."""

    def test_color_indexing(self):
        """Test color indexing."""

        c1 = Color('red')
        self.assertEqual(len(c1), 4)
        self.assertEqual(c1[0], 1)
        self.assertEqual(c1[:], [1, 0, 0, 1])
        c1[2] = 1
        self.assertEqual(c1[2], 1)
        c2 = Color('blue')
        c1[:] = c2[:]
        self.assertColorEqual(c1, c2)

    def test_print_none(self):
        """Test printing `none`."""

        self.assertEqual(Color("hsl", [NaN, NaN, 0.3]).to_string(fit=False, none=True), 'hsl(none none 30%)')

    def test_none(self):
        """Test none."""

        c = Color('color(srgb 1 none 1)')
        self.assertEqual(c[:-1:2], [1, 1])
        self.assertTrue(c.is_nan('green'))
        self.assertTrue(Color('color(srgb 1 1 1 / none)').is_nan('alpha'))

    def test_percent_none(self):
        """Test none for percents."""

        c = Color('color(--lch none 0 none)')
        self.assertEqual(c[1], 0)
        self.assertTrue(c.is_nan('l') and c.is_nan('h'))
        c = Color('hsl(30 none none)')
        self.assertEqual(c[0], 30)
        self.assertTrue(c.is_nan('s') and c.is_nan('l'))

    def test_normalize(self):
        """
        Test normalize.

        Should do nothing on a non-hue color.
        """

        self.assertColorEqual(Color('white').normalize(), Color('white'))
        self.assertColorNotEqual(Color('hsl(270 0% 50%)').normalize(), Color('hsl(270 0% 50%)'))

    def test_color_dict(self):
        """Color dictionaries."""

        c1 = Color('red')
        d = c1.to_dict()
        c2 = Color(d)

        self.assertEqual(c1, c2)

    def test_white(self):
        """Test white."""

        self.assertEqual(Color('red').white(), [0.9504559270516716, 1, 1.0890577507598784])

    def test_less_input(self):
        """Test when not enough color channels are provided."""

        with self.assertRaises(ValueError):
            Color('color(srgb 1)')

    def test_less_raw_input(self):
        """Test when not enough color channels are provided via raw input."""

        self.assertEqual(Color("srgb", [1]), Color("srgb", [1, NaN, NaN]))

    def test_too_many_input(self):
        """Test when too many color channels are provided."""

        with self.assertRaises(ValueError):
            Color("color(srgb 1 0 0 0 / 1)")

    def test_too_many_raw_input(self):
        """Test when too many color channels are provided via raw input."""

        self.assertColorEqual(Color("srgb", [1, 0, 0, 0]), Color("srgb", [1, 0, 0]))

    def test_bad_input(self):
        """Test bad input."""

        with self.assertRaises(TypeError):
            Color(3)

    def test_bad_indirect_input(self):
        """Test bad input when it is done indirectly through a method."""

        with self.assertRaises(TypeError):
            Color("red").contrast(3)

    def test_bad_sytnax_input(self):
        """Test bad string syntax input."""

        with self.assertRaises(ValueError):
            Color("nope")

    def test_bad_data_input(self):
        """Test bad data input."""

        with self.assertRaises(ValueError):
            Color("srgb")

    def test_missing_values(self):
        """Test missing values."""

        with self.assertRaises(ValueError):
            Color('color(srgb)')

    def test_filtered_input(self):
        """Test filtered input."""

        self.assertTrue(isinstance(Color("red", filters=['srgb']), Color))
        with self.assertRaises(ValueError):
            Color("hsl(20 100% 50%)", filters=['srgb'])

    def test_filtered_color_syntax_input(self):
        """Test filtered input with color syntax."""

        self.assertTrue(isinstance(Color("red", filters=['srgb']), Color))
        with self.assertRaises(ValueError):
            Color("color(--hsl 20 100% 50%)", filters=['srgb'])

    def test_filtered_color_input(self):
        """Test filtered Color input."""

        self.assertTrue(isinstance(Color(Color("red"), filters=['srgb']), Color))
        with self.assertRaises(ValueError):
            Color(Color("hsl(20 100% 50%)"), filters=['srgb'])

    def test_filtered_raw_input(self):
        """Test filtered raw input."""

        self.assertTrue(isinstance(Color(Color("srgb", [1, 1, 1]), filters=['srgb']), Color))
        with self.assertRaises(ValueError):
            Color(Color("hsl", [20, 100, 50]), filters=['srgb'])

    def test_missing_inputs(self):
        """Test missing inputs."""

        coords = Color("srgb", [])[:-1]
        for c in coords:
            self.assertTrue(math.isnan(c))

    def test_too_many_inputs(self):
        """Test too many inputs."""

        coords = Color("srgb", [0.5, 0.5, 0.5, 0.5])[:-1]
        self.assertEqual(len(coords), 3)
        for c in coords:
            self.assertEqual(c, 0.5)

    def test_new(self):
        """Test new."""

        c1 = Color('purple')
        c2 = c1.new('purple')
        self.assertEqual(c1, c2)

    def test_clone(self):
        """Test clone."""

        c1 = Color('purple')
        c2 = c1.clone()
        self.assertEqual(c1, c2)

    def test_update(self):
        """Test update."""

        c1 = Color('orange')
        c2 = Color('purple')
        self.assertNotEqual(c1, c2)
        c2.update(c1)
        self.assertEqual(c1, c2)

    def test_update_different_space(self):
        """Update from different space."""

        c1 = Color('orange')
        c2 = c1.convert('hsl')
        c3 = Color('purple').convert('hsl')
        self.assertEqual(c2, c3.update(c1))

    def test_update_self(self):
        """Update with self."""

        c1 = Color('orange')
        self.assertEqual(c1.update(c1), c1)

    def test_mutate(self):
        """Test mutate."""

        c1 = Color('orange').convert('lch')
        c2 = Color('orange')
        self.assertNotEqual(c1, c2)
        c2.mutate(c1)
        self.assertEqual(c1, c2)

    def test_convert(self):
        """Test convert."""

        c1 = Color('orange')
        c2 = c1.convert('hsl')
        self.assertColorEqual(c2, Color('hsl(39, 100%, 50%)'), precision=0)

    def test_convert_fit(self):
        """Test convert fit."""

        c1 = Color('color(srgb 2 -1 0)')
        self.assertFalse(c1.in_gamut())
        c2 = c1.convert("hsl", fit=True)
        self.assertTrue(c2.in_gamut())
        c3 = c1.convert('hsl').fit()
        self.assertColorEqual(c2, c3)

    def test_convert_fit_clip(self):
        """Test convert fit."""

        c1 = Color('color(srgb 2 -1 0)')
        self.assertFalse(c1.in_gamut())
        c2 = c1.convert("hsl", fit="clip")
        self.assertTrue(c2.in_gamut())
        c3 = c1.convert('hsl').fit(method="clip")
        self.assertColorEqual(c2, c3)
        c4 = c1.convert("hsl", fit=True)
        self.assertColorNotEqual(c2, c4)

    def test_luminance(self):
        """Test luminance."""

        c1 = Color('orange')
        c2 = c1.convert('xyz-d65')
        self.assertEqual(c1.luminance(), c2.get('y'))

    def test_property(self):
        """Test set."""

        c1 = Color('red')
        self.assertEqual(c1.get('green'), 0)
        c1.set('green', 0.5)
        self.assertEqual(c1.get('green'), 0.5)

    def test_get(self):
        """Test get."""

        c1 = Color('orange')
        self.assertEqual(c1.get("red"), 1.0)

    def test_space_get(self):
        """Test get with another space."""

        c1 = Color('orange')
        self.assertEqual(c1.get("hsl.lightness"), 0.5)

    def test_get_bad(self):
        """Test bad get."""

        c1 = Color('orange')

        with self.assertRaises(AttributeError):
            c1.get("bad")

    def test_bad_property(self):
        """Test bad property."""

        c1 = Color('orange')

        with self.assertRaises(AttributeError):
            c1.bad

    def test_get_bad_chain(self):
        """Test bad get."""

        c1 = Color('orange')

        with self.assertRaises(AttributeError):
            c1.get("hsl.hue.wrong")

    def test_set(self):
        """Test set."""

        c1 = Color('orange')
        c1.set("red", 0.5)
        self.assertEqual(c1.get("red"), 0.5)

    def test_space_set(self):
        """Test set in another space."""

        c1 = Color('orange')
        c1.set("hsl.hue", 270)
        self.assertEqual(c1.get("hsl.hue"), 270)

    def test_function_set(self):
        """Test set with a function."""

        c1 = Color('orange')
        c1.set("red", lambda x: x * 0.3)
        self.assertEqual(c1.get("red"), 0.3)

    def test_set_bad(self):
        """Test bad set."""

        c1 = Color('orange')

        with self.assertRaises(AttributeError):
            c1.set("bad", 0.5)

    def test_set_bad_chain(self):
        """Test bad set."""

        c1 = Color('orange')

        with self.assertRaises(AttributeError):
            c1.set("hsl.hue.wrong", 0.5)

    def test_set_bad_input(self):
        """Test bad set."""

        c1 = Color('orange')

        with self.assertRaises(ValueError):
            c1.set("red", "bad")

    def test_contrast_dict(self):
        """Test contrast with a dictionary mapping."""

        self.assertEqual(
            Color('white').contrast('blue'),
            Color('white').contrast({"space": "srgb", "r": 0, "g": 0, "b": 1})
        )

    def test_contrast_one(self):
        """Test contrast of one."""

        self.assertEqual(Color('blue').contrast('blue'), 1)

    def test_contrast_bigger(self):
        """Test greater contrast."""

        self.assertCompare(Color('white').contrast('blue'), 8.59301)

    def test_repr(self):
        """Test string representation."""

        self.assertEqual(str(Color('red')), 'color(srgb 1 0 0 / 1)')

    def test_repr_percent(self):
        """Test string percent representation."""

        self.assertEqual(str(Color('white').convert('lab')), 'color(--lab 100 0 0 / 1)')

    def test_is_nan_false(self):
        """Test when `is_nan` is false."""

        self.assertFalse(Color('red').convert('hsl').is_nan('hue'))

    def test_is_nan_true(self):
        """Test when `is_nan` is true."""

        self.assertTrue(Color('white').convert('hsl').is_nan('hue'))

    def test_is_nan_false_different_space(self):
        """Test when `is_nan` is false."""

        self.assertFalse(Color('red').is_nan('hsl.hue'))

    def test_is_nan_true_different_space(self):
        """Test when `is_nan` is true."""

        self.assertTrue(Color('white').is_nan('hsl.hue'))

    def test_match(self):
        """Test match."""

        obj = Color.match('red')
        self.assertEqual(obj.color, Color('red'))
        self.assertEqual(obj.start, 0)
        self.assertEqual(obj.end, 3)

    def test_match_no_fullmatch(self):
        """Test match without full match."""

        obj = Color.match('red more text')
        self.assertEqual(obj.color, Color('red'))
        self.assertEqual(obj.start, 0)
        self.assertEqual(obj.end, 3)

    def test_match_fullmatch(self):
        """Test match with full match."""

        self.assertIsNone(Color.match('red more text', fullmatch=True))
        self.assertIsNotNone(Color.match('red', fullmatch=True))

    def test_match_offset(self):
        """Test match with offset."""

        obj = Color.match('yellow green #0000FF rgb(1, 0, 0)', start=7)
        self.assertEqual(obj.color, Color('green'))
        self.assertEqual(obj.start, 7)
        self.assertEqual(obj.end, 12)

        obj = Color.match('yellow green #0000FF rgb(1, 0, 0)', start=13)
        self.assertEqual(obj.color, Color('blue'))
        self.assertEqual(obj.start, 13)
        self.assertEqual(obj.end, 20)

        obj = Color.match('yellow green #0000FF rgb(255, 0, 0)', start=21)
        self.assertEqual(obj.color, Color('red'))
        self.assertEqual(obj.start, 21)
        self.assertEqual(obj.end, 35)

    def test_match_filters(self):
        """Test match with filters."""

        self.assertIsNotNone(Color.match('lab(100% 0 0)'))
        self.assertIsNone(Color.match('lab(100% 0 0)', filters=['srgb']))

    def test_mask_in_place(self):
        """Test masking "in place"."""

        c1 = Color('white')
        c2 = c1.mask('red')
        self.assertNotEqual(c1, c2)
        self.assertIsNot(c1, c2)
        c3 = c1.mask('red', in_place=True)
        self.assertEqual(c1, c3)
        self.assertIs(c1, c3)

    def test_parse_float(self):
        """Test one that we generally handle floats with scientific notation."""

        self.assertColorEqual(Color("color(srgb 3.2e-2 0.1e+1 0.1e1 / 0.5e-)"), Color("color(srgb 0.032 1 1 / 0.5)"))
        self.assertColorEqual(Color("color(srgb +3.2e-2 +0.1e+1 +0.1e1 / 0.5e+)"), Color("color(srgb 0.032 1 1 / 0.5)"))
        self.assertColorEqual(Color("color(srgb 0.032e 1e 1e / 0.5e)"), Color("color(srgb 0.032 1 1 / 0.5)"))
