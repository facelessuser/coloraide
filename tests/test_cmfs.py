"""Test CMFs."""
import unittest
from coloraide import cmfs


class TestAlgebra(unittest.TestCase):
    """Test Algebra."""

    def test_interpolation(self):
        """Test interpolation."""

        self.assertEqual(
            cmfs.CIE_1931_2DEG[360.5],
            [0.00013771619893839714, 4.150634404044558e-06, 0.000642746187006579]
        )

    def test_extrapolation(self):
        """Test extrapolation."""

        self.assertEqual(
            cmfs.CIE_1931_2DEG[358],
            [9.800600000000004e-05, 2.9638379999999993e-06, 0.0004565416000000002]
        )
        self.assertEqual(
            cmfs.CIE_1931_2DEG[832],
            [1.069469e-06, 3.8620600000000006e-07, 0.0]
        )
