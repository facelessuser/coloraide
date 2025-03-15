"""
Deprecated CAM16 submodule.

Users should import from `coloraide.spaces.cam16` instead.
"""
from .cam16 import *  # noqa: F403
from warnings import warn

warn(
    f'The module {__name__} is deprecated, please use coloraide.spaces.cam16 instead.',
    DeprecationWarning,
    stacklevel=2
)
