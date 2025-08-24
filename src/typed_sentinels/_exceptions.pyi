from typing import Any

class SentinelError(TypeError):
    """Base class from which all `typed-sentinels` `Exception` class objects inherit."""

class InvalidHintError(SentinelError):
    """Argument for `hint` cannot be a `Sentinel` instance, the `Sentinel` class itself, or `None`."""

    def __init__(self, hint: Any, /) -> None:
        """Argument for `hint` cannot be a `Sentinel` instance, the `Sentinel` class itself, or `None`.

        Parameters
        ----------
        hint : Any
            The invalid argument for `hint` as provided to the `Sentinel` class constructor.
        """

class SubscriptedTypeError(SentinelError):
    """Subscripted type and explicit argument for `hint` must match."""

    def __init__(self, hint: Any, subscripted: Any) -> None:
        """Subscripted type and explicit argument for `hint` must match.

        Parameters
        ----------
        hint : Any
            Provided argument for `hint`.
        subscripted : Any
            Type provided via subscription notation to the `Sentinel` class object.
        """
