"""Color swatch."""
from coloraide.css import Color
from pymdownx import superfences
import xml.etree.ElementTree as Etree


def execute(cmd):
    """Execute color commands."""

    g = {'Color': Color}
    exec(cmd, g)
    return g['result']


def _block_color_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Formatter wrapper."""

    try:
        colors = execute(src.strip())
        el = '<div class="swatch swatch-gradient">{}</div>'
        style = "--swatch-stops: "
        stops = []
        for color in colors:
            color.fit("srgb", in_place=True)
            stops.append(color.convert("srgb").to_string(hex=True))
        if not stops:
            stops.extend(['transparent'] * 2)
        if len(stops) == 1:
            stops.append(stops[0])
        style += ','.join(stops)
        sub_el = '<div class="swatch-color" style="{}"></div>'.format(style)
        el = el.format(sub_el)
    except Exception as e:
        print(e)
        return superfences.fence_code_format(src, language, class_name, options, md, **kwargs)
    return el


def _color_formatter(src="", language="", class_name=None, md="", show_code=True, fit=False):
    """Formatter wrapper."""

    src = src.strip()
    try:
        color = Color(src)
        el = Etree.Element('span')
        stops = []
        if not color.in_gamut("srgb"):
            if fit:
                color.fit("srgb", in_place=True)
                attributes = {'class': "swatch", "title": src}
                sub_el = Etree.SubElement(el, 'span', attributes)
                stops.append(color.convert("srgb").to_string(hex=True, alpha=False))
                if color.alpha < 1.0:
                    stops[-1] += ' 50%'
                    stops.append(color.convert("srgb").to_string(hex=True) + ' 50%')
            else:
                attributes = {'class': "swatch out-of-gamut", "title": "Out of Gamut&#10;{}".format(src)}
                sub_el = Etree.SubElement(el, 'span', attributes)
        else:
            attributes = {'class': "swatch", "title": src}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert("srgb").to_string(hex=True, alpha=False))
            if color.alpha < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert("srgb").to_string(hex=True) + ' 50%')

        if not stops:
            stops.extend(['transparent'] * 2)
        if len(stops) == 1:
            stops.append(stops[0])

        Etree.SubElement(
            sub_el,
            'span',
            {
                "class": "swatch-color",
                "style": "--swatch-stops: {};".format(','.join(stops))
            }
        )

        if show_code:
            el.append(md.inlinePatterns['backtick'].handle_code('css-color', src))
    except Exception:
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el


def color_gradient_formatter(src="", language="", class_name=None, md=""):
    """Format gradient."""

    try:
        colors = execute(src.strip())
        el = Etree.Element('span', {'class': "swatch swatch-gradient"})
        style = "--swatch-stops: "
        stops = []
        for color in colors:
            color.fit("srgb", in_place=True)
            stops.append(color.convert("srgb").to_string(hex=True))
        if not stops:
            stops.extend(['transparent'] * 2)
        if len(stops) == 1:
            stops.append(stops[0])
        style += ','.join(stops)
        Etree.SubElement(el, 'span', {'class': 'swatch-color', 'style': style})
    except Exception:
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el


def color_steps_formatter(src="", language="", class_name=None, md=""):
    """Format steps."""

    colors = execute(src.strip())
    el = Etree.Element('span')
    el.text = "["

    try:
        last = None
        for color in colors:
            if last is not None:
                last.tail = ','
            cstring = color.to_string()
            sub_el = color_formatter_color_only(cstring, '', class_name, md)
            el.append(sub_el)
            last = sub_el
        if last is not None:
            last.tail = ']'
        else:
            el.text += ']'
    except Exception:
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el


def color_formatter(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True)


def color_formatter_fit(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True, True)


def color_formatter_color_only(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, False)


def color_formatter_color_only_fit(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, False, True)
