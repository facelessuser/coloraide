"""Test Interpolation."""
import unittest
from coloraide.everything import ColorAll as Color
from coloraide import NaN, stop, hint, ease_in
from . import util
import pytest


class TestCarryFoward(util.ColorAssertsPyTest):
    """Test carry forward."""

    CASES = [
        [
            'oklab',
            4,
            ['lch(none 30 270)', 'lab(none -2 12)', 'hsl(30 80 none)', 'oklab(0.5 0.3 -0.1)'],
            ('l', 0.5)
        ],
        [
            'oklab',
            3,
            ['lab(40 none 20)', 'oklab(0.2 none -0.2)', 'oklab(0.5 0.3 -0.1)'],
            ('a', 0.3)
        ],
        [
            'oklab',
            3,
            ['lab(40 20 none)', 'oklab(0.2 0.2 none)', 'oklab(0.5 0.3 -0.1)'],
            ('b', -0.1)
        ],
        [
            'oklch',
            5,
            [
                'lch(40 none 270)', 'hsl(30 none 75)', 'color(--hsv 300 none 0.5)',
                'color(--hsi 90 none 0.2)', 'color(--oklch 0.5 0.2 30)'],
            ('c', 0.2)
        ],
        [
            'hsl',
            5,
            [
                'lch(40 none 270)', 'color(--hsv 300 none 0.5)', 'color(--hsi 90 none 0.2)',
                'color(--oklch 0.5 none 30)', 'hsl(30 30 75)'],
            ('s', 0.3)
        ],
        [
            'hsv',
            5,
            [
                'lch(40 none 270)', 'hsl(30 none 75)', 'color(--hsi 90 none 0.2)',
                'color(--oklch 0.5 none 30)', 'color(--hsv 300 0.3 0.5)'],
            ('s', 0.3)
        ],
        [
            'hsl',
            6,
            [
                'lch(40 10 none)', 'color(--hsv none 0.1 0.5)', 'hwb(none 30 75)',
                'color(--hsi none 0.1 0.2)', 'color(--oklch 0.5 0.1 none)', 'hsl(30 30 75)'],
            ('h', 30)
        ],
        [
            'hwb',
            6,
            [
                'lch(40 10 none)', 'color(--hsv none 0.1 0.5)', 'hsl(none 30 75)',
                'color(--hsi none 0.1 0.2)', 'color(--oklch 0.5 0.1 none)', 'hwb(30 30 75)'],
            ('h', 30)
        ],
        [
            'oklab',
            3,
            [
                'lch(40 10 270 / none)', 'rgb(220 0 47 / none)', 'hsl(30 30 75 / 0.5)',
            ],
            ('alpha', 0.5)
        ],
        [
            'srgb',
            3,
            [
                'color(xyz-d65 0.24 0.34 none)', 'color(display-p3 0 1 none)', 'rgb(30 30 75)'
            ],
            ('blue', 75 / 255)
        ]
    ]

    @pytest.mark.parametrize('space, steps, colors, cmp', CASES)
    def test_round_trip(self, space, steps, colors, cmp):
        """Test round trip."""

        results = Color.steps(colors, steps=steps, space=space, method='monotone', carryforward=True)
        assert all(abs(r[cmp[0]] - cmp[1]) < 1e-12 for r in results), "{} != {} : {}".format(cmp[0], cmp[1], results)


class TestPowerless(util.ColorAsserts, unittest.TestCase):
    """Test powerless."""

    def test_powerless(self):
        """Test powerless."""

        self.assertEqual(
            Color('oklch(0.5 0 30)').mix('oklch(0.75 0.2 120)', space='oklch', powerless=True).to_string(),
            'oklch(0.625 0.1 120)'
        )

        self.assertEqual(
            Color('oklch(0.75 0.2 120)').mix('oklch(0.5 0 30)', space='oklch', powerless=True).to_string(),
            'oklch(0.625 0.1 120)'
        )

    def test_powerless_carryforward(self):
        """Test powerless with carry forward."""

        self.assertEqual(
            Color('oklch(0.5 none 30)').mix(
                'oklch(0.75 0.2 120)',
                space='oklch',
                powerless=True,
                carryforward=True
            ).to_string(),
            'oklch(0.625 0.2 120)'
        )


class TestInterpolation(util.ColorAsserts, unittest.TestCase):
    """Test interpolation."""

    def test_inputs_unmodified(self):
        """Test that interpolation inputs are unmodified."""

        c1 = Color('red')
        c2 = Color('blue')
        _ = Color.interpolate([c1, c2], space='oklab')
        self.assertEqual(c1.to_string(), 'rgb(255 0 0)')
        self.assertEqual(c2.to_string(), 'rgb(0 0 255)')

    def test_out_space_cylindrical(self):
        """Test out space with cylindrical color space."""

        i = Color.interpolate(['transparent', 'hsl(30deg 30% 40%)'], steps=100, space='hsl', out_space='srgb')
        self.assertColorEqual(i(0.5), Color('srgb', [0.52, 0.4, 0.28], 0.5))

    def test_domain(self):
        """Test that domains work."""

        i = Color.interpolate(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            domain=[-32, 32, 60, 85, 95],
        )

        self.assertColorEqual(i(-32), Color('oklab(0.45201 -0.03246 -0.31153)'))
        self.assertColorEqual(i(35), Color('oklab(0.56778 -0.13292 0.11741)'))
        self.assertColorEqual(i(60), Color('oklab(0.96798 -0.07137 0.19857)'))
        self.assertColorEqual(i(79), Color('oklab(0.83476 0.0259 0.17031)'))
        self.assertColorEqual(i(95), Color('oklab(0.62796 0.22486 0.12585)'))

    def test_domain_extrapolation(self):
        """Test extrapolation with custom domain."""

        i = Color.interpolate(['red', 'blue'], extrapolate=True, domain=[-25, 25])
        self.assertColorEqual(i(-30), Color('oklab(0.64555 0.2506 0.16958)'))
        self.assertColorEqual(i(30), Color('oklab(0.43442 -0.05819 -0.35527)'))

    def test_domain_of_one(self):
        """
        Test domain of one.

        This is pointless, but we won't break because of it.
        """

        i = Color.interpolate(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            domain=[1]
        )

        self.assertColorEqual(i(-1), Color('oklab(0.45201 -0.03246 -0.31153)'))
        self.assertColorEqual(i(0), Color('oklab(0.45201 -0.03246 -0.31153)'))
        self.assertColorEqual(i(1), Color('oklab(0.45201 -0.03246 -0.31153)'))
        self.assertColorEqual(i(2), Color('oklab(0.62796 0.22486 0.12585)'))

    def test_domain_in_step(self):
        """Test domains work in steps."""

        steps = Color.steps(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            steps=11,
            domain=[-32, 32, 60, 85, 95]
        )

        self.assertColorEqual(steps[0], Color('oklab(0.45201 -0.03246 -0.31153)'))
        self.assertColorEqual(steps[3], Color('oklab(0.49234 -0.09666 -0.06197)'))
        self.assertColorEqual(steps[5], Color('oklab(0.51922 -0.13946 0.1044)'))
        self.assertColorEqual(steps[7], Color('oklab(0.91836 -0.079 0.18851)'))
        self.assertColorEqual(steps[10], Color('oklab(0.62796 0.22486 0.12585)'))

    def test_domain_mix(self):
        """Test domains in mix."""

        self.assertColorEqual(
            Color('red').mix('blue', 0.75, domain=[0.0, 0.75, 1.0]),
            Color('red').mix('blue', 0.5)
        )

    def test_mix(self):
        """Test interpolation via mixing."""

        self.assertColorEqual(Color('red').mix('blue', 1), Color("color(--oklab 0.45201 -0.03246 -0.31153 / 1)"))
        self.assertColorEqual(Color('red').mix('blue', 0.75), Color("color(--oklab 0.496 0.03187 -0.20218 / 1)"))
        self.assertColorEqual(Color('red').mix('blue'), Color("color(--oklab 0.53998 0.0962 -0.09284 / 1)"))
        self.assertColorEqual(Color('red').mix('blue', 0.25), Color("color(--oklab 0.58397 0.16053 0.0165 / 1)"))
        self.assertColorEqual(Color('red').mix('blue', 0.0), Color("color(--oklab 0.62796 0.22486 0.12585 / 1)"))

    def test_mix_dict(self):
        """Test mixing with a mapping."""

        c1 = Color('blue')
        self.assertEqual(
            c1.mix("yellow"),
            c1.mix({"space": "srgb", "coords": [1, 1, 0]})
        )

    def test_bad_mix_input(self):
        """Test bad mix input."""

        with self.assertRaises(TypeError):
            Color('red').mix(1)

    def test_mix_input_piecewise(self):
        """Test mix with piecewise."""

        with self.assertRaises(TypeError):
            Color('red').mix(stop('blue', 0.0), 0.5, space="srgb")

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
            Color("lab(29.568% 68.287 -112.03)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.75, space="lab", out_space="lab"),
            Color("lab(35.749% 71.417 -66.55)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', space="lab", out_space="lab"),
            Color("lab(41.929% 74.546 -21.069)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.25, space="lab", out_space="lab"),
            Color("lab(48.11% 77.676 24.411)")
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.0, space="lab", out_space="lab"),
            Color("lab(54.291% 80.805 69.891)")
        )

    def test_mix_alpha(self):
        """Test mixing alpha."""

        self.assertColorEqual(
            Color('color(srgb 1 0 0 / 0.75)').mix('color(srgb 0 0 1 / 0.25)', space="srgb"),
            Color('rgb(191.25 0 63.75 / 0.5)')
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

    def test_mix_hue_adjust(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="shorter", space="lch"),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="longer", space="lch"),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="increasing", space="lch"),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="decreasing", space="lch"),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="specified", space="lch"),
            Color("lch(32.393 61.244 432.89)")
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
            Color('hsl', [NaN, 0, 0.25]).mix(Color('hsl', [NaN, 0, 0.9]), 0.50, space="hsl"),
            Color("hsl(0, 0%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 0.25]).mix(Color('hsl', [120, 0.5, 0.9]), 0.50, space="hsl"),
            Color("hsl(120, 25%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [120, 0.5, 0.25]).mix(Color('hsl', [NaN, 0, 0.9]), 0.50, space="hsl"),
            Color("hsl(120, 25%, 57.5%)")
        )

    def test_css_hue_shorter_cases(self):
        """Cover shorter hue cases."""

        # c2 - c1 > 180
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 350)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="shorter", space="lch", method='css-linear'),
            Color("lch(75% 50 375)")
        )

        # c2 - c1 < -180
        c1 = Color('lch(30% 30 350)')
        c2 = Color('lch(75% 50 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="shorter", space="lch", method='css-linear'),
            Color("lch(30% 30 375)")
        )

    def test_css_mix_hue_adjust(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="shorter", space="lch", method='css-linear'),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="longer", space="lch", method='css-linear'),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="increasing", space="lch", method='css-linear'),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="decreasing", space="lch", method='css-linear'),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="specified", space="lch", method='css-linear'),
            Color("lch(32.393 61.244 432.89)")
        )

    def test_css_hue_longer_cases(self):
        """Cover longer hue cases."""

        # 0 < (c2 - c1) < 180
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 60)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="longer", space="lch", method='css-linear'),
            Color("lch(75% 50 230)")
        )

        # -180 < (c2 - c1) < 0
        c1 = Color('lch(30% 30 60)')
        c2 = Color('lch(75% 50 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="longer", space="lch", method='css-linear'),
            Color("lch(30% 30 230)")
        )

    def test_css_hue_increasing_cases(self):
        """Cover increasing hue cases."""

        # c2 < c1
        c1 = Color('lch(75% 50 60)')
        c2 = Color('lch(30% 30 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="increasing", space="lch", method='css-linear'),
            Color("lch(75% 50 230)")
        )

    def test_css_hue_decreasing_cases(self):
        """Cover decreasing hue cases."""

        # c1 < c2
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 60)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="decreasing", space="lch", method='css-linear'),
            Color("lch(75% 50 230)")
        )

    def test_css_mix_hue_adjust_bad(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        with self.assertRaises(ValueError):
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="bad", space="lch", method='css-linear')

    def test_css_mix_hue_nan(self):
        """Test mix hue with `NaN`."""

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 0.25]).mix(Color('hsl', [NaN, 0, 0.9]), 0.50, space="hsl", method='css-linear'),
            Color("hsl(0, 0%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 0.25]).mix(Color('hsl', [120, 0.5, 0.9]), 0.50, space="hsl", method='css-linear'),
            Color("hsl(120, 25%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [120, 0.5, 0.25]).mix(Color('hsl', [NaN, 0, 0.9]), 0.50, space="hsl", method='css-linear'),
            Color("hsl(120, 25%, 57.5%)")
        )

    def test_mix_progress(self):
        """Test custom progress."""

        results = [
            Color('color(--lab 54.291 80.805 69.891 / 1)'),
            Color('color(--lab 51.98 79.635 52.888 / 1)'),
            Color('color(--lab 46.494 76.857 12.521 / 1)'),
            Color('color(--lab 38.917 73.021 -43.239 / 1)'),
            Color('color(--lab 29.568 68.287 -112.03 / 1)')
        ]
        self.assertColorEqual(
            Color('red').mix('blue', 1, out_space="lab", space="lab", progress=ease_in),
            results[4]
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.75, out_space="lab", space="lab", progress=ease_in),
            results[3]
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.5, out_space="lab", space="lab", progress=ease_in),
            results[2]
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0.25, out_space="lab", space="lab", progress=ease_in),
            results[1]
        )
        self.assertColorEqual(
            Color('red').mix('blue', 0, out_space="lab", space="lab", progress=ease_in),
            results[0]
        )

    def test_interpolate(self):
        """Test interpolation."""

        self.assertColorEqual(Color.interpolate(['red', 'blue'], space="srgb")(1), Color("srgb", [0, 0, 1]))
        self.assertColorEqual(Color.interpolate(['red', 'blue'], space="srgb")(0.75), Color("srgb", [0.25, 0, 0.75]))
        self.assertColorEqual(Color.interpolate(['red', 'blue'], space="srgb")(0.5), Color("srgb", [0.5, 0, 0.5]))
        self.assertColorEqual(Color.interpolate(['red', 'blue'], space="srgb")(0.25), Color("srgb", [0.75, 0, 0.25]))
        self.assertColorEqual(Color.interpolate(['red', 'blue'], space="srgb")(0), Color("srgb", [1, 0, 0]))

    def test_interpolate_bspline(self):
        """Test interpolation B-spline."""

        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space="srgb", method="bspline")(1), Color("srgb", [0, 0, 1])
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space="srgb", method="bspline")(0.75), Color("srgb", [0.25, 0, 0.75])
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space="srgb", method="bspline")(0.5), Color("srgb", [0.5, 0, 0.5])
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space="srgb", method="bspline")(0.25), Color("srgb", [0.75, 0, 0.25])
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space="srgb", method="bspline")(0), Color("srgb", [1, 0, 0])
        )

    def test_interpolate_channel(self):
        """Test interpolating a specific channel differently."""

        self.assertColorEqual(
            Color.interpolate(['red', Color('blue').set('alpha', 0)], progress={'alpha': lambda t: t ** 3})(0.5),
            Color('oklab(0.35883 0.12849 0.07191 / 0.875)')
        )

    def test_interpolate_channel_bspline(self):
        """Test interpolating a specific channel differently."""

        self.assertColorEqual(
            Color.interpolate(
                ['red', Color('blue').set('alpha', 0)], progress={'alpha': lambda t: t ** 3}, method='bspline'
            )(0.5),
            Color('oklab(0.35883 0.12849 0.07191 / 0.875)')
        )

    def test_interpolate_easing_inline(self):
        """Test interpolating a specific channel differently."""

        self.assertColorEqual(
            Color.interpolate(['red', lambda t: t ** 3, 'blue'])(0.5),
            Color('oklab(0.60596 0.1927 0.07117)')
        )

    def test_interpolate_color_hint(self):
        """Test interpolating with color hints."""

        self.assertColorEqual(
            Color.interpolate(['red', hint(0.75), 'blue'])(0.5),
            Color('oklab(0.59484 0.17643 0.04352)')
        )

    def test_interpolate_channel_all(self):
        """Test interpolating a specific channel differently, but setting the others via all."""

        self.assertColorEqual(
            Color.interpolate(
                ['red', Color('blue').set('alpha', 0)],
                progress={
                    'alpha': lambda t: t ** 3,
                    'all': lambda t: 0,
                },
                space='srgb'
            )(0.5),
            Color('rgb(291.43 0 0 / 0.875)')
        )

    def test_interpolate_channel_aliases(self):
        """Test interpolating a specific channel using a color's channel alias."""

        self.assertColorEqual(
            Color.interpolate(
                ['orange', Color('purple')],
                progress={
                    'red': lambda t: t ** 3
                },
                space='srgb'
            )(0.5),
            Color('rgb(191.5 82.5 64)')
        )

    def test_interpolate_input_piecewise(self):
        """Test interpolation with piecewise."""

        self.assertColorEqual(
            Color.interpolate(['red', stop('blue', 0.5)], space="srgb")(0.5), Color("srgb", [0, 0, 1])
        )

    def test_interpolate_input_bspline(self):
        """Test interpolation with piecewise."""

        self.assertColorEqual(
            Color.interpolate(['red', stop('blue', 0.5)], space="srgb", method='bspline')(0.5),
            Color("srgb", [0, 0, 1])
        )

    def test_interpolate_stop(self):
        """Test interpolation with piecewise."""

        self.assertColorEqual(
            Color.interpolate([stop('red', 0.6), 'blue'], space="srgb")(0.5), Color('red')
        )
        self.assertColorEqual(
            Color.interpolate([stop('red', 0.6), 'blue'], space="srgb")(0.7), Color('rgb(191.25 0 63.75)')
        )

    def test_interpolate_stop_bspline(self):
        """Test interpolation with piecewise."""

        self.assertColorEqual(
            Color.interpolate([stop('red', 0.6), 'blue'], space="srgb", method='bspline')(0.5), Color('red')
        )

    def test_interpolate_space(self):
        """Test color mix in different space."""

        self.assertColorEqual(Color.interpolate(['red', 'blue'], space='lab')(1), Color("lab(29.568 68.287 -112.03)"))
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space='lab')(0.75), Color("lab(35.749 71.417 -66.55)")
        )
        self.assertColorEqual(Color.interpolate(['red', 'blue'], space='lab')(0.5), Color("lab(41.929 74.546 -21.069)"))
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], space='lab')(0.25), Color("lab(48.11 77.676 24.411)")
        )
        self.assertColorEqual(Color.interpolate(['red', 'blue'], space='lab')(0), Color("lab(54.291 80.805 69.891)"))

    def test_interpolate_empty_list(self):
        """Test interpolate with empty list."""

        with self.assertRaises(IndexError):
            Color('green').interpolate([])(0.5)

    def test_interpolate_piecewise(self):
        """Test multiple inputs for interpolation."""

        func = Color.interpolate(['white', 'red', 'black'])
        self.assertColorEqual(func(0), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.81398 0.11243 0.06292 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0.62796 0.22486 0.12585 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.31398 0.11243 0.06292 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0 0 0 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0 0 0 / 1)'))

    def test_interpolate_multi_bspline(self):
        """Test multiple inputs for B-spline interpolation."""

        func = Color.interpolate(['white', 'red', 'black'], method='bspline')
        self.assertColorEqual(func(0), Color('oklab(1 0 0)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.80865 0.10306 0.05768 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0.5853 0.14991 0.0839 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.30865 0.10306 0.05768 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0 0 0 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0 0 0 / 1)'))

    def test_interpolate_multi_natural(self):
        """Test multiple inputs for Natural B-spline interpolation."""

        func = Color.interpolate(['white', 'red', 'black'], method='natural')
        self.assertColorEqual(func(0), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.83797 0.15459 0.08652 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0.62796 0.22486 0.12585 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.33797 0.15459 0.08652 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0 0 0 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0 0 0 / 1)'))

    def test_interpolate_multi_natural_more(self):
        """Test more inputs for Natural B-spline interpolation."""

        func = Color.interpolate(['white', 'red', 'black', 'purple'], method='natural')
        self.assertColorEqual(func(0), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.7663 0.21652 0.11694 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0.25451 0.11694 0.07997 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.00785 -0.00275 -0.03301 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0.42091 0.1647 -0.10147 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0.42091 0.1647 -0.10147 / 1)'))

    def test_interpolate_multi_natural_even_more(self):
        """Test even more inputs for Natural B-spline interpolation."""

        func = Color.interpolate(['white', 'red', 'black', 'purple', 'green'], method='natural')
        self.assertColorEqual(func(0), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.62796 0.22486 0.12585 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0 0 0 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.42091 0.1647 -0.10147 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0.51975 -0.1403 0.10768 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0.51975 -0.1403 0.10768 / 1)'))

    def test_interpolate_multi_catmull_rom(self):
        """Test multiple inputs for Catmull-Rom spline interpolation."""

        func = Color.interpolate(['white', 'red', 'black'], method='catrom')
        self.assertColorEqual(func(0), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.82997 0.14054 0.07865 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0.62796 0.22486 0.12585 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.32997 0.14054 0.07865 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0 0 0 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0 0 0 / 1)'))

    def test_interpolate_multi_monotone(self):
        """Test multiple inputs for monotone interpolation."""

        func = Color.interpolate(['white', 'red', 'black'], method='monotone')
        self.assertColorEqual(func(0), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(0.25), Color('color(--oklab 0.82997 0.14054 0.07865 / 1)'))
        self.assertColorEqual(func(0.5), Color('color(--oklab 0.62796 0.22486 0.12585 / 1)'))
        self.assertColorEqual(func(0.75), Color('color(--oklab 0.32997 0.14054 0.07865 / 1)'))
        self.assertColorEqual(func(1), Color('color(--oklab 0 0 0 / 1)'))
        self.assertColorEqual(func(-0.1), Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(func(1.1), Color('color(--oklab 0 0 0 / 1)'))

    def test_interpolate_out_space(self):
        """Test interpolation."""

        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab")(1),
            Color("lab(29.568% 68.287 -112.03)")
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab")(0.75),
            Color("lab(35.749% 71.417 -66.55)")
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab")(0.5),
            Color("lab(41.929% 74.546 -21.069)")
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab")(0.25),
            Color("lab(48.11% 77.676 24.411)")
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab")(0),
            Color("lab(54.291% 80.805 69.891)")
        )

    def test_interpolate_alpha(self):
        """Test mixing alpha."""

        self.assertColorEqual(
            Color.interpolate(['color(srgb 1 0 0 / 0.75)', 'color(srgb 0 0 1 / 0.25)'], space="srgb")(0.5),
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_interpolate_premultiplied_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color.interpolate(
                ['color(srgb 1 0 0 / 0.75)', 'color(srgb 0 0 1 / 0.25)'], space="srgb", premultiplied=True
            )(0.5),
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_interpolate_premultiplied_alpha_none(self):
        """Test premultiplied alpha when alphas are none."""

        self.assertColorEqual(
            Color.interpolate(
                ['color(srgb 0 0 0 / none)', 'color(srgb 0 1 0 / none)'], space="srgb", premultiplied=True
            )(0.5),
            Color('rgb(0 127.5 0 / 0)')
        )

    def test_interpolate_premultiplied_no_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color.interpolate(['color(srgb 1 0 0)', 'color(srgb 0 0 1)'], space="srgb", premultiplied=True)(0.5),
            Color.interpolate(['color(srgb 1 0 0)', 'color(srgb 0 0 1)'], space="srgb")(0.5)
        )

    def test_interpolate_nan(self):
        """Test mixing with NaN."""

        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [0.75, 0, 0])
        self.assertColorEqual(Color.interpolate([c1, c2], space="srgb")(0.5), Color("srgb", [0.75, 0.5, 0.5]))
        c1 = Color("srgb", [0.25, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(Color.interpolate([c1, c2], space="srgb")(0.5), Color("srgb", [0.25, 0.5, 0.5]))
        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(Color.interpolate([c1, c2], space="srgb")(0.5), Color("srgb", [0, 0.5, 0.5]))

    def test_interpolate_adjust(self):
        """Test mix adjust method."""

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            Color.interpolate([c1, c2.mask("red")], space="srgb")(0.5),
            Color("srgb", [0.25, 0.5, 0.5])
        )

    def test_interpolate_hue_adjust(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        self.assertColorEqual(
            Color.interpolate([c1, c2.mask("hue", invert=True)], hue="shorter", space="lch")(0.25),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            Color.interpolate([c1, c2.mask("hue", invert=True)], hue="longer", space="lch")(0.25),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            Color.interpolate([c1, c2.mask("hue", invert=True)], hue="increasing", space="lch")(0.25),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            Color.interpolate([c1, c2.mask("hue", invert=True)], hue="decreasing", space="lch")(0.25),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            Color.interpolate([c1, c2.mask("hue", invert=True)], hue="specified", space="lch")(0.25),
            Color("lch(32.393 61.244 432.89)")
        )

    def test_interpolate_progress(self):
        """Test custom progress."""

        results = [
            Color('color(--lab 54.291 80.805 69.891 / 1)'),
            Color('color(--lab 51.98 79.635 52.888 / 1)'),
            Color('color(--lab 46.494 76.857 12.521 / 1)'),
            Color('color(--lab 38.917 73.021 -43.239 / 1)'),
            Color('color(--lab 29.568 68.287 -112.03 / 1)')
        ]
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab", progress=ease_in)(1),
            results[4]
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab", progress=ease_in)(0.75),
            results[3]
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab", progress=ease_in)(0.5),
            results[2]
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab", progress=ease_in)(0.25),
            results[1]
        )
        self.assertColorEqual(
            Color.interpolate(['red', 'blue'], out_space="lab", space="lab", progress=ease_in)(0),
            results[0]
        )

    def test_steps(self):
        """Test steps."""

        colors = Color.steps(['red', 'blue'], space="srgb", steps=5)
        self.assertColorEqual(colors[4], Color("srgb", [0, 0, 1]))
        self.assertColorEqual(colors[3], Color("srgb", [0.25, 0, 0.75]))
        self.assertColorEqual(colors[2], Color("srgb", [0.5, 0, 0.5]))
        self.assertColorEqual(colors[1], Color("srgb", [0.75, 0, 0.25]))
        self.assertColorEqual(colors[0], Color("srgb", [1, 0, 0]))

    def test_steps_input_piecewise(self):
        """Test steps with piecewise."""

        self.assertColorEqual(
            Color.steps(['red', stop('blue', 0.5)], space="srgb", steps=5)[2], Color("srgb", [0, 0, 1])
        )

    def test_steps_input_bspline(self):
        """Test steps with B-spline."""

        self.assertColorEqual(
            Color.steps(['red', stop('blue', 0.5)], space="srgb", steps=5, method='bspline')[2],
            Color("srgb", [0, 0, 1])
        )

    def test_steps_multi(self):
        """Test steps with multiple color ranges."""

        colors = Color('white').steps(['white', 'red', 'black'], steps=3)
        self.assertColorEqual(colors[0], Color('color(--oklab 1 0 0 / 1)'))
        self.assertColorEqual(colors[1], Color('oklab(0.62796 0.22486 0.12585)'))
        self.assertColorEqual(colors[2], Color('color(--oklab 0 0 0 / 1)'))

    def test_steps_multi_max_delta_e(self):
        """Test steps with multiple color ranges and max_delta_e."""

        colors = Color.steps(['red', 'green', 'blue'], space="srgb", max_delta_e=10)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 10)

        colors = Color.steps(['red', 'green', 'blue'], space="srgb", max_delta_e=3)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 3)

    def test_steps_custom_delta_e(self):
        """Test a custom delta E input."""

        colors = Color.steps(['red', 'green', 'blue'], space="srgb", max_delta_e=10, delta_e='2000')
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1], method='2000') <= 10)

        colors = Color.steps(['red', 'green', 'blue'], space="srgb", max_delta_e=3, delta_e='2000')
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1], method='2000') <= 3)

    def test_steps_custom_delta_compare(self):
        """Test a custom delta E input."""

        colors1 = len(Color.steps(['orange', 'red'], space="srgb", max_delta_e=0.2, delta_e='76'))
        colors2 = len(Color.steps(['orange', 'red'], space="srgb", max_delta_e=0.2, delta_e='ok'))

        self.assertNotEqual(colors1, colors2)

    def test_steps_empty_list(self):
        """Test steps with empty list."""

        with self.assertRaises(IndexError):
            Color.steps([], steps=3)

    def test_steps_space(self):
        """Test steps different space."""

        colors = Color.steps(['red', 'blue'], space="lab", steps=5)
        self.assertColorEqual(colors[4], Color("lab(29.568 68.287 -112.03)"))
        self.assertColorEqual(colors[3], Color("lab(35.749 71.417 -66.55)"))
        self.assertColorEqual(colors[2], Color("lab(41.929 74.546 -21.069)"))
        self.assertColorEqual(colors[1], Color("lab(48.11 77.676 24.411)"))
        self.assertColorEqual(colors[0], Color("lab(54.291 80.805 69.891)"))

    def test_steps_out_space(self):
        """Test steps with output in different space."""

        colors = Color.steps(['red', 'blue'], space="srgb", steps=5, out_space="lab")
        self.assertColorEqual(
            colors[4],
            Color("lab(29.568% 68.287 -112.03)")
        )
        self.assertColorEqual(
            colors[3],
            Color("lab(24.638% 57.331 -83.546)")
        )
        self.assertColorEqual(
            colors[2],
            Color("lab(29.563% 55.954 -36.19)")
        )
        self.assertColorEqual(
            colors[1],
            Color("lab(41.111% 66.202 23.413)")
        )
        self.assertColorEqual(
            colors[0],
            Color("lab(54.291% 80.805 69.891)")
        )

    def test_steps_alpha(self):
        """Test mixing alpha."""

        self.assertColorEqual(
            Color.steps(['color(srgb 1 0 0 / 0.75)', 'color(srgb 0 0 1 / 0.25)'], space="srgb", steps=1)[0],
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_steps_premultiplied_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color.steps(
                ['color(srgb 1 0 0 / 0.75)', 'color(srgb 0 0 1 / 0.25)'], space="srgb", steps=1, premultiplied=True
            )[0],
            Color('rgb(191.25 0 63.75 / 0.5)')
        )

    def test_steps_premultiplied_no_alpha(self):
        """Test premultiplied alpha."""

        self.assertColorEqual(
            Color.steps(['color(srgb 1 0 0)', 'color(srgb 0 0 1)'], space="srgb", steps=1, premultiplied=True)[0],
            Color.steps(['color(srgb 1 0 0)', 'color(srgb 0 0 1)'], space="srgb", steps=1)[0]
        )

    def test_steps_nan(self):
        """Test steps with NaN."""

        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [0.75, 0, 0])
        self.assertColorEqual(Color.steps([c1, c2], space="srgb", steps=1)[0], Color("srgb", [0.75, 0.5, 0.5]))
        c1 = Color("srgb", [0.25, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(Color.steps([c1, c2], space="srgb", steps=1)[0], Color("srgb", [0.25, 0.5, 0.5]))
        c1 = Color("srgb", [NaN, 1, 1])
        c2 = Color("srgb", [NaN, 0, 0])
        self.assertColorEqual(Color.steps([c1, c2], space="srgb", steps=1)[0], Color("srgb", [0, 0.5, 0.5]))

    def test_steps_adjust(self):
        """Test steps with adjust method."""

        c1 = Color("color(srgb 0.25 1 1)")
        c2 = Color("color(srgb 0.75 0 0)")
        self.assertColorEqual(
            Color.steps([c1, c2.mask("red")], space="srgb", steps=1)[0],
            Color("srgb", [0.25, 0.5, 0.5])
        )

    def test_steps_hue_adjust(self):
        """Test steps with hue adjusting."""

        self.assertColorEqual(
            Color.steps(
                ['rebeccapurple', Color('lch(85% 100 805)').mask("hue", invert=True)],
                space="lch",
                steps=5,
                hue="shorter"
            )[1],
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            Color.steps(
                ['rebeccapurple', Color('lch(85% 100 805)').mask("hue", invert=True)],
                space="lch",
                steps=5,
                hue="longer"
            )[1],
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            Color.steps(
                ['rebeccapurple', Color('lch(85% 100 805)').mask("hue", invert=True)],
                space="lch",
                steps=5,
                hue="increasing"
            )[1],
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            Color.steps(
                ['rebeccapurple', Color('lch(85% 100 805)').mask("hue", invert=True)],
                space="lch",
                steps=5,
                hue="decreasing"
            )[1],
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            Color.steps(
                ['rebeccapurple', Color('lch(85% 100 805)').mask("hue", invert=True)],
                space="lch",
                steps=5,
                hue="specified"
            )[1],
            Color("lch(32.393 61.244 432.89)")
        )

    def test_steps_progress(self):
        """Test custom progress."""

        results = [
            Color('color(--lab 54.291 80.805 69.891 / 1)'),
            Color('color(--lab 51.98 79.635 52.888 / 1)'),
            Color('color(--lab 46.494 76.857 12.521 / 1)'),
            Color('color(--lab 38.917 73.021 -43.239 / 1)'),
            Color('color(--lab 29.568 68.287 -112.03 / 1)')
        ]
        colors = Color.steps(['red', 'blue'], steps=5, out_space="lab", space="lab", progress=ease_in)
        self.assertColorEqual(
            colors[4],
            results[4]
        )
        self.assertColorEqual(
            colors[3],
            results[3]
        )
        self.assertColorEqual(
            colors[2],
            results[2]
        )
        self.assertColorEqual(
            colors[1],
            results[1]
        )
        self.assertColorEqual(
            colors[0],
            results[0]
        )

    def test_steps_max_delta_e(self):
        """Test steps with a max delta e."""

        colors = Color.steps(['red', 'blue'], space="srgb", max_delta_e=10)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 10)

        colors = Color.steps(['red', 'blue'], space="srgb", max_delta_e=3)
        for index, color in enumerate(colors, 0):
            if not index:
                continue
            self.assertTrue(color.delta_e(colors[index - 1]) <= 3)

    def test_max_delta_min_step_less_than_two(self):
        """Test that when a minimum step less than 2 is given that `max_delta_e` won't break."""

        colors = Color.steps(['lightblue', 'blue'], space="srgb", steps=1, max_delta_e=10)
        self.assertTrue(len(colors) > 2)

    def test_steps_max_delta_e_steps(self):
        """Test steps with a max delta e."""

        colors = Color.steps(['red', 'blue'], space="srgb", max_delta_e=10)
        self.assertTrue(len(colors) > 5)
        colors = Color.steps(['red', 'blue'], space="srgb", max_delta_e=10, max_steps=5)
        self.assertTrue(len(colors) == 5)

    def test_too_few_colors_linear(self):
        """Test too few colors during linear interpolation."""

        with self.assertRaises(ValueError):
            Color.interpolate(['green', lambda t: t * 3])

    def test_continuos_hue_shorter_cases(self):
        """Cover shorter hue cases."""

        # c2 - c1 > 180
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 350)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="shorter", space="lch", method='continuous'),
            Color("lch(75% 50 15)")
        )

        # c2 - c1 < -180
        c1 = Color('lch(30% 30 350)')
        c2 = Color('lch(75% 50 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="shorter", space="lch", method='continuous'),
            Color("lch(30% 30 375)")
        )

    def test_continuos_mix_hue_adjust(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="shorter", space="lch", method='continuous'),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="longer", space="lch", method='continuous'),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="increasing", space="lch", method='continuous'),
            Color("lch(32.393 61.244 342.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="decreasing", space="lch", method='continuous'),
            Color("lch(32.393 61.244 252.89)")
        )
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="specified", space="lch", method='continuous'),
            Color("lch(32.393 61.244 432.89)")
        )

    def test_continuos_hue_longer_cases(self):
        """Cover longer hue cases."""

        # 0 < (c2 - c1) < 180
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 60)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="longer", space="lch", method='continuous'),
            Color("lch(75% 50 -130)")
        )

        # -180 < (c2 - c1) < 0
        c1 = Color('lch(30% 30 60)')
        c2 = Color('lch(75% 50 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="longer", space="lch", method='continuous'),
            Color("lch(30% 30 230)")
        )

    def test_continuos_hue_increasing_cases(self):
        """Cover increasing hue cases."""

        # c2 < c1
        c1 = Color('lch(75% 50 60)')
        c2 = Color('lch(30% 30 40)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="increasing", space="lch", method='continuous'),
            Color("lch(75% 50 230)")
        )

    def test_continuos_hue_decreasing_cases(self):
        """Cover decreasing hue cases."""

        # c1 < c2
        c1 = Color('lch(75% 50 40)')
        c2 = Color('lch(30% 30 60)')
        self.assertColorEqual(
            c1.mix(c2.mask("hue", invert=True), 0.50, hue="decreasing", space="lch", method='continuous'),
            Color("lch(75% 50 -130)")
        )

    def test_continuos_mix_hue_adjust_bad(self):
        """Test hue adjusting."""

        c1 = Color('rebeccapurple')
        c2 = Color('lch(85% 100 805)')
        with self.assertRaises(ValueError):
            c1.mix(c2.mask("hue", invert=True), 0.25, hue="bad", space="lch", method='continuous')

    def test_continuos_mix_hue_nan(self):
        """Test mix hue with `NaN`."""

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 0.25]).mix(Color('hsl', [NaN, 0, 0.9]), 0.50, space="hsl", method='continuous'),
            Color("hsl(0, 0%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [NaN, 0, 0.25]).mix(Color('hsl', [120, 0.5, 0.9]), 0.50, space="hsl", method='continuous'),
            Color("hsl(120, 25%, 57.5%)")
        )

        self.assertColorEqual(
            Color('hsl', [120, 0.5, 0.25]).mix(Color('hsl', [NaN, 0, 0.9]), 0.50, space="hsl", method='continuous'),
            Color("hsl(120, 25%, 57.5%)")
        )

    def test_continuous_undefined_middle(self):
        """Test continuous with undefined middle."""

        colors = [
            Color('oklab', [0, 0, 0]),
            Color('oklab', [NaN, -0.03246, -0.31153]),
            Color('oklab', [1, 0, 0])
        ]
        i = Color.interpolate(colors, space='oklab', method='continuous')
        self.assertColorEqual(
            i(0),
            Color("oklab(0 0 0)")
        )
        self.assertColorEqual(
            i(0.25),
            Color("oklab(0.25 -0.01623 -0.15576)")
        )
        self.assertColorEqual(
            i(0.5),
            Color("oklab(0.5 -0.03246 -0.31153)")
        )
        self.assertColorEqual(
            i(0.75),
            Color("oklab(0.75 -0.01623 -0.15576)")
        )
        self.assertColorEqual(
            i(1),
            Color("oklab(1 0 0)")
        )

    def test_continuous_undefined_left(self):
        """Test continuous with undefined left."""

        colors = [
            Color('oklab', [NaN, 0.22486, 0.12585]),
            Color('oklab', [NaN, -0.1403, 0.10768]),
            Color('oklab', [0.45201, -0.03246, -0.31153])
        ]
        i = Color.interpolate(colors, space='oklab', method='continuous')
        self.assertColorEqual(
            i(0),
            Color("oklab(0.45201 0.22486 0.12585)")
        )
        self.assertColorEqual(
            i(0.25),
            Color("oklab(0.45201 0.04228 0.11677)")
        )
        self.assertColorEqual(
            i(0.5),
            Color("oklab(0.45201 -0.1403 0.10768)")
        )
        self.assertColorEqual(
            i(0.75),
            Color("oklab(0.45201 -0.08638 -0.10192)")
        )
        self.assertColorEqual(
            i(1),
            Color("oklab(0.45201 -0.03246 -0.31153)")
        )

    def test_continuous_undefined_right(self):
        """Test continuous with undefined right."""

        colors = [
            Color('oklab', [0.45201, 0.22486, 0.12585]),
            Color('oklab', [NaN, -0.1403, 0.10768]),
            Color('oklab', [NaN, -0.03246, -0.31153])
        ]
        i = Color.interpolate(colors, space='oklab', method='continuous')
        self.assertColorEqual(
            i(0),
            Color("oklab(0.45201 0.22486 0.12585)")
        )
        self.assertColorEqual(
            i(0.25),
            Color("oklab(0.45201 0.04228 0.11677)")
        )
        self.assertColorEqual(
            i(0.5),
            Color("oklab(0.45201 -0.1403 0.10768)")
        )
        self.assertColorEqual(
            i(0.75),
            Color("oklab(0.45201 -0.08638 -0.10192)")
        )
        self.assertColorEqual(
            i(1),
            Color("oklab(0.45201 -0.03246 -0.31153)")
        )

    def test_too_few_colors_bspline(self):
        """Test too few colors during B-spline interpolation."""

        with self.assertRaises(ValueError):
            Color.interpolate(['green', lambda t: t * 3], method='bspline')

    def test_bad_method(self):
        """Test bad interpolation method."""

        with self.assertRaises(ValueError):
            Color.interpolate(['green', lambda t: t * 3], method='bad')

    def test_bad_easing(self):
        """Test bad color easing linear."""

        with self.assertRaises(ValueError):
            Color.interpolate([lambda t: t * 3, 'green'])

    def test_bad_color_input_bspline(self):
        """Test bad color easing B-spline."""

        with self.assertRaises(ValueError):
            Color.interpolate([lambda t: t * 3, 'green'], method='bspline')

    def test_bspline_all_none(self):
        """Test multiple B-spline inputs with the same channel all none."""

        self.assertColorEqual(
            Color.interpolate(
                ['Color(srgb 1 none 0.5)', 'Color(srgb 0.1 none 0.7)', 'Color(srgb 0.2 none 0.9)'],
                space='srgb',
                method='bspline'
            )(0.5),
            Color('rgb(68 none 178.5)')
        )

    def test_bspline_most_none(self):
        """Test multiple B-spline inputs with the same channel with most none."""

        self.assertColorEqual(
            Color.interpolate(
                ['Color(srgb 1 none 0.5)', 'Color(srgb 0.1 none 0.7)', 'Color(srgb 0.2 0.8 0.9)'],
                space='srgb',
                method='bspline'
            )(0.5),
            Color('rgb(68 204 178.5)')
        )

    def test_bspline_none_after(self):
        """Test multiple B-spline inputs with the same channel with most none but not none at the start."""

        self.assertColorEqual(
            Color.interpolate(
                ['Color(srgb 1 0.8 0.5)', 'Color(srgb 0.1 none 0.7)', 'Color(srgb 0.2 none 0.9)'],
                space='srgb',
                method='bspline'
            )(0.5),
            Color('rgb(68 204 178.5)')
        )

    def test_bspline_cylindrical(self):
        """Test B-spline with a cylindrical space."""

        self.assertColorEqual(
            Color.interpolate(
                ['hsl(250 50% 30%)', 'hsl(none 0% 10%)', 'hsl(120 75% 75%)'],
                space='hsl',
                method='bspline'
            )(0.75),
            Color('hsl(152.5 40.104% 44.271%)')
        )

    def test_bspline_undefined_alpha(self):
        """Test some cases related to undefined alpha and B-spline."""

        self.assertColorEqual(
            Color.interpolate(
                ['color(srgb 1 0 0 / none)', 'color(srgb 0 1 0 / 0.5)', 'color(srgb 0 0 1 / 1)'],
                space='srgb',
                method='bspline'
            )(0.75),
            Color('rgb(3.4932 38.425 174.66 / 0.76042)')
        )

        self.assertColorEqual(
            Color.interpolate(
                ['color(srgb 1 0 0 / 1)', 'color(srgb 0 1 0 / 0.5)', 'color(srgb 0 0 1 / none)'],
                space='srgb',
                method='bspline'
            )(0.75),
            Color('rgb(10.408 57.245 130.1 / 0.51042)')
        )

        self.assertColorEqual(
            Color.interpolate(
                ['color(srgb 1 0 0 / 1)', 'color(srgb 0 1 0 / none)', 'color(srgb 0 0 1 / 0.5)'],
                space='srgb',
                method='bspline'
            )(0.75),
            Color('rgb(8.5 140.25 106.25 / 0.625)')
        )

    def test_extrapolate_bspline(self):
        """
        Test that extrapolation of B-spline is linear after the first and last control point.

        Values have been vetted by plotting a complete curve that extrapolates past the endpoints.
        """

        i = Color.interpolate(
            ["oklab(0.7 0.15 0.1)", "oklab(0.7 -0.05 0.1)", "oklab(0.7 -0.09 0.02)", "oklab(0.7 -0.03 -0.12)"],
            method='bspline',
            extrapolate=True
        )
        self.assertColorEqual(i(-0.5), Color('oklab(0.7 0.25 0.1)'))
        self.assertColorEqual(i(1.5), Color('oklab(0.7 0 -0.19)'))

    def test_extrapolate_linear(self):
        """
        Test that extrapolation of linear makes sense.

        Values have been vetted by plotting a complete curve that extrapolates past the endpoints.
        """

        i = Color.interpolate(
            ["oklab(0.7 0.15 0.1)", "oklab(0.7 -0.05 0.1)", "oklab(0.7 -0.09 0.02)", "oklab(0.7 -0.03 -0.12)"],
            method='linear',
            extrapolate=True
        )
        self.assertColorEqual(i(-0.5), Color('color(--oklab 0.7 0.25 0.1 / 1)'))
        self.assertColorEqual(i(1.5), Color('color(--oklab 0.7 0 -0.19 / 1)'))

    def test_discrete(self):
        """Test discrete interpolation."""

        i = Color.discrete(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            domain=[-32, 32, 60, 85, 95],
            space='srgb'
        )
        self.assertColorEqual(i(-20), Color('blue'))
        self.assertColorEqual(i(60), Color('yellow'))
        self.assertColorEqual(i(87), Color('orange'))
        self.assertColorEqual(i(100), Color('red'))

    def test_discrete_steps(self):
        """Test specifying discrete steps."""

        i = Color.discrete(
            ['blue', 'green', 'yellow', 'orange', 'red'],
            domain=[-32, 32, 60, 85, 95],
            steps=3,
            space='srgb'
        )
        self.assertColorEqual(i(-20), Color('blue'))
        self.assertColorEqual(i(60), Color('yellow'))
        self.assertColorEqual(i(87), Color('red'))
        self.assertColorEqual(i(100), Color('red'))

    def test_padding(self):
        """Test padding."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        i = Color.discrete(scale, space='srgb', padding=0.25)
        steps = 5
        colors = [i(r / (steps - 1)).to_string() for r in range(steps)]
        self.assertEqual(
            colors,
            ['rgb(253 212 158)',
             'rgb(253 187 132)',
             'rgb(252 141 89)',
             'rgb(239 101 72)',
             'rgb(215 48 31)']
        )

    def test_padding_output_space(self):
        """Test padding output space."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        i = Color.discrete(scale, space='srgb', padding=0.25, out_space='oklab')
        steps = 5
        colors = [i(r / (steps - 1)).to_string() for r in range(steps)]
        self.assertEqual(
            colors,
            ['oklab(0.89246 0.02285 0.08001)',
             'oklab(0.84091 0.05126 0.09064)',
             'oklab(0.7538 0.10664 0.10608)',
             'oklab(0.67477 0.14723 0.09751)',
             'oklab(0.57443 0.17728 0.10314)']
        )

    def test_padding_sequence_one(self):
        """Test padding sequence of one."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        i = Color.discrete(scale, space='srgb', padding=[0.25])
        steps = 5
        colors = [i(r / (steps - 1)).to_string() for r in range(steps)]
        self.assertEqual(
            colors,
            ['rgb(253 212 158)',
             'rgb(253 187 132)',
             'rgb(252 141 89)',
             'rgb(239 101 72)',
             'rgb(215 48 31)']
        )

    def test_padding_sequence_two(self):
        """Test padding sequence of two."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        i = Color.discrete(scale, space='srgb', padding=[0.25, 0.15])
        steps = 5
        colors = [i(r / (steps - 1)).to_string() for r in range(steps)]
        self.assertEqual(
            colors,
            ['rgb(253 212 158)',
             'rgb(252.8 177.8 123.4)',
             'rgb(246.8 125 82.2)',
             'rgb(224.6 69.2 47.4)',
             'rgb(186.2 9.6 6.2)']
        )

    def test_no_padding(self):
        """Test that 0 applies no padding."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        i = Color.discrete(scale, space='srgb', padding=0)
        steps = 5
        colors = [i(r / (steps - 1)).to_string() for r in range(steps)]
        self.assertEqual(
            colors,
            ['rgb(255 247 236)',
             'rgb(253 212 158)',
             'rgb(252 141 89)',
             'rgb(215 48 31)',
             'rgb(127 0 0)']
        )

    def test_padding_sequence_empty(self):
        """An empty list will be treated as no padding set at all."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        i = Color.discrete(scale, space='srgb', padding=[])
        steps = 5
        colors = [i(r / (steps - 1)).to_string() for r in range(steps)]
        self.assertEqual(
            colors,
            ['rgb(255 247 236)',
             'rgb(253 212 158)',
             'rgb(252 141 89)',
             'rgb(215 48 31)',
             'rgb(127 0 0)']
        )

    def test_padding_sequence_too_many(self):
        """Test padding with too many inputs."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        with self.assertRaises(ValueError):
            Color.discrete(scale, space='srgb', padding=[0.25, 0.15, 0.3])

    def test_padding_bad_output(self):
        """Test that a bad output for padding fails."""

        scale = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
        with self.assertRaises(ValueError):
            Color.discrete(scale, space='srgb', padding=[0.25, 0.15], out_space='bad')
