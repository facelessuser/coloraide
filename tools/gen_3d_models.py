"""Generate all 3D models."""
import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())

import tools.gamut_3d_diagrams as diagrams  # noqa: E402

LOCATION = 'docs/src/markdown/images'
TEMPLATE = 'sRGB Gamut Plotted in {} Color Space'


def plot_model(name, title, filename, gamut='srgb', elev=30, azim=-60.0):
    """Generate the models."""

    print('===> Generating {} model...'.format(name))
    diagrams.plot_gamut_in_space(
        name,
        gamut=gamut,
        title=title,
        resolution=200,
        rotate_elev=elev,
        rotate_azim=azim
    )
    plt.savefig(os.path.join(LOCATION, filename), dpi=200)
    plt.close()
    plt.cla()
    plt.clf()
    print('[complete]')


plot_model(
    'srgb',
    'sRGB Color Space',
    'srgb-3d.png'
)

plot_model(
    'hsl',
    'HSL Color Space',
    'hsl-3d.png'
)

plot_model(
    'hsi',
    'HSI Color Space',
    'hsi-3d.png'
)

plot_model(
    'hsv',
    'HSV Color Space',
    'hsv-3d.png'
)

plot_model(
    'hwb',
    'HWB Color Space',
    'hwb-3d.png',
    elev=210
)

plot_model(
    'okhsl',
    'Okhsl Color Space',
    'okhsl-3d.png'
)

plot_model(
    'okhsv',
    'Okhsv Color Space',
    'okhsv-3d.png'
)

plot_model(
    'hsluv',
    'HSLuv Color Space',
    'hsluv-3d.png'
)

plot_model(
    'hpluv',
    'HPLuv Color Space',
    'hpluv-3d.png'
)

plot_model(
    'xyz-d50',
    TEMPLATE.format('XYZ D50'),
    'xyz-d50-3d.png'
)

plot_model(
    'xyz-d65',
    TEMPLATE.format('XYZ D65'),
    'xyz-d65-3d.png'
)

plot_model(
    'xyy',
    TEMPLATE.format('xyY'),
    'xyy-3d.png'
)

plot_model(
    'lab',
    TEMPLATE.format('CIELab D50'),
    'lab-3d.png'
)

plot_model(
    'lab-d65',
    TEMPLATE.format('CIELab D65'),
    'lab-d65-3d.png'
)

plot_model(
    'lch',
    TEMPLATE.format('CIELCh D50'),
    'lch-3d.png',
    azim=300
)

plot_model(
    'lch-d65',
    TEMPLATE.format('CIELCh D65'),
    'lch-d65-3d.png',
    azim=300
)

plot_model(
    'oklab',
    TEMPLATE.format('Oklab'),
    'oklab-3d.png'
)

plot_model(
    'oklch',
    TEMPLATE.format('OkLCh'),
    'oklch-3d.png',
    azim=300
)

plot_model(
    'luv',
    TEMPLATE.format('CIELuv'),
    'luv-3d.png'
)

plot_model(
    'lchuv',
    TEMPLATE.format('LChuv'),
    'lchuv-3d.png',
    azim=300
)

plot_model(
    'hunter-lab',
    TEMPLATE.format('Hunter Lab'),
    'hunter-lab-3d.png',
    elev=5,
    azim=-30
)

plot_model(
    'rlab',
    TEMPLATE.format('RLAB'),
    'rlab-3d.png'
)

plot_model(
    'jzazbz',
    TEMPLATE.format('Jzazbz'),
    'jzazbz-3d.png'
)

plot_model(
    'jzczhz',
    TEMPLATE.format('JzCzhz'),
    'jzczhz-3d.png',
    azim=300
)

plot_model(
    'ipt',
    TEMPLATE.format('IPT'),
    'ipt-3d.png'
)

plot_model(
    'ictcp',
    TEMPLATE.format('ICtCp'),
    'ictcp-3d.png',
    azim=60
)

plot_model(
    'din99o',
    TEMPLATE.format('DIN99o'),
    'din99o-3d.png'
)

plot_model(
    'lch99o',
    TEMPLATE.format('DIN99o LCh'),
    'lch99o-3d.png',
    azim=300
)

plot_model(
    'cam16',
    TEMPLATE.format('CAM16'),
    'cam16-3d.png'
)

plot_model(
    'cam16-ucs',
    TEMPLATE.format('CAM16 UCS'),
    'cam16-ucs-3d.png'
)

plot_model(
    'cam16-scd',
    TEMPLATE.format('CAM16 SCD'),
    'cam16-scd-3d.png'
)

plot_model(
    'cam16-lcd',
    TEMPLATE.format('CAM16 LCD'),
    'cam16-lcd-3d.png'
)

plot_model(
    'cam16-jmh',
    TEMPLATE.format('CAM16 JMh'),
    'cam16-jmh-3d.png'
)

plot_model(
    'hct',
    TEMPLATE.format('HCT'),
    'hct-3d.png'
)

plot_model(
    'cmy',
    TEMPLATE.format('CMY'),
    'cmy-3d.png'
)

plot_model(
    'orgb',
    TEMPLATE.format('oRGB'),
    'orgb-3d.png',
    elev=72
)
