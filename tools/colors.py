"""Color swatch."""
from coloraide.css import Color
from pymdownx import superfences
import xml.etree.ElementTree as Etree
from collections.abc import Sequence, Callable


def execute(cmd):
    """Execute color commands."""

    g = {'Color': Color}
    lines = [l for l in cmd.strip().split('\n')]
    end = lines.pop(-1)
    exec(compile('\n'.join(lines), '<string>', 'exec'), g)
    result = eval(compile(end, '<string>', 'eval'), g)
    if isinstance(result, (Color, str)):
        cmd += '\n# {}'.format(str(result))
    return result, cmd


def color_command_validator(language, inputs, options, attrs, md):
    """Color validator."""

    valid_inputs = {'fit', 'css'}

    for k, v in inputs.items():
        if k in valid_inputs:
            options[k] = True
            continue
        attrs[k] = v
    return True


def color_command_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Formatter wrapper."""

    try:
        try:
            result, processed = execute(src.strip())
        except Exception:
            result = src.strip()
        fit = options.get('fit', False)
        css = options.get('css', False)
        steps = False
        gradient = False
        lang = 'py3'
        if isinstance(result, Color):
            colors = [result]
        elif isinstance(result, Callable):
            colors = list(map(lambda x: result(x / 20), range(20)))
            gradient = True
        elif isinstance(result, str):
            colors = [Color(result)]
            if css:
                lang = 'css-color'
        elif isinstance(result, Sequence):
            colors = result
            steps = True

        if gradient:
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
        else:
            if steps:
                tag = "span"
                base_classes = "swatch"
            else:
                tag = "div"
                base_classes = "swatch swatch-gradient"
            values = []
            for color in colors:
                if not color.in_gamut('srgb') and not fit:
                    c = '<{tag} class="swatch-color"></{tag}>'.format(tag=tag)
                    classes = base_classes + " out-of-gamut"
                    title = "Out of Gamut&#10;{}".format(color.to_string())
                else:
                    color.fit('srgb', in_place=True)
                    srgb = color.convert('srgb')
                    value1 = srgb.to_string(hex=True, alpha=False)
                    value2 = srgb.to_string(hex=True)
                    style = "--swatch-stops: {} 50%, {} 50%".format(value1, value2)
                    title = color.to_string()
                    classes = base_classes
                    c = '<{tag} class="swatch-color" style="{style}"></{tag}>'.format(tag=tag, style=style)
                c = '<{tag} class="{classes}" title="{title}">{color}</{tag}>'.format(
                    tag=tag,
                    classes=classes,
                    color=c,
                    title=title
                )
                values.append(c)
            if steps:
                el = '<div class="swatch-steps">{}</div>'.format(' '.join(values))
            else:
                el = values[0]

        el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=processed,
            class_name="highlight",
            language=lang,
            md=md,
            options=options,
            **kwargs
        )
        el = '<div class="color-command">{}</div>'.format(el)
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


def color_formatter(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True)


def color_formatter_fit(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True, True)
