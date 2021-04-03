self.languagePluginUrl = 'https://cdn.jsdelivr.net/pyodide/v0.17.0a2/full/';
importScripts('https://cdn.jsdelivr.net/pyodide/v0.17.0a2/full/pyodide.js');
let pythonLoading;

const pycode = `
from collections.abc import Sequence
from collections import namedtuple
import ast
from io import StringIO
import contextlib
import sys
import re
import functools
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import find_formatter_class
HtmlFormatter = find_formatter_class('html')

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

    colors = []
    if isinstance(result, Color):
        colors.append(ColorTuple(result.to_string(), result))
    elif isinstance(result, functools.partial) and result.func.__name__ == '_interpolate':
        colors = ColorInterpolate()
        for x in range(20):
            c = result(x / 20)
            colors.append(ColorTuple(c.to_string(), c))
    elif isinstance(result, str):
        try:
            colors.append(ColorTuple(result, Color(result)))
        except Exception:
            pass
    elif isinstance(result, Sequence):
        for x in result:
            if isinstance(x, Color):
                colors.append(ColorTuple(x.to_string(), x))
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

    from coloraide import Color, NaN, __version__

    g = {'Color': Color, 'NaN': NaN, '__version__': __version__, '__builtins__': {'print': print}}
    console = ''
    colors = []

    # Build AST tree
    src = cmd.strip()
    lines = src.split('\\n')
    tree = ast.parse(src)

    for node in tree.body:
        result = None

        # Format source as Python console statements
        start = node.lineno
        end = node.end_lineno
        stmt = lines[start - 1: end]
        for i, line in enumerate(stmt, 0):
            if i == 0:
                stmt[i] = '>>> ' + line
            else:
                stmt[i] = '... ' + line
        console += '\\n'.join(stmt)
        if isinstance(node, AST_BLOCKS):
            console += '\\n... '

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

            # Output captured standard out after statements
            text = s.getvalue()
            if text:
                clist = find_colors(text)
                if clist:
                    colors.extend(clist)
                console += '\\n{}'.format(text)
            s.flush()

        # If we got a result, output it as well
        if result is not None:
            clist = get_colors(result)
            if clist:
                colors.append(clist)
            console += '{}{}'.format('\\n' if not text else '', str(result))
        console += '\\n'

    return console, colors


def colorize(src, lang, **options):
    """Colorize."""

    lexer = get_lexer_by_name(lang, **options)
    formatter = HtmlFormatter(cssclass="highlight", wrapcode=True)
    return highlight(src, lexer, formatter).strip()


def color_command_formatter(src):
    """Formatter wrapper."""

    from coloraide import Color

    try:
        fit = True
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
                    color.color.fit("srgb", in_place=True)
                    stops.append(color.color.convert("srgb").to_string(hex=True))
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
                    if not color.color.in_gamut('srgb') and not fit:
                        c = '<span class="swatch-color"></span>'
                        classes = base_classes + " out-of-gamut"
                        title = "Out of Gamut&#10;{}".format(color.string)
                    else:
                        color.color.fit('srgb', in_place=True)
                        srgb = color.color.convert('srgb')
                        value1 = srgb.to_string(hex=True, alpha=False)
                        value2 = srgb.to_string(hex=True)
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

        el += colorize(console, 'pycon', **{'python3': True})
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception as e:
        return '<div class="color-command"><div class="swatch-bar"></div>{}</div>'.format(colorize('', 'text'))
    return el
`

function analyze(str) {
    code = `
import micropip

${pycode}

text = """
${str.replace('"', '\\"')}
"""

def parse_colors(*args):
    """Get colors."""

    globals()['results'] = color_command_formatter(text)
    print(globals()['results'])

micropip.install('coloraide').add_done_callback(parse_colors)

`
    languagePluginLoader.then(() => {
      return pyodide.loadPackage(['micropip', 'Pygments']);
    }).then(() => {
      console.log(pyodide.runPython(code));
      setTimeout(post, 500);
    });
}

function post() {
   self.postMessage(pyodide.globals.get("results"));
}


self.addEventListener("message", (event) => {
    analyze(event.data);
});
