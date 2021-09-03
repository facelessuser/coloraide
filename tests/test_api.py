"""Test API."""
import unittest
from coloraide import Color, NaN, Piecewise
from . import util
import math
import warnings


class TestAPI(util.ColorAsserts, unittest.TestCase):
    """Test API."""

    def test_missing_percent(self):
        """Test missing percent."""

        self.assertIsNone(Color.match('color(--lab 90 50 -20)'))

    def test_less_input(self):
        """Test when not enough color channels are provided."""

        self.assertColorEqual(Color('color(srgb 1)'), Color('color(srgb 1 0 0)'))

    def test_less_raw_input(self):
        """Test when not enough color channels are provided via raw input."""

        self.assertEqual(Color("srgb", [1]), Color("srgb", [1, NaN, NaN]))

    def test_too_many_input(self):
        """Test when too many color channels are provided."""

        self.assertColorEqual(Color("color(srgb 1 0 0 0 / 1)"), Color("color(srgb 1 0 0 / 1)"))

    def test_too_many_raw_input(self):
        """Test when too many color channels are provided via raw input."""

        self.assertColorEqual(Color("srgb", [1, 0, 0, 0]), Color("srgb", [1, 0, 0]))

    def test_override_precision(self):
        """Test precision override."""

        class Color2(Color):
            """Color."""

            PRECISION = 3

        self.assertEqual(
            Color('color(srgb 0.1234567 0.1234567 0.1234567)').to_string(color=True),
            'color(srgb 0.12346 0.12346 0.12346)'
        )

        self.assertEqual(
            Color2('color(srgb 0.1234567 0.1234567 0.1234567)').to_string(color=True),
            'color(srgb 0.123 0.123 0.123)'
        )

    def test_override_fit(self):
        """Test fit override."""

        class Color2(Color):
            """Color."""

            FIT = "clip"

        self.assertEqual(
            Color('color(srgb 2 -1 0)').fit().to_string(),
            'rgb(255 117.9 100.4)'
        )

        self.assertEqual(
            Color2('color(srgb 2 -1 0)').fit().to_string(),
            'rgb(255 0 0)'
        )

    def test_override_delta_e(self):
        """Test delta e override."""

        class Color2(Color):
            """Color."""

            DELTA_E = "2000"

        self.assertCompare(
            Color('red').delta_e("blue"),
            184.01292
        )

        self.assertCompare(
            Color2('red').delta_e("blue"),
            55.79761
        )

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

    def test_missing_color_percent(self):
        """Test missing color percent."""

        with self.assertRaises(ValueError):
            Color("color(--lab 100 0 0)")

    def test_erroneous_color_percent(self):
        """Test percent in color function that doesn't belong."""

        with self.assertRaises(ValueError):
            Color("color(--lab 100% 0% 0)")

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
            c1.get("bad")

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

        with self.assertRaises(TypeError):
            c1.set("red", "bad")

    def test_blend(self):
        """Test blend logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertEqual(c1.compose(c2, blend='normal'), Color('color(srgb 0.5 0.5 0.5)'))

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
            Color('rgb(127.5 127.5 167.63)')
        )

    def test_blend_different_space_and_output(self):
        """Test blend logic in different space and different output."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertColorEqual(
            c1.compose(c2, blend='normal', space="display-p3", out_space="display-p3"),
            Color('color(display-p3 0.5 0.5 0.64526)')
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

    def test_disable_compose(self):
        """Test that we can disable either blend or alpha compositing."""

        c1 = Color('#07c7ed').set('alpha', 0.5).compose('#fc3d99', blend='multiply', operator=False, space="srgb")
        c2 = c1.compose('#fc3d99', blend=False, space="srgb")
        self.assertColorEqual(
            Color('#07c7ed').set('alpha', 0.5).compose('#fc3d99', blend='multiply', space="srgb"),
            c2
        )
        self.assertColorEqual(
            Color('#07c7ed').set('alpha', 0.5).compose('#fc3d99', blend=False, operator=False, space="srgb"),
            Color('#07c7ed').set('alpha', 0.5)
        )

    def test_compose_is_blend(self):
        """Test compose is the same as blend normal."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = c1.compose(c2)
        c4 = c1.compose(c2, blend='normal')
        self.assertEqual(c3, c4)

    def test_compose(self):
        """Test compose logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = c1.compose(c2)
        self.assertTrue(c1 is not c3)
        self.assertEqual(c1.compose(c2), Color('color(srgb 0.5 0.5 0.5)'))

    def test_compose_blend_multi(self):
        """Test compose blend with multiple colors."""

        self.assertColorEqual(
            Color('#07c7ed').compose(['#fc3d99', '#f5d311'], blend='multiply', space="srgb"),
            Color('rgb(6.6464 39.39 9.48)')
        )

    def test_compose_alpha_multi(self):
        """Test compose alpha compositing with multiple colors."""

        self.assertColorEqual(
            Color('#07c7ed').set('alpha', 0.5).compose(
                [Color('#fc3d99').set('alpha', 0.5), Color('#f5d311').set('alpha', 0.5), 'white'],
                blend='normal',
                space="srgb"
            ),
            Color('rgb(129 173 190.75)')
        )

    def test_compose_empty_list(self):
        """Test compose with empty list."""

        self.assertColorEqual(Color('green').compose([]), Color('green'))

    def test_compose_bad_operator(self):
        """Test compose bad operator."""

        with self.assertRaises(ValueError):
            Color('red').compose('blue', operator='bad')

    def test_compose_nan(self):
        """Test compose with `NaN` values."""

        self.assertColorEqual(
            Color('srgb', [NaN, 0.75, 0.75], 0.5).compose(Color('srgb', [1, 0.25, 0.25])),
            Color('rgb(127.5 127.5 127.5)')
        )
        self.assertColorEqual(
            Color('srgb', [NaN, 0.75, 0.75], 0.5).compose(Color('srgb', [NaN, 0.25, 0.25])),
            Color('rgb(0 127.5 127.5)')
        )
        self.assertColorEqual(
            Color('srgb', [0.2, 0.75, 0.75], 0.5).compose(Color('srgb', [NaN, 0.25, 0.25])),
            Color('rgb(25.5 127.5 127.5)')
        )

    def test_compose_bad_space(self):
        """Test compose logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        with self.assertRaises(ValueError):
            c1.compose(c2, space="bad")

    def test_compose_no_alpha(self):
        """Test compose logic when color has no alpha."""

        c1 = Color('blue')
        c2 = Color('yellow')
        c3 = c1.compose(c2)
        self.assertTrue(c1 is not c3)
        self.assertEqual(c1.compose(c2), c1)

    def test_compose_nan_alpha(self):
        """Test compose logic with alpha as `NaN`."""

        c1 = Color('blue').set('alpha', NaN)
        c2 = Color('yellow')
        c3 = c1.compose(c2)
        self.assertTrue(c1 is not c3)
        self.assertEqual(c3, Color('color(srgb 1 1 0 / 1)'))

    def test_compose_in_place(self):
        """Test compose logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        c3 = c1.compose(c2, in_place=True)
        self.assertTrue(c1 is c3)
        self.assertEqual(c1, Color('color(srgb 0.5 0.5 0.5)'))

    def test_compose_cyl(self):
        """Test compose logic."""

        c1 = Color('blue').set('alpha', 0.5)
        c2 = Color('yellow')
        self.assertEqual(c1.compose(c2, space="hsl"), Color('color(srgb 0 1 0.5)'))

    def test_overlay_no_space(self):
        """Test overlay handling of no space."""

        self.assertColorEqual(
            Color('color(display-p3 0.7 0.3 0.2 / 0.5)').overlay('red'),
            Color('color(display-p3 0.7 0.3 0.2 / 0.5)').overlay('red', space='display-p3')
        )

    def test_deprecated_overlay(self):
        """Test overlay deprecation."""

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            Color('color(srgb 1 0 0 / 1)').overlay('black')

            self.assertTrue(len(w) == 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))

    def test_contrast_one(self):
        """Test contrast of one."""

        self.assertEqual(Color('blue').contrast('blue'), 1)

    def test_contrast_bigger(self):
        """Test greater contrast."""

        self.assertCompare(Color('white').contrast('blue'), 8.59423)

    def test_repr(self):
        """Test string representation."""

        self.assertEqual(str(Color('red')), 'color(srgb 1 0 0 / 1)')

    def test_repr_percent(self):
        """Test string percent representation."""

        self.assertEqual(str(Color('white').convert('lab')), 'color(--lab 100% 0 0 / 1)')

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

    def test_fit_clip(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.fit(method="clip")
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.fit()
        self.assertColorNotEqual(color2, color3)

    def test_bad_fit(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        with self.assertRaises(ValueError):
            color.fit(method="bad")

    def test_fit_in_place(self):
        """Test fit in place."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.fit(in_place=True)
        self.assertIs(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_other_space(self):
        """Test fit in other space."""

        color = Color('hsl(330 110% 50%)')
        self.assertFalse(color.in_gamut('srgb'))
        self.assertTrue(color.fit('srgb').in_gamut('srgb'))

    def test_out_of_gamut_other_space(self):
        """Test if a color is in gamut in a different space."""

        self.assertFalse(Color('color(srgb 2 0 0)').convert('lch').in_gamut('srgb'))

    def test_bad_delta_e(self):
        """Test bad delta e input."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('blue', method='bad')

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

    def test_mix(self):
        """Test interpolation via mixing."""

        self.assertColorEqual(Color('red').mix('blue', 1), Color("rgb(0 0 255)"))
        self.assertColorEqual(Color('red').mix('blue', 0.75), Color("rgb(144.85 -24.871 194.36)"))
        self.assertColorEqual(Color('red').mix('blue'), Color("rgb(192.99 -29.51 136.17)"))
        self.assertColorEqual(Color('red').mix('blue', 0.25), Color("rgb(226.89 -24.311 79.195)"))
        self.assertColorEqual(Color('red').mix('blue', 0.0), Color("rgb(255 0 0)"))

    def test_bad_mix_input(self):
        """Test bad mix input."""

        with self.assertRaises(TypeError):
            Color('red').mix(1)

    def test_mix_input_piecewise(self):
        """Test mix with piecewise."""

        self.assertColorEqual(
            Color('red').mix(Piecewise('blue'), 0.5, space="srgb"), Color("srgb", [0.5, 0, 0.5])
        )

    def test_mix_space(self):
        """Test color mix in different space."""

        self.assertColorEqual(Color('red').mix('blue', 1, space="srgb"), Color("srgb", [0, 0, 1]))
        self.assertColorEqual(Color('red').mix('blue', 0.75, space="srgb"), Color("srgb", [0.25, 0, 0.75]))
        self.assertColorEqual(Color('red').mix('blue', space="srgb"), Color("srgb", [0.5, 0, 0.5]))
        self.assertColorEqual(Color('red').mix('blue', 0.25, space="srgb"), Color("srgb", [0.75, 0, 0.25]))
        self.assertColorEqual(Color('red').mix('blue', 0.0, space="srgb"), Color("srgb", [1, 0, 0]))

    def test_mix_out_space(self):
        """Test interpolation."""

        self.assertColorEqual(
            Color('red').mix('blue', 1, space="lab", out_space="lab"),
            Color("lab(29.568% 68.299 -112.03)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.75, space="lab", out_space="lab"),
            Color("lab(35.749% 71.427 -66.551)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', space="lab", out_space="lab"),
            Color("lab(41.93% 74.556 -21.072)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.25, space="lab", out_space="lab"),
            Color("lab(48.111% 77.684 24.406)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.0, space="lab", out_space="lab"),
            Color("lab(54.292% 80.812 69.885)")
        )

    def test_mix_alpha(self):
        """Test mixing alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').mix('color(srgb 0 0 1 / 0.25)', space="srgb"),
            Color('rgb(127.5 0 127.5 / 0.5)')
        )

    def test_mix_premultiplied_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').mix('color(srgb 0 0 1 / 0.25)', premultiplied=True, space="srgb"),
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_mix_premultiplied_no_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0)').mix('color(srgb 0 0 1)', premultiplied=True, space="srgb"),
            Color('color(srgb 1 0 0)').mix('color(srgb 0 0 1)', space="srgb")
        )

    def test_mix_premultiplied_cylindrical(self):
        """Test premultiplication in a cylindrical space."""

        self.assertColorEqual(
            Color('color(--hsl 20 30% 75% / 0.5)').mix(
                'color(--hsl 20 60% 10% / 0.75)', premultiplied=True, space="hsl"
            ),
            Color('hsl(20 48% 36% / 0.625)')
        )

    def test_mix_in_place(self):
        """Test mix in place."""

        color = Color('red')
        color2 = color.mix('blue', space="srgb")
        self.assertIsNot(color, color2)
        self.assertColorEqual(color2, Color("srgb", [0.5, 0, 0.5]))
        color = Color('red')
        color2 = color.mix('blue', space="srgb", in_place=True)
        self.assertIs(color, color2)
        self.assertColorEqual(color, Color("srgb", [0.5, 0, 0.5]))

    def test_mix_nan(self):
        """Test mixing with NaN."""

        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [0.75, 0, 0])
        self.assertColorEqual(c1.mix(c2, space="srgb"), Color("srgb", [0.75, 0.5, 0.5]))
        c1 = Color("srgb", [0.25, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(c1.mix(c2, space="srgb"), Color("srgb", [0.25, 0.5, 0.5]))
        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(c1.mix(c2, space="srgb"), Color("srgb", [0, 0.5, 0.5]))

    def test_mix_mask(self):
        """Test mix adjust method."""

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(c1.mix(c2.mask("red"), space="srgb"), Color("srgb", [0.25, 0.5, 0.5]))

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(c1.mask("red").mix(c2, space="srgb"), Color("srgb", [0.75, 0.5, 0.5]))

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(c1.mask("red").mix(c2.mask("red"), space="srgb"), Color("srgb", [0.0, 0.5, 0.5]))

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(c1.mix(c2.mask(["red", "green"]), space="srgb"), Color("srgb", [0.25, 1, 0.5]))

    def test_mix_mask_invert(self):
        """Test mix adjust method."""

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            c1.mix(c2.mask(["green", "blue"], invert=True), space="srgb"),
            Color("srgb", [0.25, 0.5, 0.5])
        )

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            c1.mask(["green", "blue"], invert=True).mix(c2, space="srgb"),
            Color("srgb", [0.75, 0.5, 0.5])
        )

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            c1.mask(["green", "blue", "alpha"], invert=True).mix(
                c2.mask(["green", "blue", "alpha"], invert=True),
                space="srgb"
            ),
            Color("srgb", [0.0, 0.5, 0.5])
        )

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            c1.mix(c2.mask("blue", invert=True), space="srgb"),
            Color("srgb", [0.25, 1, 0.5])
        )

    def test_mask_in_place(self):
        """Test masking "in place"."""

        c1 = Color('white')
        c2 = c1.mask('red')
        self.assertNotEqual(c1, c2)
        self.assertIsNot(c1, c2)
        c3 = c1.mask('red', in_place=True)
        self.assertEqual(c1, c3)
        self.assertIs(c1, c3)

    def test_mix_hue_adjust(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="shorter", space="lch"),
            Color("rgb(146.72 -3.9144 106.4)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="longer", space="lch"),
            Color("rgb(-86.816 87.629 170.01)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="increasing", space="lch"),
            Color("rgb(146.72 -3.9144 106.4)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="decreasing", space="lch"),
            Color("rgb(-86.816 87.629 170.01)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="specified", space="lch"),
            Color("rgb(112.82 63.972 -28.829)")
        )

    def test_hue_shorter_cases(self):
        """Cover shorter hue cases."""

        # c2 - c1 > 180
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 350)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="shorter", space="lch"),
            Color("lch(75% 50 375)")
        )

        # c2 - c1 < -180
        c1 = Color('lch(30% 30 350)')
        c2 = Color('lch(75% 50 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="shorter", space="lch"),
            Color("lch(30% 30 375)")
        )

    def test_hue_longer_cases(self):
        """Cover longer hue cases."""

        # 0 < (c2 - c1) < 180
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 60)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="longer", space="lch"),
            Color("lch(75% 50 230)")
        )

        # -180 < (c2 - c1) < 0
        c1 = Color('lch(30% 30 60)')
        c2 = Color('lch(75% 50 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="longer", space="lch"),
            Color("lch(30% 30 230)")
        )

    def test_hue_increasing_cases(self):
        """Cover increasing hue cases."""

        # c2 < c1
        c1 = Color('lch(75% 50 60)')
        c2 = Color('lch(30% 30 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="increasing", space="lch"),
            Color("lch(75% 50 230)")
        )

    def test_hue_decreasing_cases(self):
        """Cover decreasing hue cases."""

        # c1 < c2
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 60)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="decreasing", space="lch"),
            Color("lch(75% 50 230)")
        )

    def test_mix_hue_adjust_bad(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        with self.assertRaises(ValueError):
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="bad", space="lch")

    def test_mix_hue_nan(self):
        """Test mix hue with `NaN`."""

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 25]).mix(Color('hsl', [NaN, 0, 90]), 0.50, space="hsl"),
            Color("hsl(0, 0%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 25]).mix(Color('hsl', [120, 50, 90]), 0.50, space="hsl"),
            Color("hsl(120, 25%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [120, 50, 25]).mix(Color('hsl', [NaN, 0, 90]), 0.50, space="hsl"),
            Color("hsl(120, 25%, 57.5%)")
        )

    def test_mix_progress(self):
        """Test custom progress."""

        progress = lambda x: x * 3  # noqa: E731
        self.assertColorEqual(
            Color('red').mix('blue', 1, out_space="lab", space="lab", progress=progress),
            Color("lab(-19.881% 43.271 -475.86)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.75, out_space="lab", space="lab", progress=progress),
            Color("lab(-1.3376% 52.656 -339.42)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.5, out_space="lab", space="lab", progress=progress),
            Color("lab(17.206% 62.042 -202.99)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.25, out_space="lab", space="lab", progress=progress),
            Color("lab(35.749% 71.427 -66.551)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0, out_space="lab", space="lab", progress=progress),
            Color("lab(54.292% 80.812 69.885)")
        )

    def test_interpolate(self):
        """Test interpolation."""

        self.assertColorEqual(Color('red').interpolate('blue', space="srgb")(1), Color("srgb", [0, 0, 1]))
        self.assertColorEqual(Color('red').interpolate('blue', space="srgb")(0.75), Color("srgb", [0.25, 0, 0.75]))
        self.assertColorEqual(Color('red').interpolate('blue', space="srgb")(0.5), Color("srgb", [0.5, 0, 0.5]))
        self.assertColorEqual(Color('red').interpolate('blue', space="srgb")(0.25), Color("srgb", [0.75, 0, 0.25]))
        self.assertColorEqual(Color('red').interpolate('blue', space="srgb")(0), Color("srgb", [1, 0, 0]))

    def test_interpolate_channel(self):
        """Test interpolating a specific channel differently."""

        self.assertColorEqual(
            Color('red').interpolate(Color('blue').set('alpha', 0), progress={'alpha': lambda t: t ** 3})(0.5),
            Color('rgb(192.99 -29.51 136.17 / 0.875)')
        )

    def test_interpolate_channel_all(self):
        """Test interpolating a specific channel differently, but setting the others via all."""

        self.assertColorEqual(
            Color('red').interpolate(
                Color('blue').set('alpha', 0), progress={
                    'alpha': lambda t: t ** 3,
                    'all': lambda t: 0
                })(0.5),
            Color('rgb(255 0 0 / 0.875)')
        )

    def test_interpolate_input_piecewise(self):
        """Test interpolation with piecewise."""

        self.assertColorEqual(
            Color('red').interpolate(Piecewise('blue'), space="srgb")(0.5), Color("srgb", [0.5, 0, 0.5])
        )

    def test_interpolate_stop(self):
        """Test interpolation with piecewise."""

        self.assertColorEqual(
            Color('red').interpolate('blue', space="srgb", stop=0.6)(0.5), Color('red')
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', space="srgb", stop=0.6)(0.7), Color('rgb(191.25 0 63.75)')
        )

    def test_interpolate_space(self):
        """Test color mix in different space."""

        self.assertColorEqual(Color('red').interpolate('blue', space='lab')(1), Color("rgb(0 0 255)"))
        self.assertColorEqual(Color('red').interpolate('blue', space='lab')(0.75), Color("rgb(144.85 -24.871 194.36)"))
        self.assertColorEqual(Color('red').interpolate('blue', space='lab')(0.5), Color("rgb(192.99 -29.51 136.17)"))
        self.assertColorEqual(Color('red').interpolate('blue', space='lab')(0.25), Color("rgb(226.89 -24.311 79.195)"))
        self.assertColorEqual(Color('red').interpolate('blue', space='lab')(0), Color("rgb(255 0 0)"))

    def test_interpolate_empty_list(self):
        """Test interpolate with empty list."""

        self.assertColorEqual(Color('green').interpolate([])(0.5), Color('green'))

    def test_interpolate_piecewise(self):
        """Test multiple inputs for interpolation."""

        func = Color('white').interpolate(['red', 'black'])
        self.assertColorEqual(func(0), Color('white'))
        self.assertColorEqual(func(0.5), Color('red'))
        self.assertColorEqual(func(1), Color('black'))
        self.assertColorEqual(func(-0.1), Color('rgb(245.78 273.68 281.72)'))
        self.assertColorEqual(func(1.1), Color('rgb(-31.539 -12.727 -3.1327)'))

    def test_interpolate_out_space(self):
        """Test interpolation."""

        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab")(1),
            Color("lab(29.568% 68.299 -112.03)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab")(0.75),
            Color("lab(35.749% 71.427 -66.551)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab")(0.5),
            Color("lab(41.93% 74.556 -21.072)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab")(0.25),
            Color("lab(48.111% 77.684 24.406)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab")(0),
            Color("lab(54.292% 80.812 69.885)")
        )

    def test_interpolate_alpha(self):
        """Test mixing alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').interpolate('color(srgb 0 0 1 / 0.25)', space="srgb")(0.5),
            Color('rgb(127.5 0 127.5 / 0.5)')
        )

    def test_interpolate_premultiplied_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').interpolate(
                'color(srgb 0 0 1 / 0.25)', space="srgb", premultiplied=True
            )(0.5),
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_interpolate_premultiplied_no_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0)').interpolate('color(srgb 0 0 1)', space="srgb", premultiplied=True)(0.5),
            Color('color(srgb 1 0 0)').interpolate('color(srgb 0 0 1)', space="srgb")(0.5)
        )

    def test_interpolate_nan(self):
        """Test mixing with NaN."""

        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [0.75, 0, 0])
        self.assertColorEqual(c1.interpolate(c2, space="srgb")(0.5), Color("srgb", [0.75, 0.5, 0.5]))
        c1 = Color("srgb", [0.25, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(c1.interpolate(c2, space="srgb")(0.5), Color("srgb", [0.25, 0.5, 0.5]))
        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(c1.interpolate(c2, space="srgb")(0.5), Color("srgb", [0, 0.5, 0.5]))

    def test_interpolate_adjust(self):
        """Test mix adjust method."""

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            c1.interpolate(c2.mask("red"), space="srgb")(0.5),
            Color("srgb", [0.25, 0.5, 0.5])
        )

    def test_interpolate_hue_adjust(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        self.assertColorEqual(
            c1.interpolate(c2.mask("hue", invert=True), hue="shorter", space="lch")(0.25),
            Color("rgb(146.72 -3.9144 106.4)")
        )
        self.assertColorEqual(
            c1.interpolate(c2.mask("hue", invert=True), hue="longer", space="lch")(0.25),
            Color("rgb(-86.816 87.629 170.01)")
        )
        self.assertColorEqual(
            c1.interpolate(c2.mask("hue", invert=True), hue="increasing", space="lch")(0.25),
            Color("rgb(146.72 -3.9144 106.4)")
        )
        self.assertColorEqual(
            c1.interpolate(c2.mask("hue", invert=True), hue="decreasing", space="lch")(0.25),
            Color("rgb(-86.816 87.629 170.01)")
        )
        self.assertColorEqual(
            c1.interpolate(c2.mask("hue", invert=True), hue="specified", space="lch")(0.25),
            Color("rgb(112.82 63.972 -28.829)")
        )

    def test_interpolate_progress(self):
        """Test custom progress."""

        progress = lambda x: x * 3  # noqa: E731
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab", progress=progress)(1),
            Color("lab(-19.881% 43.271 -475.86)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab", progress=progress)(0.75),
            Color("lab(-1.3376% 52.656 -339.42)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab", progress=progress)(0.5),
            Color("lab(17.206% 62.042 -202.99)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab", progress=progress)(0.25),
            Color("lab(35.749% 71.427 -66.551)")
        )
        self.assertColorEqual(
            Color('red').interpolate('blue', out_space="lab", space="lab", progress=progress)(0),
            Color("lab(54.292% 80.812 69.885)")
        )

    def test_steps(self):
        """Test steps."""

        colors = Color('red').steps('blue', space="srgb", steps=5)
        self.assertColorEqual(colors[4], Color("srgb", [0, 0, 1]))
        self.assertColorEqual(colors[3], Color("srgb", [0.25, 0, 0.75]))
        self.assertColorEqual(colors[2], Color("srgb", [0.5, 0, 0.5]))
        self.assertColorEqual(colors[1], Color("srgb", [0.75, 0, 0.25]))
        self.assertColorEqual(colors[0], Color("srgb", [1, 0, 0]))

    def test_steps_input_piecewise(self):
        """Test steps with piecewise."""

        self.assertColorEqual(
            Color('red').steps(Piecewise('blue'), space="srgb", steps=5)[2], Color("srgb", [0.5, 0, 0.5])
        )

    def test_steps_multi(self):
        """Test steps with multiple color ranges."""

        colors = Color('white').steps(['red', 'black'], steps=3)
        self.assertColorEqual(colors[0], Color('white'))
        self.assertColorEqual(colors[1], Color('red'))
        self.assertColorEqual(colors[2], Color('black'))

    def test_steps_multi_max_delta_e(self):
        """Test steps with multiple color ranges and max_delta_e."""

        colors = Color('red').steps(['green', 'blue'], space="srgb", max_delta_e=10)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 10)

        colors = Color('red').steps(['green', 'blue'], space="srgb", max_delta_e=3)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 3)

    def test_steps_empty_list(self):
        """Test steps with empty list."""

        self.assertColorEqual(Color('green').steps([], steps=3)[1], Color('green'))

    def test_steps_space(self):
        """Test steps different space."""

        colors = Color('red').steps('blue', space="lab", steps=5)
        self.assertColorEqual(colors[4], Color("rgb(0 0 255)"))
        self.assertColorEqual(colors[3], Color("rgb(144.85 -24.871 194.36)"))
        self.assertColorEqual(colors[2], Color("rgb(192.99 -29.51 136.17)"))
        self.assertColorEqual(colors[1], Color("rgb(226.89 -24.311 79.195)"))
        self.assertColorEqual(colors[0], Color("rgb(255 0 0)"))

    def test_steps_out_space(self):
        """Test steps with output in different space."""

        colors = Color('red').steps('blue', space="srgb", steps=5, out_space="lab")
        self.assertColorEqual(
            colors[4],
            Color("lab(29.568% 68.299 -112.03)")
        )
        self.assertColorEqual(
            colors[3],
            Color("lab(24.637% 57.339 -83.545)")
        )
        self.assertColorEqual(
            colors[2],
            Color("lab(29.563% 55.96 -36.189)")
        )
        self.assertColorEqual(
            colors[1],
            Color("lab(41.112% 66.208 23.413)")
        )
        self.assertColorEqual(
            colors[0],
            Color("lab(54.292% 80.812 69.885)")
        )

    def test_steps_alpha(self):
        """Test mixing alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').steps('color(srgb 0 0 1 / 0.25)', space="srgb", steps=1)[0],
            Color('rgb(127.5 0 127.5 / 0.5)')
        )

    def test_steps_premultiplied_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').steps(
                'color(srgb 0 0 1 / 0.25)', space="srgb", steps=1, premultiplied=True
            )[0],
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_steps_premultiplied_no_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0)').steps('color(srgb 0 0 1)', space="srgb", steps=1, premultiplied=True)[0],
            Color('color(srgb 1 0 0)').steps('color(srgb 0 0 1)', space="srgb", steps=1)[0]
        )

    def test_steps_nan(self):
        """Test steps with NaN."""

        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [0.75, 0, 0])
        self.assertColorEqual(c1.steps(c2, space="srgb", steps=1)[0], Color("srgb", [0.75, 0.5, 0.5]))
        c1 = Color("srgb", [0.25, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(c1.steps(c2, space="srgb", steps=1)[0], Color("srgb", [0.25, 0.5, 0.5]))
        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(c1.steps(c2, space="srgb", steps=1)[0], Color("srgb", [0, 0.5, 0.5]))

    def test_steps_adjust(self):
        """Test steps with adjust method."""

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            c1.steps(c2.mask("red"), space="srgb", steps=1)[0],
            Color("srgb", [0.25, 0.5, 0.5])
        )

    def test_steps_hue_adjust(self):
        """Test steps with hue adjusting."""

        self.assertColorEqual(
            Color('rebeccapurple').steps(
                Color('lch(85% 100 805)').mask("hue", invert=True), space="lch", steps=5, hue="shorter"
            )[1],
            Color("rgb(146.72 -3.9144 106.4)")
        )
        self.assertColorEqual(
            Color('rebeccapurple').steps(
                Color('lch(85% 100 805)').mask("hue", invert=True), space="lch", steps=5, hue="longer"
            )[1],
            Color("rgb(-86.816 87.629 170.01)")
        )
        self.assertColorEqual(
            Color('rebeccapurple').steps(
                Color('lch(85% 100 805)').mask("hue", invert=True), space="lch", steps=5, hue="increasing"
            )[1],
            Color("rgb(146.72 -3.9144 106.4)")
        )
        self.assertColorEqual(
            Color('rebeccapurple').steps(
                Color('lch(85% 100 805)').mask("hue", invert=True), space="lch", steps=5, hue="decreasing"
            )[1],
            Color("rgb(-86.816 87.629 170.01)")
        )
        self.assertColorEqual(
            Color('rebeccapurple').steps(
                Color('lch(85% 100 805)').mask("hue", invert=True), space="lch", steps=5, hue="specified"
            )[1],
            Color("rgb(112.82 63.972 -28.829)")
        )

    def test_steps_progress(self):
        """Test custom progress."""

        progress = lambda x: x * 3  # noqa: E731
        colors = Color('red').steps('blue', steps=5, out_space="lab", space="lab", progress=progress)
        self.assertColorEqual(
            colors[4],
            Color("lab(-19.881% 43.271 -475.86)")
        )
        self.assertColorEqual(
            colors[3],
            Color("lab(-1.3376% 52.656 -339.42)")
        )
        self.assertColorEqual(
            colors[2],
            Color("lab(17.206% 62.042 -202.99)")
        )
        self.assertColorEqual(
            colors[1],
            Color("lab(35.749% 71.427 -66.551)")
        )
        self.assertColorEqual(
            colors[0],
            Color("lab(54.292% 80.812 69.885)")
        )

    def test_steps_max_delta_e(self):
        """Test steps with a max delta e."""

        colors = Color('red').steps('blue', space="srgb", max_delta_e=10)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 10)

        colors = Color('red').steps('blue', space="srgb", max_delta_e=3)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 3)

    def test_steps_max_delta_e_steps(self):
        """Test steps with a max delta e."""

        colors = Color('red').steps('blue', space="srgb", max_delta_e=10)
        self.assertTrue(len(colors) > 5)
        colors = Color('red').steps('blue', space="srgb", max_delta_e=10, max_steps=5)
        self.assertTrue(len(colors) == 5)

    def test_parse_float(self):
        """Test one that we generally handle floats with scientific notation."""

        self.assertColorEqual(Color("color(srgb 3.2e-2 0.1e+1 0.1e1 / 0.5e-)"), Color("color(srgb 0.032 1 1 / 0.5)"))
        self.assertColorEqual(Color("color(srgb +3.2e-2 +0.1e+1 +0.1e1 / 0.5e+)"), Color("color(srgb 0.032 1 1 / 0.5)"))
        self.assertColorEqual(Color("color(srgb 0.032e 1e 1e / 0.5e)"), Color("color(srgb 0.032 1 1 / 0.5)"))
