"""Variable handling."""
import re
import functools
from .util import parse

tokens = {
    "units": re.compile(
        r"""(?xi)
        # Some number of units separated by valid separators
        (?:
            {float} |
            {angle} |
            {percent} |
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?) |
            [\w][\w\d]*
        )
        """.format(**parse.COLOR_PARTS)
    ),
    "functions": re.compile(r'(?i)[\w][\w\d]*\('),
    "separators": re.compile(r'(?:{comma}|{space}|{slash})'.format(**parse.COLOR_PARTS))
}


def validate_vars(var, good_vars):
    """
    Validate variables.

    We will blindly replace values, but if we are fairly confident they follow
    the pattern of a valid, complete unit, if you replace them in a bad place,
    it will break the color (as it should) and if not, it is likely to parse fine,
    unless it breaks the syntax of the color being evaluated.
    """

    start = 0
    need_sep = False
    length = len(var)

    for k, v in var.items():
        v = v.strip()
        while True:
            if start == length:
                good_vars[k] = v
                break
            try:
                start = 0

                # Each item should be separated by some valid separator
                if need_sep:
                    m = tokens["separators"].match(v, start)
                    if m:
                        start = m.end(0)
                        need_sep = False
                        continue
                    else:
                        break

                # Validate things like `rgb()`, `contrast()` etc.
                m = tokens["functions"].match(v, start)
                if m:
                    end = None
                    brackets = 1
                    for m in parse.RE_BRACKETS.finditer(v, start + 6):
                        if m.group(2):
                            brackets -= 1
                        elif m.group(1):
                            brackets += 1

                        if brackets == 0:
                            end = m.end(2)
                            break
                    if end is None:
                        break
                    start = end
                    need_sep = True
                    continue

                # Validate that units such as percents, floats, hex colors, etc.
                m = tokens["units"].match(v, start)
                if m:
                    start = m.end(0)
                    need_sep = True
                    continue
                break
            except Exception:
                break


def _var_replace(m, var=None, parents=None):
    """Replace variables but try to prevent infinite recursion."""

    name = m.group(2)
    replacement = var.get(m.group(2))
    string = replacement if replacement and name not in parents is not None else ""
    parents.add(name)
    return parse.RE_VARS.sub(functools.partial(_var_replace, var=var, parents=parents), string)


def handle_vars(string, variables, parents=None):
    """Handle CSS variables."""

    temp_vars = {}
    validate_vars(variables, temp_vars)
    parent_vars = set() if parents is None else parents

    return parse.RE_VARS.sub(functools.partial(_var_replace, var=temp_vars, parents=parent_vars), string)
