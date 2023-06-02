# Correlated Color Temperature

When anything gets warm enough it will start to give off light, and the hotter it gets, the more energetic the light
gets. As an object increases in temperature, it will shift from the red end of the spectrum to the blue end.

```py play
Steps([Color.blackbody(t) for t in range(1000, 15000, 50)])
```

Correlated color temperature (CCT) is a measurement of the average hue of light as it appears to the eye. It is
expressed as the temperature (in Kelvins) something would need to be heated to glow at approximately the same color.

This response can be mapped with a Planckian or black body locus/curve.

//// html | figure
![Black body curve](images/blackbody.png)

///// html | figcaption
1960 Chromaticity Diagram with black body curve in the range of 1,000K - 100,000K
/////
////

## D~uv~

In addition to CCT, there is also the concept of D~uv~ or ∆~uv~. In the following image we've now drawn lines that
intersect the black body curve. These lines are called isotherms. An isotherm is simply a line connecting points having
the same temperature at a given time or on average over a given period. In the case of colors, it connects a number of
colors that are close to the locus to the same given temperature. Often, when colors are expressed with a CCT they will
also have a ∆~uv~.

//// html | figure
![Isotherms](images/isotherms.png)

///// html | figcaption
1960 Chromaticity Diagram with black body curve and isotherms.
/////
////

We can calculate a color's associated temperature and its offset along the isotherm.

```py play
'CCT: {}K Duv: {}'.format(*Color('yellow').cct())
```

CCT and ∆~uv~ can also be used together to get a specific color that satisfies those requirements.

```py play
Color.blackbody(*Color('yellow').cct())
```

## Out of Gamut Temperatures

It should be noted that `blackbody()` normalizes the returned colors by default as the colors are often much too bright
initially, all having a max luminance. This normalization is usually done under a linear RGB color space, (linear sRGB
being the default). Sometimes, depending on the range of temperature, the color can also fall outside the gamut under
evaluation.

//// html | figure
![Out of gamut CCT](images/cct-gamut.png)

///// html | figcaption
CCT of 1200K in relation to the sRGB gamut.
/////
////

Colors that are outside the gamut will only be approximations under the specified gamut and may not convert back to
exactly the same temperature.

```py play
c = Color.blackbody(1200)
c
c.cct()
```

If a larger gamut is desired, to reduce out of gamut colors, one can be specified by changing `space`. Additionally,
normalization can be turned off entirely by setting it to `None`. When specifying the space under evaluation, it is
encouraged to use linear spaces RGB spaces.

```py play
c1 = Color.blackbody(1200, space='display-p3-linear')
c1
c1.cct()
c2 = Color.blackbody(1200, space=None)
c2
c2.cct()
```

## Limitations

All algorithms to calculate to and from CCT have some limitations. This may be that the algorithm is only good for a
specific range of temperature, it may be be that it can only maintain accuracy of ∆~uv~ within a specific range.

The further a color is away from the black body curve, the less accurate CCT may be, or it may be entirely inaccurate
altogether. Isotherms, the further out they reach, will eventually cross and make associating a color with a temperature
accurately impossible. If the input exceeds the algorithm's specified temperature range, the values may not be
inaccurate and/or the behavior undefined

## Algorithm's

ColorAide currently supports only two approaches to calculating to and from CCT: Robertson 1968 and Ohno 2013 (the
default).

Algorithm       | Key              | Description
--------------- | ---------------- | -----------
Robertson\ 1968 | `robertson-1968` | An approach created by A. R. Robertson and is based on the CIE 2˚ Standard Observer with a range of 1667K - 100000K. Can suffer from moderate errors in certain ranges, but is generally pretty fast and a popular choice.
Ohno\ 2013      | `ohno-2013`      | An approach created by Yoshi Ohno. Utilizes a combined approach of a triangular and parabolic solver. As implemented, current implementation has a range of 1000K - 100000K and generally provides more accurate results when compared to the Robertson approach. Can be little slower, but all around a good default approach. Uses the default CIE 2˚ Standard Observer by default.

To use different algorithm's, just use the `method` keyword. Keep in mind that if you are using a given algorithm for
`blackbody()`, you should use that same algorithm for `cct()` to ensure consistent results.

```py play
Color.blackbody(5000)
Color.blackbody(5000, method='robertson-1968')
```

///  tip | Changing Observer
If desired, the Ohno 2013 approach can use a different standard observer, for instance, the CIE 10˚ Standard Observer.
ColorAide only provides the CIE 2˚ and 10˚ observer by default.

```py play
from coloraide.cmfs import cie_10_deg_observer
from coloraide.temperature import BlackBodyCurve

bb10 = BlackBodyCurve(cmf=cie_10_deg_observer)

Steps([Color.blackbody(t) for t in range(1000, 15000, 50)])
Steps([Color.blackbody(t, blackbody=bb10) for t in range(1000, 15000, 50)])
```
///
