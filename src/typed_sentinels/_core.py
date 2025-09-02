from __future__ import annotations

from threading import Lock
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    NoReturn,
    SupportsIndex,
    TypeGuard,
    final,
)
from weakref import WeakValueDictionary

from ._exceptions import InvalidHintError, SubscriptedTypeError

if TYPE_CHECKING:
    from collections.abc import Callable

_OBJECT = object()


@final
class Sentinel:
    """Statically-typed sentinel object with singleton qualities.

    `Sentinel` instances provide unique placeholder objects that maintain singleton behavior for a given type hint. They
    are particularly useful as default parameter values when `None` is not appropriate or when type safety is desired.

    The `Sentinel` class is particularly well-suited for use with types requiring parameters which are only available at
    runtime, where creating a default instance of the type may not be possible in advance, but the structural contract
    of the type is otherwise guaranteed to be fulfilled once present.
    """

    __slots__ = ('__weakref__', '_hint')

    _cls_cache: ClassVar[WeakValueDictionary[tuple[str, Any], Sentinel[Any]]] = WeakValueDictionary()
    _cls_hint: ClassVar[Any] = _OBJECT
    _cls_lock: ClassVar[Lock] = Lock()

    _hint: Any

    @property
    def hint(self) -> Any:
        """Type associated with this `Sentinel` instance."""
        return self._hint

    def __class_getitem__(cls, key: Any) -> Any:
        cls._cls_hint = key
        return cls

    def __new__(cls, hint: Any = _OBJECT, /) -> Any:
        """Create or retrieve a `Sentinel` instance for the given `hint` type.

        Implements the singleton pattern, ensuring that only one `Sentinel` instance exists for each unique `hint`.

        This method is thread-safe and lightweight - it attempts to return early with any cached instance that might
        exist, doing so before acquiring the class-level lock.

        Parameters
        ----------
        hint : Any, optional
            Type that this `Sentinel` should represent. If not provided, and if the class has not been otherwise
            parameterized via subscription notation, defaults to `Any`.

        Returns
        -------
        Sentinel
            `Sentinel` object instance for the given `hint` type, either created anew or retrievd from the class-level
            `WeakValueDictionary` cache.

        Raises
        ------
        InvalidHintError
            If `hint` is any of: `Sentinel`, `Ellipsis`, `True`, `False`, `None`, or a `Sentinel` instance.
        SubscriptedTypeError
            If provided both a subscripted type parameter and a direct type argument and the types should differ (e.g.,
            `Sentinel[A](B)` will raise `SubscriptedTypeError`).
        """
        if (_cls_hint := cls._cls_hint) is not _OBJECT:
            cls._cls_hint = _OBJECT
        if (hint is _OBJECT) and (_cls_hint is not _OBJECT):
            hint = _cls_hint
        if hint is _OBJECT:
            hint = Any

        key = (cls.__name__, hint)
        if (inst := cls._cls_cache.get(key)) is not None:
            return inst

        if hint not in (_OBJECT, Any) and (_cls_hint not in (_OBJECT, Any)):
            if (hint != _cls_hint) and (hint is not _cls_hint):
                raise SubscriptedTypeError(hint=hint, subscripted=_cls_hint)

        if isinstance(hint, Sentinel) or (hint in (Sentinel, Ellipsis, True, False, None)):
            raise InvalidHintError(hint)

        with cls._cls_lock:
            if (inst := cls._cls_cache.get(key)) is None:
                inst = super().__new__(cls)
                super().__setattr__(inst, '_hint', hint)
                cls._cls_cache[key] = inst

        return inst

    def __getitem__(self, key: Any) -> Any:
        return self

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self

    def __str__(self) -> str:
        if hasattr(self._hint, '__name__'):
            hint_name = self._hint.__name__
        elif hasattr(self._hint, '__qualname__'):
            hint_name = self._hint.__qualname__
        else:
            hint_name = str(self._hint)
        if hint_name.startswith("<class '") and hint_name.endswith("'>"):
            hint_name = hint_name[8:-2]
        return f'<Sentinel: {hint_name}>'

    def __repr__(self) -> str:
        return f'<Sentinel: {self._hint!r}>'

    def __hash__(self) -> int:
        return hash((self.__class__, self._hint))

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__ == other.__class__ and self._hint == other._hint

    def __copy__(self) -> Sentinel[Any]:
        return self

    def __deepcopy__(self, _: Any) -> Sentinel[Any]:
        return self

    def __reduce__(self) -> tuple[Callable[..., Sentinel[Any]], tuple[Any]]:
        return (self.__class__, (self._hint,))

    def __reduce_ex__(self, protocol: SupportsIndex) -> tuple[Callable[..., Sentinel[Any]], tuple[Any]]:
        return self.__reduce__()

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        msg = f'Cannot modify attributes of {self!r}'
        raise AttributeError(msg)

    def __delattr__(self, name: str) -> NoReturn:
        msg = f'Cannot delete attributes of {self!r}'
        raise AttributeError(msg)


def is_sentinel(obj: Any, typ: Any = None) -> TypeGuard[Sentinel[Any]]:
    """Return `True` if `obj` is a `Sentinel` instance, optionally further narrowed to be of type `typ`.

    Parameters
    ----------
    obj : Any
        Possible `Sentinel` object instance.
    typ : T | None, optional
        Optional type to be used to further narrow the type of the `Sentinel` object instance.
        If provided, and if `obj` is a `Sentinel` object instance, this must match `obj.hint`.

    Returns
    -------
    TypeGuard[Sentinel[T]]
        - `True` if `obj` is a `Sentinel` instance.
        - `False` otherwise.
    """
    if typ is not None:
        if isinstance(obj, Sentinel) and hasattr(obj, 'hint'):
            return obj.hint == typ
    return isinstance(obj, Sentinel)
