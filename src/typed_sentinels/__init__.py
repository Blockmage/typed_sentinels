"""Statically-typed sentinel objects with singleton qualities."""

# Core
from ._core import Sentinel as Sentinel
from ._core import is_sentinel as is_sentinel

# Exceptions
from ._exceptions import InvalidHintError as InvalidHintError
from ._exceptions import SentinelError as SentinelError
from ._exceptions import SubscriptedTypeError as SubscriptedTypeError
