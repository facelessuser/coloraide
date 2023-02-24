"""
Execute Python code in code blocks (color previews added specifically for ColorAide).

This can be executed in either a Pyodide environment of a normal Python environment.
3rd party libraries (that are not available directly from Pyodide) are only loaded
when needed so that Pyodide will have a chance to load them if necessary. This is also
hardcoded to work with ColorAide.

This is meant to be executed by Pyodide on preformatted HTML to allow for live execution of
code snippets using `coloraide`.

Transform Python code by executing it, transforming to a Python console output,
and finding and outputting color previews.
"""
import xml.etree.ElementTree as Etree
from collections import namedtuple
import ast
from io import StringIO
import contextlib
import sys
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import find_formatter_class
import coloraide
from coloraide import Color
from coloraide.interpolate import Interpolator, normalize_domain
try:
    from coloraide_extras.everything import ColorAll
except ImportError:
    from coloraide.everything import ColorAll
try:
    import coloraide_extras
except ImportError:
    coloraide_extras = None

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


class HtmlGradient(list):
    """HTML color gradient."""


class HtmlSteps(list):
    """HTML color steps."""


class ColorTuple(namedtuple('ColorTuple', ['string', 'color'])):
    """Color tuple."""


class HtmlRow(list):
    """Create a row with the given colors."""


class AtomicString(str):
    """Atomic string."""


class Break(Exception):
    """Break exception."""


class Continue(Exception):
    """Continue exception."""


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

    domain = []
    if isinstance(result, AtomicString):
        yield find_colors(result)

    if isinstance(result, HtmlRow):
        yield HtmlRow(
            [
                ColorTuple(c.to_string(fit=False), c.clone()) if isinstance(c, Color) else ColorTuple(c, ColorAll(c))
                for c in result
            ]
        )
    elif isinstance(result, (HtmlSteps, HtmlGradient)):
        t = type(result)
        yield t([c.clone() if isinstance(c, Color) else ColorAll(c) for c in result])
    elif isinstance(result, Color):
        yield [ColorTuple(result.to_string(fit=False), result.clone())]
    elif isinstance(result, Interpolator):
        # Since we are auto showing the gradient, we need to scale the domain to something we expect.
        if result.domain:
            domain = result.domain
            result.domain = normalize_domain(result.domain)
        grad = HtmlGradient(result.steps(steps=5, max_delta_e=2.3))
        if domain:
            result.domain = domain
            domain = []
        yield grad
    elif isinstance(result, str):
        try:
            yield [ColorTuple(result, ColorAll(result))]
        except Exception:
            pass
    elif isinstance(result, (list, tuple)):
        for r in result:
            for x in get_colors(r):
                if x:
                    yield x


def find_colors(text):
    """Find colors in text buffer."""

    colors = []
    for m in RE_COLOR_START.finditer(text):
        start = m.start()
        mcolor = ColorAll.match(text, start=start)
        if mcolor is not None:
            colors.append(ColorTuple(text[mcolor.start:mcolor.end], mcolor.color))
    return colors


def evaluate(node, g, loop=False):
    """Evaluate."""

    if loop and isinstance(node, ast.Break):
        raise Break

    if loop and isinstance(node, ast.Continue):
        raise Continue

    if isinstance(node, ast.Expr):
        _eval = ast.Expression(node.value)
        yield eval(compile(_eval, '<string>', 'eval'), g)
    elif isinstance(node, ast.If):
        if eval(compile(ast.Expression(node.test), '<string>', 'eval'), g):
            for n in node.body:
                yield from evaluate(n, g, loop)
        elif node.orelse:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
    elif isinstance(node, ast.While):
        while eval(compile(ast.Expression(node.test), '<string>', 'eval'), g):
            try:
                for n in node.body:
                    yield from evaluate(n, g, True)
            except Break:
                break
            except Continue:
                continue
        else:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
    elif isinstance(node, ast.For):
        for x in eval(compile(ast.Expression(node.iter), '<string>', 'eval'), g):
            g[node.target.id] = x
            try:
                for n in node.body:
                    yield from evaluate(n, g, True)
            except Break:
                break
            except Continue:
                continue
        else:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
    elif isinstance(node, ast.Try):
        try:
            for n in node.body:
                yield from evaluate(n, g, loop)
        except Exception as e:
            for n in node.handlers:
                if n.name:
                    g[n.name] = e
                if n.type is None:
                    for ne in n.body:
                        yield from evaluate(ne, g, loop)
                else:
                    if isinstance(e, eval(compile(ast.Expression(n.type), '<string>', 'eval'), g)):
                        for ne in n.body:
                            yield from evaluate(ne, g, loop)
        else:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
        finally:
            for n in node.finalbody:
                yield from evaluate(n, g, loop)
    else:
        _exec = ast.Module([node], [])
        exec(compile(_exec, '<string>', 'exec'), g)
        yield None


def execute(cmd, no_except=True, inline=False):
    """Execute color commands."""

    g = {k: getattr(coloraide, k) for k in coloraide.__all__}
    g['coloraide'] = coloraide
    g['Color'] = ColorAll
    g['HtmlRow'] = HtmlRow
    g['HtmlSteps'] = HtmlSteps
    g['HtmlGradient'] = HtmlGradient

    if coloraide_extras is not None:
        g['coloraide_extras'] = coloraide_extras

    console = ''
    colors = []

    # Build AST tree
    src = cmd.strip()
    lines = src.split('\n')
    try:
        tree = ast.parse(src)
    except Exception as e:
        if no_except:
            if not inline:
                from pymdownx.superfences import SuperFencesException
                raise SuperFencesException from e
            else:
                from pymdownx.inlinehilite import InlineHiliteException
                raise InlineHiliteException from e
        import traceback
        return '{}'.format(traceback.format_exc()), colors

    for node in tree.body:
        result = []

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
            with std_output() as s:
                # Execute code
                pos = 0
                for x in evaluate(node, g):
                    result.append(x)

                    # Output captured standard out after statements
                    s.flush()
                    text = s.getvalue()[pos:]
                    pos += len(text)
                    if text:
                        result.append(AtomicString(text))

                # Execution went well, so append command
                console += command

        except Exception as e:
            if no_except:
                if not inline:
                    from pymdownx.superfences import SuperFencesException
                    raise SuperFencesException from e
                else:
                    from pymdownx.inlinehilite import InlineHiliteException
                    raise InlineHiliteException from e
            import traceback
            console += '{}\n{}'.format(command, traceback.format_exc())
            # Failed for some reason, so quit
            break

        # If we got a result, output it as well
        result_text = '\n'
        for r in result:
            if r is None:
                continue
            for clist in get_colors(r):
                if clist:
                    colors.append(clist)
            result_text += '{}{}'.format(str(r), '\n' if not isinstance(r, AtomicString) else '')
        console += result_text

    return console, colors


def colorize(src, lang, **options):
    """Colorize."""

    HtmlFormatter = find_formatter_class('html')
    lexer = get_lexer_by_name(lang, **options)
    formatter = HtmlFormatter(cssclass="highlight", wrapcode=True)
    return highlight(src, lexer, formatter).strip()


def color_command_validator(language, inputs, options, attrs, md):
    """Color validator."""

    valid_inputs = set(['exceptions'])

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
        if isinstance(item, (HtmlGradient, HtmlSteps)):
            current = total = percent = last = 0
            if isinstance(item, HtmlSteps):
                total = len(item)
                percent = 100 / total
                current = percent

            if bar:
                el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                values = []
            sub_el1 = '<div class="swatch-bar"><span class="swatch swatch-gradient">{}</span></div>'
            style = "--swatch-stops: "
            stops = []
            for e, color in enumerate(item):
                color.fit(WEBSPACE)
                if current:
                    stops.append('{} {}%'.format(color.convert(WEBSPACE).to_string(), str(last)))
                    stops.append('{} {}%'.format(color.convert(WEBSPACE).to_string(), str(current)))
                    last = current
                    if e < (total - 1):
                        current += percent
                    else:
                        current = 100
                else:
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
            is_row = False
            if isinstance(item, HtmlRow):
                is_row = True
                if bar and values:
                    el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                    values = []
                bar = False

            bar = True
            for color in item:
                base_classes = "swatch"
                if not color.color.in_gamut(WEBSPACE):
                    base_classes += " out-of-gamut"
                color.color.fit(WEBSPACE)
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

            if is_row and values:
                el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                values = []
                bar = False
    if bar:
        el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
        values = []

    return el


def color_command_formatter(src="", language="", class_name=None, options=None, md="", **kwargs):
    """Formatter wrapper."""

    global code_id
    from pymdownx.superfences import SuperFencesException

    try:
        if len(md.preprocessors['fenced_code_block'].extension.stash) == 0:
            code_id = 0

        # Check if we should allow exceptions
        exceptions = options.get('exceptions', False) if options is not None else False

        console, colors = execute(src.strip(), not exceptions)
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
    except SuperFencesException:
        raise
    except Exception:
        from pymdownx import superfences
        import traceback
        print(traceback.format_exc())
        return superfences.fence_code_format(src, 'text', class_name, options, md, **kwargs)
    return el


def color_formatter(src="", language="", class_name=None, md="", exceptions=True):
    """Formatter wrapper."""

    from pymdownx.inlinehilite import InlineHiliteException

    try:
        result = src.strip()

        try:
            color = ColorAll(result.strip())
        except Exception:
            _, colors = execute(result, exceptions, inline=True)
            if len(colors) != 1 or len(colors[0]) != 1:
                if exceptions:
                    raise InlineHiliteException('Only one color allowed')
                else:
                    raise ValueError('Only one color allowed')
            color = colors[0][0].color
            result = colors[0][0].string

        el = Etree.Element('span')
        stops = []
        if not color.in_gamut(WEBSPACE):
            color.fit(WEBSPACE)
            attributes = {'class': "swatch out-of-gamut", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert(WEBSPACE).to_string(hex=True, alpha=False))
            if color[-1] < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert(WEBSPACE).to_string(hex=True) + ' 50%')
        else:
            attributes = {'class': "swatch", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert(WEBSPACE).to_string(hex=True, alpha=False))
            if color[-1] < 1.0:
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
    except InlineHiliteException:
        raise
    except Exception:
        import traceback
        print(traceback.format_exc())
        el = md.inlinePatterns['backtick'].handle_code('text', src)
    return el


#############################
# Pyodide specific code
#############################
def live_color_command_formatter(src):
    """Formatter wrapper."""

    try:
        console, colors = execute(src.strip(), False)
        el = _color_command_console(colors)

        if not colors:
            el += '<div class="swatch-bar"></div>'

        el += colorize(console, 'pycon', **{'python3': True, 'stripnl': False})
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception:
        return '<div class="color-command"><div class="swatch-bar"></div>{}</div>'.format(colorize('', 'text'))
    return el


def live_color_command_validator(language, inputs, options, attrs, md):
    """Color validator."""

    value = color_command_validator(language, inputs, options, attrs, md)
    # Live edit, we always allow exceptions so not to crash the service.
    options['exceptions'] = True
    return value


def live_color_formatter(src="", language="", class_name=None, md=""):
    """Color formatter for a live environment."""

    return color_formatter(src, language, class_name, md, exceptions=False)


def render_console(*args):
    """Render console update."""

    from js import document

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
    from pymdownx import slugs, superfences
    from js import document

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
        'pymdownx.tabbed',
        'pymdownx.arithmatex'
    ]
    extension_configs = {
        'markdown.extensions.toc': {
            'slugify': slugs.slugify(case="lower"),
            'permalink': ""
        },
        'markdown.extensions.smarty': {
            "smart_quotes": False,
        },
        'pymdownx.arithmatex': {
            'generic': True,
            'block_tag': 'pre'
        },
        'pymdownx.superfences': {
            'preserve_tabs': True,
            'custom_fences': [
                {

                    "name": "diagram",
                    "class": "diagram",
                    "format": superfences.fence_code_format
                },
                {
                    "name": 'playground',
                    "class": 'playground',
                    "format": color_command_formatter,
                    "validator": live_color_command_validator
                }
            ]
        },
        'pymdownx.inlinehilite': {
            'custom_inline': [
                {
                    'name': 'color',
                    'class': 'color',
                    'format': live_color_formatter
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
        },
        'pymdownx.tabbed': {
            'alternate_style': True
        }
    }

    try:
        html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
    except Exception:
        html = ''
    content = document.getElementById("__notebook-render")
    content.innerHTML = html
