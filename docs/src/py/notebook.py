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
# ruff: noqa: PGH001
import xml.etree.ElementTree as Etree
from collections.abc import Sequence, Mapping
from collections import namedtuple
import ast
from io import StringIO
import sys
import re
from functools import partial
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import find_formatter_class
from coloraide import Color
from coloraide.interpolate import Interpolator, normalize_domain
try:
    from coloraide_extras.everything import ColorAll
except ImportError:
    from coloraide.everything import ColorAll

PY310 = (3, 10) <= sys.version_info
PY311 = (3, 11) <= sys.version_info

WEBSPACE = "srgb"

AST_BLOCKS = (
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.FunctionDef,
    ast.ClassDef,
    ast.AsyncFor,
    ast.AsyncWith,
    ast.AsyncFunctionDef
)

if PY310:
    AST_BLOCKS = AST_BLOCKS + (ast.Match,)


if PY311:
    AST_BLOCKS = AST_BLOCKS + (ast.TryStar,)


RE_INIT = re.compile(r'^\s*#\s*pragma:\s*init\n(.*?)#\s*pragma:\s*init\n', re.DOTALL | re.I)

RE_COLOR_START = re.compile(
    r"(?i)(?:\b(?<![-#&$])(?:color|hsla?|lch|lab|hwb|rgba?)\(|\b(?<![-#&$])[\w]{3,}(?![(-])\b|(?<![&])#)"
)

LIVE_INIT = """
from coloraide import *
import coloraide
try:
    import coloraide_extras
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
"""

template = '''<div class="playground" id="__playground_{el_id}">
<div class="playground-results" id="__playground-results_{el_id}">
{results}
</div>
<div class="playground-code hidden" id="__playground-code_{el_id}" data-search-exclude>
<form autocomplete="off">
<textarea class="playground-inputs" id="__playground-inputs_{el_id}" spellcheck="false">{raw_source}</textarea>
</form>
</div>
<div class="playground-footer" data-search-exclude>
<hr>
<button id="__playground-edit_{el_id}" class="playground-edit" title="Edit the current snippet">Edit</button>
<button id="__playground-share_{el_id}" class="playground-share" title="Copy URL to current snippet">Share</button>
<button id="__playground-run_{el_id}" class="playground-run hidden" title="Run code (Ctrl + Enter)">Run</button>
<button id="__playground-cancel_{el_id}" class="playground-cancel hidden" title="Cancel edit (Escape)">Cancel</button>
<span class='gamut'>Gamut: {gamut}</span>
</div>
</div>'''

code_id = 0


class Ramp(list):
    """Create a gradient from a list of colors."""


class Steps(list):
    """Create a special display of steps from a list of colors."""


class Row(list):
    """Restrict only the provided colors to a row."""


class ColorTuple(namedtuple('ColorTuple', ['string', 'color'])):
    """Color tuple."""


class AtomicString(str):
    """Atomic string."""


class Break(Exception):
    """Break exception."""


class Continue(Exception):
    """Continue exception."""


# Legacy names
HtmlRow = Row
HtmlSteps = Steps
HtmlGradient = Ramp


def _escape(txt):
    """Basic HTML escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    return txt


class StreamOut:
    """Override the standard out."""

    def __init__(self):
        """Initialize."""
        self.old = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def read(self):
        """Read the stringIO buffer."""

        value = ''
        if self.stdout is not None:
            self.stdout.flush()
            value = self.stdout.getvalue()
            self.stdout = StringIO()
            sys.stdout = self.stdout
        return value

    def __enter__(self):
        """Enter."""
        return self

    def __exit__(self, type, value, traceback):  # noqa: A002
        """Exit."""

        sys.stdout = self.old
        self.old = None
        self.stdout = None


def get_colors(result):
    """Get color from results."""

    domain = []
    if isinstance(result, AtomicString):
        yield find_colors(result)

    if isinstance(result, Row):
        yield Row(
            [
                ColorTuple(c.to_string(fit=False), c.clone()) if isinstance(c, Color) else ColorTuple(c, ColorAll(c))
                for c in result
            ]
        )
    elif isinstance(result, (Steps, Ramp)):
        t = type(result)
        yield t([c.clone() if isinstance(c, Color) else ColorAll(c) for c in result])
    elif isinstance(result, Color):
        yield [ColorTuple(result.to_string(fit=False), result.clone())]
    elif isinstance(result, Interpolator):
        # Since we are auto showing the gradient, we need to scale the domain to something we expect.
        if result._domain:
            domain = result._domain
            result.domain(normalize_domain(result._domain))
        grad = Ramp(result.steps(steps=5, max_delta_e=2.3))
        if domain:
            result._domain = domain
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


def evaluate_with(node, g, loop, index=0):
    """Evaluate with."""

    l = len(node.items) - 1
    withitem = node.items[index]
    if withitem.context_expr:
        with eval(compile(ast.Expression(withitem.context_expr), '<string>', 'eval'), g) as w:
            g[withitem.optional_vars.id] = w
            if index < l:
                evaluate_with(node, g, loop, index + 1)
            else:
                for n in node.body:
                    yield from evaluate(n, g, loop)
    else:
        with eval(compile(ast.Expression(withitem.context_expr), '<string>', 'eval'), g):
            if index < l:
                evaluate_with(node, g, loop, index + 1)
            else:
                for n in node.body:
                    yield from evaluate(n, g, loop)


def compare_match(s, g, node):
    """Compare a match."""

    if isinstance(node, ast.MatchOr):
        for pattern in node.patterns:
            if compare_match(s, g, pattern):
                return True
    else:
        if isinstance(node, ast.MatchValue):
            p = eval(compile(ast.Expression(node.value), '<string>', 'eval'), g)
            return s == p
        elif isinstance(node, ast.MatchSingleton):
            return s is node.value
        elif isinstance(node, ast.MatchSequence):
            if isinstance(s, Sequence):
                star = isinstance(node.patterns[-1], ast.MatchStar)
                l1, l2 = len(s), len(node.patterns)
                if (star and l1 >= l2 - 1) or (l1 == l2):
                    for e, p in enumerate(node.patterns[:-1] if star else node.patterns):
                        if not compare_match(s[e], g, p):
                            return False
                    if star and node.patterns[-1].name:
                        g[node.patterns[-1].name] = s[l2 - 1:]
                    return True
            return False
        elif isinstance(node, ast.MatchMapping):
            if isinstance(s, Mapping):
                star = node.rest
                l1, l2 = len(s), len(node.patterns)
                if (star and l1 >= l2) or (l1 == l2):
                    keys = set()
                    for kp, vp in zip(node.keys, node.patterns):
                        key = eval(compile(ast.Expression(kp), '<string>', 'eval'), g)
                        keys.add(key)
                        if key not in s:
                            return False
                        if not compare_match(s[key], g, vp):
                            return False
                    if star:
                        g[star] = {k: v for k, v in s.items() if k not in keys}
                    return True
            return False
        elif isinstance(node, ast.MatchClass):
            name = g.get(node.cls.id, None)
            if name is None:
                raise NameError("name '{}' is not defined".format(node.cls.id))
            if not isinstance(s, name):
                return False
            ma = getattr(s, '__match_args__', ())
            l1 = len(ma)
            l2 = len(node.patterns)
            if l1 < l2:
                raise TypeError("{}() accepts {} positional sub-patterns ({} given)".format(name, l1, l2))
            for e, p in enumerate(node.patterns):
                if not hasattr(s, ma[e]):
                    return False
                if not compare_match(getattr(s, ma[e]), g, p):
                    return False
            for a, p in zip(node.kwd_attrs, node.kwd_patterns):
                if not hasattr(s, a):
                    return False
                if not compare_match(getattr(s, a), g, p):
                    return False
            return True
        elif isinstance(node, ast.MatchAs):
            if node.name is not None:
                g[node.name] = s
            if node.pattern:
                return compare_match(s, g, node.pattern)
            return True

    raise RuntimeError('Unknown Match pattern {}'.format(str(node)))


def evaluate_except(node, e, g, loop=False):
    """Evaluate normal except block."""

    for n in node.handlers:
        if n.name:
            g[n.name] = e
        if n.type is None:
            for ne in n.body:
                yield from evaluate(ne, g, loop)
            break
        else:
            if isinstance(e, eval(compile(ast.Expression(n.type), '<string>', 'eval'), g)):
                for ne in n.body:
                    yield from evaluate(ne, g, loop)
                break
    else:
        raise


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
            except Break:  # noqa:  PERF203
                break
            except Continue:
                continue
        else:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
    elif isinstance(node, ast.For):
        for x in eval(compile(ast.Expression(node.iter), '<string>', 'eval'), g):
            if isinstance(node.target, ast.Tuple):
                for e, t in enumerate(node.target.dims):
                    g[t.id] = x[e]
            else:
                g[node.target.id] = x
            try:
                for n in node.body:
                    yield from evaluate(n, g, True)
            except Break:  # noqa:  PERF203
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
            yield from evaluate_except(node, e, g, loop)
        else:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
        finally:
            for n in node.finalbody:
                yield from evaluate(n, g, loop)
    elif PY311 and isinstance(node, ast.TryStar):
        try:
            for n in node.body:
                yield from evaluate(n, g, loop)
        except ExceptionGroup as e:
            for n in node.handlers:
                if n.name:
                    g[n.name] = e
                m, e = e.split(eval(compile(ast.Expression(n.type), '<string>', 'eval'), g))
                if m is not None:
                    for ne in n.body:
                        yield from evaluate(ne, g, loop)
                if e is None:
                    break
            if e is not None:
                raise e
        except Exception as e:
            yield from evaluate_except(node, e, g, loop)
        else:
            for n in node.orelse:
                yield from evaluate(n, g, loop)
        finally:
            for n in node.finalbody:
                yield from evaluate(n, g, loop)
    elif PY310 and isinstance(node, ast.Match):
        s = eval(compile(ast.Expression(node.subject), '<string>', 'eval'), g)
        for c in node.cases:
            if compare_match(s, g, c.pattern):
                if not c.guard or eval(compile(ast.Expression(c.guard), '<string>', 'eval'), g):
                    for n in c.body:
                        yield from evaluate(n, g, loop)
                    break
    elif isinstance(node, ast.With):
        yield from evaluate_with(node, g, loop)
    else:
        _exec = ast.Module([node], [])
        exec(compile(_exec, '<string>', 'exec'), g)
        yield None


def execute(cmd, no_except=True, inline=False, init='', g=None):
    """Execute color commands."""

    console = ''
    colors = []

    # Setup global initialization
    if g is None:
        g = {
            "Ramp": Ramp,
            "Steps": Steps,
            "Row": Row,
            'HtmlRow': HtmlRow,
            'HtmlSteps': HtmlSteps,
            'HtmlGradient': HtmlGradient
        }
    if init:
        execute(init.strip(), g=g)

    # Build AST tree
    m = RE_INIT.match(cmd)
    if m:
        block_init = m.group(1)
        src = cmd[m.end():]
        execute(block_init, g=g)
    else:
        src = cmd
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
            with StreamOut() as s:
                # Execute code
                for x in evaluate(node, g):
                    result.append(x)

                    # Output captured standard out after statements
                    text = s.read()
                    if text:
                        result.append(AtomicString(text))

                # Execution went well, so append command
                console += command

        except Exception as e:  # noqa:  PERF203
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
                    colors.append(clist)  # noqa: PERF401
            result_text += '{}{}'.format(
                repr(r) if isinstance(r, str) and not isinstance(r, AtomicString) else str(r),
                '\n' if not isinstance(r, AtomicString) else ''
            )
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

    valid_inputs = {'exceptions', 'play'}

    for k, v in inputs.items():
        if k in valid_inputs:
            options[k] = True
            continue
        attrs[k] = v
    return True


def _color_command_console(colors, gamut=WEBSPACE):
    """Color command formatter."""

    el = ''
    bar = False
    values = []
    for item in colors:
        is_grad = isinstance(item, HtmlGradient)
        is_steps = isinstance(item, Steps)
        if is_grad or is_steps:
            current = total = percent = last = 0
            if isinstance(item, Steps):
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
                color.fit(gamut)
                color_str = color.convert(gamut).to_string()
                if current:
                    if is_steps:
                        stops.append('{} {}%'.format(color_str, str(last)))
                        stops.append('{} {}%'.format(color_str, str(current)))
                    else:
                        stops.append(color_str)
                    last = current
                    if e < (total - 1):
                        current += percent
                    else:
                        current = 100
                else:
                    stops.append(color_str)
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
            if isinstance(item, Row):
                is_row = True
                if bar and values:
                    el += '<div class="swatch-bar">{}</div>'.format(' '.join(values))
                    values = []
                bar = False

            bar = True
            for color in item:
                base_classes = "swatch"
                if not color.color.in_gamut(gamut):
                    base_classes += " out-of-gamut"
                color.color.fit(gamut)
                srgb = color.color.convert(gamut)
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


def _color_command_formatter(src="", language="", class_name=None, options=None, md="", init='', **kwargs):
    """Formatter wrapper."""

    global code_id
    from pymdownx.superfences import SuperFencesException

    # Support the new way
    gamut = kwargs.get('gamut', WEBSPACE)
    play = options.get('play', False) if options is not None else False
    # Support the old way
    if not play and language == 'playground':
        play = True

    if not play:
        return md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=src,
            class_name=class_name,
            language='py',
            md=md,
            options=options,
            **kwargs
        )

    try:
        if len(md.preprocessors['fenced_code_block'].extension.stash) == 0:
            code_id = 0

        # Check if we should allow exceptions
        exceptions = options.get('exceptions', False) if options is not None else False

        console, colors = execute(src.strip(), not exceptions, init=init)
        el = _color_command_console(colors, gamut=gamut)

        el += md.preprocessors['fenced_code_block'].extension.superfences[0]['formatter'](
            src=console,
            class_name="highlight",
            language='pycon',
            md=md,
            options=options,
            **kwargs
        )
        el = '<div class="color-command">{}</div>'.format(el)
        el = template.format(el_id=code_id, raw_source=_escape(src), results=el, gamut=gamut)
        code_id += 1
    except SuperFencesException:
        raise
    except Exception:
        from pymdownx import superfences
        import traceback
        print(traceback.format_exc())
        return superfences.fence_code_format(src, 'text', class_name, options, md, **kwargs)
    return el


def color_command_formatter(init='', gamut=WEBSPACE):
    """Return a Python command formatter with the provided imports."""

    return partial(_color_command_formatter, init=init, gamut=gamut)


def _color_formatter(src="", language="", class_name=None, md="", exceptions=True, init='', gamut=WEBSPACE):
    """Formatter wrapper."""

    from pymdownx.inlinehilite import InlineHiliteException

    try:
        result = src.strip()

        try:
            color = ColorAll(result.strip())
        except Exception as e:
            _, colors = execute(result, exceptions, inline=True, init=init)
            if len(colors) != 1 or len(colors[0]) != 1:
                if exceptions:
                    raise InlineHiliteException('Only one color allowed') from e
                else:
                    raise ValueError('Only one color allowed') from e
            color = colors[0][0].color
            result = colors[0][0].string

        el = Etree.Element('span')
        stops = []
        if not color.in_gamut(gamut):
            color.fit(gamut)
            attributes = {'class': "swatch out-of-gamut", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert(gamut).to_string(hex=True, alpha=False))
            if color[-1] < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert(gamut).to_string(hex=True) + ' 50%')
        else:
            attributes = {'class': "swatch", "title": result}
            sub_el = Etree.SubElement(el, 'span', attributes)
            stops.append(color.convert(gamut).to_string(hex=True, alpha=False))
            if color[-1] < 1.0:
                stops[-1] += ' 50%'
                stops.append(color.convert(gamut).to_string(hex=True) + ' 50%')

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


def color_formatter(init='', gamut=WEBSPACE):
    """Return a Python command formatter with the provided imports."""

    return partial(_color_formatter, init=init, gamut=gamut)


#############################
# Pyodide specific code
#############################
def _live_color_command_formatter(src, init='', gamut=WEBSPACE):
    """Formatter wrapper."""

    try:
        console, colors = execute(src.strip(), False, init=init)
        el = _color_command_console(colors, gamut=gamut)

        if not colors:
            el += '<div class="swatch-bar"></div>'

        el += colorize(console, 'pycon', **{'python3': True, 'stripnl': False})
        el = '<div class="color-command">{}</div>'.format(el)
    except Exception:
        import traceback
        return '<div class="color-command"><div class="swatch-bar"></div>{}</div>'.format(
            colorize(traceback.format_exc(), 'pycon')
        )
    return el


def live_color_command_formatter(init='', gamut=WEBSPACE):
    """Return a Python command formatter with the provided imports."""

    return partial(_live_color_command_formatter, init=init, gamut=gamut)


def live_color_command_validator(language, inputs, options, attrs, md):
    """Color validator."""

    value = color_command_validator(language, inputs, options, attrs, md)
    # Live edit, we always allow exceptions so not to crash the service.
    options['exceptions'] = True
    return value


def render_console(*args, **kwargs):
    """Render console update."""

    from js import document
    gamut = kwargs.get('gamut', WEBSPACE)

    try:
        # Run code
        inputs = document.getElementById("__playground-inputs_{}".format(globals()['id_num']))
        results = document.getElementById("__playground-results_{}".format(globals()['id_num']))
        footer = document.querySelector("#__playground_{} .gamut".format(globals()['id_num']))
        result = live_color_command_formatter(LIVE_INIT, gamut)(inputs.value)
        temp = document.createElement('div')
        temp.innerHTML = result

        # Replace swatch bars
        cmd = results.querySelector('.color-command')
        for el in cmd.querySelectorAll('.swatch-bar'):
            el.remove()
        for el in temp.querySelectorAll('.swatch-bar'):
            cmd.insertBefore(el, cmd.lastChild)
        footer.innerHTML = 'Gamut: {}'.format(gamut)

        # Update code content
        pre = cmd.querySelector('pre')
        pre.replaceChild(temp.querySelector('code'), pre.querySelector('code'))

        # Clean up stray element.
        temp.remove()

        # Adjust scorlling
        scrollingElement = results.querySelector('code')
        scrollingElement.scrollTop = scrollingElement.scrollHeight
    except Exception as e:
        print(e)


def render_notebook(*args, **kwargs):
    """Render notebook."""

    import markdown
    from pymdownx import slugs, superfences
    from js import document

    gamut = kwargs.get('gamut', WEBSPACE)
    text = globals().get('content', '')
    extensions = [
        'markdown.extensions.toc',
        'markdown.extensions.smarty',
        'pymdownx.betterem',
        'markdown.extensions.attr_list',
        'markdown.extensions.tables',
        'markdown.extensions.abbr',
        'markdown.extensions.footnotes',
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
        'pymdownx.saneheaders',
        'pymdownx.arithmatex',
        'pymdownx.blocks.admonition',
        'pymdownx.blocks.details',
        'pymdownx.blocks.html',
        'pymdownx.blocks.definition',
        'pymdownx.blocks.tab'
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
                    "format": color_command_formatter(LIVE_INIT, gamut),
                    "validator": live_color_command_validator
                },
                {
                    "name": 'python',
                    "class": 'highlight',
                    "format": color_command_formatter(LIVE_INIT, gamut),
                    "validator": live_color_command_validator
                },
                {
                    "name": 'py',
                    "class": 'highlight',
                    "format": color_command_formatter(LIVE_INIT, gamut),
                    "validator": live_color_command_validator
                }
            ]
        },
        'pymdownx.inlinehilite': {
            'custom_inline': [
                {
                    'name': 'color',
                    'class': 'color',
                    'format': color_formatter(LIVE_INIT, gamut)
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
        'pymdownx.blocks.tab': {
            'alternate_style': True
        },
        'pymdownx.blocks.admonition': {
            'types': [
                'new', 'settings', 'note', 'abstract', 'info', 'tip', 'success',
                'question', 'warning', 'failure', 'danger', 'bug', 'example', 'quote'
            ]
        }
    }

    try:
        html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
    except Exception:
        html = ''
    content = document.getElementById("__notebook-render")
    content.innerHTML = html
