"""Test distance methods."""
from coloraide.everything import ColorAll as Color
from . import util
import pytest
import unittest


class TestDistance(util.ColorAssertsPyTest):
    """Test distance."""

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
            ('red', 'orange', 79.0759),
            ('red', 'yellow', 149.1486),
            ('red', 'green', 139.9281),
            ('red', 'blue', 195.9973),
            ('red', 'indigo', 156.5844),
            ('red', 'violet', 123.1464),
            ('red', 'white', 151.3129),
            ('red', 'black', 157.7871),
            ('red', 'gray', 104.8979),
            ('red', 'red', 0),
            ('orange', 'red', 79.0759),
            ('yellow', 'red', 149.1486),
            ('green', 'red', 139.9281),
            ('blue', 'red', 195.9973),
            ('indigo', 'red', 156.5844),
            ('violet', 'red', 123.1464),
            ('white', 'red', 151.3129),
            ('black', 'red', 157.7871),
            ('gray', 'red', 104.8979)
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
            ('red', 'orange', 137.1706),
            ('red', 'yellow', 207.1558),
            ('red', 'green', 238.2887),
            ('red', 'blue', 349.7161),
            ('red', 'indigo', 260.892),
            ('red', 'violet', 188.922),
            ('red', 'white', 232.6248),
            ('red', 'black', 370.0251),
            ('red', 'gray', 204.962),
            ('red', 'red', 0),
            ('orange', 'red', 137.1706),
            ('yellow', 'red', 207.1558),
            ('green', 'red', 238.2887),
            ('blue', 'red', 349.7161),
            ('indigo', 'red', 260.892),
            ('violet', 'red', 188.922),
            ('white', 'red', 232.6248),
            ('black', 'red', 370.0251),
            ('gray', 'red', 204.962)
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
            ('red', 'orange', 45.7235),
            ('red', 'yellow', 69.0519),
            ('red', 'green', 79.4296),
            ('red', 'blue', 116.572),
            ('red', 'indigo', 86.964),
            ('red', 'violet', 62.974),
            ('red', 'white', 77.5416),
            ('red', 'black', 123.3417),
            ('red', 'gray', 68.3207),
            ('red', 'red', 0),
            ('orange', 'red', 45.7235),
            ('yellow', 'red', 69.0519),
            ('green', 'red', 79.4296),
            ('blue', 'red', 116.572),
            ('indigo', 'red', 86.964),
            ('violet', 'red', 62.974),
            ('white', 'red', 77.5416),
            ('black', 'red', 123.3417),
            ('gray', 'red', 68.3207)
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
            ('red', 'orange', 61.3442),
            ('red', 'yellow', 114.0364),
            ('red', 'green', 133.1035),
            ('red', 'blue', 176.3085),
            ('red', 'indigo', 128.0797),
            ('red', 'violet', 107.9504),
            ('red', 'black', 117.3239),
            ('red', 'white', 114.5315),
            ('red', 'gray', 104.5506),
            ('red', 'red', 0),
            ('orange', 'red', 61.3442),
            ('yellow', 'red', 114.0364),
            ('green', 'red', 133.1035),
            ('blue', 'red', 176.3085),
            ('indigo', 'red', 128.0797),
            ('violet', 'red', 107.9504),
            ('black', 'red', 117.3239),
            ('white', 'red', 114.5315),
            ('gray', 'red', 104.5506),
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab-d65 50% 30 40)', 'color(--lab-d65 50% 0 0)', 50),
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
            ('red', 'orange', 58.1253),
            ('red', 'yellow', 108.4044),
            ('red', 'green', 130.3599),
            ('red', 'blue', 184.019),
            ('red', 'indigo', 133.2445),
            ('red', 'violet', 110.9902),
            ('red', 'black', 119.8401),
            ('red', 'white', 116.2047),
            ('red', 'gray', 106.8395),
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab 50% 30 40)', 'color(--lab 50% 0 0)', 50),
        ]
    )
    def test_delta_e_76_d50(self, color1, color2, value):
        """Test delta e 76 D50."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="76", space='lab'),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 30.1848),
            ('red', 'yellow', 59.9971),
            ('red', 'green', 50.9748),
            ('red', 'blue', 70.577),
            ('red', 'indigo', 57.3326),
            ('red', 'violet', 42.7662),
            ('red', 'black', 56.3033),
            ('red', 'white', 50.2259),
            ('red', 'gray', 18.3301),
            ('red', 'red', 0),
            ('orange', 'red', 32.4524),
            ('yellow', 'red', 61.315),
            ('green', 'red', 62.8766),
            ('blue', 'red', 61.2377),
            ('indigo', 'red', 65.939),
            ('violet', 'red', 53.2084),
            ('black', 'red', 117.3239),
            ('white', 'red', 114.5315),
            ('gray', 'red', 104.5506),
            # Pythagorean 3, 4, 5 triangle
            ('lab(50% 30 40)', 'lab(50% 0 0)', 15.2334),
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
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab 50% 30 40)', 'color(--lab 50% 0 0)', 15.3846),
        ]
    )
    def test_delta_e_94_d50(self, color1, color2, value):
        """Test delta e 94 D50."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="94", space='lab'),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0.0),
            ('red', 'orange', 35.0602),
            ('red', 'yellow', 68.462),
            ('red', 'green', 81.1088),
            ('red', 'blue', 108.5693),
            ('red', 'indigo', 76.9117),
            ('red', 'violet', 63.8109),
            ('red', 'black', 38.4316),
            ('red', 'white', 36.729),
            ('red', 'gray', 30.279),
            ('red', 'red', 0.0),
            ('orange', 'red', 36.1519),
            ('yellow', 'red', 49.9011),
            ('green', 'red', 58.0162),
            ('blue', 'red', 73.3546),
            ('indigo', 'red', 65.7278),
            ('violet', 'red', 50.8812),
            ('black', 'red', 171.9516),
            ('white', 'red', 164.6293),
            ('gray', 'red', 163.8716),
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab-d65 50% 30 40)', 'color(--lab-d65 50% 0 0)', 19.4894),
            # Brilliant red
            ('lab(38.64% 64.26 52.16)', 'lab(38.59% 62.06 51.11)', 0.882),
            ('lab(38.83% 33.35 26.67)', 'lab(38.69% 31.14 25.21)', 1.1444),
            # Brilliant yellow
            ('lab(84.25% 5.74 96.00)', 'lab(84.46% 8.88 96.49)', 1.635),
            ('lab(84.25% 5.74 96.00)', 'lab(84.52% 5.75 93.09)', 0.9231),
            ('lab(84.25% 5.74 96.00)', 'lab(84.37% 5.86 99.42)', 1.0802)
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
            ('red', 'orange', 32.7965),
            ('red', 'yellow', 64.9048),
            ('red', 'green', 78.8614),
            ('red', 'blue', 114.2301),
            ('red', 'indigo', 79.8767),
            ('red', 'violet', 65.2371),
            ('red', 'black', 38.9135),
            ('red', 'white', 36.7155),
            ('red', 'gray', 30.7143),
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab 50% 30 40)', 'color(--lab 50% 0 0)', 19.4894),
        ]
    )
    def test_delta_e_cmc_d50(self, color1, color2, value):
        """Test delta e CMC D50."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="cmc", space='lab'),
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
            ('red', 'orange', 33.7562),
            ('red', 'yellow', 64.3045),
            ('red', 'green', 72.1805),
            ('red', 'blue', 52.8782),
            ('red', 'indigo', 50.9987),
            ('red', 'violet', 41.3161),
            ('red', 'black', 50.4085),
            ('red', 'white', 45.8128),
            ('red', 'gray', 31.1964),
            ('red', 'red', 0.0),
            ('orange', 'red', 33.7562),
            ('yellow', 'red', 64.3045),
            ('green', 'red', 72.1805),
            ('blue', 'red', 52.8782),
            ('indigo', 'red', 50.9987),
            ('violet', 'red', 41.3161),
            ('black', 'red', 50.4085),
            ('white', 'red', 45.8128),
            ('gray', 'red', 31.1964),
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab-d65 50% 30 40)', 'color(--lab-d65 50% 0 0)', 24.1219),
            # Sharma: http://www2.ece.rochester.edu/~gsharma/
            ('color(--lab-d65 50% 2.6772 -79.7751)', 'color(--lab-d65 50% 0 -82.7485)', 2.0425),
            ('color(--lab-d65 50% 3.1571 -77.2803)', 'color(--lab-d65 50% 0 -82.7485)', 2.8615),
            ('color(--lab-d65 50% 2.8361 -74.0200)', 'color(--lab-d65 50% 0 -82.7485)', 3.4412),
            ('color(--lab-d65 50% -1.3802 -84.2814)', 'color(--lab-d65 50% 0 -82.7485)', 1.0000),
            ('color(--lab-d65 50% -1.1848 -84.8006)', 'color(--lab-d65 50% 0 -82.7485)', 1.0000),
            ('color(--lab-d65 50% -0.9009 -85.5211)', 'color(--lab-d65 50% 0 -82.7485)', 1.0000),
            ('color(--lab-d65 50% 0 0)', 'color(--lab-d65 50% -1 2)', 2.3669),
            ('color(--lab-d65 50% -1 2)', 'color(--lab-d65 50% 0 0)', 2.3669),
            ('color(--lab-d65 50% 2.4900 -0.0010)', 'color(--lab-d65 50% -2.4900 0.0009)', 7.1792),
            ('color(--lab-d65 50% 2.4900 -0.0010)', 'color(--lab-d65 50% -2.4900 0.0010)', 7.1792),
            ('color(--lab-d65 50% 2.4900 -0.0010)', 'color(--lab-d65 50% -2.4900 0.0011)', 7.2195),
            ('color(--lab-d65 50% 2.4900 -0.0010)', 'color(--lab-d65 50% -2.4900 0.0012)', 7.2195),
            ('color(--lab-d65 50% -0.0010 2.4900)', 'color(--lab-d65 50% 0.0009 -2.4900)', 4.8045),
            ('color(--lab-d65 50% -0.0010 2.4900)', 'color(--lab-d65 50% 0.00010 -2.4900)', 4.8045),
            ('color(--lab-d65 50% -0.0010 2.4900)', 'color(--lab-d65 50% 0.0011 -2.4900)', 4.7461),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 50% 0 -2.5)', 4.3065),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 73% 25 -18)', 27.1492),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 61% -5 29)', 22.8977),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 56% -27 -3)', 31.9030),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 58% 24 15)', 19.4535),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 50% 3.1736 0.5854)', 1.0000),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 50% 3.2972 0)', 1.0000),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 50% 1.8634 0.5757)', 1.0000),
            ('color(--lab-d65 50% 2.5 0)', 'color(--lab-d65 50% 3.2592 0.3350)', 1.0000),
            ('color(--lab-d65 60.2574% -34.0099 36.2677)', 'color(--lab-d65 60.4626% -34.1751 39.4387)', 1.2644),
            ('color(--lab-d65 63.0109% -31.0961 -5.8663)', 'color(--lab-d65 62.8187% -29.7946 -4.0864)', 1.2630),
            ('color(--lab-d65 61.2901% 3.7196 -5.3901)', 'color(--lab-d65 61.4292% 2.2480 -4.9620)', 1.8731),
            ('color(--lab-d65 35.0831% -44.1164 3.7933)', 'color(--lab-d65 35.0232% -40.0716 1.5901)', 1.8645),
            ('color(--lab-d65 22.7233% 20.0904 -46.6940)', 'color(--lab-d65 23.0331% 14.9730 -42.5619)', 2.0373),
            ('color(--lab-d65 36.4612% 47.8580 18.3852)', 'color(--lab-d65 36.2715% 50.5065 21.2231)', 1.4146),
            ('color(--lab-d65 90.8027% -2.0831 1.4410)', 'color(--lab-d65 91.1528% -1.6435 0.0447)', 1.4441),
            ('color(--lab-d65 90.9257% -0.5406 -0.9208)', 'color(--lab-d65 88.6381% -0.8985 -0.7239)', 1.5381),
            ('color(--lab-d65 6.7747% -0.2908 -2.4247)', 'color(--lab-d65 5.8714% -0.0985 -2.2286)', 0.6377),
            ('color(--lab-d65 2.0776% 0.0795 -1.1350)', 'color(--lab-d65 0.9033% -0.0636 -0.5514)', 0.9082)
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
            ('red', 'orange', 31.4666),
            ('red', 'yellow', 60.9841),
            ('red', 'green', 70.2367),
            ('red', 'blue', 55.7998),
            ('red', 'indigo', 52.847),
            ('red', 'violet', 41.6922),
            ('red', 'black', 51.3402),
            ('red', 'white', 45.2646),
            ('red', 'gray', 31.4011),
            # Pythagorean 3, 4, 5 triangle
            ('color(--lab 50% 30 40)', 'color(--lab 50% 0 0)', 24.1219),
        ]
    )
    def test_delta_e_2000_d50(self, color1, color2, value):
        """Test delta e 2000 D50."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="2000", space='lab'),
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

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 40.2541),
            ('red', 'yellow', 72.9114),
            ('red', 'green', 72.2197),
            ('red', 'blue', 74.514),
            ('red', 'indigo', 61.3361),
            ('red', 'violet', 44.1253),
            ('red', 'white', 69.1797),
            ('red', 'black', 72.2004),
            ('red', 'gray', 50.2454),
            ('red', 'red', 0),
            ('orange', 'red', 40.2541),
            ('yellow', 'red', 72.9114),
            ('green', 'red', 72.2197),
            ('blue', 'red', 74.514),
            ('indigo', 'red', 61.3361),
            ('violet', 'red', 44.1253),
            ('white', 'red', 69.1797),
            ('black', 'red', 72.2004),
            ('gray', 'red', 50.2454)
        ]
    )
    def test_delta_e_hct(self, color1, color2, value):
        """Test delta e HCT."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="hct"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 37.32),
            ('red', 'yellow', 66.5558),
            ('red', 'green', 68.7175),
            ('red', 'blue', 71.0578),
            ('red', 'indigo', 59.7878),
            ('red', 'violet', 41.6256),
            ('red', 'white', 63.1299),
            ('red', 'black', 74.938),
            ('red', 'gray', 47.5086),
            ('red', 'red', 0),
            ('orange', 'red', 37.32),
            ('yellow', 'red', 66.5558),
            ('green', 'red', 68.7175),
            ('blue', 'red', 71.0578),
            ('indigo', 'red', 59.7878),
            ('violet', 'red', 41.6256),
            ('white', 'red', 63.1299),
            ('black', 'red', 74.938),
            ('gray', 'red', 47.5086)
        ]
    )
    def test_delta_e_cam16(self, color1, color2, value):
        """Test delta e CAM16 UCS."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="cam16"),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 53.9171),
            ('red', 'yellow', 92.4214),
            ('red', 'green', 97.1066),
            ('red', 'blue', 101.0159),
            ('red', 'indigo', 82.9438),
            ('red', 'violet', 59.6913),
            ('red', 'white', 87.6459),
            ('red', 'black', 102.335),
            ('red', 'gray', 69.1376),
            ('red', 'red', 0),
            ('orange', 'red', 53.9171),
            ('yellow', 'red', 92.4214),
            ('green', 'red', 97.1066),
            ('blue', 'red', 101.0159),
            ('indigo', 'red', 82.9438),
            ('violet', 'red', 59.6913),
            ('white', 'red', 87.6459),
            ('black', 'red', 102.335),
            ('gray', 'red', 69.1376)
        ]
    )
    def test_delta_e_cam16_lcd(self, color1, color2, value):
        """Test delta e CAM16 LCD."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="cam16", model='lcd'),
            value,
            rounding=4
        )

    @pytest.mark.parametrize(
        'color1,color2,value',
        [
            ('red', 'red', 0),
            ('red', 'orange', 30.4827),
            ('red', 'yellow', 54.8533),
            ('red', 'green', 57.3138),
            ('red', 'blue', 58.8291),
            ('red', 'indigo', 49.2931),
            ('red', 'violet', 34.3513),
            ('red', 'white', 51.7972),
            ('red', 'black', 60.9053),
            ('red', 'gray', 39.3403),
            ('red', 'red', 0),
            ('orange', 'red', 30.4827),
            ('yellow', 'red', 54.8533),
            ('green', 'red', 57.3138),
            ('blue', 'red', 58.8291),
            ('indigo', 'red', 49.2931),
            ('violet', 'red', 34.3513),
            ('white', 'red', 51.7972),
            ('black', 'red', 60.9053),
            ('gray', 'red', 39.3403)
        ]
    )
    def test_delta_e_cam16_scd(self, color1, color2, value):
        """Test delta e CAM16 SCD."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertCompare(
            Color(color1).delta_e(color2, method="cam16", model='scd'),
            value,
            rounding=4
        )


class TestDistanceSpecificCases(util.ColorAsserts, unittest.TestCase):
    """Test distance specific cases."""

    def test_delta_e_alternate_calls(self):
        """Test alternative delta e calls."""

        self.assertCompare(
            Color('red').delta_e('blue', method='2000'),
            Color('red').delta_e('blue', method='2000')
        )

    def test_delta_e_alternate_calls_with_params(self):
        """Test alternative delta e calls with parameters."""

        self.assertCompare(
            Color('red').delta_e('blue', method='hyab', space="din99o"),
            Color('red').delta_e('blue', method='hyab', space="din99o")
        )

    def test_hyab_bad_space(self):
        """Test HyAB with bad space."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('orange', method="hyab", space="lch")

    def test_76_bad_space(self):
        """Test 76 bad space."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('orange', method="76", space="oklab")

    def test_94_bad_space(self):
        """Test 94 bad space."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('orange', method="94", space="oklab")

    def test_2000_bad_space(self):
        """Test 2000 bad space."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('orange', method="2000", space="oklab")

    def test_cmc_bad_space(self):
        """Test CMC bad space."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('orange', method="cmc", space="oklab")


class TestClosest(util.ColorAsserts, unittest.TestCase):
    """Test closest implementation."""

    def test_closest(self):
        """Test closest."""

        self.assertColorEqual(
            Color('red').closest(['pink', 'green', 'blue', 'orange', 'purple', 'maroon']),
            Color('maroon')
        )

    def test_method(self):
        """Test with different methods."""

        self.assertColorEqual(
            Color('aqua').closest(['pink', 'green', 'blue', 'orange', 'purple', 'maroon'], method='2000'),
            Color('green')
        )

    def test_bad_method(self):
        """Test bad method."""

        with self.assertRaises(ValueError):
            Color('red').closest(['blue'], method='bad')

    def test_no_colors(self):
        """Test empty list."""

        with self.assertRaises(ValueError):
            Color('red').closest([])

    def test_bad_delta_e(self):
        """Test bad delta e input."""

        with self.assertRaises(ValueError):
            Color('red').delta_e('blue', method='bad')
