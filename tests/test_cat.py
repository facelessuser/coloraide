"""Test chromatic adaptation."""
from coloraide.everything import ColorAll as Color
from coloraide import cat
from coloraide import util as cutil
from . import util
import pytest


class TestCAT(util.ColorAssertsPyTest):
    """Test CAT."""

    @pytest.mark.parametrize(
        'method,cat1,cat2',
        [
            ('bradford', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('von-kries', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('xyz-scaling', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('cat02', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('cmccat97', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('sharp', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('cmccat2000', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50']),
            ('cat16', cat.WHITES['2deg']['D65'], cat.WHITES['2deg']['D50'])

        ]
    )
    def test_cat(self, method, cat1, cat2):
        """Test CAT methods."""

        c1 = Color('white').convert('xyz-d65')
        c2 = Color('xyz-d50', c1.chromatic_adaptation(cat1, cat2, c1[:-1], method=method))
        c3 = Color('xyz-d65', c2.chromatic_adaptation(cat2, cat1, c2[:-1], method=method))
        self.assertColorEqual(c1, c3)
        self.assertColorEqual(c2, Color('xyz-d50', cutil.xy_to_xyz(cat2)))
