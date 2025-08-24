# pyright: reportAttributeAccessIssue=none
# pyright: reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none
# pyright: reportUnknownVariableType=none

import copy
import pickle
import typing
import weakref
from collections.abc import Callable

import pytest

from typed_sentinels import InvalidHintError, Sentinel, SubscriptedTypeError, is_sentinel


def test_subscription_affects_hint() -> None:
    s1 = Sentinel[Callable[..., str]]()
    typing.reveal_type(s1)
    # v1s1: (variable) def s1(...) -> str

    s2 = Sentinel(Callable[..., str])
    typing.reveal_type(s2)
    # v1s2: (variable) s2: Any

    s3 = Sentinel[str](str)
    typing.reveal_type(s3)
    # v1s3: (variable) s3: str

    s4 = Sentinel(str)
    typing.reveal_type(s4)
    # v1s4: (variable) s4: str

    s5 = Sentinel[str]()
    typing.reveal_type(s5)
    # v1s5: (variable) s5: str

    s6 = Sentinel()
    typing.reveal_type(s6)
    # v1s6: (variable) s6: Sentinel[Unknown]

    assert repr(s1) == repr(s2) == '<Sentinel: collections.abc.Callable[..., str]>'
    assert s3 is s4
    assert s5 is not s6


def test_subscription() -> None:
    s1 = Sentinel[str](str)
    s2: Callable[..., str] = Sentinel[Callable[..., str]]()
    s3: Callable[..., bytes] = Sentinel[Callable[..., bytes]]()
    s4: Callable[..., int] = Sentinel[Callable[..., int]]()
    s5: Callable[..., bytes] = Sentinel[Callable[..., bytes]]()

    assert repr(s1) == "<Sentinel: <class 'str'>>"
    assert repr(s2) == '<Sentinel: collections.abc.Callable[..., str]>'

    assert s2 is not s4
    assert s3 is s5

    assert s2 is not s3
    assert s2 is not s4


def test_is_sentinel() -> None:
    s1, s2 = Sentinel(object), Sentinel(str)

    assert is_sentinel(s1) is True
    assert is_sentinel(Sentinel) is False

    assert is_sentinel(s2) is True
    assert is_sentinel(s2, str) is True
    assert is_sentinel(s1, bytes) is False


def test_singleton_behavior() -> None:
    s1, s2, s3 = Sentinel(object), Sentinel(object), Sentinel(str)

    assert s1 is s2
    assert s3 is not s1
    assert s3 is Sentinel(str)


def test_hint() -> None:
    s1, s2 = Sentinel(object), Sentinel(str)

    assert s1.hint is object
    assert s2.hint is str

    assert Sentinel(str) is not s1.hint
    assert Sentinel(object).hint is s1.hint
    assert Sentinel(bytes).hint is bytes


def test_str() -> None:
    s1, s2 = Sentinel(), Sentinel(int)

    assert str(s1) == '<Sentinel: typing.Any>'
    assert str(s2) == '<Sentinel: int>'

    assert str(Sentinel(bytes)) == '<Sentinel: bytes>'
    assert str(Sentinel(object)) == '<Sentinel: object>'


def test_repr() -> None:
    s1, s2 = Sentinel(), Sentinel(float)

    assert repr(s1) == '<Sentinel: typing.Any>'
    assert repr(s2) == "<Sentinel: <class 'float'>>"

    assert repr(Sentinel(bytes)) == "<Sentinel: <class 'bytes'>>"
    assert repr(Sentinel(object)) == "<Sentinel: <class 'object'>>"


def test_hash() -> None:
    s1, s2 = Sentinel(), Sentinel()
    s3, s4 = Sentinel(bytes), Sentinel(str)

    assert hash(s1) == hash(s2)
    assert hash(s3) != hash(s4)

    assert hash(Sentinel()) == hash(s1) == hash(s2)
    assert hash(Sentinel(bytes)) == hash(s3)
    assert hash(Sentinel(str)) == hash(s4)


def test_equality() -> None:
    s1, s2 = Sentinel(), Sentinel()
    s3, s4 = Sentinel(bytes), Sentinel(str)

    assert s1 == s2
    assert s3 != s4

    assert Sentinel() == s1 == s2
    assert Sentinel(bytes) == s3
    assert Sentinel(str) == s4


def test_reduce() -> None:
    s = Sentinel(bytes)
    reduce_func, reduce_args = s.__reduce__()

    assert reduce_func(*reduce_args) is s  # pyright: ignore[reportCallIssue]


def test_copy() -> None:
    s = Sentinel(bytes)

    assert copy.copy(s) is s
    assert copy.deepcopy(s) is s


def test_slots() -> None:
    s = Sentinel(str)

    assert hasattr(s, '__slots__')
    assert '_hint' in s.__slots__


def test_bool() -> None:
    s1, s2 = Sentinel(), Sentinel(complex)

    assert bool(s1) is False
    assert bool(not s1 and not s2)


def test_hint_mismatch_raises() -> None:
    with pytest.raises(SubscriptedTypeError):
        Sentinel[str](bool)


def test_hint_is_sentinel_raises() -> None:
    with pytest.raises(InvalidHintError):
        Sentinel(Sentinel())
    with pytest.raises(InvalidHintError):
        Sentinel(Sentinel)


def test_none_hint_raises() -> None:
    with pytest.raises(InvalidHintError):
        Sentinel(None)


def test_other_types_not_equal() -> None:
    assert Sentinel() != object()
    assert Sentinel(int) != 123

    assert Sentinel(str) is not str
    assert Sentinel(float) is not float


def test_sentinel_is_final() -> None:
    assert typing.get_origin(Sentinel) is None


def test_weakref() -> None:
    s = Sentinel(str)
    ref = weakref.ref(s)

    assert ref() is s


def test_custom_types() -> None:
    class Dummy:
        pass

    s = Sentinel(Dummy)
    r = repr(Dummy)

    if r.startswith("<class '") and r.endswith("'>"):
        r = r[8:-2]

    assert s.hint is Dummy
    assert str(s) == f'<Sentinel: {r}>'


def test_pickle() -> None:
    s1 = Sentinel(bytes)
    p1 = pickle.dumps(s1)
    s2 = pickle.loads(p1)

    assert s2 is s1

    s3 = Sentinel(str)
    p2 = pickle.dumps(s3)
    s4 = pickle.loads(p2)

    assert s3 is s4

    s5 = Sentinel(str)

    assert s3 is s4 is s5 is Sentinel(str)

    assert s3 is not s1
    assert s4 is not s2


def test_delattr() -> None:
    s = Sentinel()
    with pytest.raises(AttributeError, match=f'Cannot delete attributes of {s!r}'):
        del s.hint


def test_setattr() -> None:
    s = Sentinel()
    with pytest.raises(AttributeError, match=f'Cannot modify attributes of {s!r}'):
        s.hint = bytes
