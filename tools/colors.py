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

    valid_inputs = {'fit'}

    for k, v in inputs.items():
        if k in valid_inputs:
            options[k] = True
            continue
        attrs[k] = v
    return True


def command_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Commands."""

    try:
        result = execute(src.strip())
        options['linenums'] = '1'
        el = md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=src,
            class_name="highlight",
            language='py3',
            md=md,
            options=options,
            **kwargs
        )
        el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=str(result),
            class_name="highlight",
            language='pycon3',
            md=md,
            options=[],
            **kwargs
        )
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception:
        import traceback
        print(traceback.format_exc())
        return superfences.fence_code_format(src, language, class_name, options, md, **kwargs)
    return el


def color_command_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Formatter wrapper."""

    try:
        css = False
        fit = options.get('fit', False)
        try:
            result = execute(src.strip())
        except Exception:
            css = True
            lang = 'css-color'
            result = src.strip()
        gradient = False
        lang = 'py3'
        output = ''
        if isinstance(result, Color):
            colors = [result]
            output = '\n'.join([x.to_string() for x in colors])
        elif isinstance(result, Callable):
            colors = list(map(lambda x: result(x / 20), range(20)))
            output = '\n'.join([x.to_string() for x in colors])
            gradient = True
        elif isinstance(result, str):
            colors = [Color(result)]
            if not css:
                output = '{}'.format(result)
        elif isinstance(result, Sequence):
            colors = []
            text = []
            for x in result:
                colors.append(Color(x))
                text.append(x if isinstance(x, str) else colors[-1].to_string())
            output = '\n'.join(text)
        else:
            raise TypeError('Not a string, color, or sequence')

        if gradient:
            el = '<div class="swatch-bar"><div class="swatch swatch-gradient">{}</div></div>'
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
            values = []
            base_classes = "swatch"
            for color in colors:
                if not color.in_gamut('srgb') and not fit:
                    c = '<span class="swatch-color"></span>'
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
                    c = '<span class="swatch-color" style="{style}"></span>'.format(style=style)
                c = '<span class="{classes}" title="{title}">{color}</span>'.format(
                    classes=classes,
                    color=c,
                    title=title
                )
                values.append(c)
            el = '<div class="swatch-bar">{}</div>'.format(' '.join(values))

        if not css:
            options['linenums'] = '1'

        el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=src,
            class_name="highlight",
            language=lang,
            md=md,
            options=options,
            **kwargs
        )

        if not css and output:
            el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
                src=output,
                class_name="highlight",
                language='css-color',
                md=md,
                options=[],
                **kwargs
            )
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception:
        import traceback
        print(traceback.format_exc())
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
        except Exception:
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
    except Exception:
        # print(e)
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el


def color_formatter(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True)


def color_formatter_fit(src="", language="", class_name=None, md=""):
    """Format color."""

    return _color_formatter(src, language, class_name, md, True, True)
