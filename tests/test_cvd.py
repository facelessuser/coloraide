"""Test CVD method."""
from coloraide import Color
from . import util
import pytest
import unittest


class TestCVD(util.ColorAssertsPyTest):
    """Test distance."""

    @pytest.mark.parametrize(
        'color1,color2,deficiency,method,severity',
        [
            ('red', 'rgb(104.96 91.131 13.778)', 'protan', 'brettel', 1),
            ('orange', 'rgb(200.46 174.78 6.9316)', 'protan', 'brettel', 1),
            ('yellow', 'rgb(286.95 250.72 -5.1084)', 'protan', 'brettel', 1),
            ('green', 'rgb(137.49 119.18 -4.1668)', 'protan', 'brettel', 1),
            ('blue', 'rgb(-159.05 58.055 255.2)', 'protan', 'brettel', 1),
            ('indigo', 'rgb(-73.334 35.005 130.19)', 'protan', 'brettel', 1),
            ('violet', 'rgb(87.172 152.44 238.47)', 'protan', 'brettel', 1),
            ('red', 'rgb(162.13 139.68 -38.405)', 'deutan', 'brettel', 1),
            ('orange', 'rgb(216.24 188.13 -24.868)', 'deutan', 'brettel', 1),
            ('yellow', 'rgb(279.2 244.17 20.224)', 'deutan', 'brettel', 1),
            ('green', 'rgb(119.84 104.29 17.436)', 'deutan', 'brettel', 1),
            ('blue', 'rgb(-138.37 90.974 254.11)', 'deutan', 'brettel', 1),
            ('indigo', 'rgb(-49.268 57.397 129.15)', 'deutan', 'brettel', 1),
            ('violet', 'rgb(147.86 179.22 235.86)', 'deutan', 'brettel', 1),
            ('red', 'rgb(256.51 -28.291 78.438)', 'tritan', 'brettel', 1),
            ('orange', 'rgb(262.4 152.8 166.25)', 'tritan', 'brettel', 1),
            ('yellow', 'rgb(271.78 239.08 242.15)', 'tritan', 'brettel', 1),
            ('green', 'rgb(58.612 117.1 135.86)', 'tritan', 'brettel', 1),
            ('blue', 'rgb(-102.2 95.731 134.67)', 'tritan', 'brettel', 1),
            ('indigo', 'rgb(53.643 48.018 48.534)', 'tritan', 'brettel', 1),
            ('violet', 'rgb(226.56 149.29 158.01)', 'tritan', 'brettel', 1),

            ('red', 'rgb(92.76 92.76 14.209)', 'protan', 'vienot', 1),
            ('orange', 'rgb(177.81 177.81 9.1864)', 'protan', 'vienot', 1),
            ('yellow', 'rgb(255 255 0)', 'protan', 'vienot', 1),
            ('green', 'rgb(121.34 121.34 -3.1792)', 'protan', 'vienot', 1),
            ('blue', 'rgb(0 0 255)', 'protan', 'vienot', 1),
            ('indigo', 'rgb(21.312 21.312 130.08)', 'protan', 'vienot', 1),
            ('violet', 'rgb(147.05 147.05 238.35)', 'protan', 'vienot', 1),
            ('red', 'rgb(146.65 146.65 -40.784)', 'deutan', 'vienot', 1),
            ('orange', 'rgb(196.84 196.84 -30.998)', 'deutan', 'vienot', 1),
            ('yellow', 'rgb(255 255 0)', 'deutan', 'vienot', 1),
            ('green', 'rgb(109.09 109.09 14.91)', 'deutan', 'vienot', 1),
            ('blue', 'rgb(0 0 255)', 'deutan', 'vienot', 1),
            ('indigo', 'rgb(39.146 39.146 129.58)', 'deutan', 'vienot', 1),
            ('violet', 'rgb(170.88 170.88 236.29)', 'deutan', 'vienot', 1),
            ('red', 'rgb(255 0 0)', 'tritan', 'vienot', 1),
            ('orange', 'rgb(261.32 154.68 154.68)', 'tritan', 'vienot', 1),
            ('yellow', 'rgb(271.38 239.49 239.49)', 'tritan', 'vienot', 1),
            ('green', 'rgb(50.833 119.81 119.81)', 'tritan', 'vienot', 1),
            ('blue', 'rgb(-108.83 101.99 101.99)', 'tritan', 'vienot', 1),
            ('indigo', 'rgb(53.573 48.087 48.087)', 'tritan', 'vienot', 1),
            ('violet', 'rgb(225.76 150.49 150.49)', 'tritan', 'vienot', 1),

            ('red', 'rgb(108.79 95.027 -12.596)', 'protan', 'machado', 1),
            ('orange', 'rgb(195.42 171.59 -40.805)', 'protan', 'machado', 1),
            ('yellow', 'rgb(276.72 243.54 -64.46)', 'protan', 'machado', 1),
            ('green', 'rgb(131.07 114.46 -26.091)', 'protan', 'machado', 1),
            ('blue', 'rgb(-124.94 88.706 260.74)', 'protan', 'machado', 1),
            ('indigo', 'rgb(-52.54 48.562 133)', 'protan', 'machado', 1),
            ('violet', 'rgb(120.65 161.38 241.7)', 'protan', 'machado', 1),
            ('red', 'rgb(163.22 144.28 -28.312)', 'deutan', 'machado', 1),
            ('orange', 'rgb(216.62 192.97 13.854)', 'deutan', 'machado', 1),
            ('yellow', 'rgb(279.03 249.61 49.346)', 'deutan', 'machado', 1),
            ('green', 'rgb(119.39 106.36 24.233)', 'deutan', 'machado', 1),
            ('blue', 'rgb(-131.27 61.499 251.48)', 'deutan', 'machado', 1),
            ('indigo', 'rgb(-43.863 48.637 127.89)', 'deutan', 'machado', 1),
            ('violet', 'rgb(151.4 175.26 234.64)', 'deutan', 'machado', 1),
            ('red', 'rgb(281.76 -79.111 14.888)', 'tritan', 'machado', 1),
            ('orange', 'rgb(278.9 142.32 140.64)', 'tritan', 'machado', 1),
            ('yellow', 'rgb(274.08 237.68 217.31)', 'tritan', 'machado', 1),
            ('green', 'rgb(-34.707 123.82 107.76)', 'tritan', 'machado', 1),
            ('blue', 'rgb(-117.27 107.2 149.76)', 'tritan', 'machado', 1),
            ('indigo', 'rgb(62.17 46.101 73.836)', 'tritan', 'machado', 1),
            ('violet', 'rgb(243.86 141.14 173.06)', 'tritan', 'machado', 1),

            ('red', 'red', 'protan', 'machado', 0),
            ('red', 'rgb(238.14 47.812 -9.4884)', 'protan', 'machado', 0.1),
            ('red', 'rgb(222.58 64.361 -15.379)', 'protan', 'machado', 0.2),
            ('red', 'rgb(207.94 74.375 -18.565)', 'protan', 'machado', 0.3),
            ('red', 'rgb(193.92 81.127 -20.283)', 'protan', 'machado', 0.4),
            ('red', 'rgb(180.29 85.877 -20.99)', 'protan', 'machado', 0.5),
            ('red', 'rgb(166.81 89.269 -20.889)', 'protan', 'machado', 0.6),
            ('red', 'rgb(153.24 91.676 -20.06)', 'protan', 'machado', 0.7),
            ('red', 'rgb(139.3 93.339 -18.496)', 'protan', 'machado', 0.8),
            ('red', 'rgb(124.66 94.418 -16.098)', 'protan', 'machado', 0.9),

            ('red', 'rgb(193.92 81.127 -20.283)', 'protan', 'machado', 0.4),
            ('red', 'rgb(191.3 82.103 -20.426)', 'protan', 'machado', 0.42),
            ('red', 'rgb(187.27 83.542 -20.639)', 'protan', 'machado', 0.45),
            ('red', 'rgb(184.52 84.486 -20.78)', 'protan', 'machado', 0.47),
            ('red', 'rgb(181.72 85.416 -20.92)', 'protan', 'machado', 0.49),

            ('red', 'red', 'protan', 'brettel', 0),
            ('red', 'rgb(245.12 26.262 1.4195)', 'protan', 'brettel', 0.1),
            ('red', 'rgb(234.68 39.752 2.8389)', 'protan', 'brettel', 0.2),
            ('red', 'rgb(223.59 49.65 4.2584)', 'protan', 'brettel', 0.3),
            ('red', 'rgb(211.73 57.759 5.6778)', 'protan', 'brettel', 0.4),
            ('red', 'rgb(198.91 64.753 7.0973)', 'protan', 'brettel', 0.5),
            ('red', 'rgb(184.92 70.971 8.5168)', 'protan', 'brettel', 0.6),
            ('red', 'rgb(169.39 76.609 9.9362)', 'protan', 'brettel', 0.7),
            ('red', 'rgb(151.76 81.795 11.31)', 'protan', 'brettel', 0.8),
            ('red', 'rgb(131.02 86.615 12.584)', 'protan', 'brettel', 0.9),

            ('red', 'red', 'protan', 'vienot', 0),
            ('red', 'rgb(244.74 26.886 1.4728)', 'protan', 'vienot', 0.1),
            ('red', 'rgb(233.87 40.585 2.9456)', 'protan', 'vienot', 0.2),
            ('red', 'rgb(222.3 50.636 4.4184)', 'protan', 'vienot', 0.3),
            ('red', 'rgb(209.87 58.87 5.8912)', 'protan', 'vienot', 0.4),
            ('red', 'rgb(196.38 65.973 7.364)', 'protan', 'vienot', 0.5),
            ('red', 'rgb(181.57 72.287 8.8367)', 'protan', 'vienot', 0.6),
            ('red', 'rgb(164.99 78.013 10.31)', 'protan', 'vienot', 0.7),
            ('red', 'rgb(145.92 83.279 11.702)', 'protan', 'vienot', 0.8),
            ('red', 'rgb(122.98 88.173 12.996)', 'protan', 'vienot', 0.9),

            ('red', Color('red').filter('tritan'), 'tritan', 'brettel', 1),
            ('red', Color('red').filter('protan'), 'protan', 'vienot', 1),
            ('red', Color('red').filter('deutan'), 'deutan', 'vienot', 1),
            ('red', Color('red').filter('tritan', 0.5), 'tritan', 'brettel', 0.5),
            ('red', Color('red').filter('protan', 0.5), 'protan', 'machado', 0.5),
            ('red', Color('red').filter('deutan', 0.5), 'deutan', 'machado', 0.5)
        ]
    )
    def test_cvd(self, color1, color2, deficiency, method, severity):
        """Test CVD."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertColorEqual(
            Color(color1).filter(deficiency, severity, method=method),
            Color(color2) if isinstance(color2, str) else color2
        )


class TestBad(unittest.TestCase):
    """Test bad cases."""

    def test_bad_method(self):
        """Test empty list."""

        with self.assertRaises(ValueError):
            Color('red').filter('protan', method='bad')
