"""
Color playground.

Any fenced code blocks with `playground` as the language will be converted to interactive playgrounds that
are initialized with the results of the initial contents.

Any inline code blocks with `color` as the language will be evaluated as a simple color swatch.
"""
import coloraide
from coloraide import Color, NaN, Piecewise
from coloraide.interpolate import Interpolator
from pymdownx import superfences
import xml.etree.ElementTree as Etree
from collections.abc import Sequence
from collections import namedtuple
import ast
from io import StringIO
import contextlib
import sys
import re
import traceback

AST_BLOCKS = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.FunctionDef, ast.ClassDef)

RE_COLOR_START = re.compile(
    r"(?i)(?:\b(?<![-#&$])(?:color|hsla?|lch|lab|hwb|rgba?)\(|\b(?<![-#&$])[\w]{3,}(?![(-])\b|(?<![&])#)"
)

template = '''<div class="playground" id="__playground_{el_id}">
<div class="playground-results" id="__playground-results_{el_id}">
{results}
</div>
<div class="playground-code hidden" id="__playground-code_{el_id}">
<form autocomplete="off">
<textarea class="playground-inputs" id="__playground-inputs_{el_id}" spellcheck="false">{raw_source}</textarea>
</form>
</div>

<button id="__playground-edit_{el_id}" class="playground-edit" title="Edit the current snippet">Edit</button>
<button id="__playground-share_{el_id}" class="playground-share" title="Copy URL to current snippet">Share</button>
<button id="__playground-run_{el_id}" class="playground-run hidden" title="Run code (Ctrl + Enter)">Run</button>
<button id="__playground-cancel_{el_id}" class="playground-cancel hidden" title="Cancel edit (Escape)">Cancel</button>
</div>'''

code_id = 0


class ColorInterpolate(list):
    """Color interpolate."""


class ColorTuple(namedtuple('ColorTuple', ['string', 'color'])):
    """Color tuple."""


def _escape(txt):
    """Basic HTML escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    return txt


@contextlib.contextmanager
def std_output(stdout=None):
    """Capture standard out."""
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def get_colors(result):
    """Get color from results."""

    colors = []
    if isinstance(result, Color):
        colors.append(ColorTuple(result.to_string(fit=False), result))
    elif isinstance(result, Interpolator):
        colors = ColorInterpolate(result.steps(steps=5, max_delta_e=4))
    elif isinstance(result, str):
        try:
            colors.append(ColorTuple(result, Color(result)))
        except Exception:
            pass
    elif isinstance(result, Sequence):
        for x in result:
            if isinstance(x, Color):
                colors.append(ColorTuple(x.to_string(fit=False), x))
            elif isinstance(x, str):
                try:
                    colors.append(ColorTuple(x, Color(x)))
                except Exception:
                    pass
    return colors


def find_colors(text):
    """Find colors in text buffer."""

    colors = []
    for m in RE_COLOR_START.finditer(text):
        start = m.start()
        mcolor = Color.match(text, start=start)
        if mcolor is not None:
            colors.append(ColorTuple(text[mcolor.start:mcolor.end], mcolor.color))
    return colors


def execute(cmd):
    """Execute color commands."""

    g = {'Color': Color, 'coloraide': coloraide, 'NaN': NaN, 'Piecewise': Piecewise}
    console = ''
    colors = []

    # Build AST tree
    src = cmd.strip()
    lines = src.split('\n')
    tree = ast.parse(src)

    for node in tree.body:
        result = None

        # Format source as Python console statements
        start = node.lineno
        end = node.end_lineno
        stmt = lines[start - 1: end]
        command = ''
        for i, line in enumerate(stmt, 0):
            if i == 0:
                stmt[i] = '>>> ' + line
            else:
                stmt[i] = '... ' + line
        command += '\n'.join(stmt)
        if isinstance(node, AST_BLOCKS):
            command += '\n... '

        # Capture anything sent to standard out
        try:
            text = ''
            with std_output() as s:
                # Execute code
                if isinstance(node, ast.Expr):
                    _eval = ast.Expression(node.value)
                    result = eval(compile(_eval, '<string>', 'eval'), g)
                else:
                    _exec = ast.Module([node], [])
                    exec(compile(_exec, '<string>', 'exec'), g)

                # Execution went well, so append command
                console += command

                # Output captured standard out after statements
                text = s.getvalue()
                if text:
                    clist = find_colors(text)
                    if clist:
                        colors.append(clist)
                    console += '\n{}'.format(text)
                s.flush()
        except Exception:
            console += '{}\n{}'.format(command, traceback.format_exc())
            # Failed for some reason, so quit
            break

        # If we got a result, output it as well
        if result is not None:
            clist = get_colors(result)
            if clist:
                colors.append(clist)
            console += '{}{}\n'.format('\n' if not text else '', str(result))
        else:
            console += '\n' if not text else ''

    return console, colors


def color_command_validator(language, inputs, options, attrs, md):
    """Color validator."""

    valid_inputs = set()

    for k, v in inputs.items():
        if k in valid_inputs:
            options[k] = True
            continue
        attrs[k] = v
    return True


def color_command_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Formatter wrapper."""

    global code_id

    try:
        if len(md.preprocessors['fenced_code_block'].extension.stash) == 0:
            code_id = 0

        console, colors = execute(src.strip())
        el = ''
        bar = False
        values = []
        for item in colors:
            if isinstance(item, ColorInterpolate):
                if bar:
                    el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                    values = []
                sub_el1 = '<div class="swatch-bar"><span class="swatch swatch-gradient">{}</span></div>'
                style = "--swatch-stops: "
                stops = []
                for color in item:
                    color.fit("srgb", in_place=True)
                    stops.append(color.convert("srgb").to_string())
                if not stops:
                    stops.extend(['transparent'] * 2)
                if len(stops) == 1:
                    stops.append(stops[0])
                style += ','.join(stops)
                sub_el2 = '<span class="swatch-color" style="{}"></span>'.format(style)
                el += sub_el1.format(sub_el2)
                bar = False
            else:
                bar = True
                base_classes = "swatch"
                for color in item:
                    if not color.color.in_gamut('srgb'):
                        base_classes += " out-of-gamut"
                    color.color.fit('srgb', in_place=True)
                    srgb = color.color.convert('srgb')
                    value1 = srgb.to_string(alpha=False)
                    value2 = srgb.to_string()
                    style = "--swatch-stops: {} 50%, {} 50%".format(value1, value2)
                    title = color.string
                    classes = base_classes
                    c = '<span class="swatch-color" style="{style}"></span>'.format(style=style)
                    c = '<span class="{classes}" title="{title}">{color}</span>'.format(
                        classes=classes,
                        color=c,
                        title=title
                    )
                    values.append(c)
        if bar:
            el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
            values = []

        el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=console,
            class_name="highlight",
            language='pycon3',
            md=md,
            options=options,
            **kwargs
        )
        el = '<div class="color-command">{}</div>'.format(el)
        el = template.format(el_id=code_id, raw_source=_escape(src), results=el)
        code_id += 1
    except Exception:
        import traceback
        print(traceback.format_exc())
        return superfences.fence_code_format(src, 'text', class_name, options, md, **kwargs)

    return el


def color_formatter(src="", language="", class_name=None, md=""):
    """Formatter wrapper."""

    try:
        result = src.strip()
        try:
            console, colors = execute(result)
            if len(colors) != 1 or len(colors[0]) != 1:
                raise ValueError('Need one color only')
            color = colors[0][0].color
            result = colors[0][0].string
        except Exception:
            color = Color(result.strip())
        el = Etree.Element('span')
        stops = []
        if not color.in_gamut("srgb"):
            color.fit("srgb", in_place=True)
            attributes = {'class': "swatch out-of-gamut", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert("srgb").to_string(hex=True, alpha=False))
            if color.alpha < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert("srgb").to_string(hex=True) + ' 50%')
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

        el.append(md.inlinePatterns['backtick'].handle_code('css-color', result))
    except Exception:
        import traceback
        print(traceback.format_exc())
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el
