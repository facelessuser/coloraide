# ColorAide Plugins

ColorAide implements extendable portions of the `Color` object as plugins. This makes adding things such as new ∆E
methods or even new color spaces quite easy. Currently, ColorAide implements the following areas as plugins:

-   [CCT](./cct.md)
-   [Chromatic adaptation](./cat.md)
-   [Color spaces](./space.md)
-   [Contrast](./contrast.md)
-   [∆E methods](./delta_e.md)
-   [Filters](./filter.md)
-   [Fit/Gamut mapping](./fit.md)
-   [Gamuts](./gamut.md)
-   [Interpolation](./interpolate.md)

While these documents will touch on each plugin, looking at the source code will provide a better view on how plugins
are actually used as all functionality for all of these categories are implemented as plugins in ColorAide.
