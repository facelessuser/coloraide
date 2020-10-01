"""Color-mod."""
import re
from . import Color as ColorCSS
from ..colors import ColorMatch
from ..colors import _convert as convert
from ..colors import _parse as parse
from .. import util
import functools
import math

WHITE = [1.0] * 3
BLACK = [0.0] * 3

TOKENS = {
    "units": re.compile(
        r"""(?xi)
        # Some number of units separated by valid separators
        (?:
            {float} |
            {angle} |
            {percent} |
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?) |
            [\w][\w\d]*
        )
        """.format(**parse.COLOR_PARTS)
    ),
    "functions": re.compile(r'(?i)[\w][\w\d]*\('),
    "separators": re.compile(r'(?:{comma}|{space}|{slash})'.format(**parse.COLOR_PARTS))
}

RE_ADJUSTERS = {
    "red": re.compile(
        r'(?i)\s+red\(\s*(?:(\+\s+|\-\s+)?({percent}|{float})|(\*)?\s*({percent}|{float}))\s*\)'.format(
            **parse.COLOR_PARTS
        )
    ),
    "green": re.compile(
        r'(?i)\s+green\(\s*(?:(\+\s+|\-\s+)?({percent}|{float})|(\*)?\s*({percent}|{float}))\s*\)'.format(
            **parse.COLOR_PARTS
        )
    ),
    "blue": re.compile(
        r'(?i)\s+blue\(\s*(?:(\+\s+|\-\s+)?({percent}|{float})|(\*)?\s*({percent}|{float}))\s*\)'.format(
            **parse.COLOR_PARTS
        )
    ),
    "alpha": re.compile(
        r'(?i)\s+a(?:lpha)?\(\s*(?:(\+\s+|\-\s+)?({percent}|{float})|(\*)?\s*({percent}|{float}))\s*\)'.format(
            **parse.COLOR_PARTS
        )
    ),
    "rgb": re.compile(
        r'(?i)\s+rgb\(\s*([\+\-]\s+)?((?:{percent}|{float})\s+(?:{percent}|{float})\s+(?:{percent}|{float}))\s*\)'.format(  # noqa: E501
            **parse.COLOR_PARTS
        )
    ),
    "hex": re.compile(
        r'(?i)\s+rgb\(\s*([\+\-]\s+)?\#((?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?))\s*\)'.format(
            **parse.COLOR_PARTS
        )
    ),
    "rgbmult": re.compile(
        r'(?i)\s+rgb\(\s*(\*)?\s*({percent})\s*\)'.format(
            **parse.COLOR_PARTS
        )
    ),
    "hue": re.compile(r'(?i)\s+h(?:ue)?\((\+\s|\-\s|\*)?\s*({angle})\s*\)'.format(**parse.COLOR_PARTS)),
    "saturation": re.compile(r'(?i)\s+s(?:aturation)?\((\+\s|\-\s|\*)?\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "lightness": re.compile(r'(?i)\s+l(?:ightness)?\((\+\s|\-\s|\*)?\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "whiteness": re.compile(r'(?i)\s+w(?:hiteness)?\((\+\s|\-\s|\*)?\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "blackness": re.compile(r'(?i)\s+b(?:lackness)?\((\+\s|\-\s|\*)?\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "tint": re.compile(r'(?i)\s+tint\(\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "shade": re.compile(r'(?i)\s+shade\(\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "min-contrast_start": re.compile(r'(?i)\s+min-contrast\(\s*'),
    "contrast": re.compile(r'(?i)\s+contrast\(\s*({percent})\s*\)'.format(**parse.COLOR_PARTS)),
    "blend_start": re.compile(r'(?i)\s+blenda?\(\s*'),
    "end": re.compile(r'(?i)\s*\)')
}

RE_COLOR_START = re.compile(r'(?i)color\(\s*')
RE_BLEND_END = re.compile(r'(?i)\s+({percent})(?:\s+(rgb|hsl|hwb))?\s*\)'.format(**parse.COLOR_PARTS))
RE_HUE = re.compile(r'(?i){angle}'.format(**parse.COLOR_PARTS))
RE_BRACKETS = re.compile(r'(?:(\()|(\))|[^()]+)')
RE_MIN_CONTRAST_END = re.compile(r'(?i)\s+({float})\s*\)'.format(**parse.COLOR_PARTS))
RE_VARS = re.compile(r'(?i)(?:(?<=^)|(?<=[\s\t\(,/]))(var\(\s*([-\w][-\w\d]*)\s*\))(?!\()(?=[\s\t\),/]|$)')


def validate_vars(var, good_vars):
    """
    Validate variables.

    We will blindly replace values, but if we are fairly confident they follow
    the pattern of a valid, complete unit, if you replace them in a bad place,
    it will break the color (as it should) and if not, it is likely to parse fine,
    unless it breaks the syntax of the color being evaluated.
    """

    for k, v in var.items():
        v = v.strip()
        start = 0
        need_sep = False
        length = len(v)
        while True:
            if start == length:
                good_vars[k] = v
                break
            try:
                # Each item should be separated by some valid separator
                if need_sep:
                    m = TOKENS["separators"].match(v, start)
                    if m:
                        start = m.end(0)
                        need_sep = False
                        continue
                    else:
                        break

                # Validate things like `rgb()`, `contrast()` etc.
                m = TOKENS["functions"].match(v, start)
                if m:
                    end = None
                    brackets = 1
                    for m in RE_BRACKETS.finditer(v, start + 6):
                        if m.group(2):
                            brackets -= 1
                        elif m.group(1):
                            brackets += 1

                        if brackets == 0:
                            end = m.end(0)
                            break
                    if end is None:
                        break
                    start = end
                    need_sep = True
                    continue

                # Validate that units such as percents, floats, hex colors, etc.
                m = TOKENS["units"].match(v, start)
                if m:
                    start = m.end(0)
                    need_sep = True
                    continue
                break
            except Exception:
                break


def _var_replace(m, var=None, parents=None):
    """Replace variables but try to prevent infinite recursion."""

    name = m.group(2)
    replacement = var.get(m.group(2))
    string = replacement if replacement and name not in parents is not None else ""
    parents.add(name)
    return RE_VARS.sub(functools.partial(_var_replace, var=var, parents=parents), string)


def handle_vars(string, variables, parents=None):
    """Handle CSS variables."""

    temp_vars = {}
    validate_vars(variables, temp_vars)
    parent_vars = set() if parents is None else parents

    return RE_VARS.sub(functools.partial(_var_replace, var=temp_vars, parents=parent_vars), string)


def contrast_ratio(lum1, lum2):
    """Get contrast ratio."""

    return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)


class ColorMod:
    """Color utilities."""

    def __init__(self, fullmatch=True):
        """Associate with parent."""

        self.OP_MAP = {
            "": self._op_null,
            "*": self._op_mult,
            "+": self._op_add,
            "-": self._op_sub
        }

        self.adjusting = False
        self._color = None
        self.fullmatch = fullmatch

    @staticmethod
    def _op_mult(a, b):
        """Multiply."""

        return a * b

    @staticmethod
    def _op_add(a, b):
        """Multiply."""

        return a + b

    @staticmethod
    def _op_sub(a, b):
        """Multiply."""

        return a - b

    @staticmethod
    def _op_null(a, b):
        """Multiply."""

        return b

    def _adjust(self, string, start=0):
        """Adjust."""

        nested = self.adjusting
        self.adjusting = True

        color = None
        done = False
        old_parent = self._color
        hue = None

        try:
            m = RE_COLOR_START.match(string, start)
            if m:
                start = m.end(0)
                m = RE_HUE.match(string, start)
                if m:
                    hue = parse.norm_hue_channel(m.group(0))
                    color = Color("hsl", [hue, 1, 0.5]).convert("srgb")
                    start = m.end(0)
                if color is None:
                    m = RE_COLOR_START.match(string, start)
                    if m:
                        color2, start = self._adjust(string, start=start)
                        if color2 is None:
                            raise ValueError("Found unterminated or invalid 'color('")
                        color = color2.convert("srgb")
                        if not color.is_achromatic():
                            hue = convert.srgb_to_hsv(*color._color.coords())[0]
                if color is None:
                    obj = Color.match(string, start=start, fullmatch=False)
                    if obj is not None:
                        color = obj.color
                        if color.space != "srgb":
                            color = color.convert("srgb")
                        if not color.is_achromatic():
                            hue = convert.srgb_to_hsv(*color._color.coords())[0]
                        start = obj.end

            if color is not None:
                self._color = color
                if not self._color.in_gamut():
                    self._color.fit(method="clip", in_place=True)

                while not done:
                    m = None
                    for name, pattern in RE_ADJUSTERS.items():
                        m = pattern.match(string, start)
                        if m:
                            start = m.end(0)
                            break
                    if m is None:
                        break

                    if name in ("red", "green", "blue"):
                        start, hue = self.process_rgb(name, m, hue)
                    elif name in ("rgb", "rgbmult"):
                        start, hue = self.process_rgb_multi(m, hue)
                    elif name == "hex":
                        start, hue = self.process_hex(m, hue)
                    elif name == "alpha":
                        start, hue = self.process_alpha(m, hue)
                    elif name == "hue":
                        start, hue = self.process_hue(m, hue)
                    elif name in ("saturation", "lightness", "whiteness", "blackness"):
                        start, hue = self.process_hwb_hsl_channels(name, m, hue)
                    elif name in ("tint", "shade"):
                        start, hue = self.process_tint_shade(name, m, hue)
                    elif name == "contrast":
                        start, hue = self.process_contrast(m, hue)
                    elif name == "min-contrast_start":
                        start, hue = self.process_min_contrast(m, string, hue)
                    elif name == "blend_start":
                        start, hue = self.process_blend(m, string, hue)
                    elif name == "end":
                        done = True
                        start = m.end(0)
                    else:
                        break

                    if not self._color.in_gamut():
                        self._color.fit(method="clip", in_place=True)
            else:
                raise ValueError('Could not calculate base color')
        except Exception:
            pass

        if not done or (self.fullmatch and start != len(string)):
            result = None
        else:
            result = self._color

        self._color = old_parent

        if not nested:
            self.adjusting = False

        return result, start

    def adjust_base(self, base, string):
        """Adjust base."""

        self._color = base
        pattern = "color({} {})".format(self._color.to_string(fit="clip"), string)
        color, start = self._adjust(pattern)
        if color is not None:
            self._color.update(color)
        else:
            raise ValueError(
                "'{}' doesn't appear to be a valid and/or supported CSS color or color-mod instruction".format(string)
            )

    def adjust(self, string, start=0):
        """Adjust."""

        color, end = self._adjust(string, start=start)
        return color, end

    def process_rgb(self, name, m, hue):
        """Process R, G, and B."""

        if m.group(2):
            value = m.group(2)
        else:
            value = m.group(4)
        if value.endswith('%'):
            value = float(value.strip('%')) * parse.SCALE_PERCENT
        else:
            value = float(value) * parse.RGB_CHANNEL_SCALE
        op = ""
        if m.group(1):
            op = m.group(1).strip()
        elif m.group(3):
            op = m.group(3).strip()
        getattr(self, name)(value, op=op)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_rgb_multi(self, m, hue):
        """Process RGB multi."""

        values = [
            float(i.strip('%')) * parse.SCALE_PERCENT
            if i.endswith('%')
            else float(i) * parse.RGB_CHANNEL_SCALE
            for i in m.group(2).strip().split(' ')
        ]
        if len(values) == 1:
            values = values * 3
        op = ""
        if m.group(1):
            op = m.group(1).strip()
        self.red(values[0], op=op)
        self.green(values[1], op=op)
        self.blue(values[2], op=op)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_hex(self, m, hue):
        """Process hex."""

        op = ""
        s = m.group(2)
        length = len(s)
        size = int((length / 3) if length in (6, 3) else (length / 4))
        values = [int(s[i:i + size], 16) * parse.RGB_CHANNEL_SCALE for i in range(0, length, size)]
        if m.group(1):
            op = m.group(1).strip()
        self.red(values[0], op=op)
        self.green(values[1], op=op)
        self.blue(values[2], op=op)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_alpha(self, m, hue):
        """Process alpha."""

        if m.group(2):
            value = m.group(2)
        else:
            value = m.group(4)
        if value.endswith('%'):
            value = float(value.strip('%')) * parse.SCALE_PERCENT
        else:
            value = float(value)
        op = ""
        if m.group(1):
            op = m.group(1).strip()
        elif m.group(3):
            op = m.group(3).strip()
        self.alpha(value, op=op)
        return m.end(0), hue

    def process_hue(self, m, hue):
        """Process hue."""

        value = m.group(2)
        value = parse.norm_angle(value)
        op = m.group(1).strip() if m.group(1) else ""
        self.hue(value, hue, op=op)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_hwb_hsl_channels(self, name, m, hue):
        """Process HWB and HSL channels (except hue)."""

        value = m.group(2)
        value = float(value.strip('%'))
        op = m.group(1).strip() if m.group(1) else ""
        getattr(self, name)(value, op=op, hue=hue)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_tint_shade(self, name, m, hue):
        """Process tint/shade."""

        value = m.group(1)
        value = float(value.strip('%'))
        getattr(self, name)(value)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_contrast(self, m, hue):
        """Process contrast."""

        value = m.group(1)
        value = float(value.strip('%'))
        self.contrast(value)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return m.end(0), hue

    def process_blend(self, m, string, hue):
        """Process blend."""

        start = m.end(0)
        alpha = m.group(0).startswith('blenda')
        m = RE_COLOR_START.match(string, start)
        if m:
            color2, start = self._adjust(string, start=start)
            if color2 is None:
                raise ValueError("Found unterminated or invalid 'color('")
        else:
            color2 = None
            obj = Color.match(string, start=start, fullmatch=False)
            if obj is not None:
                color2 = obj.color
                start = obj.end
            if color2 is None:
                raise ValueError("Could not find a valid color for 'blend'")
        m = RE_BLEND_END.match(string, start)
        if m:
            value = float(m.group(1).strip('%')) * parse.SCALE_PERCENT
            space = "srgb"
            if m.group(2):
                space = m.group(2).lower()
                if space == "rgb":
                    space = "srgb"
            start = m.end(0)
        else:
            raise ValueError("Found unterminated or invalid 'blend('")

        self.blend(color2, 1.0 - value, alpha, space=space)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return start, hue

    def tint(self, percent):
        """Tint color."""

        self.blend(self._color.new(WHITE, "srgb"), percent, space="srgb")

    def shade(self, percent):
        """Tint color."""

        self.blend(self._color.new(BLACK, "srgb"), percent, space="srgb")

    def contrast(self, percent):
        """
        Get the color with the best contrast.

        # https://drafts.csswg.org/css-color/#contrast-adjuster
        """

        lum1 = self._color.luminance()

        max_hwb = self._color.convert("hwb")
        if lum1 < 0.5:
            max_hwb.whiteness = 100.0
            max_hwb.blackness = 0.0
        else:
            max_hwb.whiteness = 0.0
            max_hwb.blackness = 100.0

        max_white = max_hwb.whiteness
        max_black = max_hwb.blackness
        lum2 = max_hwb.luminance()
        ratio = contrast_ratio(lum1, lum2)

        if ratio > 4.5:
            min_hwb = self._color.convert("hwb")
            min_white = min_hwb.whiteness
            min_black = min_hwb.blackness

            last_ratio = 1000
            last_values = (max_white, max_black)

            while (abs(min_white - max_white) > 0.001 if lum1 < 0.5 else abs(min_black - max_black) > 0.001):
                if lum1 < 0.5:
                    mid_white = (max_white + min_white) / 2
                    mid_black = 100.0 - mid_white
                else:
                    mid_black = (max_black + min_black) / 2
                    mid_white = 100.0 - mid_black

                min_hwb.whiteness = mid_white
                min_hwb.blackness = mid_black
                lum2 = min_hwb.luminance()
                ratio = contrast_ratio(lum2, lum1)

                if ratio > 4.5:
                    max_white = mid_white
                    max_black = mid_black
                else:
                    min_white = mid_white
                    min_black = mid_black

                if ratio < last_ratio and ratio >= 4.5:
                    last_ratio = ratio
                    last_values = (mid_white, mid_black)

            # Use the best, last values
            min_hwb.whiteness = last_values[0]
            min_hwb.blackness = last_values[1]
        else:
            min_hwb = max_hwb.clone()

        self._color.update(max_hwb.mix(min_hwb, 1.0 - percent, alpha=False, space="hwb"))

    def process_min_contrast(self, m, string, hue):
        """Process blend."""

        # Gather the min-contrast parameters
        start = m.end(0)
        m = RE_COLOR_START.match(string, start)
        if m:
            color2, start = self._adjust(string, start=start)
            if color2 is None:
                raise ValueError("Found unterminated or invalid 'color('")
        else:
            color2 = None
            obj = Color.match(string, start=start, fullmatch=False)
            if obj is not None:
                color2 = obj.color
                start = obj.end
        m = RE_MIN_CONTRAST_END.match(string, start)
        if m:
            value = float(m.group(1))
            start = m.end(0)
        else:
            raise ValueError("Found unterminated or invalid 'min-contrast('")

        this = self._color.convert("srgb")
        color2 = color2.convert("srgb")
        color2.alpha = 1.0

        self.min_contrast(this, color2, value)
        self._color.update(this)
        if not self._color.is_achromatic():
            hue = convert.srgb_to_hsv(*self._color._color.coords())[0]
        return start, hue

    def min_contrast(self, color1, color2, target):
        """
        Get the color with the best contrast.

        This mimics Sublime Text's custom `min-contrast` for `color-mod` (now defunct - the CSS version).
        It ensure the color has at least the specified contrast ratio.

        While there seems to be slight differences with ours and Sublime, maybe due to some rounding,
        this essentially fulfills the intention of their min-contrast.
        """

        ratio = color1.contrast_ratio(color2)

        # Already meet the minimum contrast or the request is impossible
        if ratio > target or target < 1:
            return

        lum2 = color2.luminance()

        is_dark = lum2 < 0.5
        orig = color1.convert("hwb")
        if is_dark:
            primary = "whiteness"
            secondary = "blackness"
            min_mix = orig.whiteness
            max_mix = 100.0
        else:
            primary = "blackness"
            secondary = "whiteness"
            min_mix = orig.blackness
            max_mix = 100.0
        last_ratio = 0
        last_mix = 0
        last_other = 0

        temp = orig.clone()
        while abs(min_mix - max_mix) > 0.2:
            mid_mix = round((max_mix + min_mix) / 2, 1)
            mid_other = (
                orig.get(secondary) -
                ((mid_mix - orig.get(primary)) / (100.0 - orig.get(primary))) * orig.get(secondary)
            )
            temp.set(primary, mid_mix)
            temp.set(secondary, mid_other)
            ratio = temp.contrast_ratio(color2)

            if ratio < target:
                min_mix = mid_mix
            else:
                max_mix = mid_mix

            if (
                (last_ratio < target and ratio > last_ratio) or
                (ratio > target and ratio < last_ratio)
            ):
                last_ratio = ratio
                last_mix = mid_mix
                last_other = mid_other

        # Use the best, last values
        final = orig.new("hwb", [orig.hue, last_mix, last_other] if is_dark else [orig.hue, last_other, last_mix])
        final = final.convert('srgb')
        # If we are lightening the color, then we'd like to round up to ensure we are over the luminance threshold
        # as sRGB will clip off decimals. If we are darkening, then we want to just floor the values as the algorithm
        # leans more to the light side.
        rnd = util.round_half_up if is_dark else math.floor
        final = Color("srgb", [rnd(c * 255.0) / 255.0 for c in final.coords()], final.alpha)
        color1.update(final)

    def blend(self, color, percent, alpha=False, space="srgb"):
        """Blend color."""

        space = space.lower()
        if space not in ("srgb", "hsl", "hwb"):
            raise ValueError(
                "ColorMod's does not support the '{}' colorspace, only 'srgb', 'hsl', and 'hwb' are supported"
            ).format(space)
        this = self._color.convert(space) if self._color.space() != space else self._color

        if color.space() != space:
            hue = color.hue
            color = color.convert(space)
            color.hue = hue

        self._color.update(this.mix(color, percent, alpha=False, space=space))

    def red(self, value, op=""):
        """Red."""

        this = self._color.convert("SRGB") if self._color.space() != "srgb" else self._color
        op = self.OP_MAP.get(op, self._op_null)
        this.red = op(this.red, value)
        self._color.update(this)

    def green(self, value, op=""):
        """Green."""

        this = self._color.convert("SRGB") if self._color.space() != "srgb" else self._color
        op = self.OP_MAP.get(op, self._op_null)
        this.green = op(this.green, value)
        self._color.update(this)

    def blue(self, value, op=""):
        """Blue."""

        this = self._color.convert("SRGB") if self._color.space() != "srgb" else self._color
        op = self.OP_MAP.get(op, self._op_null)
        this.blue = op(this.blue, value)
        self._color.update(this)

    def alpha(self, value, op=""):
        """Alpha."""

        this = self._color
        op = self.OP_MAP.get(op, self._op_null)
        this.alpha = op(this.alpha, value)
        self._color.update(this)

    def hue(self, value, op=""):
        """Hue."""

        if self._color.is_achromatic():
            return
        this = self._color.convert("hsl") if self._color.space() != "hsl" else self._color
        op = self.OP_MAP.get(op, self._op_null)
        this.hue = op(this.hue, value)
        self._color.update(this)

    def lightness(self, value, op="", hue=None):
        """Lightness."""

        this = self._color.convert("hsl") if self._color.space() != "hsl" else self._color
        if this.is_achromatic() and hue is not None:
            this.hue = hue
        op = self.OP_MAP.get(op, self._op_null)
        this.lightness = op(this.lightness, value)
        self._color.update(this)

    def saturation(self, value, op="", hue=None):
        """Saturation."""

        this = self._color.convert("hsl") if self._color.space() != "hsl" else self._color
        if this.is_achromatic() and hue is not None:
            this.hue = hue
        op = self.OP_MAP.get(op, self._op_null)
        this.saturation = op(this.saturation, value)
        self._color.update(this)

    def whiteness(self, value, op="", hue=None):
        """White."""

        this = self._color.convert('hwb') if self._color.space() != "hwb" else self._color
        if this.is_achromatic() and hue is not None:
            this.hue = hue
        achromatic = this.is_achromatic()
        op = self.OP_MAP.get(op, self._op_null)
        this.whiteness = op(this.whiteness, value)
        if achromatic:
            self.blackness = 100.0 - self.whiteness
        self._color.update(this)

    def blackness(self, value, op="", hue=None):
        """Black."""

        this = self._color.convert('hsb') if self._color.space() != "hwb" else self._color
        if this.is_achromatic() and hue is not None:
            this.hue = hue
        achromatic = this.is_achromatic()
        op = self.OP_MAP.get(op, self._op_null)
        this.blackness = op(this.blackness, value)
        if achromatic:
            self.whiteness = 100.0 - self.blackness
        self._color.update(this)


class Color(ColorCSS):
    """Color modify class."""

    def __init__(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, variables=None):
        """Initialize."""

        self._attach(self._parse(color, data, alpha, filters=filters, variables=variables))

    @classmethod
    def _parse(cls, color, data=None, alpha=util.DEF_ALPHA, filters=None, variables=None):
        """Parse the color."""

        obj = None
        if data is not None:
            filters = set(filters) if filters is not None else set()
            for space, space_class in cls.CS_MAP.items():
                s = color.lower()
                if space == s and (not filters or s in filters):
                    obj = space_class(data[:space_class.NUM_COLOR_CHANNELS] + [alpha])
                    return obj
        elif isinstance(color, Color):
            if not filters or color.space() in filters:
                obj = cls.CS_MAP[color.space()](color._color)
        else:
            m = cls._match(color, fullmatch=True, filters=filters, variables=variables)
            if m is None:
                raise ValueError("'{}' is not a valid color".format(color))
            obj = m.color
        if obj is None:
            raise ValueError("Could not process the provided color")
        return obj

    @classmethod
    def _match(cls, string, start=0, fullmatch=False, filters=None, variables=None):
        """
        Match a color in a buffer and return a color object.

        This must return the color space, not the Color object.
        """

        # Handle variable
        end = None
        is_mod = False
        if variables:
            m = RE_VARS.match(string, start)
            if m and (not fullmatch or len(string) == m.end(0)):
                end = m.end(0)
                start = 0
                string = string[start:end]
                string = handle_vars(string, variables)
                variables = None

        temp = parse.bracket_match(RE_COLOR_START, string, start, fullmatch)
        if end is None and temp:
            end = temp
            is_mod = True
        elif end is not None and temp is not None:
            is_mod = True

        if is_mod:
            if variables:
                string = handle_vars(string, variables)
            obj, match_end = ColorMod(fullmatch).adjust(string, start)
            if obj is not None:
                return ColorMatch(obj._color, start, end if end is not None else match_end)
        else:
            filters = set(filters) if filters is not None else set()
            obj = None
            for space, space_class in cls.CS_MAP.items():
                if filters and space not in filters:
                    continue
                value, match_end = space_class.match(string, start, fullmatch)
                if value is not None:
                    color = space_class(value)
                    obj = ColorMatch(color, start, match_end)
            if obj is not None and end:
                obj.end = end
            return obj

    @classmethod
    def match(cls, string, start=0, fullmatch=False, *, filters=None, variables=None):
        """Match color."""

        obj = cls._match(string, start, fullmatch, filters=filters, variables=variables)
        if obj is not None:
            obj.color = cls(obj.color.space(), obj.color.coords(), obj.color.alpha)
        return obj

    @classmethod
    def new(cls, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, variables=None):
        """Create new color object."""

        return cls(color, data, alpha, filters=filters, variables=variables)

    def update(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, variables=None):
        """Update the existing color space with the provided color."""

        obj = self._parse(color, data, alpha, filters=filters, variables=variables)
        self._color.update(obj)
        return self

    def mutate(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, variables=None):
        """Mutate the current color to a new color."""

        self._attach(self._parse(color, data, alpha, filters=filters, variables=variables))
        return self
