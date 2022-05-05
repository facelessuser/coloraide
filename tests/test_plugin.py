"""Test plugins and general configuration."""
import unittest
from coloraide import Color
from coloraide import util as cutil
from . import util


class TestCustom(util.ColorAsserts, unittest.TestCase):
    """Test custom overrides and plugins."""

    def test_override_precision(self):
        """Test precision override."""

        class Color2(Color):
            """Color."""

            PRECISION = 3

        self.assertEqual(
            Color('color(srgb 0.1234567 0.1234567 0.1234567)').to_string(color=True),
            'color(srgb 0.12346 0.12346 0.12346)'
        )

        self.assertEqual(
            Color2('color(srgb 0.1234567 0.1234567 0.1234567)').to_string(color=True),
            'color(srgb 0.123 0.123 0.123)'
        )

    def test_override_fit(self):
        """Test fit override."""

        class Color2(Color):
            """Color."""

            FIT = "clip"

        self.assertEqual(
            Color('color(srgb 2 -1 0)').fit().to_string(),
            'rgb(255 118.31 100.77)'
        )

        self.assertEqual(
            Color2('color(srgb 2 -1 0)').fit().to_string(),
            'rgb(255 0 0)'
        )

    def test_override_interpolate(self):
        """Test interpolation override."""

        class Color2(Color):
            """Color."""

            INTERPOLATE = "din99o"

        self.assertEqual(
            Color('red').mix('green').to_string(),
            Color('red').mix('green', space=cutil.DEF_INTERPOLATE).to_string()
        )
        self.assertEqual(
            Color2('red').mix('green').to_string(),
            Color2('red').mix('green', space='din99o').to_string()
        )

    def test_override_harmony(self):
        """Test harmony override."""

        class Color2(Color):
            """Color."""

            HARMONY = "hsl"

        self.assertEqual(
            Color('red').harmony('complement'),
            Color('red').harmony('complement', space=Color.HARMONY)
        )
        self.assertEqual(
            Color2('red').harmony('complement'),
            Color2('red').harmony('complement', space='hsl')
        )

    def test_override_delta_e(self):
        """Test delta e override."""

        class Color2(Color):
            """Color."""

            DELTA_E = "2000"

        self.assertCompare(
            Color('red').delta_e("blue"),
            184.01905
        )

        self.assertCompare(
            Color2('red').delta_e("blue"),
            55.79977
        )

    def test_plugin_registration_space(self):
        """Test plugin registration of `Space`."""

        from coloraide.spaces import jzazbz

        expected = Color('red').convert('jzazbz').to_string()

        # Deregistration should have taken place
        class Custom(Color):
            pass

        Custom.deregister('space:jzazbz')
        with self.assertRaises(ValueError):
            Custom('red').convert('jzazbz')

        # But it should not affect the base class
        self.assertEqual(Color('red').convert('jzazbz').to_string(), expected)

        # Now it is registered again
        Custom.register(jzazbz.Jzazbz)
        self.assertEqual(Custom('red').convert('jzazbz').to_string(), expected)

    def test_plugin_registration_delta_e(self):
        """Test plugin registration of `DeltaE`."""

        from coloraide.distance import delta_e_z

        expected = Color('red').delta_e('green', method='jz')

        # Deregistration should have taken place
        class Custom(Color):
            pass

        Custom.deregister('delta-e:jz')
        with self.assertRaises(ValueError):
            Custom('red').delta_e('green', method='jz')

        # But it should not affect the base class
        self.assertEqual(Color('red').delta_e('green', method='jz'), expected)

        # Now it is registered again
        Custom.register(delta_e_z.DEZ)
        self.assertEqual(Custom('red').delta_e('green', method='jz'), expected)

    def test_plugin_registration_fit(self):
        """Test plugin registration of `Fit`."""

        from coloraide.gamut import fit_lch_chroma

        expected = Color('color(srgb 110% 140% 20%)').fit(method='lch-chroma').to_string()

        # Deregistration should have taken place
        class Custom(Color):
            pass

        Custom.deregister('fit:lch-chroma')
        with self.assertRaises(ValueError):
            Custom('color(srgb 110% 140% 20%)').fit(method='lch-chroma')

        # But it should not affect the base class
        self.assertEqual(Color('color(srgb 110% 140% 20%)').fit(method='lch-chroma').to_string(), expected)

        # Now it is registered again
        Custom.register(fit_lch_chroma.LchChroma)
        self.assertEqual(Custom('color(srgb 110% 140% 20%)').fit(method='lch-chroma').to_string(), expected)

    def test_plugin_registration_cat(self):
        """Test plugin registration of `cat`."""

        from coloraide.cat import VonKries, WHITES

        expected = [0.42980066937825656, 0.21417803538899305, 0.014645639757305108]

        # Deregistration should have taken place
        class Custom(Color):
            pass

        Custom.deregister('cat:von-kries')
        c1 = Custom('red').convert('xyz-d65')
        with self.assertRaises(ValueError):
            Custom.chromatic_adaptation(
                WHITES['2deg']['D65'],
                WHITES['2deg']['D50'],
                c1[:-1],
                method='von-kries'
            )

        # But it should not affect the base class
        self.assertEqual(
            Color.chromatic_adaptation(
                WHITES['2deg']['D65'],
                WHITES['2deg']['D50'],
                c1[:-1],
                method='von-kries'
            ),
            expected
        )

        # Now it is registered again
        Custom.register(VonKries)
        self.assertEqual(
            Custom.chromatic_adaptation(
                WHITES['2deg']['D65'],
                WHITES['2deg']['D50'],
                c1[:-1],
                method='von-kries'
            ),
            expected
        )

    def test_plugin_registration_filter(self):
        """Test plugin registration of `filter`."""

        from coloraide.filters.w3c_filter_effects import Sepia

        # Deregistration should have taken place
        class Custom(Color):
            pass

        Custom.deregister('filter:sepia')
        color = Color('red').filter('sepia')

        with self.assertRaises(ValueError):
            Custom('red').filter('sepia')

        # Now it is registered again
        Custom.register(Sepia)
        self.assertColorEqual(
            Custom('red').filter('sepia'),
            color
        )

    def test_deregister_all_category(self):
        """Test deregistration of all plugins in a category."""

        class Custom(Color):
            pass

        Custom.deregister('fit:*')
        self.assertEqual(Custom.FIT_MAP, {})
        self.assertNotEqual(Custom.CS_MAP, {})

    def test_deregister_all(self):
        """Test deregistration of all plugins."""

        class Custom(Color):
            pass

        Custom.deregister('*')
        self.assertEqual(Custom.FIT_MAP, {})
        self.assertEqual(Custom.CS_MAP, {})
        self.assertEqual(Custom.DE_MAP, {})

    def test_reserved_registration_fit(self):
        """Test override registration of reserved fit method."""

        from coloraide.gamut import Fit

        class Custom(Color):
            pass

        class CustomFit(Fit):
            NAME = 'clip'

            @staticmethod
            def fit(color):
                return [0, 0, 0]

        with self.assertRaises(ValueError):
            Custom.register(CustomFit, overwrite=True)

    def test_bad_registration_type(self):
        """Test bad registration type."""

        class Custom(Color):
            pass

        class BadClass:
            pass

        with self.assertRaises(TypeError):
            Custom.register(BadClass)

    def test_bad_registration_star(self):
        """Test bad registration type."""

        from coloraide.distance import DeltaE

        class Custom(Color):
            pass

        class CustomDE(DeltaE):
            NAME = '*'

            @staticmethod
            def distance(color, sample, **kwargs):
                return 0

        with self.assertRaises(ValueError):
            Custom.register(CustomDE)

    def test_bad_registration_exists(self):
        """Test bad registration of plugin that exists."""

        from coloraide.spaces.jzazbz import Jzazbz

        class Custom(Color):
            pass

        with self.assertRaises(ValueError):
            Custom.register(Jzazbz)

        Custom.register(Jzazbz, overwrite=True)

    def test_bad_deregister_category(self):
        """Test bad deregistration category."""

        class Custom(Color):
            pass

        with self.assertRaises(ValueError):
            Custom.deregister('bad:srgb')

    def test_bad_deregister_plugin(self):
        """Test bad deregistration category."""

        class Custom(Color):
            pass

        with self.assertRaises(ValueError):
            Custom.deregister('space:bad')

    def test_reserved_deregistration_fit(self):
        """Test deregistration of reserved fit method."""

        class Custom(Color):
            pass

        with self.assertRaises(ValueError):
            Custom.deregister('fit:clip')
