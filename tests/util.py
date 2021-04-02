"""Color test mix-in."""


class ColorAsserts:
    """Asserts."""

    def assertCompare(self, value1, value2, rounding=5):
        """Compare with rounding."""

        self.assertEqual(round(value1, rounding), round(value2, rounding))

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
