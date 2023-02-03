"""Test CAM16 UCS."""
import unittest
from . import util
from coloraide.spaces.cam16 import cam16_to_xyz_d65, CAM16
from collections import namedtuple

CAM16Coords = namedtuple("CAM16Coords", "J C h s Q M H")


class TestCAM16ApperanceModel(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 appearance model."""

    COORDS = CAM16Coords(
        45.33435136131785, 45.26195932727762, 258.92464993097565,
        62.67686398624793, 83.29355481993107, 32.720950777696196, 310.5279473979526
    )

    def test_no_lightness(self):
        """Test conversion failure when no equivalent lightness."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(C=self.COORDS.C, h=self.COORDS.h, env=CAM16.ENV)

    def test_no_chroma(self):
        """Test conversion failure when no equivalent chroma."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(J=self.COORDS.J, h=self.COORDS.h, env=CAM16.ENV)

    def test_no_hue(self):
        """Test conversion failure when no equivalent hue."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, env=CAM16.ENV)

    def test_no_environment(self):
        """Test no test no environment."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h)

    def test_lightness_convert(self):
        """Test convert lightness."""

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16.ENV),
            cam16_to_xyz_d65(Q=self.COORDS.Q, C=self.COORDS.C, h=self.COORDS.h, env=CAM16.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_chroma_convert(self):
        """Test convert chroma."""

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16.ENV),
            cam16_to_xyz_d65(Q=self.COORDS.Q, s=self.COORDS.s, h=self.COORDS.h, env=CAM16.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16.ENV),
            cam16_to_xyz_d65(Q=self.COORDS.Q, M=self.COORDS.M, h=self.COORDS.h, env=CAM16.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_convert(self):
        """Test convert hue."""

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16.ENV),
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=CAM16.ENV)
        ):
            self.assertCompare(a, b, 14)
