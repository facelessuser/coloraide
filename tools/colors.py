"""Color swatch."""
from coloraide.css import Color
import xml.etree.ElementTree as Etree


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
            el.append(md.inlinePatterns['backtick'].handle_code('', src))
    except Exception:
        el = md.inlinePatterns['backtick'].handle_code('', src)
    return el


def color_gradient_formatter(src="", language="", class_name=None, md=""):
    """Format gradient."""

    src_color = [c.strip() for c in src.strip().split(';')]

    el = Etree.Element('span', {'class': "swatch swatch-gradient"})
    try:
        style = "--swatch-stops: "
        stops = []
        for c in src_color:
            color = Color(c)
            color.fit("srgb", in_place=True)
            stops.append(color.convert("srgb").to_string(hex=True))
        if not stops:
            stops.extend(['transparent'] * 2)
        if len(stops) == 1:
            stops.append(stops[0])
        style += ','.join(stops)
        Etree.SubElement(el, 'span', {'class': 'swatch-color', 'style': style})
    except Exception:
        el = md.inlinePatterns['backtick'].handle_code('', src)
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
