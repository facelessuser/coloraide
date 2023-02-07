"""Snapshot tests for HSLuv and HPLuv."""
import unittest
from .. import util
from coloraide.everything import ColorAll as Color
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
        our path from sRGB to HSLuv and HPLuv is correct, both forward and backwards, as our conversion path is noted
        below:

            ```
            srgb -> srgb-linear -> xyz-d65 -> luv -> lchuv -> hsluv
            srgb -> srgb-linear -> xyz-d65 -> luv -> lchuv -> hpluv
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

            self.assertColorEqual(
                Color(rgb).convert('hpluv'),
                Color('hpluv', colors['hpluv'])
            )

            self.assertColorEqual(
                Color('hpluv', colors['hpluv']).convert('srgb'),
                Color('srgb', colors['rgb'])
            )
