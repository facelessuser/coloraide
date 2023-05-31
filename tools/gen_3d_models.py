"""Generate all 3D models."""
import sys
import os
import argparse

sys.path.insert(0, os.getcwd())

import tools.gamut_3d_plotly as diagrams  # noqa: E402

LOCATION = 'docs/src/markdown/images'
TEMPLATE = 'sRGB Gamut Plotted in {} Color Space'


def plot_model(name, title, filename, gamut='srgb', elev=45, azim=-60.0):
    """Generate the models."""

    print('===> Generating {} model...'.format(name))
    fig = diagrams.plot_gamut_in_space(
        name,
        gamut=gamut,
        title=title,
        resolution=200,
        size=(800, 800),
        camera={'a': azim, 'e': elev, 'r': 2.5}
    )

    with open(os.path.join(LOCATION, filename), 'wb') as f:
        f.write(fig.to_image(format='png'))
    del fig
    print('[complete]')


models = {
    'srgb': {'title': 'sRGB Color Space', 'filename': 'srgb-3d.png'},
    'hsl': {'title': 'HSL Color Space', 'filename': 'hsl-3d.png'},
    'hsi': {'title': 'HSI Color Space', 'filename': 'hsi-3d.png'},
    'hsv': {'title': 'HSV Color Space', 'filename': 'hsv-3d.png'},
    'hwb': {'title': 'HWB Color Space', 'filename': 'hwb-3d.png', 'elev': 210},
    'okhsl': {'title': 'Okhsl Color Space', 'filename': 'okhsl-3d.png'},
    'okhsv': {'title': 'Okhsv Color Space', 'filename': 'okhsv-3d.png'},
    'hsluv': {'title': 'HSLuv Color Space', 'filename': 'hsluv-3d.png'},
    'hpluv': {'title': 'HPLuv Color Space', 'filename': 'hpluv-3d.png'},
    'xyz-d50': {'title': TEMPLATE.format('XYZ D50'), 'filename': 'xyz-d50-3d.png'},
    'xyz-d65': {'title': TEMPLATE.format('XYZ D65'), 'filename': 'xyz-d65-3d.png'},
    'xyy': {'title': TEMPLATE.format('xyY'), 'filename': 'xyy-3d.png'},
    'lab': {'title': TEMPLATE.format('CIELab D50'), 'filename': 'lab-3d.png'},
    'lab-d65': {'title': TEMPLATE.format('CIELab D65'), 'filename': 'lab-d65-3d.png'},
    'lch': {'title': TEMPLATE.format('CIELCh D50'), 'filename': 'lch-3d.png', 'azim': 300},
    'lch-d65': {'title': TEMPLATE.format('CIELCh D65'), 'filename': 'lch-d65-3d.png', 'azim': 300},
    'oklab': {'title': TEMPLATE.format('Oklab'), 'filename': 'oklab-3d.png'},
    'oklch': {'title': TEMPLATE.format('OkLCh'), 'filename': 'oklch-3d.png', 'azim': 300},
    'luv': {'title': TEMPLATE.format('CIELuv'), 'filename': 'luv-3d.png'},
    'lchuv': {'title': TEMPLATE.format('LChuv'), 'filename': 'lchuv-3d.png', 'azim': 300},
    'din99o': {'title': TEMPLATE.format('DIN99o'), 'filename': 'din99o-3d.png'},
    'lch99o': {'title': TEMPLATE.format('DIN99o LCh'), 'filename': 'lch99o-3d.png', 'azim': 300},
    'jzazbz': {'title': TEMPLATE.format('Jzazbz'), 'filename': 'jzazbz-3d.png'},
    'jzczhz': {'title': TEMPLATE.format('JzCzhz'), 'filename': 'jzczhz-3d.png', 'azim': 300},
    'rlab': {'title': TEMPLATE.format('RLAB'), 'filename': 'rlab-3d.png'},
    'hunter-lab': {'title': TEMPLATE.format('Hunter Lab'), 'filename': 'hunter-lab-3d.png', 'elev': 5, 'azim': -30},
    'ipt': {'title': TEMPLATE.format('IPT'), 'filename': 'ipt-3d.png'},
    'ictcp': {'title': TEMPLATE.format('ICtCp'), 'filename': 'ictcp-3d.png', 'azim': 60},
    'igpgtg': {'title': TEMPLATE.format('IgPgTg'), 'filename': 'igpgtg-3d.png'},
    'cam16': {'title': TEMPLATE.format('CAM16'), 'filename': 'cam16-3d.png'},
    'cam16-ucs': {'title': TEMPLATE.format('CAM16 UCS'), 'filename': 'cam16-ucs-3d.png'},
    'cam16-scd': {'title': TEMPLATE.format('CAM16 SCD'), 'filename': 'cam16-scd-3d.png'},
    'cam16-lcd': {'title': TEMPLATE.format('CAM16 LCD'), 'filename': 'cam16-lcd-3d.png'},
    'cam16-jmh': {'title': TEMPLATE.format('CAM16 JMh'), 'filename': 'cam16-jmh-3d.png'},
    'hct': {'title': TEMPLATE.format('HCT'), 'filename': 'hct-3d.png'},
    'cmy': {'title': TEMPLATE.format('CMY'), 'filename': 'cmy-3d.png'},
    'orgb': {'title': TEMPLATE.format('oRGB'), 'filename': 'orgb-3d.png', 'elev': 72},
    'xyb': {'title': TEMPLATE.format('XYB'), 'filename': 'xyb-3d.png', 'azim': 45},
    'ucs': {'title': TEMPLATE.format('UCS'), 'filename': 'ucs-3d.png', 'azim': 60, 'elev': 10},
}


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='gen_3d_models', description='Generate 3D models of color spaces.')
    parser.add_argument('--space', '-s', action='append', help="Color space.")
    args = parser.parse_args()

    if args.space:
        for space in args.space:
            kwargs = models.get(space)
            if kwargs is not None:
                plot_model(space, **kwargs)
    else:
        for space, kwargs in models.items():
            plot_model(space, **kwargs)


if __name__ == "__main__":
    sys.exit(main())
