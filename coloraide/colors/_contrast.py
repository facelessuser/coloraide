"""Contrast."""


def contrast(lum1, lum2):
    """Get contrast ratio."""

    return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)


class Contrast:
    """Contrast."""

    def luminance(self):
        """Get color's luminance."""

        return self.convert("xyz").y

    def contrast(self, color):
        """Compare the contrast ration of this color and the provided color."""

        return contrast(self.luminance(), color.luminance())
