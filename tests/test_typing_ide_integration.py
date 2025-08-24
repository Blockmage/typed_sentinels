import typing
from collections.abc import Callable

from typed_sentinels import Sentinel


def test_subscription_affects_hint() -> None:
    s0 = Sentinel[Callable[..., str]](Callable[..., str])
    typing.reveal_type(s0)
    # v1-s0: (variable) s0: Any
    # v2-s0: (variable) s0: Any

    s1 = Sentinel[Callable[..., str]]()
    typing.reveal_type(s1)
    # v1-s1: (variable) def s1(...) -> str
    # v2-s1: (variable) s1: Any

    s2 = Sentinel(Callable[..., str])
    typing.reveal_type(s2)
    # v1-s2: (variable) s2: Any
    # v2-s2: (variable) s2: Any

    s3 = Sentinel[str](str)
    typing.reveal_type(s3)
    # v1-s3: (variable) s3: str
    # v2-s3: (variable) s3: str

    s4 = Sentinel(str)
    typing.reveal_type(s4)
    # v1-s4: (variable) s4: str
    # v2-s4: (variable) s4: str

    s5 = Sentinel[str]()
    typing.reveal_type(s5)
    # v1-s5: (variable) s5: str
    # v2-s5: (variable) s5: Any

    s6 = Sentinel()
    typing.reveal_type(s6)
    # v1-s6: (variable) s6: Sentinel[Unknown]
    # v2-s6: (variable) s6: Any

    s7: str = Sentinel()
    typing.reveal_type(s7)
    # v2-s7: (variable) s7: str

    assert repr(s1) == repr(s2) == '<Sentinel: collections.abc.Callable[..., str]>'
    assert s3 is s4
    assert s5 is not s6
