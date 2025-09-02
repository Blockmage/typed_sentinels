# pyright: reportAttributeAccessIssue=none
# pyright: reportCallIssue=none
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

from .conftest import BatchPyrightRunner, ExpectedType


def test_subscription() -> None:
    s1, s2 = Sentinel[str](str), Sentinel[Callable[..., str]]()

    assert repr(s1) == "<Sentinel: <class 'str'>>"
    assert repr(s2) == '<Sentinel: collections.abc.Callable[..., str]>'

    s3, s4 = Sentinel[Callable[[], int]](), Sentinel[Callable[..., bytes]]()

    assert s2 is not s3
    assert s3 is not s4


def test_subscription_affects_hint() -> None:
    s1, s2 = Sentinel[str](), Sentinel(str)

    assert s1.hint is str
    assert s1.hint is s2.hint
    assert s2.hint == s1.hint

    s3 = Sentinel[tuple[dict[str, str], ...]]()

    assert s3.hint != s1.hint
    assert s3.hint == tuple[dict[str, str], ...]


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
    s1, s2 = Sentinel(), Sentinel(tuple[str, int, dict[str, str]])

    assert str(s1) == '<Sentinel: Any>'
    assert str(s2) == '<Sentinel: tuple[str, int, dict[str, str]]>'

    assert str(Sentinel(bytes)) == '<Sentinel: bytes>'
    assert str(Sentinel(object)) == '<Sentinel: object>'


def test_repr() -> None:
    s1, s2 = Sentinel(), Sentinel(float)

    assert repr(s1) == '<Sentinel: typing.Any>'
    assert repr(s2) == "<Sentinel: <class 'float'>>"

    assert repr(Sentinel(object)) == "<Sentinel: <class 'object'>>"
    assert repr(Sentinel(tuple[str, int, dict[str, str]])) == '<Sentinel: tuple[str, int, dict[str, str]]>'


def test_hash() -> None:
    s1, s2, s3, s4 = Sentinel(), Sentinel(), Sentinel(bytes), Sentinel(str)

    assert hash(s1) == hash(s2)
    assert hash(s3) != hash(s4)

    assert hash(Sentinel()) == hash(s1) == hash(s2)
    assert hash(Sentinel(bytes)) == hash(s3)
    assert hash(Sentinel(str)) == hash(s4)


def test_equality() -> None:
    s1, s2, s3, s4 = Sentinel(), Sentinel(), Sentinel(bytes), Sentinel(str)

    assert s1 == s2
    assert s3 != s4

    assert Sentinel() == s1 == s2
    assert Sentinel(bytes) == s3
    assert Sentinel(str) == s4


def test_reduce() -> None:
    s = Sentinel(bytes)
    reduce_func, reduce_args = s.__reduce__()

    assert reduce_func(*reduce_args) is s


def test_copy() -> None:
    s = Sentinel(bytes)

    assert copy.copy(s) is s
    assert copy.deepcopy(s) is s


def test_slots() -> None:
    s = Sentinel(str)

    assert hasattr(s, '__slots__')
    assert '_hint' in s.__slots__


def test_bool() -> None:
    sntl_1, sntl_2 = Sentinel(), Sentinel(complex)

    assert bool(sntl_1) is False
    assert bool(not sntl_1 and not sntl_2)

    result = False

    if sntl_1:  # pragma: no cover
        result = True
    if sntl_2:  # pragma: no cover
        result = True
    if sntl_1 or sntl_2:  # pragma: no cover
        result = True

    assert result is False


def test_hint_mismatch_raises() -> None:
    with pytest.raises(SubscriptedTypeError):
        Sentinel[str](bool)


def test_hint_is_sentinel_raises() -> None:
    with pytest.raises(InvalidHintError):
        Sentinel(Sentinel())
    with pytest.raises(InvalidHintError):
        Sentinel(Sentinel)


def test_hint_is_ellipses_raises() -> None:
    with pytest.raises(InvalidHintError):
        Sentinel(...)


def test_hint_is_true_or_false_raises() -> None:
    with pytest.raises(InvalidHintError):
        Sentinel(True)  # noqa: FBT003
    with pytest.raises(InvalidHintError):
        Sentinel(False)  # noqa: FBT003


def test_hint_is_none_raises() -> None:
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
    sntl = Sentinel(str)
    ref = weakref.ref(sntl)

    assert ref() is sntl


def test_custom_types() -> None:
    class Dummy:
        pass

    sntl = Sentinel(Dummy)
    assert sntl.hint is Dummy
    assert str(sntl) == f'<Sentinel: {Dummy.__name__}>'


def test_complex_custom_types(pyright_runner: BatchPyrightRunner) -> None:
    """Test that complex custom types work both at runtime and static analysis."""

    class Dummy:
        def __init__(self, req_param1: str, req_param2: tuple[dict[str, str], ...]) -> None:
            if not req_param1 or not req_param2:
                raise RuntimeError

    sntl = Sentinel(Dummy)

    assert sntl.hint is Dummy
    assert is_sentinel(sntl, Dummy)
    assert str(sntl) == '<Sentinel: Dummy>'

    success, message = pyright_runner.check_type_expectation(
        ExpectedType(
            'complex_custom_sentinel',
            'ComplexDummy',
            lambda x: is_sentinel(x) and x.hint.__name__ == 'ComplexDummy',
        )
    )
    assert success, f'Static type test failed: {message}'


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
    sntl = Sentinel()
    with pytest.raises(AttributeError, match=f'Cannot delete attributes of {sntl!r}'):
        del sntl.hint


def test_setattr() -> None:
    sntl = Sentinel()
    with pytest.raises(AttributeError, match=f'Cannot modify attributes of {sntl!r}'):
        sntl.hint = bytes


def test_called_sentinel_returns_self() -> None:
    sntl = Sentinel()
    also_sntl = sntl()

    assert also_sntl is sntl
    assert sntl == also_sntl


def test_getitem_returns_self() -> None:
    sntl = Sentinel()
    also_sntl = sntl['anything']

    assert also_sntl is sntl
    assert sntl == also_sntl
