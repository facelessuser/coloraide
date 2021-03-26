"""Color test mix-in."""


class ColorAsserts:
    """Asserts."""

    def assertColorEqual(self, color1, color2, fit=False, precision=5):
        """Compare two colors."""

        self.assertEqual(
            color1.to_string(fit=fit, precision=precision),
            color2.to_string(fit=fit, precision=precision)
        )

    def assertColorNotEqual(self, color1, color2, fit=False, precision=5):
        """Compare two colors."""

        self.assertNotEqual(
            color1.to_string(fit=fit, precision=precision),
            color2.to_string(fit=fit, precision=precision)
        )
