# Correlated Color Temperature

When anything gets warm enough it will start to give off light, and the hotter it gets, the more energetic the light
is. As an object increases in temperature, it will shift from the red end of the spectrum to the blue end.

```py play
Steps([Color.blackbody(t, out_space='srgb') for t in range(1000, 15000, 50)])
```

Correlated color temperature (CCT) is a measurement of the average hue of light as it appears to the eye. It is
expressed as the temperature (in Kelvins) something would need to be heated to glow at approximately the same color.

This response can be modeled with a Planckian or black body locus/curve.

//// html | figure
![Black body curve](images/blackbody.png)

///// html | figcaption
1960 Chromaticity Diagram with black body curve in the range of 1,000K - 100,000K
/////
////

## D~uv~

In addition to CCT, there is also the concept of D~uv~ or ∆~uv~. In the following image, we've now drawn perpendicular
lines that intersect the black body curve. These lines are called isotherms. An isotherm is simply a line connecting
points having the same temperature at a given time or on average over a given period. In the case of colors, they
connect a number of colors that are close to the locus with the same temperature.

//// html | figure
![Isotherms](images/isotherms.png)

///// html | figcaption
1960 Chromaticity Diagram with black body curve and isotherms.
/////
////

We can calculate a color's associated temperature and its ∆~uv~ along the associated isotherm.

```py play
'CCT: {}K Duv: {}'.format(*Color('yellow').cct())
```

CCT and ∆~uv~ can also be used together to get a specific color that satisfies those requirements.

```py play
Color.blackbody(*Color('yellow').cct())
```

## Limitations

All algorithms to calculate to and from CCT have some limitations and are approximations, some being more accurate than
others. Many algorithms are only accurate up to a certain temperature range. Additionally, it is recommend that colors
that exhibit a ∆~uv~ larger than |5e-2| should be considered inaccurate, and some algorithm's may not do as well out to
even this limit.

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
encouraged to use linear RGB spaces.

```py play
c1 = Color.blackbody(1200, space='display-p3-linear')
c1
c1.cct()
c2 = Color.blackbody(1200, space=None)
c2
c2.cct()
```

## Algorithms

There are quite a few approaches to calculating to and from CCT, each with their strengths and weaknesses. ColorAide
currently only supports a few approaches.

Algorithm       | Key              | Description
--------------- | ---------------- | -----------
Robertson\ 1968 | `robertson-1968` | Uses the CIE 2˚ Standard Observer and can handle a range of 1667K - 100000K.
Ohno\ 2013      | `ohno-2013`      | Utilizes a combined approach of a triangular and parabolic solver. Current implementation allows for a range of 1000K - 100000K.

### Robertson 1968

An approach created by A. R. Robertson and is based on the CIE 2˚ Standard Observer with a range of 1667K - 100000K.
This approach uses a look up table containing some precalculated points and approximates the points along the black
body curve.

It is not the most accurate method and can suffer from moderate errors in certain ranges, but is generally pretty fast
and probably "good enough" for values within the 1667K - 100000K.

```py play
Color.blackbody(5000, duv=0.02, method='robertson-1968').cct(method='robertson-1968')
```

### Ohno 2013

This is an approach researched by Yoshi Ohno and aims to provide better accuracy. It uses a look up table similar to
the Roberson method and employs a combined approach of a triangular solver and a parabolic solver. This can lead to
high accuracy if the table is large enough.

Additionally, an "automatic expansion" technique can be used that starts with a small table and expands the table on
smaller intervals based on the first solution. This can allow for a high accuracy without having to keep a large table
in memory.

For good accuracy throughout the range of 1000K - 100000K, as ColorAide supports, a very large table would be needed. If
the "automatic expansion" technique was used, without caching the data which would cause the table to balloon in memory,
the process is much slower.

To mitigate the downside of storing a massive table in memory and to reduce the performance issues when using "automatic
expansion", ColorAide uses a moderately sized table and creates a spline to interpolate points in between. The expansion
technique is used to get close to the target using the spline as the data table, and then more accurate values are
calculated for use in the triangular and parabolic solver. This allows us to use a smaller table while mitigating the
performance issues associated with the expansion technique, all while maintaining good accuracy. The technique is still
slower than the [Roberson](#robertson-1968) approach, but it is more accurate.

```py play
Color.blackbody(5000, duv=0.02).cct()
```

If a more _pure_ approach is desired, `exact` can be used to directly use the "automatic expansion" without using the
spline. The values for the table will explicitly be calculated on the fly. Performance will be affected.

```py play
Color.blackbody(5000, duv=0.02).cct(exact=True)
```

///  tip | Changing Observer
If desired, the Ohno 2013 approach can use a different standard observer, for instance, the CIE 10˚ Standard Observer.
ColorAide only provides the CIE 2˚ and 10˚ observer by default. If providing another set of CMFs, they should be at 5nm
resolution or better as that is the current default step size.

```py play
from coloraide import cmfs
from coloraide import cat
from coloraide.temperature.ohno_2013 import Ohno2013, BlackBodyCurve


class Custom(Color):
    ...


Custom.register(
    Ohno2013(BlackBodyCurve(cmfs=cmfs.cie_1964_10deg, white=cat.WHITES['10deg']['D65'])),
    overwrite=True
)

Steps([Color.blackbody(t) for t in range(1000, 15000, 50)])
Steps([Custom.blackbody(t) for t in range(1000, 15000, 50)])
```
///
