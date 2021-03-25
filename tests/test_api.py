"""Test API."""
import unittest
from coloraide import Color, NaN
import math


class TestAPI(unittest.TestCase):
    """Test API."""

    def test_bad_input(self):
        """Test bad input."""

        with self.assertRaises(TypeError):
            Color({'dict': True})

    def test_bad_indirect_input(self):
        """Test bad input when it is done indirectly through a method."""

        with self.assertRaises(TypeError):
            Color("red").contrast({'dict': True})

    def test_bad_sytnax_input(self):
        """Test bad string syntax input."""

        with self.assertRaises(ValueError):
            Color("nope")

    def test_bad_data_input(self):
        """Test bad data input."""

        with self.assertRaises(ValueError):
            Color("srgb")

    def test_filtered_input(self):
        """Test filtered input."""

        self.assertTrue(isinstance(Color("red", filters=['srgb']), Color))
        with self.assertRaises(ValueError):
            Color("hsl(20 100% 50%)", filters=['srgb'])

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

        coords = Color("srgb", []).coords()
        for c in coords:
            self.assertTrue(math.isnan(c))

    def test_too_many_inputs(self):
        """Test too many inputs."""

        coords = Color("srgb", [0.5, 0.5, 0.5, 0.5]).coords()
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

    def test_mutate(self):
        """Test mutate."""

        c1 = Color('orange').convert('lch')
        c2 = Color('orange')
        self.assertNotEqual(c1, c2)
        c2.mutate(c1)
        self.assertEqual(c1, c2)

    def test_luminance(self):
        """Test luminance."""

        c1 = Color('orange')
        c2 = c1.convert('xyz')
        self.assertEqual(c1.luminance(), c2.y)

    def test_property(self):
        """Test set."""

        c1 = Color('red')
        self.assertEqual(c1.green, 0)
        c1.green = 0.5
        self.assertEqual(c1.green, 0.5)

    def test_get(self):
        """Test get."""

        c1 = Color('orange')
        self.assertEqual(c1.get("red"), 1.0)

    def test_space_get(self):
        """Test get with another space."""

        c1 = Color('orange')
        self.assertEqual(c1.get("hsl.lightness"), 50.0)

    def test_get_bad(self):
        """Test bad get."""

        c1 = Color('orange')

        with self.assertRaises(ValueError):
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

        with self.assertRaises(ValueError):
            c1.set("hsl.hue.wrong", 0.5)

    def test_overlay(self):
        """Test overlay logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = c1.overlay(c2)
        self.assertTrue(c1 is not c3)
        self.assertEqual(c1.overlay(c2), Color('color(srgb 0.5 0.5 0.5)'))

    def test_overlay_nan_alpha(self):
        """Test overlay logic with alpha as `NaN`."""

        c1 = Color('blue').set('alpha', NaN)
        c2 = Color('yellow')
        c3 = c1.overlay(c2)
        self.assertTrue(c1 is not c3)
        self.assertEqual(c3, Color('color(srgb 1 1 0 / 1)'))

    def test_overlay_in_place(self):
        """Test overlay logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = c1.overlay(c2, in_place=True)
        self.assertTrue(c1 is c3)
        self.assertEqual(c1, Color('color(srgb 0.5 0.5 0.5)'))

    def test_overlay_cyl(self):
        """Test overlay logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertEqual(c1.overlay(c2, space="hsl"), Color('color(srgb 0 1 0.5)'))

    def test_contrast_one(self):
        """Test contrast of one."""

        self.assertEqual(Color('blue').contrast('blue'), 1)

    def test_contrast_bigger(self):
        """Test greater contrast."""

        self.assertEqual(Color('white').contrast('blue'), 9.490930554456146)

    def test_repr(self):
        """Test string representation."""

        self.assertEqual(str(Color('red')), 'color(srgb 1 0 0 / 1)')

    def test_in_gamut(self):
        """Test in gamut check."""

        self.assertTrue(Color('red').in_gamut())

    def test_out_of_gamut(self):
        """Test in gamut check."""

        self.assertFalse(Color('color(srgb 2 0 0)').in_gamut())

    def test_in_gamut_other_space(self):
        """Test if a color is in gamut in a different space."""

        self.assertTrue(Color('red').convert('lch').in_gamut('srgb'))

    def test_fit(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.fit()
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_in_place(self):
        """Test fit in place."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.fit(in_place=True)
        self.assertIs(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_other_space(self):
        """Test fit in other space."""

        color = Color('lab(100% 0 0)')
        self.assertFalse(color.in_gamut('srgb'))
        self.assertTrue(color.fit('srgb').in_gamut('srgb'))

    def test_out_of_gamut_other_space(self):
        """Test if a color is in gamut in a different space."""

        self.assertFalse(Color('color(srgb 2 0 0)').convert('lch').in_gamut('srgb'))

    def test_euclidean_distance_equal(self):
        """Test Euclidean distance that that is equal."""

        self.assertEqual(Color('red').distance('red'), 0)

    def test_euclidean_distance_unequal(self):
        """Test Euclidean distance that is unequal."""

        self.assertEqual(Color('red').distance('blue'), 184.01647404809094)

    def test_euclidean_distance_equal_different_space(self):
        """Test Euclidean distance in sRGB that is equal."""

        self.assertEqual(Color('red').distance('red', space='srgb'), 0)

    def test_euclidean_distance_unequal_different_space(self):
        """Test Euclidean distance in sRGB that is unequal."""

        self.assertEqual(Color('red').distance('blue', space='srgb'), 1.4142135623730951)

    def test_delta_e_76_equal(self):
        """Test delta e 76 equal."""

        self.assertEqual(Color('red').delta_e('red', method="76"), 0)

    def test_delta_e_94_equal(self):
        """Test delta e 94 equal."""

        self.assertEqual(Color('red').delta_e('red', method="94"), 0)

    def test_delta_e_cmc_equal(self):
        """Test delta e CMC equal."""

        self.assertEqual(Color('red').delta_e('red', method="cmc"), 0)

    def test_delta_e_2000_equal(self):
        """Test delta e 2000 equal."""

        self.assertEqual(Color('red').delta_e('red', method="2000"), 0)

    def test_delta_e_76_unequal(self):
        """Test delta e 76 unequal."""

        self.assertEqual(Color('red').delta_e('blue', method="76"), 184.01647404809094)

    def test_delta_e_94_unequal(self):
        """Test delta e 94 unequal."""

        self.assertEqual(Color('red').delta_e('blue', method="94"), 73.82493940241469)

    def test_delta_e_cmc_unequal(self):
        """Test delta e CMC unequal."""

        self.assertEqual(Color('red').delta_e('blue', method="cmc"), 114.22041264760853)

    def test_delta_e_2000_unequal(self):
        """Test delta e 2000 unequal."""

        self.assertEqual(Color('red').delta_e('blue', method="2000"), 55.79505955791144)

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

        obj = Color.match('yellow red', start=7)
        self.assertEqual(obj.color, Color('red'))
        self.assertEqual(obj.start, 7)
        self.assertEqual(obj.end, 10)

    def test_match_filters(self):
        """Test match with filters."""

        self.assertIsNotNone(Color.match('lab(100% 0 0)'))
        self.assertIsNone(Color.match('lab(100% 0 0)', filters=['srgb']))
