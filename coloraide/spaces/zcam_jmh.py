"""
Deprecated ZCAM submodule.

Users should import from `coloraide.spaces.zcam` instead.
"""
from .zcam import *  # noqa: F403
from warnings import warn

warn(
    f'The module {__name__} is deprecated, please use coloraide.spaces.zcam instead.',
    DeprecationWarning,
    stacklevel=2
)
