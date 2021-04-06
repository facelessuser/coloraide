# Compositing and Blending

## Alpha Compositing

Alpha compositing or alpha blending is the process of combining one image with a background to create the appearance of
partial or full transparency.

ColorAide implements alpha compositing using [Porter Duff Compositing][porter-duff] as described in the current
[Compositing and Blending Level 1][compositing-level-1] specification. Specifically, the [Source Over][source-over]
operator is used.

Given two colors, we can determine the resultant color by applying simple alpha compositing.

Keep in mind, many browsers support color management and may blend in your current display's color space. So some
compositing may appear, at first glance, to not match your browser unless you do so in the correct space. For instance,
if you are on a recent Apple computer in Safari or Chrome, it is likely that your browser matches the `display-p3`
example below. Take a look. Which of the below matches your browser?

<span class="isolate blend-normal dual">
  <span class="circle circle-1"></span>
  <span class="circle circle-2" style="opacity: 0.5"></span>
</span>

=== "Display P3"
    ```color
    Color('#07c7ed').set('alpha', 0.5).composite('#fc3d99', space="display-p3")
    ```

=== "sRGB"
    ```color
    Color('#07c7ed').set('alpha', 0.5).composite('#fc3d99', space="srgb")
    ```

The `composite` function simply runs the colors through the blend `normal` blend mode and then applies alpha
compositing. `composite` is mainly a convenience function to get the result of two colors with at least one having an
opacity of less than 100%.

```color
Color('#07c7ed').set('alpha', 0.5).composite('#fc3d99', space="srgb")
Color('#07c7ed').set('alpha', 0.5).blend('#fc3d99', 'normal', space="srgb")
```

## Blending

Blending is the aspect of compositing that calculates the mixing of colors where the source element and backdrop
overlap. Conceptually, the colors in the source element (top layer) are blended in place with the backdrop
(bottom layer).

<span class="isolate blend-normal dual">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
</span>

But you could do something like multiply the color channels together:

<span class="isolate blend-multiply dual">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
</span>

Or get the color difference:

<span class="isolate blend-difference dual">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
</span>

ColorAide can perform all the blend modes as specified in the the [Compositing and Blending Level 1](https://www.w3.org/TR/compositing-1/)
specification.

Keep in mind, many browsers support color management and may blend in your current display's color space. So some
blending may appear, at first glance, to not match your browser unless you blend in the correct space. For instance, if
you are on a recent Apple computer in Safari or Chrome, it is likely that your browser matches the `display-p3` example
below. Take a look. Which of the below matches your browser?

<span class="isolate blend-multiply dual">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
</span>

=== "Display P3"
    ```color
    Color('#07c7ed').blend('#fc3d99', 'multiply', space="display-p3")
    ```

=== "sRGB"
    ```color
    Color('#07c7ed').blend('#fc3d99', 'multiply', space="srgb")
    ```

If one or both colors have opacity, `blend` will also apply alpha compositing.

<span class="isolate blend-multiply dual">
  <span class="circle circle-1"></span>
  <span class="circle circle-2" style="opacity: 0.5"></span>
</span>

```color
Color('#07c7ed').set('alpha', 0.5).blend('#fc3d99', 'multiply', space="srgb")
Color('#07c7ed').set('alpha', 0.5).blend('#fc3d99', 'multiply', space="display-p3")
```

We can also stack up the compositing. In this example, we use the three colors `#!color #07c7ed`, `#!color #fc3d99`, and
`#!color #f5d311`. We apply 50% transparency to all of them. Note, as all the colors are transparent, and we have
isolated the blend, we must first do a source-over compositing of the colors on top of the `#!color white` background.
We've provided both the P3 and sRGB outputs to make it easy to compare in case your browser blends in one instead of the
other.

<div style="background: white; display: inline-block; padding: 10px;">
<span class="isolate blend-multiply">
  <span class="circle circle-1" style="opacity: 0.5"></span>
  <span class="circle circle-2" style="opacity: 0.5"></span>
  <span class="circle circle-3" style="opacity: 0.5"></span>
</span>
</div>

=== "Display P3"
    ```color
    c1 = Color('#07c7ed').set('alpha', 0.5).blend('white', 'normal', space='display-p3')
    c2 = Color('#fc3d99').set('alpha', 0.5).blend('white', 'normal', space='display-p3')
    c3 = Color('#f5d311').set('alpha', 0.5).blend('white', 'normal', space='display-p3')

    r1 = c2.blend(c3, 'multiply', space='display-p3')
    r2 = c1.blend(c2, 'multiply', space='display-p3')
    r3 = c1.blend(c3, 'multiply', space='display-p3')

    r1, r2, r3

    c1.blend(r1, 'multiply', space='display-p3')
    ```

=== "sRGB"
    ```color
    c1 = Color('#07c7ed').set('alpha', 0.5).blend('white', 'normal', space='srgb')
    c2 = Color('#fc3d99').set('alpha', 0.5).blend('white', 'normal', space='srgb')
    c3 = Color('#f5d311').set('alpha', 0.5).blend('white', 'normal', space='srgb')

    r1 = c2.blend(c3, 'multiply', space='srgb')
    r2 = c1.blend(c2, 'multiply', space='srgb')
    r3 = c1.blend(c3, 'multiply', space='srgb')

    r1, r2, r3

    c1.blend(r1, 'multiply', space='srgb')
    ```

## Blend Modes

<div class="blend-wrap" markdown="1">
<span class="isolate blend-normal">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Normal

The blending formula simply selects the source color.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-multiply">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Multiply

The source color is multiplied by the destination color and replaces the destination.. The resultant color is always at
least as dark as either the source or destination color. Multiplying any color with black results in black. Multiplying
any color with white preserves the original color.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-screen">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Screen

Multiplies the complements of the backdrop and source color values, then complements the result. The result color is
always at least as light as either of the two constituent colors. Screening any color with white produces white;
screening with black leaves the original color unchanged. The effect is similar to projecting multiple photographic
slides simultaneously onto a single screen.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-overlay">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Overlay

Multiplies or screens the colors, depending on the backdrop color value. Source colors overlay the backdrop while
preserving its highlights and shadows. The backdrop color is not replaced but is mixed with the source color to reflect
the lightness or darkness of the backdrop.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-darken">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Darken

Selects the darker of the backdrop and source colors. The backdrop is replaced with the source where the source is
darker; otherwise, it is left unchanged.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-lighten">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Lighten

Selects the lighter of the backdrop and source colors. The backdrop is replaced with the source where the source is
lighter; otherwise, it is left unchanged.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-color-dodge">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Color Dodge

Brightens the backdrop color to reflect the source color. Painting with black produces no changes.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-color-burn">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Color Burn

Darkens the backdrop color to reflect the source color. Painting with white produces no change.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-hard-light">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Hard Light

Multiplies or screens the colors, depending on the source color value. The effect is similar to shining a harsh
spotlight on the backdrop.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-soft-light">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Soft Light

Darkens or lightens the colors, depending on the source color value. The effect is similar to shining a diffused
spotlight on the backdrop.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-difference">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Difference

Subtracts the darker of the two constituent colors from the lighter color. Painting with white inverts the backdrop
color; painting with black produces no change.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-exclusion">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Exclusion

Produces an effect similar to that of the Difference mode but lower in contrast. Painting with white inverts the
backdrop color; painting with black produces no change.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-hue">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Hue

Creates a color with the hue of the source color and the saturation and luminosity of the backdrop color.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-saturation">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Saturation

Creates a color with the saturation of the source color and the hue and luminosity of the backdrop color. Painting with
this mode in an area of the backdrop that is a pure gray (no saturation) produces no change.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-luminosity">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Luminosity

Creates a color with the luminosity of the source color and the hue and saturation of the backdrop color. This produces
an inverse effect to that of the Color mode. This mode is the one you can use to create monochrome "tinted" image
effects like the ones you can see in different website headers.
</div>
</div>

---

<div class="blend-wrap" markdown="1">
<span class="isolate blend-color">
  <span class="circle circle-1"></span>
  <span class="circle circle-2"></span>
  <span class="circle circle-3"></span>
</span>

<div class="blend-content" markdown="1">

### Color

Creates a color with the hue and saturation of the source color and the luminosity of the backdrop color. This preserves
the gray levels of the backdrop and is useful for coloring monochrome images or tinting color images.
</div>
</div>

<style>
.circle {
  display: block;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  position: absolute;
  transition: all 0.5s ease;
  z-index: 10;
}

.isolate label {
    position: absolute;
    bottom: 0;
    width: 100%;
    text-align: center;
}

.circle-1 {
  background: #f5d311;
}

.dual .circle-1 {
  background: #fc3d99;
}

.isolate:not(.dual):hover .circle-1 {
  transform: translateX(-10px) translateY(-7.5px);
}

.isolate.dual:hover .circle-1 {
  transform: translateX(-10px);
}

.circle-2 {
  background: #fc3d99;
  left: 40px;
}

.dual .circle-2 {
  background: #07c7ed;
}

.isolate:not(.dual):hover .circle-2 {
  transform: translateX(10px) translateY(-7.5px);
}

.isolate.dual:hover .circle-2 {
  transform: translateX(20px);
}

.circle-3 {
  background: #07c7ed;
  left: 20px;
  top: 40px;
}

.isolate:not(.dual):hover .circle-3 {
  transform: translateY(7.5px);
}

.isolate {
  display: block;
  height: 120px;
  width:  120px;
  isolation: isolate;
  position: relative;
  margin: 0 10px;
}

.isolate.dual {
  height: 80px;
}

div.blend-wrap {
  display: flex;
  min-height: calc(120px + 0.8em);
  width: 100%;
}

div.blend-wrap > :not(.blend-content) {
  order: 0;
}

div.blend-wrap .isolate {
  margin-top:  0.8em;
}

div.blend-wrap > .blend-content {
  order: 1;
}

.blend-normal .circle {
  mix-blend-mode: normal;
}

.blend-multiply .circle {
  mix-blend-mode: multiply;
}

.blend-screen .circle {
  mix-blend-mode: screen;
}

.blend-overlay .circle {
  mix-blend-mode: overlay;
}

.blend-color-burn .circle {
  mix-blend-mode: color-burn;
}

.blend-color-dodge .circle {
  mix-blend-mode: color-dodge;
}

.blend-exclusion .circle {
  mix-blend-mode: exclusion;
}

.blend-difference .circle {
  mix-blend-mode: difference;
}

.blend-darken .circle {
  mix-blend-mode: darken;
}

.blend-lighten .circle {
  mix-blend-mode: lighten;
}

.blend-soft-light .circle {
  mix-blend-mode: soft-light;
}

.blend-hard-light .circle {
  mix-blend-mode: hard-light;
}

.blend-hue .circle {
  mix-blend-mode: hue;
}

.blend-saturation .circle {
  mix-blend-mode: saturation;
}

.blend-luminosity .circle {
  mix-blend-mode: luminosity;
}

.blend-color .circle {
  mix-blend-mode: color;
}
</style>
