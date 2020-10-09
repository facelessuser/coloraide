# ColorAide

This is still a work in progress.

## Motivation

This is a color library to aide in working with colors. The aim of the project was to provide a way to convert between
different color spaces and provide a few tools for mixing, etc. The heavy influence of modeling after the CSS
specification came from the fact that this project was also started to help with the Sublime Text plugin
[ColorHelper](https://github.com/facelessuser/ColorHelper) which highlights colors, which are more than often, in HTML
and CSS.

We needed a library that could recognize and convert CSS color syntax and output that syntax as well. We wanted to be
able to convert between various color spaces, perform mixing, and a number of other utilities. Our intention is not to
be a one stop shop for handling, but to allow basic color manipulation. Other things can be built on top of this, but
how much we build in is yet to be determined.

As far as conversions and supported colors, it is mainly derived from the latest CSS color draft documents drafts:
https://drafts.csswg.org/css-color/#named-colors. Most of the conversion logic was lifted directly from there. While
the current color space set is CSS specific, it may or may not expand beyond that in the future.

Well into writing this, [color.js](https://github.com/LeaVerou/color.js) was also discovered. Color.js is
created/maintained by the co-authors of some of the CSS color specifications. In the end, that project had a heavy
influence on this project and became a reference implementation for a lot of the logic and behavior, though is some
cases we may deviate. Color.js is written and maintained by coauthors of some of the CSS color specifications, so as we
were generally coded to that specification, it made sense to use the project as a reference. That project also seemed to
take some hints from other popular color projects such as [d3-color](https://github.com/d3/d3-color) and
[chroma.js](https://gka.github.io/chroma.js/).

## Features

- Recognize and convert CSS color syntax into color objects.
- Manipulation of color coordinates.
- Interpolating colors for color mixing.
- Color distancing calculation.
- Contrast and relative luminance calculations.
- Overlaying transparent colors onto other colors.
- Mapping out of gamut colors into color spaces.
- Output colors to CSS strings.

## License

MIT
