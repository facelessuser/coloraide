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
            ('red', 'rgb(106.54 92.47 12.52)', 'protan', 'brettel', 1),
            ('orange', 'rgb(200.81 175.07 6.2029)', 'protan', 'brettel', 1),
            ('yellow', 'rgb(286.79 250.59 -4.5708)', 'protan', 'brettel', 1),
            ('green', 'rgb(137.15 118.89 -3.7285)', 'protan', 'brettel', 1),
            ('blue', 'rgb(-158.7 58.987 255.17)', 'protan', 'brettel', 1),
            ('indigo', 'rgb(-72.951 35.633 130.17)', 'protan', 'brettel', 1),
            ('violet', 'rgb(88.928 153.07 238.42)', 'protan', 'brettel', 1),
            ('red', 'rgb(162.7 140.17 -38.752)', 'deutan', 'brettel', 1),
            ('orange', 'rgb(216.43 188.3 -25.127)', 'deutan', 'brettel', 1),
            ('yellow', 'rgb(279.09 244.09 20.449)', 'deutan', 'brettel', 1),
            ('green', 'rgb(119.6 104.09 17.644)', 'deutan', 'brettel', 1),
            ('blue', 'rgb(-138.12 91.329 254.1)', 'deutan', 'brettel', 1),
            ('indigo', 'rgb(-48.903 57.629 129.14)', 'deutan', 'brettel', 1),
            ('violet', 'rgb(148.42 179.53 235.83)', 'deutan', 'brettel', 1),
            ('red', 'rgb(256.43 -29.214 77.854)', 'tritan', 'brettel', 1),
            ('orange', 'rgb(262.02 152.05 165.5)', 'tritan', 'brettel', 1),
            ('yellow', 'rgb(270.95 238.09 241.15)', 'tritan', 'brettel', 1),
            ('green', 'rgb(57.038 116.41 135.29)', 'tritan', 'brettel', 1),
            ('blue', 'rgb(-99.677 98.406 136.44)', 'tritan', 'brettel', 1),
            ('indigo', 'rgb(54.969 49.532 50.026)', 'tritan', 'brettel', 1),
            ('violet', 'rgb(227.16 150.35 158.94)', 'tritan', 'brettel', 1),

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
            ('red', 'rgb(245.17 26.775 1.2702)', 'protan', 'brettel', 0.1),
            ('red', 'rgb(234.8 40.437 2.5404)', 'protan', 'brettel', 0.2),
            ('red', 'rgb(223.77 50.46 3.8106)', 'protan', 'brettel', 0.3),
            ('red', 'rgb(211.99 58.673 5.0808)', 'protan', 'brettel', 0.4),
            ('red', 'rgb(199.27 65.756 6.351)', 'protan', 'brettel', 0.5),
            ('red', 'rgb(185.39 72.053 7.6212)', 'protan', 'brettel', 0.6),
            ('red', 'rgb(170 77.763 8.8914)', 'protan', 'brettel', 0.7),
            ('red', 'rgb(152.57 83.015 10.162)', 'protan', 'brettel', 0.8),
            ('red', 'rgb(132.1 87.896 11.38)', 'protan', 'brettel', 0.9),

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

            ('red', Color('red').filter('tritan', out_space='srgb'), 'tritan', 'brettel', 1),
            ('red', Color('red').filter('protan', out_space='srgb'), 'protan', 'vienot', 1),
            ('red', Color('red').filter('deutan', out_space='srgb'), 'deutan', 'vienot', 1),
            ('red', Color('red').filter('tritan', 0.5, out_space='srgb'), 'tritan', 'brettel', 0.5),
            ('red', Color('red').filter('protan', 0.5, out_space='srgb'), 'protan', 'machado', 0.5),
            ('red', Color('red').filter('deutan', 0.5, out_space='srgb'), 'deutan', 'machado', 0.5)
        ]
    )
    def test_cvd(self, color1, color2, deficiency, method, severity):
        """Test CVD."""

        print('color1: ', color1)
        print('color2: ', color2)
        self.assertColorEqual(
            Color(color1).filter(deficiency, severity, out_space='srgb', method=method),
            Color(color2) if isinstance(color2, str) else color2
        )


class TestBad(unittest.TestCase):
    """Test bad cases."""

    def test_bad_method(self):
        """Test empty list."""

        with self.assertRaises(ValueError):
            Color('red').filter('protan', method='bad')
