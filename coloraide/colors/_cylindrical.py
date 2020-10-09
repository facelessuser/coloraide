"""Cylindrical color space."""


class Cylindrical:
    """Cylindrical space."""

    def is_hue_null(self):
        """Test if hue is null."""

        raise NotImplementedError("Base 'CylindricalSpace' class does not impolement 'is_hue_null'")

    def hue_name(self):
        """Hue channel name."""

        return "hue"

    def hue_index(self):
        """Get hue index."""

        return 0
