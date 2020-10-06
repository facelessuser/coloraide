"""Color swatch."""
from coloraide.css import Color
import xml.etree.ElementTree as etree
from markdown import util as md_util


def _escape(txt):
    """Basic html escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


def _color_formatter(src="", language="", class_name=None, md="", show_code=True, fit=False):
    """Formatter wrapper."""

    src = src.strip()
    try:
        color =  Color(src)
        el = etree.Element('span')
        if not color.in_gamut("srgb"):
            if fit:
                color.fit("srgb", in_place=True)
                attributes = {'class': "swatch", "title": src}
                sub_el = etree.SubElement(el, 'span', attributes)
            else:
                attributes = {'class': "swatch out-of-gamut", "title": "Out of Gamut&#10;{}".format(src)}
                sub_el = etree.SubElement(el, 'span', attributes)
        else:
            attributes = {'class': "swatch", "title": src}
            sub_el = etree.SubElement(el, 'span', attributes)
        etree.SubElement(
            sub_el,
            'span',
            {
                "class": "swatch-color",
                "style": "background-color: {};".format(color.convert("srgb").to_string(hex=True, alpha=False))
            }
        )
        if color.alpha < 1.0:
            etree.SubElement(
                sub_el,
                'span',
                {
                    "class": "swatch-color",
                    "style": "background-color: {};".format(color.convert("srgb").to_string(hex=True))
                }
            )
        if show_code:
            el.append(md.inlinePatterns['backtick'].handle_code('', src))
    except Exception as e:
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
