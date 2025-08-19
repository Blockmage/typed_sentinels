from collections.abc import Callable
from threading import Lock
from typing import Any, ClassVar, NoReturn, SupportsIndex, TypeGuard, TypeVar, cast, final
from weakref import WeakValueDictionary

from ._exceptions import InvalidHintError, SubscriptedTypeError

type _InstanceCache = WeakValueDictionary[tuple[str, Any, Any], 'Sentinel[Any]']

OBJECT = object()


@final
class Sentinel[T: Any]:
    __slots__ = ('__weakref__', '_hint')

    _cls_cache: ClassVar[_InstanceCache] = WeakValueDictionary()
    _cls_hint: ClassVar[Any] = OBJECT
    _cls_lock: ClassVar[Lock] = Lock()

    _hint: T

    @property
    def hint(self) -> T:
        return self._hint

    def __class_getitem__(cls, key: Any) -> T:
        cls._cls_hint = key
        if type(key) is TypeVar:
            cls._cls_hint = Any
        return cast('T', cls)

    def __getitem__(self, key: Any) -> T:
        return cast('T', self)

    def __call__(self, *args: Any, **kwds: Any) -> T:
        return cast('T', self)

    def __new__(cls, hint: Any = OBJECT, /) -> Any:
        if (_cls_hint := cls._cls_hint) is not OBJECT:
            cls._cls_hint = OBJECT

        if (hint is not OBJECT) and (_cls_hint is not OBJECT) and (hint != _cls_hint):
            raise SubscriptedTypeError(hint=hint, subscripted=_cls_hint)
        if (hint is OBJECT) and (_cls_hint is not OBJECT):
            hint = _cls_hint
        elif hint is OBJECT:
            hint = Any

        if isinstance(hint, Sentinel) or (hint is Sentinel) or (hint is None):
            raise InvalidHintError(hint)

        key = (cls.__name__, _cls_hint, hint)
        if (inst := cls._cls_cache.get(key)) is None:
            with cls._cls_lock:
                if (inst := cls._cls_cache.get(key)) is None:
                    inst = super().__new__(cls)
                    super().__setattr__(inst, '_hint', hint)
                    cls._cls_cache[key] = inst

        return cast('T', inst)

    def __str__(self) -> str:
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

    def __copy__(self) -> 'Sentinel[T]':
        return self

    def __deepcopy__(self, _: Any) -> 'Sentinel[T]':
        return self

    def __reduce__(self) -> tuple[Callable[..., 'Sentinel[T]'], tuple[T]]:
        return (self.__class__, (self._hint,))

    def __reduce_ex__(self, protocol: SupportsIndex) -> tuple[Callable[..., 'Sentinel[T]'], tuple[T]]:
        return self.__reduce__()

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        msg = f'Cannot modify attributes of {self!r}'
        raise AttributeError(msg)

    def __delattr__(self, name: str) -> NoReturn:
        msg = f'Cannot delete attributes of {self!r}'
        raise AttributeError(msg)


def is_sentinel[T](obj: Any, typ: T | None = None) -> TypeGuard[Sentinel[T]]:
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
        return isinstance(obj, Sentinel) and obj.hint == typ
    return isinstance(obj, Sentinel)
