# ColorAide Plugins

ColorAide implements extendable portions of the `Color` object as plugins. This makes adding things such as new ∆E
methods or even new color spaces quite easy. Currently, ColorAide implements the following areas as plugins:

- [∆E methods](./delta_e.md)
- [Fit/Gamut mapping](./fit.md)
- [Chromatic adaptation](./cat.md)
- [Filters](./filter.md)
- [Contrast](./contrast.md)
- [Color spaces](./space.md)
- [Interpolation](./interpolate.md)

While these documents will touch on each plugin, looking at the source code will provide a better view on how plugins
are actually used as all functionality for all of these categories are implemented as plugins in ColorAide.
