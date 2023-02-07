"""Color test mix-in."""


class ColorAsserts:
    """Asserts."""

    def assertCompare(self, value1, value2, rounding=5):
        """Compare with rounding."""

        self.assertEqual(round(value1, rounding), round(value2, rounding))

    def assertColorEqual(self, color1, color2, *, fit=False, **kwargs):
        """Compare two colors."""

        self.assertEqual(
            color1.to_string(fit=fit, **kwargs),
            color2.to_string(fit=fit, **kwargs)
        )

    def assertColorNotEqual(self, color1, color2, *, fit=False, **kwargs):
        """Compare two colors."""

        self.assertNotEqual(
            color1.to_string(fit=fit, **kwargs),
            color2.to_string(fit=fit, **kwargs)
        )


class ColorAssertsPyTest(ColorAsserts):
    """Asserts for `pytest`."""

    def assertEqual(self, a, b):
        """Assert equal."""

        assert a == b, "{} != {}".format(a, b)

    def assertNotEqual(self, a, b):
        """Assert not equal."""

        assert a != b, "{} != {}".format(a, b)
