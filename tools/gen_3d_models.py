"""Generate all 3D models."""
import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())

import tools.gamut_3d_diagrams as diagrams  # noqa: E402

LOCATION = 'docs/src/markdown/images'
TEMPLATE = 'sRGB Gamut Plotted in {} Color Space'


def plot_model(name, title, filename, elev=30, azim=-60.0):
    """Generate the models."""

    print('===> Generating {} model...'.format(name))
    diagrams.plot_space_in_srgb(
        name,
        title=title,
        resolution=200,
        rotate_elev=elev,
        rotate_azim=azim
    )
    plt.savefig(os.path.join(LOCATION, filename), dpi=200)
    plt.figure().clear()
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
    azim=120
)

plot_model(
    'lch-d65',
    TEMPLATE.format('CIELCh D65'),
    'lch-d65-3d.png',
    azim=120
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
    azim=120
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
    azim=120
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
    azim=120
)

plot_model(
    'ictcp',
    TEMPLATE.format('ICtCp'),
    'ictcp-3d.png',
    azim=30
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
    azim=120
)
