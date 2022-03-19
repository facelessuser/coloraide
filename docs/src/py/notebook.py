"""
Execute Python code in code blocks (color previews added specifically for ColorAide).

This is meant to be executed by Pyodide on preformatted HTML to allow for live execution of
code snippets using `coloraide`.

Transform Python code by executing it, transforming to a Python console output,
and finding and outputting color previews.
"""
import micropip
from js import document, location
import xml.etree.ElementTree as Etree
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

WEBSPACE = "srgb"
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


class ColorRow():
    """Force a new color row."""


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

    from coloraide import Color
    import coloraide_extras
    from coloraide.interpolate import Interpolator

    colors = []
    if isinstance(result, Color):
        colors.append(ColorTuple(result.to_string(fit=False), result.clone()))
    elif isinstance(result, Interpolator):
        colors = ColorInterpolate(result.steps(steps=5, max_delta_e=3))
    elif isinstance(result, ColorRow):
        colors = result
    elif isinstance(result, str):
        try:
            colors.append(ColorTuple(result, coloraide_extras.Color(result)))
        except Exception:
            pass
    elif isinstance(result, Sequence):
        for x in result:
            if isinstance(x, Color):
                colors.append(ColorTuple(x.to_string(fit=False), x.clone()))
            elif isinstance(x, str):
                try:
                    colors.append(ColorTuple(x, coloraide_extras.Color(x)))
                except Exception:
                    pass
    return colors


def find_colors(text):
    """Find colors in text buffer."""

    import coloraide_extras

    colors = []
    for m in RE_COLOR_START.finditer(text):
        start = m.start()
        mcolor = coloraide_extras.Color.match(text, start=start)
        if mcolor is not None:
            colors.append(ColorTuple(text[mcolor.start:mcolor.end], mcolor.color))
    return colors


def execute(cmd):
    """Execute color commands."""

    import coloraide
    import coloraide_extras

    g = {
        'Color': coloraide.Color,
        'coloraide_extras': coloraide_extras,
        'coloraide': coloraide,
        'NaN': coloraide.NaN,
        'Piecewise': coloraide.Piecewise,
        'ColorRow': ColorRow
    }
    console = ''
    colors = []

    # Build AST tree
    src = cmd.strip()
    lines = src.split('\n')
    try:
        tree = ast.parse(src)
    except Exception:
        import traceback
        return '{}'.format(traceback.format_exc()), colors

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
            import traceback
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


def colorize(src, lang, **options):
    """Colorize."""

    lexer = get_lexer_by_name(lang, **options)
    formatter = HtmlFormatter(cssclass="highlight", wrapcode=True)
    return highlight(src, lexer, formatter).strip()


def color_command_validator(language, inputs, options, attrs, md):
    """Color validator."""

    valid_inputs = set()

    for k, v in inputs.items():
        if k in valid_inputs:
            options[k] = True
            continue
        attrs[k] = v
    return True


def _color_command_console(colors):
    """Color command formatter."""

    el = ''
    bar = False
    values = []
    for item in colors:
        if isinstance(item, ColorRow):
            if bar:
                el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                values = []
            bar = False
        elif isinstance(item, ColorInterpolate):
            if bar:
                el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                values = []
            sub_el1 = '<div class="swatch-bar"><span class="swatch swatch-gradient">{}</span></div>'
            style = "--swatch-stops: "
            stops = []
            for color in item:
                color.fit(WEBSPACE, in_place=True)
                stops.append(color.convert(WEBSPACE).to_string())
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
                if not color.color.in_gamut(WEBSPACE):
                    base_classes += " out-of-gamut"
                color.color.fit(WEBSPACE, in_place=True)
                srgb = color.color.convert(WEBSPACE)
                value1 = srgb.to_string(alpha=False)
                value2 = srgb.to_string()
                style = "--swatch-stops: {} 50%, {} 50%".format(value1, value2)
                title = color.string
                classes = base_classes
                c = '<span class="swatch-color" style="{style}"></span>'.format(style=style)
                c = '<span class="{classes}" title="{title}&#013;Copy to clipboard">{color}</span>'.format(
                    classes=classes,
                    color=c,
                    title=title
                )
                values.append(c)
    if bar:
        el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
        values = []

    return el


def color_command_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Formatter wrapper."""

    global code_id

    try:
        if len(md.preprocessors['fenced_code_block'].extension.stash) == 0:
            code_id = 0

        console, colors = execute(src.strip())
        el = _color_command_console(colors)

        el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=console,
            class_name="highlight",
            language='pycon',
            md=md,
            options=options,
            **kwargs
        )
        el = '<div class="color-command">{}</div>'.format(el)
        el = template.format(el_id=code_id, raw_source=_escape(src), results=el)
        code_id += 1
    except Exception:
        from pymdownx import superfences
        import traceback
        print(traceback.format_exc())
        return superfences.fence_code_format(src, 'text', class_name, options, md, **kwargs)
    return el


def live_color_command_formatter(src):
    """Formatter wrapper."""

    try:
        console, colors = execute(src.strip())
        el = _color_command_console(colors)

        if not colors:
            el += '<div class="swatch-bar"></div>'

        el += colorize(console, 'pycon', **{'python3': True, 'stripnl': False})
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception:
        return '<div class="color-command"><div class="swatch-bar"></div>{}</div>'.format(colorize('', 'text'))
    return el


def color_formatter(src="", language="", class_name=None, md=""):
    """Formatter wrapper."""

    from coloraide_extras import Color

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
        if not color.in_gamut(WEBSPACE):
            color.fit(WEBSPACE, in_place=True)
            attributes = {'class': "swatch out-of-gamut", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert(WEBSPACE).to_string(hex=True, alpha=False))
            if color.alpha < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert(WEBSPACE).to_string(hex=True) + ' 50%')
        else:
            attributes = {'class': "swatch", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert(WEBSPACE).to_string(hex=True, alpha=False))
            if color.alpha < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert(WEBSPACE).to_string(hex=True) + ' 50%')

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


def render_console(*args):
    """Render console update."""

    try:
        # Run code
        inputs = document.getElementById("__playground-inputs_{}".format(globals()['id_num']))
        results = document.getElementById("__playground-results_{}".format(globals()['id_num']))
        results.innerHTML = live_color_command_formatter(inputs.value)
        scrollingElement = results.querySelector('code')
        scrollingElement.scrollTop = scrollingElement.scrollHeight
    except Exception as e:
        print(e)


def render_notebook(*args):
    """Render notebook."""

    import markdown
    from pymdownx import slugs

    text = globals().get('content', '')
    extensions = [
        'markdown.extensions.toc',
        'markdown.extensions.admonition',
        'markdown.extensions.smarty',
        'pymdownx.betterem',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.tables',
        'markdown.extensions.abbr',
        'markdown.extensions.footnotes',
        'markdown.extensions.md_in_html',
        'pymdownx.superfences',
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
        'pymdownx.magiclink',
        'pymdownx.tilde',
        'pymdownx.caret',
        'pymdownx.smartsymbols',
        'pymdownx.emoji',
        'pymdownx.escapeall',
        'pymdownx.tasklist',
        'pymdownx.striphtml',
        'pymdownx.snippets',
        'pymdownx.keys',
        'pymdownx.details',
        'pymdownx.saneheaders',
        'pymdownx.tabbed'
    ]
    extension_configs = {
        'markdown.extensions.toc': {
            'slugify': slugs.slugify(case="lower"),
            'permalink': ""
        },
        'markdown.extensions.smarty': {
            "smart_quotes": False,
        },
        'pymdownx.superfences': {
            'preserve_tabs': True,
            'custom_fences': [
                {
                    "name": 'playground',
                    "class": 'playground',
                    "format": color_command_formatter,
                    "validator": color_command_validator
                }
            ]
        },
        'pymdownx.inlinehilite': {
            'custom_inline': [
                {
                    'name': 'color',
                    'class': 'color',
                    'format': color_formatter
                }
            ]
        },
        'pymdownx.magiclink': {
            'repo_url_shortener': True,
            'repo_url_shorthand': True,
            'social_url_shorthand': True,
            'user': 'facelessuser',
            'repo': 'coloraide'
        },
        'pymdownx.keys': {
            'separator': "\uff0b"
        }
    }

    try:
        html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
    except Exception:
        html = ''
    content = document.getElementById("__notebook-render")
    content.innerHTML = html


# Load up necessary wheels and then execute the appropriate payload
cwheel = ''
mwheel = ''
pwheel = ''
ewheel = ''

wheels = [
    location.origin + '/coloraide/playground/' + cwheel,
    location.origin + '/coloraide/playground/' + ewheel
]

action = globals().get('action')
if action == 'render':
    callback = render_notebook
    wheels.extend(
        [
            location.origin + '/coloraide/playground/' + mwheel,
            location.origin + '/coloraide/playground/' + pwheel
        ]
    )
else:
    callback = render_console

# We run this from inside an async JavaScript function
# so it is okay to call await outside a coroutine as
# we are technically still inside one.
await micropip.install(wheels)
callback()
