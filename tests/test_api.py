"""Test miscellaneous API features."""
import unittest
from coloraide import Color, NaN
from coloraide.everything import ColorAll
from . import util
import math


class TestMisc(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous API features."""

    def test_max_precision(self):
        """Test max precision."""

        self.assertEqual(
            Color('purple').convert('lab').to_string(precision=-1),
            'lab(29.6915242415228703976026736199855804443359375 56.11166698871137015203203191049396991729736328125 -36.29266541032566095736910938285291194915771484375)'  # noqa:  E501
        )

    def test_repr(self):
        """Test string representation."""

        self.assertEqual(str(Color('red')), 'color(srgb 1 0 0 / 1)')

    def test_repr_percent(self):
        """Test string percent representation."""

        self.assertEqual(str(Color('white').convert('lab')), 'color(--lab 100 0 0 / 1)')

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

    def test_dict_input(self):
        """Test dictionary inputs."""

        c1 = Color('srgb', [1, 0, 1], 0.5)
        c2 = Color({'space': 'srgb', 'coords': [1, 0, 1], 'alpha': 0.5})
        c3 = Color({'space': 'srgb', 'coords': [1, 0, 1], 'alpha': 0.5})
        self.assertColorEqual(c1, c2)
        self.assertColorEqual(c1, c3)

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

        with self.assertRaises(AttributeError):
            Color("srgb", [1, 0, 0, 0])

    def test_bad_input(self):
        """Test bad input."""

        with self.assertRaises(TypeError):
            Color(3)

    def test_bad_sytnax_input(self):
        """Test bad string syntax input."""

        with self.assertRaises(ValueError):
            Color("nope")

        with self.assertRaises(ValueError):
            Color("nope", [0, 0, 0])

    def test_bad_class(self):
        """Test bad class."""

        c = ColorAll('hunter-lab', [0, 0, 0])
        with self.assertRaises(ValueError):
            Color(c)

    def test_bad_data_input(self):
        """Test bad data input."""

        with self.assertRaises(ValueError):
            Color("srgb")

    def test_missing_values(self):
        """Test missing values."""

        with self.assertRaises(ValueError):
            Color('color(srgb)')

    def test_missing_inputs(self):
        """Test missing inputs."""

        coords = Color("srgb", [])[:-1]
        for c in coords:
            self.assertTrue(math.isnan(c))

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
        c3 = c1.convert('hsl').clone().fit()
        self.assertColorEqual(c2, c3)

    def test_convert_fit_clip(self):
        """Test convert fit."""

        c1 = Color('color(srgb 2 -1 0)')
        self.assertFalse(c1.in_gamut())
        c2 = c1.convert("hsl", fit="clip")
        self.assertTrue(c2.in_gamut())
        c3 = c1.convert('hsl').clone().fit(method="clip")
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

        with self.assertRaises(ValueError):
            c1.get("bad")

    def test_bad_property(self):
        """Test bad property."""

        c1 = Color('orange')

        with self.assertRaises(AttributeError):
            c1.bad

    def test_get_bad_chain(self):
        """Test bad get."""

        c1 = Color('orange')

        with self.assertRaises(ValueError):
            c1.get("hsl.hue.wrong")

    def test_set(self):
        """Test set."""

        c1 = Color('orange')
        c1.set("red", 0.5)
        self.assertEqual(c1.get("red"), 0.5)

    def test_multi_set(self):
        """Test setting multiple channels via set."""

        color = Color('orange')
        color2 = color.clone()
        color2.convert('oklch', in_place=True)
        color2.set('hue', 270).set('lightness', lambda l: l - l * 0.25)
        color2.convert('srgb', in_place=True).set('alpha', 0.5)
        color.set(
            {
                'oklch.lightness': lambda l: l - l * 0.25,
                'alpha': 0.5,
                'oklch.hue': 270
            }
        )

        self.assertColorEqual(color, color2)

    def test_bad_multi_set_dict(self):
        """Test that a dictionary input with a value fails."""

        with self.assertRaises(ValueError):
            Color('red').set({'red': 0}, 0)

    def test_bad_multi_set_string(self):
        """Test that a string input with no value fails."""

        with self.assertRaises(ValueError):
            Color('red').set('red')

    def test_multi_get(self):
        """Test that we can get multiple values."""

        color = Color('orange')
        color.get(['oklch.lightness', 'alpha', 'oklch.hue'])
        oklch = color.convert('oklch')
        self.assertEqual(
            color.get(['oklch.lightness', 'alpha', 'oklch.hue']),
            [oklch['l'], color[-1], oklch['h']]
        )

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

        with self.assertRaises(ValueError):
            c1.set("bad", 0.5)

    def test_set_bad_chain(self):
        """Test bad set."""

        c1 = Color('orange')

        with self.assertRaises(ValueError):
            c1.set("hsl.hue.wrong", 0.5)

    def test_set_bad_input(self):
        """Test bad set."""

        c1 = Color('orange')

        with self.assertRaises(ValueError):
            c1.set("red", "bad")

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

    def test_random_space(self):
        """Test that random colors are generated in the specified space."""

        c = Color.random('srgb')
        self.assertEqual(c.space(), 'srgb')

        c = Color.random('display-p3')
        self.assertEqual(c.space(), 'display-p3')

    def test_random_range(self):
        """Test that random colors are generated within the space's range."""

        for _ in range(10):
            for c in Color.random('srgb'):
                self.assertTrue(0 <= c <= 1)

    def test_random_limits(self):
        """Test random limits."""

        for _ in range(10):
            for i, c in enumerate(Color.random('srgb', limits=[None, (0, 0.5)])):
                if i == 1:
                    self.assertTrue(0 <= c <= 0.5)
                else:
                    self.assertTrue(0 <= c <= 1)
