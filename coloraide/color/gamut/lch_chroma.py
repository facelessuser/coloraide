"""Fit by compressing chroma in Lch."""


def fit(base, color):
    """
    Gamut mapping via chroma Lch.

    Algorithm comes from https://colorjs.io/docs/gamut-mapping.html.

    The idea is to hold hue and lightness constant and decrease lightness until
    color comes under gamut.

    We'll use a binary search and at after each stage, we will clip the color
    and compare the distance of the two colors (clipped and current color via binary search).
    If the distance is less than two, we can return the clipped color.

    ---
    Original Authors: Lea Verou, Chris Lilley
    License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
    """

    # Compare clipped against original to
    # judge how far we are off with the worst case fitting
    space = color.space()
    clipped = color.clone()
    clipped.fit(space=space, method="clip", in_place=True)
    base_error = base.delta_e(clipped, method="2000")

    if base_error > 2.3:
        threshold = .001
        # Compare mapped against desired space
        mapcolor = color.convert("lch")
        error = color.delta_e(mapcolor, method="2000")
        low = 0.0
        high = mapcolor.chroma

        # Adjust chroma (using binary search).
        # This helps preserve the color more (in most cases).
        # After each adjustment, see if clipping gets us close enough.
        while (high - low) > threshold and error < base_error:
            clipped = mapcolor.clone()
            clipped.fit(space, method="clip", in_place=True)
            delta = mapcolor.delta_e(clipped, method="2000")
            error = color.delta_e(mapcolor, method="2000")
            if delta - 2 < threshold:
                low = mapcolor.chroma
            else:
                if abs(delta - 2) < threshold:  # pragma: no cover
                    # Can this occur?
                    break
                high = mapcolor.chroma
            mapcolor.chroma = (high + low) / 2
        # Trim off noise allowed by our tolerance
        color.update(mapcolor)
        color.fit(space, method="clip", in_place=True)
    else:
        # We are close enough that we should just clip.
        color.update(clipped)
    return color.coords()
