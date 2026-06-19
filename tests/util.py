"""Color test mix-in."""


class ColorAsserts:
    """Asserts."""

    def assertCompare(self, value1, value2, rounding=5):
        """Compare with rounding."""

        self.assertEqual(round(value1, rounding), round(value2, rounding))

    def assertColorEqual(self, color1, color2, **kwargs):
        """Compare two colors."""

        self.assertEqual(
            color1.serialize(**kwargs),
            color2.serialize(**kwargs)
        )

    def assertColorNotEqual(self, color1, color2, **kwargs):
        """Compare two colors."""

        self.assertNotEqual(
            color1.serialize(**kwargs),
            color2.serialize(**kwargs)
        )


class ColorAssertsPyTest(ColorAsserts):
    """Asserts for `pytest`."""

    def assertEqual(self, a, b):
        """Assert equal."""

        assert a == b, f"{a} != {b}"

    def assertNotEqual(self, a, b):
        """Assert not equal."""

        assert a != b, f"{a} != {b}"
