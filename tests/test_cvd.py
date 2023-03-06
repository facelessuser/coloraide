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
            ('red', 'rgb(105.67 92.601 12.553)', 'protan', 'brettel', 1),
            ('orange', 'rgb(199.21 175.31 6.3568)', 'protan', 'brettel', 1),
            ('yellow', 'rgb(284.54 250.92 -4.2241)', 'protan', 'brettel', 1),
            ('green', 'rgb(136.02 119.06 -3.6618)', 'protan', 'brettel', 1),
            ('blue', 'rgb(-157.73 58.576 255.17)', 'protan', 'brettel', 1),
            ('indigo', 'rgb(-72.403 35.481 130.16)', 'protan', 'brettel', 1),
            ('violet', 'rgb(90.045 152.99 238.42)', 'protan', 'brettel', 1),
            ('red', 'rgb(161.66 140.69 -38.929)', 'deutan', 'brettel', 1),
            ('orange', 'rgb(215.13 188.94 -25.612)', 'deutan', 'brettel', 1),
            ('yellow', 'rgb(277.47 244.88 19.405)', 'deutan', 'brettel', 1),
            ('green', 'rgb(118.87 104.44 17.474)', 'deutan', 'brettel', 1),
            ('blue', 'rgb(-137.33 90.779 254.11)', 'deutan', 'brettel', 1),
            ('indigo', 'rgb(-48.353 57.44 129.14)', 'deutan', 'brettel', 1),
            ('violet', 'rgb(148.73 179.43 235.83)', 'deutan', 'brettel', 1),
            ('red', 'rgb(256.5 -30.176 79.899)', 'tritan', 'brettel', 1),
            ('orange', 'rgb(262.07 151.94 166.09)', 'tritan', 'brettel', 1),
            ('yellow', 'rgb(270.97 238.06 241.3)', 'tritan', 'brettel', 1),
            ('green', 'rgb(57.569 116.19 136.41)', 'tritan', 'brettel', 1),
            ('blue', 'rgb(-99.163 97.898 138.48)', 'tritan', 'brettel', 1),
            ('indigo', 'rgb(54.973 49.529 50.049)', 'tritan', 'brettel', 1),
            ('violet', 'rgb(227.2 150.28 159.33)', 'tritan', 'brettel', 1),

            ('red', 'rgb(94.181 94.181 12.947)', 'protan', 'vienot', 1),
            ('orange', 'rgb(178.21 178.21 8.2317)', 'protan', 'vienot', 1),
            ('yellow', 'rgb(255 255 0)', 'protan', 'vienot', 1),
            ('green', 'rgb(121.12 121.12 -2.8488)', 'protan', 'vienot', 1),
            ('blue', 'rgb(0 0 255)', 'protan', 'vienot', 1),
            ('indigo', 'rgb(21.782 21.782 130.08)', 'protan', 'vienot', 1),
            ('violet', 'rgb(147.56 147.56 238.31)', 'protan', 'vienot', 1),
            ('red', 'rgb(147.23 147.23 -41.168)', 'deutan', 'vienot', 1),
            ('orange', 'rgb(197.08 197.08 -31.314)', 'deutan', 'vienot', 1),
            ('yellow', 'rgb(255 255 0)', 'deutan', 'vienot', 1),
            ('green', 'rgb(108.91 108.91 15.113)', 'deutan', 'vienot', 1),
            ('blue', 'rgb(0 0 255)', 'deutan', 'vienot', 1),
            ('indigo', 'rgb(39.335 39.335 129.58)', 'deutan', 'vienot', 1),
            ('violet', 'rgb(171.18 171.18 236.26)', 'deutan', 'vienot', 1),
            ('red', 'rgb(255 0 0)', 'tritan', 'vienot', 1),
            ('orange', 'rgb(261.01 154.03 154.03)', 'tritan', 'vienot', 1),
            ('yellow', 'rgb(270.57 238.52 238.52)', 'tritan', 'vienot', 1),
            ('green', 'rgb(49.428 119.3 119.3)', 'tritan', 'vienot', 1),
            ('blue', 'rgb(-106.17 104.82 104.82)', 'tritan', 'vienot', 1),
            ('indigo', 'rgb(54.905 49.602 49.602)', 'tritan', 'vienot', 1),
            ('violet', 'rgb(226.41 151.6 151.6)', 'tritan', 'vienot', 1),

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
            ('red', 'rgb(245.14 26.825 1.274)', 'protan', 'brettel', 0.1),
            ('red', 'rgb(234.73 40.504 2.5479)', 'protan', 'brettel', 0.2),
            ('red', 'rgb(223.67 50.54 3.8219)', 'protan', 'brettel', 0.3),
            ('red', 'rgb(211.84 58.762 5.0958)', 'protan', 'brettel', 0.4),
            ('red', 'rgb(199.07 65.854 6.3698)', 'protan', 'brettel', 0.5),
            ('red', 'rgb(185.13 72.159 7.6438)', 'protan', 'brettel', 0.6),
            ('red', 'rgb(169.66 77.876 8.9177)', 'protan', 'brettel', 0.7),
            ('red', 'rgb(152.12 83.134 10.192)', 'protan', 'brettel', 0.8),
            ('red', 'rgb(131.5 88.021 11.412)', 'protan', 'brettel', 0.9),

            ('red', 'red', 'protan', 'vienot', 0),
            ('red', 'rgb(244.78 27.431 1.3197)', 'protan', 'vienot', 0.1),
            ('red', 'rgb(233.96 41.312 2.6395)', 'protan', 'vienot', 0.2),
            ('red', 'rgb(222.44 51.497 3.9592)', 'protan', 'vienot', 0.3),
            ('red', 'rgb(210.07 59.841 5.279)', 'protan', 'vienot', 0.4),
            ('red', 'rgb(196.66 67.038 6.5987)', 'protan', 'vienot', 0.5),
            ('red', 'rgb(181.94 73.436 7.9184)', 'protan', 'vienot', 0.6),
            ('red', 'rgb(165.48 79.238 9.2382)', 'protan', 'vienot', 0.7),
            ('red', 'rgb(146.57 84.574 10.552)', 'protan', 'vienot', 0.8),
            ('red', 'rgb(123.88 89.533 11.788)', 'protan', 'vienot', 0.9),

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
