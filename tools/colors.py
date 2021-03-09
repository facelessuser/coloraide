"""Color swatch."""
from coloraide.css import Color
from pymdownx import superfences
import xml.etree.ElementTree as Etree
from collections.abc import Sequence, Callable
import ast


def execute(cmd):
    """Execute color commands."""

    g = {'Color': Color}
    tree = ast.parse(cmd)
    _exec = ast.Module(tree.body[:-1], [])
    _eval = ast.Expression(tree.body[-1].value)
    exec(compile(_exec, '<string>', 'exec'), g)
    result = eval(compile(_eval, '<string>', 'eval'), g)
    return result


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
            result = execute(src.strip())
        except Exception:
            result = src.strip()
        fit = options.get('fit', False)
        css = options.get('css', False)
        steps = False
        gradient = False
        lang = 'py3'
        processed = src
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
                    if not steps:
                        processed += '\n# {}'.format(color.to_string())
                    c = '<{tag} class="swatch-color"></{tag}>'.format(tag=tag)
                    classes = base_classes + " out-of-gamut"
                    title = "Out of Gamut&#10;{}".format(color.to_string())
                else:
                    if not steps:
                        processed += '\n# {}'.format(color.to_string())
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

    try:
        result = src.strip()
        cmd = False
        try:
            result = execute(result)
            cmd = True
        except Exception as e:
            print(e)
            result = src.strip()
        if isinstance(result, (str, Color)):
            color = Color(result)
            if cmd:
                result = color.to_string()
        else:
            raise TypeError('Not a string or color')
        el = Etree.Element('span')
        stops = []
        if not color.in_gamut("srgb"):
            if fit:
                color.fit("srgb", in_place=True)
                attributes = {'class': "swatch", "title": result}
                sub_el = Etree.SubElement(el, 'span', attributes)
                stops.append(color.convert("srgb").to_string(hex=True, alpha=False))
                if color.alpha < 1.0:
                    stops[-1] += ' 50%'
                    stops.append(color.convert("srgb").to_string(hex=True) + ' 50%')
            else:
                attributes = {'class': "swatch out-of-gamut", "title": "Out of Gamut&#10;{}".format(result)}
                sub_el = Etree.SubElement(el, 'span', attributes)
        else:
            attributes = {'class': "swatch", "title": result}
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
            el.append(md.inlinePatterns['backtick'].handle_code('css-color', result))
    except Exception as e:
        print(e)
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el


def color_formatter(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True)


def color_formatter_fit(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True, True)
