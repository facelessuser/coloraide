"""Test distance methods."""
from coloraide import Color
from . import util
import pytest
import unittest


class TestDistance(util.ColorAsserts):
    """Test distance."""

    def assertEqual(self, a, b):
        """Assert equal."""

        assert a == b

    def assertNotEqual(self, a, b):
        """Assert not equal."""

        assert a != b

    @pytest.mark.parametrize(
        'color1,color2,space,value',
        [
            ('red', 'orange', 'lab', 75.3854),
            ('red', 'orange', 'lab-d65', 79.06950),
            ('red', 'orange', 'luv', 125.1865),
            ('red', 'orange', 'din99o', 45.6107),
            ('red', 'orange', 'oklab', 0.3367),
            ('red', 'orange', 'jzazbz', 0.1224),
            ('red', 'orange', 'ictcp', 0.2688)
        ]
    )
    def test_delta_e_hyab_spaces(self, color1, color2, space, value):
        """Test delta e HyAB."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="hyab", space=space),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 75.3854),
            ('red', 'yellow', 142.6999),
            ('red', 'green', 138.1441),
            ('red', 'blue', 207.0685),
            ('red', 'indigo', 163.2506),
            ('red', 'violet', 125.2466),
            ('red', 'white', 152.5473),
            ('red', 'black', 161.1308),
            ('red', 'gray', 107.5457),
            ('red', 'red', 0),
            ('orange', 'red', 75.3854),
            ('yellow', 'red', 142.6999),
            ('green', 'red', 138.1441),
            ('blue', 'red', 207.0685),
            ('indigo', 'red', 163.2506),
            ('violet', 'red', 125.2466),
            ('white', 'red', 152.5473),
            ('black', 'red', 161.1308),
            ('gray', 'red', 107.5457)
        ]
    )
    def test_delta_e_hyab(self, color1, color2, value):
        """Test delta e HyAB."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="hyab"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 32.4071),
            ('red', 'yellow', 63.8142),
            ('red', 'green', 70.1885),
            ('red', 'blue', 74.4103),
            ('red', 'indigo', 67.608),
            ('red', 'violet', 51.6678),
            ('red', 'white', 65.6918),
            ('red', 'black', 75.9866),
            ('red', 'gray', 49.9161),
            ('red', 'red', 0),
            ('orange', 'red', 32.4071),
            ('yellow', 'red', 63.8142),
            ('green', 'red', 70.1885),
            ('blue', 'red', 74.4103),
            ('indigo', 'red', 67.608),
            ('violet', 'red', 51.6678),
            ('white', 'red', 65.6918),
            ('black', 'red', 75.9866),
            ('gray', 'red', 49.9161)
        ]
    )
    def test_delta_e_99o(self, color1, color2, value):
        """Test delta e 99o."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="99o"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 0.0941),
            ('red', 'yellow', 0.1663),
            ('red', 'green', 0.1996),
            ('red', 'blue', 0.3396),
            ('red', 'indigo', 0.2401),
            ('red', 'violet', 0.1785),
            ('red', 'white', 0.1848),
            ('red', 'black', 0.2109),
            ('red', 'gray', 0.1635),
            ('red', 'red', 0),
            ('orange', 'red', 0.0941),
            ('yellow', 'red', 0.1663),
            ('green', 'red', 0.1996),
            ('blue', 'red', 0.3396),
            ('indigo', 'red', 0.2401),
            ('violet', 'red', 0.1785),
            ('white', 'red', 0.1848),
            ('black', 'red', 0.2109),
            ('gray', 'red', 0.1635)
        ]
    )
    def test_delta_e_jz(self, color1, color2, value):
        """Test delta e z."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="jz"),
            value,
            rounding=4
        )

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

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 58.1292),
            ('red', 'yellow', 108.4136),
            ('red', 'green', 130.3764),
            ('red', 'blue', 184.0129),
            ('red', 'indigo', 133.2387),
            ('red', 'violet', 110.9833),
            ('red', 'black', 119.8423),
            ('red', 'white', 116.206),
            ('red', 'gray', 106.8414),
            ('red', 'red', 0),
            ('orange', 'red', 58.1292),
            ('yellow', 'red', 108.4136),
            ('green', 'red', 130.3764),
            ('blue', 'red', 184.0129),
            ('indigo', 'red', 133.2387),
            ('violet', 'red', 110.9833),
            ('black', 'red', 119.8423),
            ('white', 'red', 116.206),
            ('gray', 'red', 106.8414),
            # Pythagorean 3, 4, 5 triangle
            ('lab(50% 30 40)', 'lab(50% 0 0)', 50),
        ]
    )
    def test_delta_e_76(self, color1, color2, value):
        """Test delta e 76."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="76"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 28.6829),
            ('red', 'yellow', 57.5942),
            ('red', 'green', 48.8485),
            ('red', 'blue', 73.8242),
            ('red', 'indigo', 59.1206),
            ('red', 'violet', 42.5254),
            ('red', 'black', 57.3237),
            ('red', 'white', 49.2712),
            ('red', 'gray', 18.4095),
            ('red', 'red', 0),
            ('orange', 'red', 30.7736),
            ('yellow', 'red', 59.5159),
            ('green', 'red', 62.742),
            ('blue', 'red', 65.8069),
            ('indigo', 'red', 69.4025),
            ('violet', 'red', 54.8404),
            ('black', 'red', 119.8423),
            ('white', 'red', 116.206),
            ('gray', 'red', 106.8414),
            # Pythagorean 3, 4, 5 triangle
            ('lab(50% 30 40)', 'lab(50% 0 0)', 15.3846),
        ]
    )
    def test_delta_e_94(self, color1, color2, value):
        """Test delta e 94."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="94"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0.0),
            ('red', 'orange', 32.7958),
            ('red', 'yellow', 64.9058),
            ('red', 'green', 78.8665),
            ('red', 'blue', 114.2168),
            ('red', 'indigo', 79.8669),
            ('red', 'violet', 65.2282),
            ('red', 'black', 38.9139),
            ('red', 'white', 36.7153),
            ('red', 'gray', 30.7146),
            ('red', 'red', 0.0),
            ('orange', 'red', 34.4713),
            ('yellow', 'red', 48.5999),
            ('green', 'red', 57.9017),
            ('blue', 'red', 79.4325),
            ('indigo', 'red', 70.1518),
            ('violet', 'red', 53.0886),
            ('black', 'red', 175.6834),
            ('white', 'red', 168.1679),
            ('gray', 'red', 167.4596),
            # Pythagorean 3, 4, 5 triangle
            ('lab(50% 30 40)', 'lab(50% 0 0)', 19.4894),
            # Brilliant red
            ('lab(38.64% 64.26 52.16)', 'lab(38.59% 62.06 51.11)', 0.8423),
            ('lab(38.83% 33.35 26.67)', 'lab(38.69% 31.14 25.21)', 1.1297),
            # Brilliant yellow
            ('lab(84.25% 5.74 96.00)', 'lab(84.46% 8.88 96.49)', 1.6364),
            ('lab(84.25% 5.74 96.00)', 'lab(84.52% 5.75 93.09)', 0.8770),
            ('lab(84.25% 5.74 96.00)', 'lab(84.37% 5.86 99.42)', 1.0221)
        ]
    )
    def test_delta_e_cmc(self, color1, color2, value):
        """Test delta e CMC."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="cmc"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0.0),
            ('red', 'orange', 31.4672),
            ('red', 'yellow', 60.9883),
            ('red', 'green', 70.2453),
            ('red', 'blue', 55.7976),
            ('red', 'indigo', 52.8451),
            ('red', 'violet', 41.6887),
            ('red', 'black', 51.3412),
            ('red', 'white', 45.264),
            ('red', 'gray', 31.4013),
            ('red', 'red', 0.0),
            ('orange', 'red', 31.4672),
            ('yellow', 'red', 60.9883),
            ('green', 'red', 70.2453),
            ('blue', 'red', 55.7976),
            ('indigo', 'red', 52.8451),
            ('violet', 'red', 41.6887),
            ('black', 'red', 51.3412),
            ('white', 'red', 45.264),
            ('gray', 'red', 31.4013),
            # Pythagorean 3, 4, 5 triangle
            ('lab(50% 30 40)', 'lab(50% 0 0)', 24.1219),
            # Sharma: http://www2.ece.rochester.edu/~gsharma/
            ('lab(50% 2.6772 -79.7751)', 'lab(50% 0 -82.7485)', 2.0425),
            ('lab(50% 3.1571 -77.2803)', 'lab(50% 0 -82.7485)', 2.8615),
            ('lab(50% 2.8361 -74.0200)', 'lab(50% 0 -82.7485)', 3.4412),
            ('lab(50% -1.3802 -84.2814)', 'lab(50% 0 -82.7485)', 1.0000),
            ('lab(50% -1.1848 -84.8006)', 'lab(50% 0 -82.7485)', 1.0000),
            ('lab(50% -0.9009 -85.5211)', 'lab(50% 0 -82.7485)', 1.0000),
            ('lab(50% 0 0)', 'lab(50% -1 2)', 2.3669),
            ('lab(50% -1 2)', 'lab(50% 0 0)', 2.3669),
            ('lab(50% 2.4900 -0.0010)', 'lab(50% -2.4900 0.0009)', 7.1792),
            ('lab(50% 2.4900 -0.0010)', 'lab(50% -2.4900 0.0010)', 7.1792),
            ('lab(50% 2.4900 -0.0010)', 'lab(50% -2.4900 0.0011)', 7.2195),
            ('lab(50% 2.4900 -0.0010)', 'lab(50% -2.4900 0.0012)', 7.2195),
            ('lab(50% -0.0010 2.4900)', 'lab(50% 0.0009 -2.4900)', 4.8045),
            ('lab(50% -0.0010 2.4900)', 'lab(50% 0.00010 -2.4900)', 4.8045),
            ('lab(50% -0.0010 2.4900)', 'lab(50% 0.0011 -2.4900)', 4.7461),
            ('lab(50% 2.5 0)', 'lab(50% 0 -2.5)', 4.3065),
            ('lab(50% 2.5 0)', 'lab(73% 25 -18)', 27.1492),
            ('lab(50% 2.5 0)', 'lab(61% -5 29)', 22.8977),
            ('lab(50% 2.5 0)', 'lab(56% -27 -3)', 31.9030),
            ('lab(50% 2.5 0)', 'lab(58% 24 15)', 19.4535),
            ('lab(50% 2.5 0)', 'lab(50% 3.1736 0.5854)', 1.0000),
            ('lab(50% 2.5 0)', 'lab(50% 3.2972 0)', 1.0000),
            ('lab(50% 2.5 0)', 'lab(50% 1.8634 0.5757)', 1.0000),
            ('lab(50% 2.5 0)', 'lab(50% 3.2592 0.3350)', 1.0000),
            ('lab(60.2574% -34.0099 36.2677)', 'lab(60.4626% -34.1751 39.4387)', 1.2644),
            ('lab(63.0109% -31.0961 -5.8663)', 'lab(62.8187% -29.7946 -4.0864)', 1.2630),
            ('lab(61.2901% 3.7196 -5.3901)', 'lab(61.4292% 2.2480 -4.9620)', 1.8731),
            ('lab(35.0831% -44.1164 3.7933)', 'lab(35.0232% -40.0716 1.5901)', 1.8645),
            ('lab(22.7233% 20.0904 -46.6940)', 'lab(23.0331% 14.9730 -42.5619)', 2.0373),
            ('lab(36.4612% 47.8580 18.3852)', 'lab(36.2715% 50.5065 21.2231)', 1.4146),
            ('lab(90.8027% -2.0831 1.4410)', 'lab(91.1528% -1.6435 0.0447)', 1.4441),
            ('lab(90.9257% -0.5406 -0.9208)', 'lab(88.6381% -0.8985 -0.7239)', 1.5381),
            ('lab(6.7747% -0.2908 -2.4247)', 'lab(5.8714% -0.0985 -2.2286)', 0.6377),
            ('lab(2.0776% 0.0795 -1.1350)', 'lab(0.9033% -0.0636 -0.5514)', 0.9082)
        ]
    )
    def test_delta_e_2000(self, color1, color2, value):
        """Test delta e 2000."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="2000"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'blue', 184.0129),
        ]
    )
    def test_euclidean(self, color1, color2, value):
        """Test Euclidean distance."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).distance(color2),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'blue', 1.4142),
        ]
    )
    def test_euclidean_different_space(self, color1, color2, value):
        """Test Euclidean distance."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).distance(color2, space="srgb"),
            value,
            rounding=4
        )


class TestDistanceSpecifcCases(util.ColorAsserts, unittest.TestCase):
    """Test distance specific cases."""

    def test_delta_e_alternate_calls(self):
        """Test alternative delta e calls."""

        self.assertCompare(
            Color('red').delta_e('blue', method='2000'),
            Color('red').delta_e_2000('blue')
        )

    def test_delta_e_alternate_calls_with_params(self):
        """Test alternative delta e calls with parameters."""

        self.assertCompare(
            Color('red').delta_e('blue', method='hyab', space="din99o"),
            Color('red').delta_e_hyab('blue', space="din99o")
        )

    def test_hyab_bad_space(self):
        """Test HyAB with bad space."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('orange', method="hyab", space="lch")
