try:
    from .version import __version__  # Generated by sconsUtils
except ImportError:
    __version__ = "?"

from .DurationParser import parseDuration
from .TimeCache import TimeCache
