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

    def _on_convert(self):
        """
        Run after a convert operation.

        Gives us an opportunity to normalize hues.
        """

        if not (0.0 <= self.hue <= 360.0):
            self.hue = self.hue % 360.0
