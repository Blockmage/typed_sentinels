# pyright: reportUnknownVariableType=none

import typing
from collections.abc import Callable

from typed_sentinels import Sentinel

_test_unreachable_sntl_cls = False
_test_unreachable_sntl_inst = False
_test_unreachable_none_hint = False
_test_unreachable_type_mismatch = False

# fmt: off

s0 = Sentinel[Callable[..., str]](Callable[..., str])  # 👀: (variable) s0: Any
s0_t = typing.reveal_type(s0)                          # 👀: Type of "s0" is "Any"
                                                       # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'

s1 = Sentinel[Callable[..., tuple[str, ...]]]() # 👀: (variable) def s1(...) -> tuple[str, ...]
s1_t = typing.reveal_type(s1)                   # 👀: Type of "s1" is "(...) -> tuple[str, ...]"
                                                # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'

s2 = Sentinel(Callable[..., str])   # 👀: (variable) s2: Any
s2_t = typing.reveal_type(s2)       # 👀: Type of "s2" is "Any"
                                    # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'


# Mismatched `hint` and subscripted type; shows as `Any` when it would really raise an error, but there's apparently
# no real way for us to express that sort of `Never` return scenario with type annotations currently.
if  _test_unreachable_type_mismatch:
    s3a = Sentinel[dict[str, tuple[str, ...]]](str)     # 👀: (variable) s3a: Any
    s3a_t = typing.reveal_type(s3a)                     # 👀: Type of "s3a" is "Any"
                                                        # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'
else:
    # Subscripted type without `hint` -> Effectively subscripted type
    s3b = Sentinel[dict[str, tuple[str, ...]]]()        # 👀: (variable) s3b: dict[str, tuple[str, ...]]
    s3b_t = typing.reveal_type(s3b)                     # 👀: (variable) s3b_t: dict[str, tuple[str, ...]]
                                                        # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'

    # `hint` without subscripted type -> Effectively the `hint` type
    s3c = Sentinel(dict[str, tuple[str, ...]])          # 👀: (variable) s3c: dict[str, tuple[str, ...]]
    s3c_t = typing.reveal_type(s3c)                     # 👀: Type of "s3c" is "dict[str, tuple[str, ...]]"
                                                        # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'


s4 = Sentinel(str)                  # 👀: (variable) s4: str
s4_t = typing.reveal_type(s4)       # 👀: Type of "s4" is "str"
                                    # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'

s5 = Sentinel[str]()                # 👀: (variable) s5: str
s5_t = typing.reveal_type(s5)       # 👀: Type of "s5" is "str"
                                    # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'

s6 = Sentinel()                     # 👀: (variable) s6: Any
s6_t = typing.reveal_type(s6)       # 👀: Type of "s6" is "Any"
                                    # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'

s7: str = Sentinel()                # 👀: (variable) s7: str
s7_t = typing.reveal_type(s7)       # 👀: Type of "s7" is "str"
                                    # 🏃🏼‍➡️: -> Runtime type is 'Sentinel'


# --- Unreachable code -------------------------------------------------------------------------------------------------

if _test_unreachable_sntl_cls:
    s8 = Sentinel(Sentinel)             # 👀: (variable) s8: Never
    s8_t = typing.reveal_type(s8)       # 👀: Type analysis indicates code is unreachable

if _test_unreachable_sntl_inst:
    s9 = Sentinel(Sentinel())           # 👀: (variable) s9: str
    s9_t = typing.reveal_type(s9)       # 👀: Type analysis indicates code is unreachable

if _test_unreachable_none_hint:
    s10 = Sentinel(None)                # 👀: (variable) s10: str
    s10_t = typing.reveal_type(s10)     # 👀: Type analysis indicates code is unreachable

# fmt: on
