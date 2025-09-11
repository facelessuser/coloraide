"""Generate 24 swatch color chart."""
from PIL import Image
from PIL import ImageCms
import argparse
import sys
import os

# We want to load ColorAide from the working directory to pick up the version under development
sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide import algebra as alg

round_to = alg.vectorize(lambda x: int(alg.round_to(x * 255)))


def get_swatches_before_nov2014(space):
    """
    Get color swatches using data before November 2014.

    ```
    Date: 3/27/2000  Time: 19:04
    LGOROWLENGTH 12
    ORIGINATOR "ColorChecker24 - Before November2014 edition
    MANUFACTURER "X-Rite - http://www.xrite.com"
    NUMBER_OF_FIELDS 4
    BEGIN_DATA_FORMAT
    SAMPLE_NAME Lab_L   Lab_a   Lab_b
    END_DATA_FORMAT
    NUMBER_OF_SETS 24
    BEGIN_DATA
    A1  37.986  13.555  14.059
    A2  62.661  36.067  57.096
    A3  28.778  14.179  -50.297
    A4  96.539  -0.425  1.186
    B1  65.711  18.13   17.81
    B2  40.02   10.41   -45.964
    B3  55.261  -38.342 31.37
    B4  81.257  -0.638  -0.335
    C1  49.927  -4.88   -21.905
    C2  51.124  48.239  16.248
    C3  42.101  53.378  28.19
    C4  66.766  -0.734  -0.504
    D1  43.139  -13.095 21.905
    D2  30.325  22.976  -21.587
    D3  81.733  4.039   79.819
    D4  50.867  -0.153  -0.27
    E1  55.112  8.844   -25.399
    E2  72.532  -23.709 57.255
    E3  51.935  49.986  -14.574
    E4  35.656  -0.421  -1.231
    F1  70.719  -33.397 -0.199
    F2  71.941  19.363  67.857
    F3  51.038  -28.631 -28.638
    F4  20.461  -0.079  -0.973
    END_DATA
    ```
    """

    return (
        round_to(Color('lab', [37.986, 13.555, 14.059]).convert(space).coords()),
        round_to(Color('lab', [62.661, 36.067, 57.096]).convert(space).coords()),
        round_to(Color('lab', [28.778, 14.179, -50.297]).convert(space).coords()),
        round_to(Color('lab', [96.539, -0.425, 1.186]).convert(space).coords()),
        round_to(Color('lab', [65.711, 18.13,  17.81]).convert(space).coords()),
        round_to(Color('lab', [40.02, 10.41, -45.964]).convert(space).coords()),
        round_to(Color('lab', [55.261, -38.342, 31.37]).convert(space).coords()),
        round_to(Color('lab', [81.257, -0.638, -0.335]).convert(space).coords()),
        round_to(Color('lab', [49.927, -4.88, -21.905]).convert(space).coords()),
        round_to(Color('lab', [51.124, 48.239, 16.248]).convert(space).coords()),
        round_to(Color('lab', [42.101, 53.378, 28.19]).convert(space).coords()),
        round_to(Color('lab', [66.766, -0.734, -0.504]).convert(space).coords()),
        round_to(Color('lab', [43.139, -13.095, 21.905]).convert(space).coords()),
        round_to(Color('lab', [30.325, 22.976, -21.587]).convert(space).coords()),
        round_to(Color('lab', [81.733, 4.039, 79.819]).convert(space).coords()),
        round_to(Color('lab', [50.867, -0.153, -0.27]).convert(space).coords()),
        round_to(Color('lab', [55.112, 8.844, -25.399]).convert(space).coords()),
        round_to(Color('lab', [72.532, -23.709, 57.255]).convert(space).coords()),
        round_to(Color('lab', [51.935, 49.986, -14.574]).convert(space).coords()),
        round_to(Color('lab', [35.656, -0.421, -1.231]).convert(space).coords()),
        round_to(Color('lab', [70.719, -33.397, -0.199]).convert(space).coords()),
        round_to(Color('lab', [71.941, 19.363, 67.857]).convert(space).coords()),
        round_to(Color('lab', [51.038, -28.631, -28.638]).convert(space).coords()),
        round_to(Color('lab', [20.461, -0.079, -0.973]).convert(space).coords())
    )


def get_swatches_after_nov2014(space):
    """
    Get color chart swatches using data after November 2014.

    ```
    LGOROWLENGTH 12
    ORIGINATOR "ColorChecker24 - November2014 edition and newer"
    MANUFACTURER "X-Rite - http://www.xrite.com"

    4/28/2015  # Time: 14:33
    "i1Pro 2 ; Serial number 1001785
    "MeasurementCondition=M0    Filter=no

    NUMBER_OF_FIELDS 4
    BEGIN_DATA_FORMAT
    SAMPLE_NAME Lab_L   Lab_a   Lab_b
    END_DATA_FORMAT
    NUMBER_OF_SETS 24
    BEGIN_DATA
    A1  37,54   14,37   14,92
    A2  62,73   35,83   56,5
    A3  28,37   15,42   -49,8
    A4  95,19   -1,03   2,93
    B1  64,66   19,27   17,5
    B2  39,43   10,75   -45,17
    B3  54,38   -39,72  32,27
    B4  81,29   -0,57   0,44
    C1  49,32   -3,82   -22,54
    C2  50,57   48,64   16,67
    C3  42,43   51,05   28,62
    C4  66,89   -0,75   -0,06
    D1  43,46   -12,74  22,72
    D2  30,1    22,54   -20,87
    D3  81,8    2,67    80,41
    D4  50,76   -0,13   0,14
    E1  54,94   9,61    -24,79
    E2  71,77   -24,13  58,19
    E3  50,63   51,28   -14,12
    E4  35,63   -0,46   -0,48
    F1  70,48   -32,26  -0,37
    F2  71,51   18,24   67,37
    F3  49,57   -29,71  -28,32
    F4  20,64   0,07    -0,46
    END_DATA
    ```
    """

    return (
        round_to(Color('lab', [37.54, 14.37, 14.92]).convert(space).coords()),
        round_to(Color('lab', [62.73, 35.83, 56.5]).convert(space).coords()),
        round_to(Color('lab', [28.37, 15.42, -49.8]).convert(space).coords()),
        round_to(Color('lab', [95.19, -1.03, 2.93]).convert(space).coords()),
        round_to(Color('lab', [64.66, 19.27, 17.5]).convert(space).coords()),
        round_to(Color('lab', [39.43, 10.75, -45.17]).convert(space).coords()),
        round_to(Color('lab', [54.38, -39.72, 32.27]).convert(space).coords()),
        round_to(Color('lab', [81.29, -0.57, 0.44]).convert(space).coords()),
        round_to(Color('lab', [49.32, -3.82, -22.54]).convert(space).coords()),
        round_to(Color('lab', [50.57, 48.64, 16.67]).convert(space).coords()),
        round_to(Color('lab', [42.43, 51.05, 28.62]).convert(space).coords()),
        round_to(Color('lab', [66.89, -0.75, -0.06]).convert(space).coords()),
        round_to(Color('lab', [43.46, -12.74, 22.72]).convert(space).coords()),
        round_to(Color('lab', [30.1, 22.54, -20.87]).convert(space).coords()),
        round_to(Color('lab', [81.8, 2.67,  80.41]).convert(space).coords()),
        round_to(Color('lab', [50.76, -0.13, 0.14]).convert(space).coords()),
        round_to(Color('lab', [54.94, 9.61,  -24.79]).convert(space).coords()),
        round_to(Color('lab', [71.77, -24.13, 58.19]).convert(space).coords()),
        round_to(Color('lab', [50.63, 51.28, -14.12]).convert(space).coords()),
        round_to(Color('lab', [35.63, -0.46, -0.48]).convert(space).coords()),
        round_to(Color('lab', [70.48, -32.26, 0.37]).convert(space).coords()),
        round_to(Color('lab', [71.51, 18.24, 67.37]).convert(space).coords()),
        round_to(Color('lab', [49.57, -29.71, -28.32]).convert(space).coords()),
        round_to(Color('lab', [20.64, 0.07,  -0.46]).convert(space).coords())
    )


def generate_image(space, icc, output, width, before_nov_2014):
    """
    Generate the image by calculating maximum saturated colors.

    Colors are generated in HSL and converted to sRGB. The RGB values are simply
    treated like they are for the target RGB space.
    """

    third = width // 3
    width = third * 3
    height = third * 2
    swidth = sheight = int((width * 0.80) // 6)
    leftover = width - int(swidth * 6)
    dividers = int((leftover * 0.70) // 5)
    leftover -= dividers * 5
    left = int(leftover // 2)
    top = int((height - sheight * 4 - dividers * 3) // 2)
    colors = get_swatches_before_nov2014(space) if before_nov_2014 else get_swatches_after_nov2014(space)

    if not icc:
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    else:
        profile = ImageCms.ImageCmsProfile(icc).tobytes()

    with Image.new(mode="RGB", size=(width, height)) as im:
        pixels = im.load()
        x_offset = left
        swatch = 0
        for _ in range(6):
            y_offset = top
            for _ in range(4):
                for t in range(y_offset, y_offset + sheight):
                    for l in range(x_offset, x_offset + swidth):
                        pixels[l, t] = tuple(colors[swatch])
                swatch += 1
                y_offset += int(sheight + dividers)
            x_offset += int(swidth + dividers)
        im.save(output, icc_profile=profile, quality=100)


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        prog='gen_colorchart.py',
        description='Generate a 24 swatch color chart.'
    )
    parser.add_argument('--space', '-s', default='srgb', help='Color space.')
    parser.add_argument('--icc', '-i', help='ICC profile.')
    parser.add_argument('--output', '-o', help='Output name and location.')
    parser.add_argument('--width', '-W', type=int, default=900, help="Width.")
    parser.add_argument('--before-nov-2014', '-b', action='store_true', help="Use data before Novemeber 2014")
    args = parser.parse_args()

    generate_image(
        args.space,
        args.icc,
        args.output,
        args.width,
        args.before_nov_2014
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
