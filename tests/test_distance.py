"""Test distance methods."""
from coloraide import Color
from . import util
import pytest


class TestDistance(util.ColorAsserts):
    """Test distance."""

    def assertEqual(self, a, b):
        """Assert equal."""

        assert a == b

    def assertNotEqual(self, a, b):
        """Assert not equal."""

        assert a != b

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 137.1861),
            ('red', 'yellow', 207.1759),
            ('red', 'green', 238.3253),
            ('red', 'blue', 349.7736),
            ('red', 'indigo', 260.9437),
            ('red', 'violet', 188.974),
            ('red', 'white', 232.6692),
            ('red', 'black', 370.0502),
            ('red', 'gray', 205.0097),
            ('red', 'red', 0),
            ('orange', 'red', 137.1861),
            ('yellow', 'red', 207.1759),
            ('green', 'red', 238.3253),
            ('blue', 'red', 349.7736),
            ('indigo', 'red', 260.9437),
            ('violet', 'red', 188.974),
            ('white', 'red', 232.6692),
            ('black', 'red', 370.0502),
            ('gray', 'red', 205.0097)
        ]
    )
    def test_delta_e_itp(self, color1, color2, value):
        """Test delta e ITP."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="itp"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 45.7287),
            ('red', 'yellow', 69.0586),
            ('red', 'green', 79.4418),
            ('red', 'blue', 116.5912),
            ('red', 'indigo', 86.9812),
            ('red', 'violet', 62.9913),
            ('red', 'white', 77.5564),
            ('red', 'black', 123.3501),
            ('red', 'gray', 68.3366),
            ('red', 'red', 0),
            ('orange', 'red', 45.7287),
            ('yellow', 'red', 69.0586),
            ('green', 'red', 79.4418),
            ('blue', 'red', 116.5912),
            ('indigo', 'red', 86.9812),
            ('violet', 'red', 62.9913),
            ('white', 'red', 77.5564),
            ('black', 'red', 123.3501),
            ('gray', 'red', 68.3366)
        ]
    )
    def test_delta_e_itp_2000(self, color1, color2, value):
        """
        Test delta e ITP with scalar of 240.

        240 is supposed to give an equivalence to the average delta E 2000 results.
        """

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="itp", scalar=240),
            value,
            rounding=4
        )
