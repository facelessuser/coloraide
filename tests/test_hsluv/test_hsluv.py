"""Tests for HSLuv."""
from coloraide.util import NaN
import unittest
from .. import util
from coloraide import Color
import json
import os


class TestHSLuvSnapshot(util.ColorAsserts, unittest.TestCase):
    """Run tests against the official snapshot."""

    def setUp(self):
        """Load snapshot."""

        snapshot = os.path.join(os.path.dirname(__file__), 'snapshot-rev4.json')
        with open(snapshot, 'r') as f:
            self.snapshot = json.loads(f.read())

    def test_snapshot(self):
        """
        Test the snapshot.

        https://github.com/hsluv/hsluv/tree/master/snapshots.

        The snapshot contains a number of unnecessary tests, at least for our purposes. It is sufficient to verify that
        our path from sRGB to HSLuv is correct, both forward and backwards, as our conversion path is noted below:

            ```
            srgb -> srgb-linear -> xyz-d65 -> luv -> lchuv -> hsluv
            ```

        Verifying each step in the chain makes no sense. If we are able to get through this entire chain and the sRGB
        to HSLuv checks out, both forward and backwards through the path, then we can consider our implementation
        successful. Any failure in the chain would cause errors to propagate up that would cause the test to fail. It
        would only be useful to test each point in the chain if we were trying to identify where in the chain breakage
        occurred.
        """

        for rgb, colors in self.snapshot.items():
            self.assertColorEqual(
                Color(rgb).convert('hsluv'),
                Color('hsluv', colors['hsluv'])
            )

            self.assertColorEqual(
                Color('hsluv', colors['hsluv']).convert('srgb'),
                Color('srgb', colors['rgb'])
            )


class TestHSLuvInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test HSLuv."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("hsluv", [20, 50, 0.75]), Color('color(--hsluv 20 50 0.75)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("hsluv", [20, 50, 75])), Color('color(--hsluv 20 50 75)'))

    def test_percent(self):
        """Test that percents work properly."""

        color = "color(--hsluv 20 50% 75% / 100%)"
        hsluv = Color(color)
        self.assertEqual("color(--hsluv 20 50 75)", hsluv.to_string())

        color = "color(--hsluv 20 50 75 / 20%)"
        hsluv = Color(color)
        self.assertEqual("color(--hsluv 20 50 75 / 0.2)", hsluv.to_string())

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(--hsluv 20 50% 75% / 0.2)"
        hsluv = Color(color)
        self.assertEqual("color(--hsluv 20 50 75)", hsluv.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(--hsluv 20 50% 75% / 1)"
        hsluv = Color(color)
        self.assertEqual("color(--hsluv 20 50 75 / 1)", hsluv.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--hsluv 20.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(--hsluv 20.123 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--hsluv 20.1 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--hsluv 20 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--hsluv 20.12345669999999842048055143095552921295166015625 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--hsluv 50 40% 110%)').to_string(),
            'color(--hsluv 0 0 100)'
        )

        self.assertEqual(
            Color('color(--hsluv 50 40% 110%)').to_string(fit="clip"),
            'color(--hsluv 50 40 100)'
        )

        self.assertEqual(
            Color('color(--hsluv 50 40% 110%)').to_string(fit=False),
            'color(--hsluv 50 40 110)'
        )


class TestHSluvProperties(util.ColorAsserts, unittest.TestCase):
    """Test HSLuv."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c.saturation, 50)
        c.saturation = 60
        self.assertEqual(c.saturation, 60)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c.lightness, 90)
        c.lightness = 80
        self.assertEqual(c.lightness, 80)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hsluv', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--hsluv none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--hsluv 270 0% 0.75 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_light(self):
        """Test maximum lightness."""

        c = Color('color(--hsluv 270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_light(self):
        """Test minimum lightness."""

        c = Color('color(--hsluv 270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))
