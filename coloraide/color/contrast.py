"""Color contrast."""


class Contrast:
    """Contrast."""

    def luminance(self):
        """Get color's luminance."""

        return self.convert("xyz-d65").y

    def contrast(self, color):
        """Compare the contrast ratio of this color and the provided color."""

        color = self._handle_color_input(color)
        lum1 = self.luminance()
        lum2 = color.luminance()
        return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)
