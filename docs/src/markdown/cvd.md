# Color Vision Deficiency Simulation

Color blindness or color vision deficiency (CVD) affects approximately 1 in 12 men (8%) and 1 in 200 women. CVD affects
millions of people in the world. Many people have no idea that they are color blind and not seeing the full spectrum
that others see.

CVD simulation allows those who do not suffer with one of the many different variations of color blindness, to simulate
what someone with a CVD would see. Keep in mind that these are just approximations, and that a given type of CVD can be
quite different from person to person in severity.

While it may be impossible to create a simulation the accurately represents everyone, there are a number of algorithms
that have been implemented and tested to some degree to vet their accuracy and usefulness.

## Types of Color Blindness

The human eye has 3 types of cones that are used to perceive colors. Each of these cones can become deficient, either
through genetics, or other means. Each type of cone is responsible for perceiving either red, green, or blue colors.

Color blindness is usually the cause of one or more of these cones not behaving appropriately. There are sever cases
where one of the three cones will not perceive color, and there are others were the cones may just be less sensitive.

### Dichromacy

Dichromacy is a type of color blindness where only two of the cones perceive colors. Protanopia describes the CVD where
the cone responsible for red light does not function, deuteranopia describes the CVD where the green cone doesn't work,
and tritanopia describes deficiencies with the blue cone.

=== "Normal"

    ![Normal](./images/color-wheel.png)

=== "Protanopia"

    ![Protanopia](./images/color-wheel-protan.png)

=== "Deuteranopia"

    ![Deuteranopia](./images/color-wheel-deutan.png)

=== "Tritanopia"

    ![Tritanopia](./images/color-wheel-tritan.png)

By default, ColorAide uses the [Brettel 1997 method](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.496.7153&rep=rep1&type=pdf)
to simulate tritanopia and the [Viénot, Brettel, and Mollon 1999 approach](http://vision.psychol.cam.ac.uk/jdmollon/papers/colourmaps.pdf)
to simulate protanopia and and deuteranopia. While Brettel is probably the best approach for all cases, Viénot is much
faster and does quite well for protanopia and deuteranopia.

```playground
inputs = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
colors = Color(inputs[0]).steps(inputs[1:], steps=10, space='srgb')
colors
ColorRow()
[c.cvd('protan').clip() for c in colors]
ColorRow()
[c.cvd('deutan').clip() for c in colors]
ColorRow()
[c.cvd('tritan').clip() for c in colors]
```

If desired, other approaches can be used, though your mileage may vary:

```playground
inputs = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
colors = Color(inputs[0]).steps(inputs[1:], steps=10, space='srgb')
colors
ColorRow()
[c.cvd('protan', method='brettel').clip() for c in colors]
ColorRow()
[c.cvd('protan', method='vienot').clip() for c in colors]
ColorRow()
[c.cvd('protan', method='machado').clip() for c in colors]
```

### Anomalous Trichromacy

While Dichromacy is probably the more sever case with only two function cones, people with anomalous trichromacy have
three function cones, but not all of the function with full sensitivity. Sometimes, the sensitivity can be so low, that
their ability to perceive color may be close to someone with dichromacy.

While dichromacy may be considered a severity 1, a given case of anomalous trichromacy could be anywhere between 0 and
1, where 0 would be no CVD.

Like dichromacy, the related deficiencies are named in a similar manner: protanomaly (reduced red sensitivity),
deuteranomaly (reduced green sensitivity), or tritanomaly (reduced blue sensitivity).

=== "Normal"

    ![Normal](./images/color-wheel.png)

=== "Protanopia Severity 0.5"

    ![Protanopia 0.5](./images/color-wheel-protan-machado-0.5.png)

=== "Protanopia Severity 0.7"

    ![Protanopia 0.7](./images/color-wheel-protan-machado-0.7.png)

=== "Protanopia Severity 0.9"

    ![Protanopia 0.9](./images/color-wheel-protan-machado-0.9.png)

To represent anomalous trichromacy, ColorAide leans on the [Machado 2009 approach](https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html#Reference)
which has a more nuanced approach to handling severity levels below 1. As the Machado tests did not focus on tritanopia
those results are not really that great, so instead of using Machado for tritanomaly, we just interpolate severity 1
tritanopia against the original color with the given severity factor.

```playground
inputs = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
colors = Color(inputs[0]).steps(inputs[1:], steps=10, space='srgb')
colors
ColorRow()
[c.cvd('protan', 0.75).clip() for c in colors]
ColorRow()
[c.cvd('deutan', 0.75).clip() for c in colors]
ColorRow()
[c.cvd('tritan', 0.75).clip() for c in colors]
```

### Monochromacy / Achromatopsia

Lastly, monochromacy (or achromatopsia) is a condition where a person will see no color, only shades of gray.

=== "Normal"

    ![Normal](./images/color-wheel.png)

=== "Monochromacy / Achromatopsia"

    ![Monochromacy](./images/color-wheel-achroma.png)

ColorAide can simulate this lack of color, or any degree percentage of it by adjusting the severity. Severity is simply
calculated by interpolating the full achromatopsia against the original color.

```playground
inputs = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
colors = Color(inputs[0]).steps(inputs[1:], steps=10, space='srgb')
colors
ColorRow()
[c.cvd('achroma').clip() for c in colors]
ColorRow()
[c.cvd('achroma', 0.75).clip() for c in colors]
ColorRow()
[c.cvd('achroma', 0.50).clip() for c in colors]
```
