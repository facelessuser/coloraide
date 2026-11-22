"""Test Munsell."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
from coloraide.spaces import munsell
from coloraide.util import xy_to_xyz, xyz_to_xyY as util_xyz_to_xyy
import math
import pytest


class TestMunsell(util.ColorAssertsPyTest):
    """Test Munsell."""

    COLORS = [
        ('red', 'color(--munsell 28.105 5.2406 20.557)'),
        ('orange', 'color(--munsell 64.077 7.4175 13.263)'),
        ('yellow', 'color(--munsell 110.81 9.694 12.908)'),
        ('green', 'color(--munsell 141.01 4.5152 11.237)'),
        ('blue', 'color(--munsell 276.95 3.2756 29.484)'),
        ('indigo', 'color(--munsell 290.77 2.0656 15.746)'),
        ('violet', 'color(--munsell 315.63 6.9083 15.604)'),
        ('white', 'color(--munsell none 10 0)'),
        ('gray', 'color(--munsell none 5.2547 0)'),
        ('black', 'color(--munsell none 0 0)'),
        # Test color
        ('color(--munsell 50 5 10)', 'color(--munsell 50 5 10)'),
        ('color(--munsell 50 5 10 / 0.5)', 'color(--munsell 50 5 10 / 0.5)'),
        ('color(--munsell 180 50% 50% / 50%)', 'color(--munsell 180 5 17.5 / 0.5)'),
        ('color(--munsell none none none / none)', 'color(--munsell none none none / none)'),
        # Test percent ranges
        ('color(--munsell 0 0% 0%)', 'color(--munsell 0 0 0)'),
        ('color(--munsell 360 100% 100%)', 'color(--munsell 360 10 35)'),
        ('color(--munsell -360 -100% -100%)', 'color(--munsell -360 -10 -35)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('munsell'), Color(color2))


class TestMunsellSerialize(util.ColorAssertsPyTest):
    """Test Munsell serialization."""

    COLORS = [
        # Test color
        ('color(--munsell 50 5 10 / 0.5)', {}, 'color(--munsell 50 5 10 / 0.5)'),
        # Test alpha
        ('color(--munsell 50 5 10)', {'alpha': True}, 'color(--munsell 50 5 10 / 1)'),
        ('color(--munsell 50 5 10 / 0.5)', {'alpha': False}, 'color(--munsell 50 5 10)'),
        # Test None
        ('color(--munsell none 5 10)', {}, 'color(--munsell 0 5 10)'),
        ('color(--munsell none 5 10)', {'none': True}, 'color(--munsell none 5 10)'),
        # Test Fit (not bound)
        ('color(--munsell 50 12 10)', {}, 'color(--munsell 50 12 10)'),
        ('color(--munsell 50 12 10)', {'fit': False}, 'color(--munsell 50 12 10)'),
        ('color(--munsell 50 5 60)', {}, 'color(--munsell 50 5 60)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestMunsellReference(util.ColorAsserts, unittest.TestCase):
    """Test against the published renotation data and external reference."""

    def test_renotation_nodes(self):
        """Test that data nodes are reproduced exactly (`x` and `y` of Illuminant C)."""

        # (hue number, value, chroma, x, y) taken from `all.dat`
        nodes = [
            (5.0, 5.0, 8.0, 0.4413, 0.324),
            (5.0, 5.0, 12.0, 0.5071, 0.3194),
            (75.0, 3.0, 8.0, 0.1908, 0.1799),
            (75.0, 3.0, 12.0, 0.1557, 0.1356),
            (35.0, 9.0, 2.0, 0.3284, 0.3534),
            (35.0, 9.0, 8.0, 0.3698, 0.4497),
        ]
        for hue, value, chroma, x, y in nodes:
            xyz = munsell.munsell_to_xyz([hue * 3.6, value, chroma])
            self.assertAlmostEqual(xyz[0] / sum(xyz), x, places=9)
            self.assertAlmostEqual(xyz[1] / sum(xyz), y, places=9)

    def test_luminance(self):
        """Test luminance is calculated from the ASTM D1535 polynomial relative to the perfect diffuser."""

        self.assertAlmostEqual(munsell.value_to_y(10), 1.0, places=4)
        self.assertAlmostEqual(munsell.value_to_y(5), 0.192718, places=5)
        for v in (0.1, 1, 2.5, 5, 7.3, 9, 10, 11):
            self.assertAlmostEqual(munsell.y_to_value(munsell.value_to_y(v)), v, places=10)

    def test_reference_color(self):
        """
        Test an external reference.

        The `colour-science` docs list `4.2YR 8.1/5.3` as `xyY (0.3873694, 0.3575165, 0.59362)`. The two interpolate
        differently, so only expect agreement to a few thousandths.
        """

        # The reference is under Illuminant C, so use the space's conversion directly (no adaptation).
        x, y, Y = util_xyz_to_xyy(munsell.munsell_to_xyz([14.2 * 3.6, 8.1, 5.3]))
        self.assertAlmostEqual(x, 0.3873694, delta=5e-4)
        self.assertAlmostEqual(y, 0.3575165, delta=5e-4)
        self.assertAlmostEqual(Y, 0.59362, places=4)

        h, v, chroma = munsell.xyz_to_munsell(xy_to_xyz((0.3873694, 0.3575165), 0.59362))
        self.assertAlmostEqual(h / 3.6, 14.2, delta=0.1)
        self.assertAlmostEqual(v, 8.1, delta=0.01)
        self.assertAlmostEqual(chroma, 5.3, delta=0.05)

    def test_white_is_illuminant_c(self):
        """Test that Illuminant C is the achromatic axis of the space."""

        self.assertEqual(Color.CS_MAP['munsell'].WHITE, (0.31006, 0.31616))
        for v in (1, 5, 9):
            xyz = Color('munsell', [180, v, 0]).convert('xyz-d65')
            self.assertColorEqual(xyz.convert('munsell').set('h', 180), Color('munsell', [180, v, 0]), precision=5)


class TestMunsellRoundTrip(util.ColorAsserts, unittest.TestCase):
    """Test round trips."""

    def test_node_inverse(self):
        """Test hue and chroma are recovered at data nodes."""

        for hue in (0, 12.5, 40, 57.5, 80, 97.5):
            for value in (0.5, 1, 3.3, 5, 8.7, 9.5):
                for chroma in (0.5, 2, 5, 8):
                    h, v, c = Color('munsell', [hue * 3.6, value, chroma]).convert('xyz-d65').convert('munsell')[:-1]
                    self.assertAlmostEqual((h / 3.6 - hue + 50) % 100 - 50, 0, places=7)
                    self.assertAlmostEqual(v, value, places=8)
                    self.assertAlmostEqual(c, chroma, places=7)

    def test_rgb_gamuts(self):
        """Test that colors in common RGB gamuts survive a round trip."""

        for space in ('srgb', 'display-p3', 'prophoto-rgb'):
            for r in (0, 0.25, 0.5, 0.75, 1):
                for g in (0, 0.25, 0.5, 0.75, 1):
                    for b in (0, 0.25, 0.5, 0.75, 1):
                        c1 = Color(space, [r, g, b])
                        c2 = c1.convert('munsell').convert(space)
                        for a, e in zip(c2[:-1], c1[:-1]):
                            self.assertAlmostEqual(a, e, places=8)


class TestMunsellMisc(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous cases."""

    def test_zero_luminance(self):
        """Test black is not given any chroma or hue."""

        self.assertColorEqual(Color('color(--munsell 120 0 20)').convert('xyz-d65'), Color('xyz-d65', [0, 0, 0]))

    def test_negative_value(self):
        """Test negative Value is the mirror of positive Value."""

        c1 = Color('color(--munsell 120 -4 8)').convert('xyz-d65')
        c2 = Color('color(--munsell 120 4 8)').convert('xyz-d65')
        self.assertAlmostEqual(c1['y'], -c2['y'], places=12)
        self.assertColorEqual(c1.convert('munsell'), Color('color(--munsell 120 -4 8)'), precision=6)

    def test_over_range_value(self):
        """Test Value beyond the data is converted and round trips."""

        c = Color('color(--munsell 120 12 3)')
        self.assertColorEqual(c.convert('xyz-d65').convert('munsell'), c, precision=6)

    def test_negative_chroma(self):
        """Test negative chroma reflects through the white point and normalizes."""

        c = Color('color(--munsell 90 5 -4)')
        n = c.normalize()
        self.assertGreaterEqual(n['c'], 0)
        self.assertColorEqual(n.convert('xyz-d65'), c.convert('xyz-d65'), precision=6)
        a = Color('color(--munsell 90 5 4)').convert('xyz-d65')
        b = Color('color(--munsell 90 5 -4)').convert('xyz-d65')
        wx, wy = munsell.XC, munsell.YC
        xa, ya = a[0] / sum(a[:-1]), a[1] / sum(a[:-1])
        xb, yb = b[0] / sum(b[:-1]), b[1] / sum(b[:-1])
        # Reflection through the white point is in Illuminant C, so compare in that space
        ac = Color('color(--munsell 90 5 4)')._space.to_base([90, 5, 4])
        bc = Color('color(--munsell 90 5 -4)')._space.to_base([90, 5, -4])
        self.assertAlmostEqual(ac[0] / sum(ac) + bc[0] / sum(bc), 2 * wx, places=12)
        self.assertAlmostEqual(ac[1] / sum(ac) + bc[1] / sum(bc), 2 * wy, places=12)
        self.assertTrue(math.isfinite(xa + ya + xb + yb))

    def test_hue_wrap(self):
        """Test hue wraps around the circle."""

        for h1, h2 in ((0, 360), (359.9, -0.1), (10, 730)):
            self.assertColorEqual(
                Color('munsell', [h1, 5, 8]).convert('xyz-d65'),
                Color('munsell', [h2, 5, 8]).convert('xyz-d65'),
                precision=8
            )

    def test_extreme_luminance(self):
        """Test absurd luminance still returns a finite Value as Newton's method is capped."""

        value = munsell.y_to_value(1e30)
        self.assertTrue(math.isfinite(value))
        self.assertGreater(value, 1000)

    def test_near_neutral_chromaticity(self):
        """
        Test a chromaticity so close to the white point that hue cannot be resolved.

        At this distance the finite difference for hue falls below floating point resolution, so there
        is no usable Jacobian. The result should still be a finite, effectively neutral color.
        """

        h, v, c = munsell.xyz_to_munsell(xy_to_xyz((munsell.XC + 1e-12, munsell.YC), 0.5))
        self.assertTrue(math.isfinite(h))
        self.assertAlmostEqual(v, munsell.y_to_value(0.5), places=10)
        self.assertLess(c, 1e-9)

    def test_extreme_input(self):
        """Test that extreme inputs do not raise, loop forever, or produce non-finite coordinates."""

        for xyz in (
            [0, 0, 0],
            [1e-300, 1e-300, 1e-300],
            [0.5, 0, 0.5],
            [-0.1, 0.5, 0.2],
            [0.5, -0.5, 0.2],
            [50, 100, 120],
            [0.95047, 1.0, 1.08883]
        ):
            m = Color('xyz-d65', xyz).convert('munsell')
            for coord in m[:-1]:
                self.assertTrue(math.isnan(coord) or math.isfinite(coord))


class TestMunsellPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Munsell properties."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--munsell 111.05 5 12)')
        self.assertEqual(c._space.names(), ('v', 'c', 'h'))
        self.assertEqual(c._space.lightness_name(), 'v')
        self.assertEqual(c._space.radial_name(), 'c')
        self.assertEqual(c._space.hue_name(), 'h')

    def test_h(self):
        """Test `h`."""

        c = Color('color(--munsell 111.05 5 12)')
        self.assertEqual(c['h'], 111.05)
        c['h'] = 270
        self.assertEqual(c['h'], 270)

    def test_v(self):
        """Test `v`."""

        c = Color('color(--munsell 111.05 5 12)')
        self.assertEqual(c['v'], 5)
        c['v'] = 7
        self.assertEqual(c['v'], 7)

    def test_c(self):
        """Test `c`."""

        c = Color('color(--munsell 111.05 5 12)')
        self.assertEqual(c['c'], 12)
        c['c'] = 30
        self.assertEqual(c['c'], 30)

    def test_aliases(self):
        """Test channel aliases."""

        c = Color('color(--munsell 111.05 5 12)')
        self.assertEqual(c['value'], 5)
        self.assertEqual(c['lightness'], 5)
        self.assertEqual(c['chroma'], 12)
        self.assertEqual(c['hue'], 111.05)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--munsell 111.05 5 12)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('munsell', [NaN, 5, 12], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--munsell none 5 12 / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum chroma."""

        c = Color(Color('munsell', [270, 5, 0]).convert('munsell').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_gray_has_no_hue(self):
        """Test grays from RGB spaces do not get a hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'prophoto-rgb'):
            for i in range(0, 256, 5):
                self.assertTrue(Color(space, [i / 255] * 3).convert('munsell').is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('munsell').set('c', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('munsell', [270, 5, 0.000001]).is_achromatic(), True)
        self.assertEqual(Color('munsell', [270, 5, NaN]).is_achromatic(), True)
        self.assertEqual(Color('munsell', [270, 5, 10]).is_achromatic(), False)
        self.assertEqual(Color('munsell', [NaN, 5, 10]).is_achromatic(), False)
        self.assertEqual(Color('munsell', [270, 5, -10]).is_achromatic(), False)
        self.assertEqual(Color('munsell', [NaN, NaN, NaN]).is_achromatic(), True)


class TestMunsellNotationParse(util.ColorAssertsPyTest):
    """Test parsing Munsell notation."""

    COLORS = [
        ('5R 4/14', 'color(--munsell 18 4 14)'),
        ('2.8Y 6.95/2.3', 'color(--munsell 82.08 6.95 2.3)'),
        ('7.5PB 3/12', 'color(--munsell 279 3 12)'),
        # Every hue family
        ('5R 5/5', 'color(--munsell 18 5 5)'),
        ('5YR 5/5', 'color(--munsell 54 5 5)'),
        ('5Y 5/5', 'color(--munsell 90 5 5)'),
        ('5GY 5/5', 'color(--munsell 126 5 5)'),
        ('5G 5/5', 'color(--munsell 162 5 5)'),
        ('5BG 5/5', 'color(--munsell 198 5 5)'),
        ('5B 5/5', 'color(--munsell 234 5 5)'),
        ('5PB 5/5', 'color(--munsell 270 5 5)'),
        ('5P 5/5', 'color(--munsell 306 5 5)'),
        ('5RP 5/5', 'color(--munsell 342 5 5)'),
        # Hue `0` of a family is `10` of the previous family and `10RP` is `0R`
        ('10R 5/5', 'color(--munsell 36 5 5)'),
        ('0YR 5/5', 'color(--munsell 36 5 5)'),
        ('10RP 5/5', 'color(--munsell 0 5 5)'),
        ('0R 5/5', 'color(--munsell 0 5 5)'),
        # Flexible whitespace and case
        ('5r4/14', 'color(--munsell 18 4 14)'),
        ('5R  4 / 14', 'color(--munsell 18 4 14)'),
        ('5rp 4/14', 'color(--munsell 342 4 14)'),
        # Fractional forms
        ('5.R 4./14.', 'color(--munsell 18 4 14)'),
        ('.5R .5/.5', 'color(--munsell 1.8 0.5 0.5)'),
        # Neutral
        ('N 5/', 'color(--munsell none 5 0)'),
        ('N5', 'color(--munsell none 5 0)'),
        ('n 5.25', 'color(--munsell none 5.25 0)'),
        ('N 5.25/', 'color(--munsell none 5.25 0)'),
        ('N0/', 'color(--munsell none 0 0)'),
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        color = Color(color1)
        self.assertEqual(color.space(), 'munsell')
        self.assertColorEqual(color, Color(color2))



class TestMunsellNotationParseMisc(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous notation parsing cases."""

    def test_neutral_hue_is_null(self):
        """Test neutral notation has a null hue."""

        self.assertTrue(Color('N 5/').is_nan('hue'))

    def test_alpha_is_opaque(self):
        """Test notation has no alpha."""

        self.assertEqual(Color('5R 4/14')[-1], 1.0)

    def test_invalid(self):
        """Test strings that are not valid notation or any other color."""

        for string in (
            '11R 5/5',     # Hue out of range
            '5X 5/5',      # Not a hue family
            '5R 5/',       # Missing chroma
            '5R 5',        # Missing chroma
            '5R /5',       # Missing value
            'R 5/5',       # Missing hue
            '5R 5/5 x',    # Trailing characters
            ' 5R 5/5',     # Leading whitespace
            '5R 5/5 ',     # Trailing whitespace
            '5R 5/-5',     # Negative chroma
            'N',           # Missing value
            'N 5/5',       # Neutral has no chroma
        ):
            with self.assertRaises(ValueError, msg=string):
                Color(string)

    def test_match_not_full(self):
        """Test matching notation within a larger string."""

        m = Color.match('x 5R 4/14 y', 2)
        self.assertIsNotNone(m)
        self.assertEqual((m.start, m.end), (2, 9))
        self.assertColorEqual(m.color, Color('5R 4/14'))
        self.assertIsNone(Color.match('x 5R 4/14 y', 2, fullmatch=True))
        self.assertIsNone(Color.match('x 5R 4/14 y', 0))

    def test_match_neutral_end(self):
        """Test the neutral slash is consumed only when present."""

        self.assertEqual(Color.match('N 5/ x').end, 4)
        self.assertEqual(Color.match('N 5 x').end, 3)

    def test_fallback(self):
        """Test normal matching still works when it is not notation."""

        self.assertColorEqual(Color('color(--munsell 50 5 10 / 0.5)'), Color('munsell', [50, 5, 10], 0.5))
        self.assertColorEqual(Color('color(--munsell none 5 10)'), Color('munsell', [NaN, 5, 10]))
        self.assertColorEqual(Color('red'), Color('srgb', [1, 0, 0]))
        self.assertColorEqual(Color('#ff0000'), Color('srgb', [1, 0, 0]))
        self.assertColorEqual(Color('lab(50% 10 10)'), Color('lab', [50, 10, 10]))
        self.assertColorEqual(Color('navy'), Color('srgb', [0, 0, 128 / 255]))
        self.assertIsNone(Color.match('nonsense'))


class TestMunsellNotationSerialize(util.ColorAssertsPyTest):
    """Test serializing Munsell notation."""

    COLORS = [
        ('color(--munsell 82.08 6.95 2.3)', {}, '2.8Y 6.95/2.3'),
        ('color(--munsell 18 4 14)', {}, '5R 4/14'),
        ('color(--munsell 279 3 12)', {}, '7.5PB 3/12'),
        # Hue family boundaries
        ('color(--munsell 0 5 5)', {}, '10RP 5/5'),
        ('color(--munsell 36 5 5)', {}, '10R 5/5'),
        ('color(--munsell 72 5 5)', {}, '10YR 5/5'),
        ('color(--munsell 359.9 5 5)', {'precision': 2, 'rounding': 'decimal'}, '9.97RP 5/5'),
        ('color(--munsell 359.99 5 5)', {'precision': 1, 'rounding': 'decimal'}, '10RP 5/5'),
        ('color(--munsell 35.99 5 5)', {'precision': 1, 'rounding': 'decimal'}, '10R 5/5'),
        ('color(--munsell 0.01 5 5)', {'precision': 1, 'rounding': 'decimal'}, '10RP 5/5'),
        ('color(--munsell 36.01 5 5)', {'precision': 1, 'rounding': 'decimal'}, '10R 5/5'),
        ('color(--munsell 360 5 5)', {}, '10RP 5/5'),
        ('color(--munsell -18 5 5)', {}, '5RP 5/5'),
        # Neutral
        ('color(--munsell none 5 0)', {}, 'N 5/'),
        ('color(--munsell 120 5 0)', {}, 'N 5/'),
        ('color(--munsell 120 5 0.000001)', {}, 'N 5/'),
        ('color(--munsell 120 5.25 0.04)', {'precision': 1, 'rounding': 'decimal'}, 'N 5.3/'),
        ('color(--munsell 120 0 0)', {}, 'N 0/'),
        # `none` and alpha are not part of the notation
        ('color(--munsell none 5 4)', {'none': True}, '10RP 5/4'),
        ('color(--munsell 18 5 4 / 0.5)', {}, '5R 5/4'),
        ('color(--munsell 18 5 4 / 0.5)', {'alpha': True}, '5R 5/4'),
        # Negative chroma is normalized
        ('color(--munsell 90 5 -4)', {}, '5.0798PB 5/7.7269'),
        # Precision and rounding apply to the hue within the family, value, and chroma
        ('color(--munsell 82.08 6.95 2.3)', {'precision': 1, 'rounding': 'decimal'}, '2.8Y 7/2.3'),
        ('color(--munsell 82.08 6.95 2.34)', {'precision': 1, 'rounding': 'decimal'}, '2.8Y 7/2.3'),
        ('color(--munsell 82.08 6.95 2.3)', {'precision': 2}, '2.8Y 7/2.3'),
        ('color(--munsell 82.08 6.95 2.3)', {'precision': [1, 3, 5]}, '3Y 6.95/2.3'),
        ('color(--munsell 82.08 6.95 2.3)', {'precision': [2]}, '2.8Y 6.95/2.3'),
        # Notation is not default and `False` is the normal serialization
        ('color(--munsell 82.08 6.95 2.3)', {'notation': False}, 'color(--munsell 82.08 6.95 2.3)'),
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        options.setdefault('notation', True)
        self.assertEqual(Color(color1).to_string(**options), color2)



class TestMunsellNotationSerializeMisc(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous notation serialization cases."""

    def test_default_is_not_notation(self):
        """Test notation must be explicitly enabled."""

        self.assertEqual(Color('5R 4/14').to_string(), 'color(--munsell 18 4 14)')
        self.assertEqual(Color('5R 4/14').serialize(), 'color(--munsell 18 4 14)')

    def test_negative_chroma_without_fit(self):
        """Test negative chroma is normalized for notation even when fitting does not do it."""

        self.assertEqual(Color('color(--munsell 90 5 -4)').serialize(notation=True), '5.0798PB 5/7.7269')
        self.assertEqual(Color('color(--munsell 90 5 -4)').to_string(notation=True, fit=False), '5.0798PB 5/7.7269')

    def test_serialize_notation(self):
        """Test `serialize` accepts notation."""

        self.assertEqual(Color('color(--munsell 18 4 14)').serialize(notation=True), '5R 4/14')

    def test_converted_color(self):
        """Test notation of a converted color."""

        red = Color('red').convert('munsell')
        self.assertEqual(red.to_string(notation=True, precision=2, rounding='decimal'), '7.81R 5.24/20.56')
        self.assertEqual(Color('white').convert('munsell').to_string(notation=True), 'N 10/')
        self.assertEqual(Color('black').convert('munsell').to_string(notation=True), 'N 0/')
        gray = Color('gray').convert('munsell')
        self.assertEqual(gray.to_string(notation=True, precision=2, rounding='decimal'), 'N 5.25/')

    def test_round_trip(self):
        """Test notation survives parsing and serializing."""

        for hue in range(0, 360, 7):
            for value in (0.5, 3.3, 5, 9.1):
                for chroma in (0.5, 4, 17.25):
                    color = Color('munsell', [hue, value, chroma])
                    string = color.to_string(notation=True, precision=12)
                    parsed = Color(string)
                    for a, b in zip(parsed[:-1], color[:-1]):
                        self.assertAlmostEqual(a, b, places=7)
                    self.assertEqual(parsed.to_string(notation=True, precision=12), string)

    def test_neutral_round_trip(self):
        """Test neutral notation survives parsing and serializing."""

        for string in ('N 0/', 'N 5/', 'N 5.25/', 'N 10/'):
            self.assertEqual(Color(string).to_string(notation=True), string)
