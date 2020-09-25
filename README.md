# ColorAide

This is still a work in progress.

This is a color library that to aide in working with colors. It is mainly derived from the current CSS color
specification documents and some of the drafts: https://drafts.csswg.org/css-color/#named-colors. Many of the conversion
algorithms are lifted directly from there.

Well into writing this, I also discovered [Color.js](https://github.com/LeaVerou/color.js) which is created/maintained
by the co-authors of some of the CSS color specifications. Some work, such as their gamut mapping algorithm using Lch
chroma was lifted, it eventually also helped influence some the API, but is not intended to be or match the work they
are doing over there.
