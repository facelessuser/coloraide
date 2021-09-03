"""
Execute Python code in code blocks (color previews added specifically for ColorAide).

This is meant to be executed by Pyodide on preformatted HTML to allow for live execution of
code snippets using `coloraide`.

Transform Python code by executing it, transforming to a Python console output,
and finding and outputting color previews.
"""
import micropip
from js import document, location
from collections.abc import Sequence
from collections import namedtuple
import ast
from io import StringIO
import contextlib
import sys
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import find_formatter_class
HtmlFormatter = find_formatter_class('html')

inputs = document.getElementById("__playground-inputs_{}".format(globals()['id_num']))
results = document.getElementById("__playground-results_{}".format(globals()['id_num']))
pgcode = document.getElementById("__playground-code_{}".format(globals()['id_num']))

AST_BLOCKS = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.FunctionDef, ast.ClassDef)

RE_COLOR_START = re.compile(
    r"(?i)(?:\\b(?<![-#&$])(?:color|hsla?|lch|lab|hwb|rgba?)\\(|\\b(?<![-#&$])[\\w]{3,}(?![(-])\\b|(?<![&])#)"
)


class ColorInterpolate(list):
    """Color interpolate."""


class ColorTuple(namedtuple('ColorTuple', ['string', 'color'])):
    """Color tuple."""


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

    from coloraide import Color
    from coloraide.color.interpolate import Interpolator

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

    from coloraide import Color

    colors = []
    for m in RE_COLOR_START.finditer(text):
        start = m.start()
        mcolor = Color.match(text, start=start)
        if mcolor is not None:
            colors.append(ColorTuple(text[mcolor.start:mcolor.end], mcolor.color))
    return colors


def execute(cmd):
    """Execute color commands."""

    import coloraide
    from coloraide import Color, NaN, Piecewise

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

        try:
            # Capture anything sent to standard out
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


def colorize(src, lang, **options):
    """Colorize."""

    lexer = get_lexer_by_name(lang, **options)
    formatter = HtmlFormatter(cssclass="highlight", wrapcode=True)
    return highlight(src, lexer, formatter).strip()


def color_command_formatter(src):
    """Formatter wrapper."""

    try:
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
        if not colors:
            el += '<div class="swatch-bar"></div>'

        el += colorize(console, 'pycon', **{'python3': True, 'stripnl': False})
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception:
        return '<div class="color-command"><div class="swatch-bar"></div>{}</div>'.format(colorize('', 'text'))
    return el


def process_code(*args):
    """Process code."""

    try:
        # Run code
        results.innerHTML = color_command_formatter(inputs.value)
        scrollingElement = results.querySelector('code')
        scrollingElement.scrollTop = scrollingElement.scrollHeight
    except Exception as e:
        print(e)


wheel = ''

micropip.install(location.origin + '/coloraide/playground/' + wheel).add_done_callback(process_code)
