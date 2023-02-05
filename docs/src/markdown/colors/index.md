# Color Spaces

ColorAide aims to support all the color spaces and models currently offered in modern CSS, such as sRGB, Display P3,
CIELab, Oklab, etc. We also include a number of color spaces that are not available in CSS.

ColorAide registers a subset of the offered color spaces by [default](#default-color-spaces). But additional color
spaces can be registered by subclassing the `Color` object and then registering any [additional](#color-space-map)
required plugins, such as color spaces.

!!! tip "Everything but the Kitchen Sink"
    It is not generally recommended to register all possible color spaces (and plugins in general). The suggested
    approach is to cherry pick additional color spaces as needed by simply subclassing `Color` and then registering the
    desired plugins, but if desired `coloraide.everything.ColorAll` already includes all plugins and can be imported to
    get access to every supported plugin.

## Default Color Spaces

While ColorAide supports a lot of color spaces, it is rare that a user would ever need every color space implemented by
ColorAide available at all times, so to keep the Color object lighter, and color matching logic quicker, the
`coloraide.Color` object does not register all color spaces by default.

&nbsp;                                   | &nbsp;                                           | Default Color\ Spaces           | &nbsp;                                       | &nbsp;
---------------------------------------- | ------------------------------------------------ | ------------------------------- | -------------------------------------------- | -----
[XYZ\ D65](./xyz_d65.md)                 | [XYZ\ D50](./xyz_d50.md)                         | [Linear sRGB](./srgb_linear.md) | [Linear Display\ P3](./display_p3_linear.md) | [Linear A98\ RGB](./a98_rgb.md)
[Linear Rec.\ 2020](./rec2020_linear.md) | [Linear ProPhoto\ RGB](./prophoto_rgb_linear.md) | [sRGB](./srgb.md)               | [Display\ P3](./display_p3.md)               | [A98\ RGB](./a98_rgb.md)
[Rec.\ 2020](./rec2020.md)               | [ProPhoto\ RGB](./prophoto_rgb.md)               | [HSL](./hsl.md)                 | [HSV](./hsv.md)                              | [HWB](./hwb.md)
[Lab](./lab.md)                          | [LCh](./lch.md)                                  | [Lab\ D65](./lab_d65.md)        | [LCh\ D65](./lch_d65.md)                     | [Oklab](./oklab.md)
[OkLCh](./oklch.md)                      |                                                  |                                 |                                              |

## Color Space Map

When registering a plugin, it is important that all required plugins in the conversion path are registered as well.
Below we've provided a diagram of all available color spaces and how they translate to one another.

Click any of the color spaces to jump to the related documentation.

```diagram
flowchart TB

    acescc --- acescg ---- xyz-d65
        acescct --- acescg

    aces2065-1 --- xyz-d65

    oklch --- oklab ----- xyz-d65
        okhsl --- oklab
        okhsv --- oklab

    display-p3 --- display-p3-linear --- xyz-d65

    a98-rgb --- a98-rgb-linear --- xyz-d65

    hwb --- hsv --- hsl --- srgb --- srgb-linear ----- xyz-d65
        orgb --- srgb
        prismatic --- srgb
        hsi --- srgb
        cmy --- srgb
        cmyk --- srgb

    rec2020 --- rec2020-linear --- xyz-d65
        rec2100-pq --- rec2020-linear
        rec2100-hlg --- rec2020-linear

    prophoto-rgb --- prophoto-rgb-linear --- xyz-d50 ----- xyz-d65
        lch --- lab --- xyz-d50

    xyz-d65 --- lab-d65 --- lch-d65

    xyz-d65 --- cam16 --- cam16-jmh
        cam16 --- cam16-ucs
        cam16 --- cam16-scd
        cam16 --- cam16-lcd

    xyz-d65 --- hct

    xyz-d65 --- jzazbz --- jzczhz

    xyz-d65 --- ipt

    xyz-d65 --- ictcp

    xyz-d65 --- igpgtg

    xyz-d65 --- din99o --- lch99o

    xyz-d65 --- hunter-lab

    xyz-d65 --- rlab

    xyz-d65 --- luv --- lchuv
        luv --- hsluv
        luv --- hpluv

    xyz-d65 --- xyy

    xyz-d65(XYZ D65)
    xyz-d50(XYZ D50)
    rec2020(Rec. 2020)
    rec2020-linear(Linear Rec. 2020)
    rec2100-pq(Rec. 2100 PQ)
    rec2100-hlg(Rec. 2100 HLG)
    srgb-linear(Linear sRGB)
    srgb(sRGB)
    hsl(HSL)
    hsv(HSV)
    hwb(HWB)
    display-p3-linear(Linear Display P3)
    display-p3(Display P3)
    a98-rgb-linear(Linear A98 RGB)
    a98-rgb(A98 RGB)
    prophoto-rgb-linear(Linear ProPhoto RGB)
    prophoto-rgb(ProPhoto RGB)
    lab(Lab)
    lch(LCh)
    lab-d65(Lab D65)
    lch-d65(LCh D65)
    oklab(Oklab)
    oklch(OkLCh)
    okhsl(Okhsl)
    okhsv(Okhsv)
    luv(Luv)
    lchuv(LChuv)
    hsluv(HSLuv)
    hpluv(HPLuv)
    din99o(DIN99o)
    lch99o(DIN99o LCh)
    jzazbz(Jzazbz)
    jzczhz(JzCzhz)
    ictcp(ICtCp)
    orgb(oRGB)
    ipt(IPT)
    igpgtg(IgPgTg)
    hunter-lab(Hunter Lab)
    rlab(RLAB)
    hsi(HSI)
    cmy(CMY)
    cmyk(CMYK)
    xyy(xyY)
    prismatic(Prismatic)
    aces2065-1(ACES2065-1)
    acescg(ACEScg)
    acescc(ACEScc)
    acescct(ACEScct)
    cam16(CAM16)
    cam16-jmh(CAM16 JMh)
    cam16-ucs(CAM16 UCS)
    cam16-scd(CAM16 SCD)
    cam16-lcd(CAM16 LCD)
    hct(HCT)

    click xyz-d65 "./xyz_d65/" _self
    click xyz-d50 "./xyz_d50/" _self
    click rec2020 "./rec2020/" _self
    click rec2020-linear "./rec2020_linear/" _self
    click rec2100-pq "./rec2100_pq/" _self
    click rec2100-hlg "./rec2100_hlg/" _self
    click srgb-linear "./srgb_linear/" _self
    click srgb "./srgb/" _self
    click hsl "./hsl/" _self
    click hsv "./hsv/" _self
    click hwb "./hwb/" _self
    click display-p3-linear "./display_p3_linear/" _self
    click display-p3 "./display_p3/" _self
    click a98-rgb-linear "./a98_rgb_linear/" _self
    click a98-rgb "./a98_rgb/" _self
    click prophoto-rgb-linear "./prophoto_rgb_linear/" _self
    click prophoto-rgb "./prophoto_rgb/" _self
    click lab "./lab/" _self
    click lch "./lch/" _self
    click lab-d65 "./lab_d65/" _self
    click lch-d65 "./lch_d65/" _self
    click oklab "./oklab/" _self
    click oklch "./oklch/" _self
    click okhsl "./okhsl/" _self
    click okhsv "./okhsv/" _self
    click luv "./luv/" _self
    click lchuv "./lchuv/" _self
    click hsluv "./hsluv/" _self
    click hpluv "./hpluv/" _self
    click din99o "./din99o/" _self
    click lch99o "./lch99o/" _self
    click jzazbz "./jzazbz/" _self
    click jzczhz "./jzczhz/" _self
    click ictcp "./ictcp/" _self
    click orgb "./orgb/" _self
    click ipt "./ipt/" _self
    click igpgtg "./igpgtg/" _self
    click hunter-lab "./hunter_lab/" _self
    click rlab "./rlab/" _self
    click hsi "./hsi/" _self
    click cmy "./cmy/" _self
    click cmyk "./cmyk/" _self
    click xyy "./xyy/" _self
    click prismatic "./prismatic/" _self
    click aces2065-1 "./aces2065_1/" _self
    click acescg "./acescg/" _self
    click acescc "./acescc/" _self
    click acescct "./acescct/" _self
    click cam16 "./cam16/" _self
    click cam16-jmh "./cam16_jmh/" _self
    click cam16-ucs "./cam16_ucs/" _self
    click cam16-scd "./cam16_scd/" _self
    click cam16-lcd "./cam16_lcd/" _self
    click hct "./hct/" _self
```
