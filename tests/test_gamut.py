"""Test gamut mapping fitting."""
import unittest
import math
from coloraide.everything import ColorAll as Color
from coloraide import gamut
from coloraide.gamut.fit_raytrace import raytrace_box
from . import util


class TestGamut(util.ColorAsserts, unittest.TestCase):
    """Test gamut mapping/fitting."""

    def test_hue_clipping(self):
        """Test hue clipping."""

        self.assertEqual(Color('hsl(-120 50% 75% / 1)').clip().to_string(), 'hsl(240 50% 75%)')

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
        color2 = color.clone().fit()
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_self(self):
        """Test fit explicitly in own gamut."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clone().fit('srgb')
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_clip(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clone().fit(method="clip")
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.clone().fit()
        self.assertColorNotEqual(color2, color3)

    def test_clip(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clone().clip()
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.clone().fit()
        self.assertColorNotEqual(color2, color3)

    def test_clip_in_place(self):
        """Test clip in place."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clip()
        self.assertIs(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.clone().fit()
        self.assertColorEqual(color2, color3)

    def test_clip_other_space(self):
        """Test clip other space."""

        color = Color('hsl(330 110% 50%)')
        self.assertFalse(color.in_gamut('srgb'))
        self.assertTrue(color.clip('srgb').in_gamut('srgb'))

    def test_clip_undefined(self):
        """Test that clip leaves undefined channels alone."""

        color = Color('rgb(none 255.1 -0.1)')
        self.assertFalse(color.in_gamut('srgb'))
        color2 = color.clone().clip('srgb')
        self.assertColorEqual(color2, Color('rgb(0 255 0)'))
        self.assertTrue(color2.in_gamut('srgb'))

    def test_clip_other_gamut(self):
        """Test clip when a space defines another space as the gamut."""

        color = Color('orgb', [0.2, 1, 0.8])
        self.assertColorEqual(color.clip(), Color('color(--orgb 0.28313 0.1328 0.6872)'))

    def test_clip_other_gamut_in_gamut(self):
        """Test clip when a space defines another space as the gamut but it is in gamut."""

        color = Color('orange').convert('orgb')
        color2 = color.clone()
        self.assertColorEqual(color.clip(), color2)

    def test_sdr_extremes_low(self):
        """Test SDR extreme low case."""

        color = Color('hsl(none 0% -10%)')
        self.assertColorEqual(color.fit(), Color('hsl(0 0% 0%)'))

    def test_sdr_extremes_high(self):
        """Test SDR extreme high case."""

        color = Color('hsl(none 0% 110%)')
        self.assertColorEqual(color.fit(), Color('hsl(0 50% 100%)'))

    def test_hdr_extreme_high(self):
        """Test HDR extreme high case."""

        color = Color('color(--rec2100-pq 1.01 0.2 0)')
        self.assertColorEqual(color.fit(), Color('color(--rec2100-pq 1 0.45327 0)'))

    def test_hdr_extreme_low(self):
        """Test HDR extreme low case."""

        color = Color('color(--rec2100-pq -0.3 -0.2 0)')
        self.assertColorEqual(color.fit(), Color('color(--rec2100-pq 0.0 0.0 0.0)'))

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
        color2 = color.fit()
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

    def test_fit_options(self):
        """Test fit options."""

        self.assertColorEqual(
            Color('color(display-p3 0 1 0)').convert('srgb').fit(method='oklch-chroma', jnd=0.002),
            Color('rgb(0 247.37 75.73)')
        )

        self.assertColorEqual(
            Color('color(display-p3 0 1 0)').convert('srgb').fit(method='oklch-chroma', jnd=0.0),
            Color('rgb(0 246.92 78.614)')
        )

    def test_fit_method_to_string(self):
        """Test fit method to string."""

        self.assertEqual(
            Color('color(display-p3 0 1 0)').convert('srgb').to_string(fit='oklch-chroma'),
            'rgb(0 251.37 40.734)'
        )

    def test_fit_options_to_string(self):
        """Test fit options to string."""

        self.assertEqual(
            Color('color(display-p3 0 1 0)').convert('srgb').to_string(fit={'method': 'oklch-chroma', 'jnd': 0.002}),
            'rgb(0 247.37 75.73)'
        )


class TestRayTrace(util.ColorAsserts, unittest.TestCase):
    """Test gamut mapping/fitting with ray tracing."""

    def test_sdr_extremes_low(self):
        """Test SDR extreme low case."""

        color = Color('oklch(-10% 0 none)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0 0 none)'))

    def test_sdr_extremes_high(self):
        """Test SDR extreme high case."""

        color = Color('oklch(110% 0 none)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(100% 0 none)'))

    def test_non_rgb_space(self):
        """Test coercion to RGB."""

        color = Color('oklch(90% .4 270)')
        self.assertColorEqual(color.fit('hpluv', method='oklch-raytrace'), Color('oklch(0.9 0.04254 270)'))

        color = Color('oklch(90% .4 270)')
        self.assertColorEqual(color.fit('okhsv', method='oklch-raytrace'), Color('oklch(0.89999 0.04813 270)'))

    def test_sdr_extremes_high_non_rgb_space(self):
        """Test coercion of extreme high to RGB."""

        color = Color('oklch(110% 0 none)')
        self.assertColorEqual(color.fit('okhsl', method='oklch-raytrace'), Color('oklch(100% 0 none)'))

    def test_sdr_extremes_low_non_rgb_space(self):
        """Test failure with non-RGB space."""

        color = Color('oklch(-10% 0 none)')
        self.assertColorEqual(color.fit('okhsl', method='oklch-raytrace'), Color('oklch(0 0 none)'))

    def test_trace_face1(self):
        """Test tracing of face 1."""

        color = Color('oklch(30% .4 160)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0.3 0.06787 160)'))

    def test_trace_face2(self):
        """Test tracing of face 2."""

        color = Color('oklch(90% .4 60)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0.9 0.06469 59.901)'))

    def test_trace_face3(self):
        """Test tracing of face 3."""

        color = Color('oklch(30% .4 10)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0.3 0.11997 9.9994)'))

    def test_trace_face4(self):
        """Test tracing of face 4."""

        color = Color('oklch(90% .4 150)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0.9 0.18155 150)'))

    def test_trace_face5(self):
        """Test tracing of face 5."""

        color = Color('oklch(30% .4 100)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0.3 0.06237 100.02)'))

    def test_trace_face6(self):
        """Test tracing of face 6."""

        color = Color('oklch(90% .4 270)')
        self.assertColorEqual(color.fit('srgb', method='oklch-raytrace'), Color('oklch(0.9 0.04813 270)'))

    def test_trace_perpendicular(self):
        """
        Test perpendicular cases.

        Cases are unlikely to occur, but were broken in the original implementation.
        """

        self.assertEqual(raytrace_box([1, 1, 1], [-2, 0.5, 0.5], [2, 0.5, 0.5]), (1, [0, 0.5, 0.5]))
        self.assertEqual(raytrace_box([1, 1, 1], [0.5, -2, 0.5], [0.5, 2, 0.5]), (3, [0.5, 0, 0.5]))
        self.assertEqual(raytrace_box([1, 1, 1], [0.5, 0.5, -2], [0.5, 0.5, 2]), (5, [0.5, 0.5, 0]))

        self.assertEqual(raytrace_box([1, 1, 1], [2, 0.5, 0.5], [-2, 0.5, 0.5]), (2, [1, 0.5, 0.5]))
        self.assertEqual(raytrace_box([1, 1, 1], [0.5, 2, 0.5], [0.5, -2, 0.5]), (4, [0.5, 1, 0.5]))
        self.assertEqual(raytrace_box([1, 1, 1], [0.5, 0.5, 2], [0.5, 0.5, -2]), (6, [0.5, 0.5, 1]))

        self.assertEqual(raytrace_box([1, 1, 1], [2, 0.5, 0.5], [1.5, 0.5, 0.5]), (0, []))
        self.assertEqual(raytrace_box([1, 1, 1], [0, 2, 0.5], [1, -2, 0.5]), (4, [0.25, 1, 0.5]))
        self.assertEqual(raytrace_box([1, 1, 1], [1, 2, 0.5], [0, -2, 0.5]), (4, [0.75, 1, 0.5]))

        self.assertEqual(raytrace_box([1, 1, 1], [0.25, 2, 0.5], [0.75, -2, 0.5]), (4, [0.375, 1.0, 0.5]))
        self.assertEqual(raytrace_box([1, 1, 1], [1, 2, 0.5], [0, -2, 0.5]), (4, [0.75, 1.0, 0.5]))


class TestHCTGamut(util.ColorAsserts, unittest.TestCase):
    """
    Test HCT gamut mapping by producing tonal maps.

    When we are off, we seem to only be off on a given channel by at most < +/- 1 (between 0 - 255 floating point).
    As this is not a 1:1 port of the Material utilities, different precision of matrices and different gamut mapping
    can cause slight differences in results. We are not aiming to match the Material implementation, but aiming to match
    the intent.
    """

    def test_blue(self):
        """Test blue tonal maps."""

        hct = Color('#0000ff').convert('hct')
        tones = [100, 95, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
        expect = ['#ffffff', '#f1efff', '#e0e0ff', '#bec2ff',
                  '#9da3ff', '#7c84ff', '#5a64ff', '#343dff',
                  '#0000ef', '#0001ac', '#00006e', '#000000']

        # A channel should be off no more than by 1 in a scale of 0 - 255
        # Due to the fact that Material uses less precise matrices
        options = {'method': 'hct-chroma', 'jnd': 0.0}
        for tone, answer in zip(tones, expect):
            s1 = [c * 255 for c in hct.clone().set('tone', tone).convert('srgb').fit(**options)[:-1]]
            s2 = [c * 255 for c in Color(answer)[:-1]]
            for c1, c2 in zip(s1, s2):
                self.assertTrue(math.isclose(c1, c2, abs_tol=1.0))

        hct.set('chroma', 16)
        expect = ['#ffffff', '#f1efff', '#e1e0f9', '#c5c4dd',
                  '#a9a9c1', '#8f8fa6', '#75758b', '#5c5d72',
                  '#444559', '#2e2f42', '#191a2c', '#000000']

        for tone, answer in zip(tones, expect):
            s1 = [c * 255 for c in hct.clone().set('tone', tone).convert('srgb').fit(**options)[:-1]]
            s2 = [c * 255 for c in Color(answer)[:-1]]
            for c1, c2 in zip(s1, s2):
                self.assertTrue(math.isclose(c1, c2, abs_tol=1.0))

    def test_inside_but_high_chroma(self):
        """Test gamut mapping a color with high chroma, but inside gamut due to technically of algorithm."""

        self.assertColorEqual(
            Color('hct', [270, 30, 0]).fit('srgb', method='hct-chroma'),
            Color('hct', [float('nan'), 0, 0])
        )


class TestPointerGamut(util.ColorAsserts, unittest.TestCase):
    """Test Pointer's gamut."""

    def test_in_pointer_gamut_too_light(self):
        """Test gamut check when too light."""

        self.assertFalse(Color('white').in_pointer_gamut())

    def test_in_pointer_gamut_too_dark(self):
        """Test gamut check when too dark."""

        self.assertFalse(Color('black').in_pointer_gamut())

    def test_in_pointer_gamut(self):
        """Test gamut check in gamut."""

        self.assertTrue(Color('orange').in_pointer_gamut())

    def test_out_of_pointer_gamut(self):
        """Test gamut check out of gamut."""

        self.assertFalse(Color('red').in_pointer_gamut())

    def test_hue_wrap(self):
        """Test when hue interpolation wraps."""

        self.assertFalse(Color('deeppink').in_pointer_gamut())

    def test_fit_pointer_gamut_too_light(self):
        """Test fitting gamut when too light."""

        self.assertColorEqual(Color('white').fit_pointer_gamut(), Color('rgb(226.33 226.33 226.33)'))

    def test_fit_pointer_gamut_too_dark(self):
        """Test fitting gamut when too dark."""

        self.assertColorEqual(Color('black').fit_pointer_gamut(), Color('rgb(37.667 37.667 37.667)'))

    def test_fit_pointer_gamut(self):
        """Test gamut check out of gamut."""

        self.assertColorEqual(Color('red').fit_pointer_gamut(), Color('rgb(244 46.539 23.139)'))

    def test_pointer_boundary_too_light(self):
        """Test when pointer boundary is request is too light."""

        with self.assertRaises(ValueError):
            gamut.pointer.pointer_gamut_boundary(0)

    def test_pointer_boundary_too_dark(self):
        """Test when pointer boundary is request is too dark."""

        with self.assertRaises(ValueError):
            gamut.pointer.pointer_gamut_boundary(100)

    def test_pointer_boundary_mid(self):
        """Test when pointer boundary request."""

        boundary = gamut.pointer.pointer_gamut_boundary(50)
        # Test a sample of the values
        test = [boundary[0], boundary[5], boundary[8]]
        expected = [[0.47971142940104206, 0.2384179501289976, 18.418651851244416],
                    [0.634800855490809, 0.35129621215430396, 18.418651851244416],
                    [0.49892034937725527, 0.45347791373057683, 18.418651851244416]]

        for coords1, coords2 in zip(test, expected):
            [self.assertCompare(a, b) for a, b in zip(coords1, coords2)]

    def test_pointer_boundary_max(self):
        """Test pointer boundary max request."""

        boundary = gamut.pointer.pointer_gamut_boundary()
        # Test a sample of the values
        test = [boundary[0], boundary[5], boundary[8]]
        expected = [[0.5076988072583095, 0.2255929648510513, 11.250973799663784],
                    [0.634800855490809, 0.35129621215430396, 18.418651851244416],
                    [0.5260711281340981, 0.462168144862833, 48.2781043708229]]

        for coords1, coords2 in zip(test, expected):
            [self.assertCompare(a, b) for a, b in zip(coords1, coords2)]
