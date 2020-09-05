"""Color-mod."""
import re
from .colors import SUPPORTED
from .color_css import colorcss, colorcss_match, ColorMatch
from .. import parse
import traceback

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

        try:
            m = RE_COLOR_START.match(string, start)
            if m:
                start = m.end(0)
                m = RE_HUE.match(string, start)
                if m:
                    hue = parse.norm_hue_channel(m.group(0))
                    color = SUPPORTED["hsl"]([hue, 1, 0.5]).convert("srgb")
                    start = m.end(0)
                if color is None:
                    m = RE_COLOR_START.match(string, start)
                    if m:
                        color2, start = self._adjust(string, start=start)
                        if color2 is None:
                            raise ValueError("Found unterminated or invalid 'color('")
                        color = color2.convert("srgb")
                if color is None:
                    for obj in SUPPORTED:
                        print('---attempt---')
                        print(obj.MATCH.pattern)
                        m = obj.MATCH.match(string, start)
                        if m:
                            try:
                                color = colorcss(string[start:m.end(0)])
                                if color.space() != "srgb":
                                    color = color.convert("srgb")
                                start = m.end(0)
                                break
                            except Exception:
                                print(traceback.format_exc())
                                pass

            if color is not None:
                self._color = color

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
                        start = self.process_rgb(name, m)
                    elif name in ("rgb", "rgbmult"):
                        start = self.process_rgb_multi(m)
                    elif name == "hex":
                        start = self.process_hex(m)
                    elif name == "alpha":
                        start = self.process_alpha(m)
                    elif name == "hue":
                        start = self.process_hue(m)
                    elif name in ("saturation", "lightness", "whiteness", "blackness"):
                        start = self.process_hwb_hsl_channels(name, m)
                    elif name in ("tint", "shade"):
                        start = self.process_tint_shade(name, m)
                    elif name == "contrast":
                        start = self.process_contrast(m)
                    elif name == "min-contrast_start":
                        start = self.process_min_contrast(m, string)
                    elif name == "blend_start":
                        start = self.process_blend(m, string)
                    elif name == "end":
                        done = True
                        start = m.end(0)
                    else:
                        break
            else:
                raise ValueError('Could not calculate base color')
        except Exception:
            print(traceback.format_exc())
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
        pattern = "color({} {})".format(self._color.to_string(alpha=True), string)
        color, start = self._adjust(pattern)
        if color is not None:
            self._color.mutate(color)
        else:
            raise ValueError(
                "'{}' doesn't appear to be a valid and/or supported CSS color or color-mod instruction".format(string)
            )

    def adjust(self, string, start=0):
        """Adjust."""

        color, end = self._adjust(string, start=start)
        return color, end

    def process_rgb(self, name, m):
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
        return m.end(0)

    def process_rgb_multi(self, m):
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
        return m.end(0)

    def process_hex(self, m):
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
        return m.end(0)

    def process_alpha(self, m):
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
        return m.end(0)

    def process_hue(self, m):
        """Process hue."""

        value = m.group(2)
        value = parse.norm_angle(value) * parse.HUE_SCALE
        op = m.group(1).strip() if m.group(1) else ""
        self.hue(value, op=op)
        return m.end(0)

    def process_hwb_hsl_channels(self, name, m):
        """Process HWB and HSL channels (except hue)."""

        value = m.group(2)
        value = float(value.strip('%')) * parse.SCALE_PERCENT
        op = m.group(1).strip() if m.group(1) else ""
        getattr(self, name)(value, op=op)
        return m.end(0)

    def process_tint_shade(self, name, m):
        """Process tint/shade."""

        value = m.group(1)
        value = float(value.strip('%')) * parse.SCALE_PERCENT
        getattr(self, name)(value)
        return m.end(0)

    def process_contrast(self, m):
        """Process contrast."""

        value = m.group(1)
        value = float(value.strip('%')) * parse.SCALE_PERCENT
        self.contrast(value)
        return m.end(0)

    def process_blend(self, m, string):
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
            for obj in SUPPORTED:
                m = obj.MATCH.match(string, start)
                if m:
                    color2 = colorcss(string[start:m.end(0)])
                    start = m.end(0)
                    break
            if color2 is None:
                raise ValueError("Could not find a valid color for 'blend'")
        m = RE_BLEND_END.match(string, start)
        if m:
            value = float(m.group(1).strip('%')) * parse.SCALE_PERCENT
            cs = "srgb"
            if m.group(2):
                cs = m.group(2).lower()
                if cs == "rgb":
                    cs = "srgb"
            start = m.end(0)
        else:
            raise ValueError("Found unterminated or invalid 'blend('")
        self.blend(color2, value, alpha, cs=cs)
        return start

    def tint(self, percent):
        """Tint color."""

        self.blend(self._color.new("srgb", 'white'), percent, cs="srgb")

    def shade(self, percent):
        """Tint color."""

        self.blend(self._color.new("srgb", 'black'), percent, cs="srgb")

    def contrast(self, percent):
        """
        Get the color with the best contrast.

        # https://drafts.csswg.org/css-color/#contrast-adjuster
        """

        lum1 = self._color.luminance()

        max_hwb = self._color.convert("hwb")
        max_hwb._ch = self._color._ch
        if lum1 < 0.5:
            max_hwb.whiteness = 1.0
            max_hwb.blackness = 0.0
        else:
            max_hwb.whiteness = 0.0
            max_hwb.blackness = 1.0

        max_white = max_hwb.whiteness
        max_black = max_hwb.blackness
        lum2 = max_hwb.luminance()
        ratio = contrast_ratio(lum1, lum2)

        if ratio > 4.5:
            min_hwb = self._color.convert("hwb")
            min_hwb._ch = self._color._ch
            min_white = min_hwb.whiteness
            min_black = min_hwb.blackness

            last_ratio = ratio
            last_values = (max_white, max_black)

            while (abs(min_white - max_white) > 0.01 or abs(min_black - max_black) > 0.01):
                if lum1 < 0.5:
                    mid_white = round((max_white + min_white) / 2, 3)
                    mid_black = 1.0 - mid_white
                else:
                    mid_black = round((max_black + min_black) / 2, 3)
                    mid_white = 1.0 - mid_black

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

                if ratio < last_ratio and ratio > 4.5:
                    last_ratio = ratio
                    last_values = (mid_white, mid_black)

            # Use the best, last values
            min_hwb.whiteness = last_values[0]
            min_hwb.blackness = last_values[1]
        else:
            min_hwb = max_hwb.clone()

        max_hwb.mix(min_hwb, percent, cs="hwb")
        self._color.mutate(max_hwb)

    def process_min_contrast(self, m, string):
        """Process blend."""

        # Gather the min-contrast parameters
        start = m.end(0)
        alpha = m.group(0).startswith('blenda')
        m = RE_COLOR_START.match(string, start)
        if m:
            color2, start = self._adjust(string, start=start)
            if color2 is None:
                raise ValueError("Found unterminated or invalid 'color('")
        else:
            color2 = None
            for obj in SUPPORTED:
                m = obj.CSS_MATCH.match(string, start)
                if m:
                    color2 = colorcss(string[start:m.end(0)])
                    start = m.end(0)
                    break
            if color2 is None:
                raise ValueError("Could not find a valid color for 'min-contrast'")
        m = RE_MIN_CONTRAST_END.match(string, start)
        if m:
            value = float(m.group(1))
            start = m.end(0)
        else:
            raise ValueError("Found unterminated or invalid 'min-contrast('")

        # We can work with contrast lower than zero
        if value < 0:
            value = 0

        # Calculate current contrast ratio
        lum1 = self._color.luminance()
        temp = self._color.convert("srgb")
        lum2 = temp.luminance()
        ratio = contrast_ratio(lum1, lum2)

        # Set contrast range
        if (lum2 < 0.5 and ratio < value) or (lum2 >= 0.5 and ratio > value):
            max_contrast = 1.0 - min(min(temp.red, temp.green), temp.blue)
            min_contrast = 0.0
        else:
            max_contrast = 1.0 - max(max(temp.red, temp.green), temp.blue)
            min_contrast = -1.0

        # Set the max ratio as the current best
        last_ratio = ratio
        last_contrast = max_contrast

        # Use a binary search to quickly get close to the desired contrast
        mid = temp.clone()
        while (ratio < value or ratio > value + 0.1) and abs(min_contrast - max_contrast) > 0.01:
            mid_contrast = round((max_contrast + min_contrast) / 2, 3)
            mid.red = temp.red + mid_contrast
            mid.green = temp.green + mid_contrast
            mid.blue = temp.blue + mid_contrast
            lum2 = mid.luminance()
            ratio = contrast_ratio(lum1, lum2)

            if ratio < value:
                max_contrast = max_contrast
                min_contrast = mid_contrast
            else:
                max_contrast = min_contrast
                min_contrast = mid_contrast

            if (last_ratio < value and ratio > value) or (last_ratio > value and ration < last_ratio):
                last_contrast = ratio
                last_contrast = mid_contrast

        mid.red = temp.red + last_contrast
        mid.green = temp.green + last_contrast
        mid.blue = temp.blue + last_contrast
        self._color.mutate(mid)
        return start

    def blend(self, color, percent, alpha=False, cs="srgb"):
        """Blend color."""

        cs = cs.lower()
        if cs not in ("srgb", "hsl", "hwb"):
            raise ValueError(
                "ColorMod's does not support the '{}' colorspace, only 'srgb', 'hsl', and 'hwb' are SUPPORTED"
            ).format(cs)
        this = self._color.convert(cs) if self._color.space() != cs else self._color
        this._ch = self._color._ch

        if color.space() != cs:
            hue = color._ch
            color = color.convert(cs)
            color._ch = hue

        this.mix(color, percent, alpha=False, cs=cs)
        self._color.mutate(this)

    def red(self, value, op=""):
        """Red."""

        this = self._color.convert("SRGB") if self._color.space() != "srgb" else self._color
        this._ch = self._color._ch
        op = self.OP_MAP.get(op, self._op_null)
        this._cr = op(this._cr, value)
        self._color.mutate(this)

    def green(self, value, op=""):
        """Green."""

        this = self._color.convert("SRGB") if self._color.space() != "srgb" else self._color
        this._ch = self._color._ch
        op = self.OP_MAP.get(op, self._op_null)
        this._cg = op(this._cg, value)
        self._color.mutate(this)

    def blue(self, value, op=""):
        """Blue."""

        this = self._color.convert("SRGB") if self._color.space() != "srgb" else self._color
        this._ch = self._color._ch
        op = self.OP_MAP.get(op, self._op_null)
        this._cb = op(this._cb, value)
        self._color.mutate(this)

    def alpha(self, value, op=""):
        """Alpha."""

        this = self._color
        op = self.OP_MAP.get(op, self._op_null)
        this._alpha = op(this._alpha, value)
        self._color.mutate(this)

    def hue(self, value, op=""):
        """Hue."""

        if self._color.is_achromatic():
            return
        this = self._color.convert("hsl") if self._color.space() != "hsl" else self._color
        op = self.OP_MAP.get(op, self._op_null)
        this._ch = op(this._ch, value)
        self._color.mutate(this)

    def lightness(self, value, op=""):
        """Lightness."""

        this = self._color.convert("hsl") if self._color.space() != "hsl" else self._color
        this._ch = self._color._ch
        op = self.OP_MAP.get(op, self._op_null)
        this._cl = op(this._cl, value)
        self._color.mutate(this)

    def saturation(self, value, op=""):
        """Saturation."""

        this = self._color.convert("hsl") if self._color.space() != "hsl" else self._color
        this._ch = self._color._ch
        op = self.OP_MAP.get(op, self._op_null)
        this._cs = op(this._cs, value)
        self._color.mutate(this)

    def whiteness(self, value, op=""):
        """White."""

        this = self._color.convert('hsb') if self._color.space() != "hwb" else self._color
        this._ch = self._color._ch
        achromatic = this.is_achromatic()
        op = self.OP_MAP.get(op, self._op_null)
        this._cw = op(this._cw, value)
        if achromatic:
            self._c3 = 1.0 - self._c2
        self._color.mutate(this)

    def blackness(self, value, op=""):
        """Black."""

        this = self._color.convert('hsb') if self._color.space() != "hwb" else self._color
        this._ch = self._color._ch
        achromatic = this.is_achromatic()
        op = self.OP_MAP.get(op, self._op_null)
        this._cb = op(this._cb, value)
        if achromatic:
            self._c2 = 1.0 - self._c3
        self._color.mutate(this)


def colormod(string, variables=None):
    """Parse a CSS color."""

    match = colormod_match(string, variables, fullmatch=True)
    if match is not None:
        return match.color


def colormod_match(string, variables=None, start=0, fullmatch=False):
    """Match a color at the given position."""

    # Handle variable
    end = None
    is_mod = False
    if variables:
        m = parse.RE_VARS.match(string, start)
        if m and (not fullmatch or len(string) == m.end(0)):
            end = m.end(0)
            start = 0
            string = string[start:end]
            string = parse.handle_vars(string, variables)
            variables = None

    temp = parse.bracket_match(RE_COLOR_START, string, start, fullmatch)
    if end is None and temp:
        end = temp
        is_mod = True
    elif end is not None and temp is not None:
        is_mod = True

    if is_mod:
        if variables:
            string = parse.handle_vars(string, variables)
        obj, match_end = ColorMod(fullmatch).adjust(string, start)
        if obj is not None:
            return ColorMatch(obj, start, end if end is not None else match_end)
    else:
        obj = colorcss_match(string, start=start, fullmatch=fullmatch, variables=variables)
        if end:
            obj.end = end
        return obj
