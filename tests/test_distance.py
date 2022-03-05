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
            ('red', 'orange', 'lab', 75.3815),
            ('red', 'orange', 'lab-d65', 79.0759),
            ('red', 'orange', 'luv', 128.225),
            ('red', 'orange', 'din99o', 45.6156),
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
            ('red', 'orange', 75.3815),
            ('red', 'yellow', 142.6905),
            ('red', 'green', 138.1262),
            ('red', 'blue', 207.0731),
            ('red', 'indigo', 163.2557),
            ('red', 'violet', 125.2543),
            ('red', 'white', 152.5466),
            ('red', 'black', 161.1277),
            ('red', 'gray', 107.5427),
            ('red', 'red', 0),
            ('orange', 'red', 75.3815),
            ('yellow', 'red', 142.6905),
            ('green', 'red', 138.1262),
            ('blue', 'red', 207.0731),
            ('indigo', 'red', 163.2557),
            ('violet', 'red', 125.2543),
            ('white', 'red', 152.5466),
            ('black', 'red', 161.1277),
            ('gray', 'red', 107.5427)
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
            ('red', 'orange', 32.4106),
            ('red', 'yellow', 63.8178),
            ('red', 'green', 70.1862),
            ('red', 'blue', 74.4057),
            ('red', 'indigo', 67.6052),
            ('red', 'violet', 51.6698),
            ('red', 'white', 65.6938),
            ('red', 'black', 75.9837),
            ('red', 'gray', 49.9157),
            ('red', 'red', 0),
            ('orange', 'red', 32.4106),
            ('yellow', 'red', 63.8178),
            ('green', 'red', 70.1862),
            ('blue', 'red', 74.4057),
            ('indigo', 'red', 67.6052),
            ('violet', 'red', 51.6698),
            ('white', 'red', 65.6938),
            ('black', 'red', 75.9837),
            ('gray', 'red', 49.9157)
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
            ('red', 'violet', 0.1786),
            ('red', 'white', 0.1848),
            ('red', 'black', 0.2109),
            ('red', 'gray', 0.1635),
            ('red', 'red', 0),
            ('orange', 'red', 0.0941),
            ('yellow', 'red', 0.1663),
            ('green', 'red', 0.1996),
            ('blue', 'red', 0.3396),
            ('indigo', 'red', 0.2401),
            ('violet', 'red', 0.1786),
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
            ('red', 'orange', 137.1968),
            ('red', 'yellow', 207.1857),
            ('red', 'green', 238.3213),
            ('red', 'blue', 349.7702),
            ('red', 'indigo', 260.9548),
            ('red', 'violet', 188.9953),
            ('red', 'white', 232.6841),
            ('red', 'black', 370.0395),
            ('red', 'gray', 205.0192),
            ('red', 'red', 0),
            ('orange', 'red', 137.1968),
            ('yellow', 'red', 207.1857),
            ('green', 'red', 238.3213),
            ('blue', 'red', 349.7702),
            ('indigo', 'red', 260.9548),
            ('violet', 'red', 188.9953),
            ('white', 'red', 232.6841),
            ('black', 'red', 370.0395),
            ('gray', 'red', 205.0192)
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
            ('red', 'orange', 45.7323),
            ('red', 'yellow', 69.0619),
            ('red', 'green', 79.4404),
            ('red', 'blue', 116.5901),
            ('red', 'indigo', 86.9849),
            ('red', 'violet', 62.9984),
            ('red', 'white', 77.5614),
            ('red', 'black', 123.3465),
            ('red', 'gray', 68.3397),
            ('red', 'red', 0),
            ('orange', 'red', 45.7323),
            ('yellow', 'red', 69.0619),
            ('green', 'red', 79.4404),
            ('blue', 'red', 116.5901),
            ('indigo', 'red', 86.9849),
            ('violet', 'red', 62.9984),
            ('white', 'red', 77.5614),
            ('black', 'red', 123.3465),
            ('gray', 'red', 68.3397)
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
            ('red', 'orange', 58.1253),
            ('red', 'yellow', 108.4044),
            ('red', 'green', 130.3599),
            ('red', 'blue', 184.019),
            ('red', 'indigo', 133.2445),
            ('red', 'violet', 110.9902),
            ('red', 'black', 119.8401),
            ('red', 'white', 116.2047),
            ('red', 'gray', 106.8395),
            ('red', 'red', 0),
            ('orange', 'red', 58.1253),
            ('yellow', 'red', 108.4044),
            ('green', 'red', 130.3599),
            ('blue', 'red', 184.019),
            ('indigo', 'red', 133.2445),
            ('violet', 'red', 110.9902),
            ('black', 'red', 119.8401),
            ('white', 'red', 116.2047),
            ('gray', 'red', 106.8395),
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
            ('red', 'orange', 28.6827),
            ('red', 'yellow', 57.5928),
            ('red', 'green', 48.8419),
            ('red', 'blue', 73.8268),
            ('red', 'indigo', 59.1223),
            ('red', 'violet', 42.5283),
            ('red', 'black', 57.3225),
            ('red', 'white', 49.2723),
            ('red', 'gray', 18.4094),
            ('red', 'red', 0),
            ('orange', 'red', 30.7727),
            ('yellow', 'red', 59.5131),
            ('green', 'red', 62.7354),
            ('blue', 'red', 65.8099),
            ('indigo', 'red', 69.4058),
            ('violet', 'red', 54.8456),
            ('black', 'red', 119.8401),
            ('white', 'red', 116.2047),
            ('gray', 'red', 106.8395),
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
            ('red', 'orange', 32.7965),
            ('red', 'yellow', 64.9048),
            ('red', 'green', 78.8614),
            ('red', 'blue', 114.2301),
            ('red', 'indigo', 79.8767),
            ('red', 'violet', 65.2371),
            ('red', 'black', 38.9135),
            ('red', 'white', 36.7155),
            ('red', 'gray', 30.7143),
            ('red', 'red', 0.0),
            ('orange', 'red', 34.4675),
            ('yellow', 'red', 48.5955),
            ('green', 'red', 57.8963),
            ('blue', 'red', 79.4377),
            ('indigo', 'red', 70.1565),
            ('violet', 'red', 53.0944),
            ('black', 'red', 175.6803),
            ('white', 'red', 168.1651),
            ('gray', 'red', 167.4567),
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
            ('red', 'red', 0),
            ('red', 'orange', 0.2381),
            ('red', 'yellow', 0.4568),
            ('red', 'green', 0.3813),
            ('red', 'blue', 0.5371),
            ('red', 'indigo', 0.422),
            ('red', 'violet', 0.272),
            ('red', 'white', 0.4526),
            ('red', 'black', 0.6788),
            ('red', 'gray', 0.2592),
            ('red', 'red', 0),
            ('orange', 'red', 0.2381),
            ('yellow', 'red', 0.4568),
            ('green', 'red', 0.3813),
            ('blue', 'red', 0.5371),
            ('indigo', 'red', 0.422),
            ('violet', 'red', 0.272),
            ('white', 'red', 0.4526),
            ('black', 'red', 0.6788),
            ('gray', 'red', 0.2592)
        ]
    )
    def test_delta_e_ok(self, color1, color2, value):
        """Test delta e OK."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="ok"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0.0),
            ('red', 'orange', 31.4666),
            ('red', 'yellow', 60.9841),
            ('red', 'green', 70.2367),
            ('red', 'blue', 55.7998),
            ('red', 'indigo', 52.847),
            ('red', 'violet', 41.6922),
            ('red', 'black', 51.3402),
            ('red', 'white', 45.2646),
            ('red', 'gray', 31.4011),
            ('red', 'red', 0.0),
            ('orange', 'red', 31.4666),
            ('yellow', 'red', 60.9841),
            ('green', 'red', 70.2367),
            ('blue', 'red', 55.7998),
            ('indigo', 'red', 52.847),
            ('violet', 'red', 41.6922),
            ('black', 'red', 51.3402),
            ('white', 'red', 45.2646),
            ('gray', 'red', 31.4011),
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
            ('red', 'blue', 184.019),
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
