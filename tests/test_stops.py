"""Test API."""
from coloraide.interpolate import calc_stops
import pytest


class TestStops:
    """
    Test stops.

    https://drafts.csswg.org/css-images-4/#color-stop-fixup
    """

    STOPS = [
        ({1: 0.2}, 3, {0: 0, 1: 0.2, 2: 1.0}),
        ({0: 0.4}, 4, {0: 0.4, 1: 0.6, 2: 0.8, 3: 1.0}),
        ({0: -0.5}, 3, {0: -0.5, 1: 0.25, 2: 1.0}),
        ({0: 0.2, 1: 0.0, 2: 0.4}, 3, {0: 0.2, 1: 0.2, 2: 0.4}),
        ({1: -0.5, 2: 1.5}, 4, {0: 0.0, 1: 0.0, 2: 1.5, 3: 1.5}),
        ({0: 0.8, 1: 0.0, 3: 1.0}, 4, {0: 0.8, 1: 0.8, 2: 0.9, 3: 1.0})
    ]

    @pytest.mark.parametrize('stops1,count,stops2', STOPS)
    def test_stops(self, stops1, count, stops2):
        """Test stops."""

        assert calc_stops(stops1, count) == stops2
