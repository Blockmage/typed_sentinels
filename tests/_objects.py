import typing
from collections.abc import Callable

from typed_sentinels import Sentinel


# --------------------------------------------------- Custom Classes ---------------------------------------------------
class SimpleDummy:
    pass


class ComplexDummy:
    def __init__(self, req_param1: str, req_param2: tuple[dict[str, str], ...]) -> None:
        if not req_param1 or not req_param2:
            raise RuntimeError


# ---------------------------------------------------- Basic Types -----------------------------------------------------
basic_str_sentinel = Sentinel(str)
typing.reveal_type(basic_str_sentinel)

basic_int_sentinel = Sentinel(int)
typing.reveal_type(basic_int_sentinel)

subscripted_str_sentinel = Sentinel[str]()
typing.reveal_type(subscripted_str_sentinel)

any_sentinel = Sentinel()
typing.reveal_type(any_sentinel)


# ----------------------------------------------- Complex Generic Types ------------------------------------------------
callable_sentinel = Sentinel[Callable[..., str]]()
typing.reveal_type(callable_sentinel)

nested_dict_sentinel = Sentinel[dict[str, tuple[str, ...]]]()
typing.reveal_type(nested_dict_sentinel)

list_sentinel = Sentinel[list[int]]()
typing.reveal_type(list_sentinel)


# ---------------------------------------------------- Custom Types ----------------------------------------------------
simple_custom_sentinel = Sentinel(SimpleDummy)
typing.reveal_type(simple_custom_sentinel)

complex_custom_sentinel = Sentinel(ComplexDummy)
typing.reveal_type(complex_custom_sentinel)


# ---------------------------------------------------- Union Types -----------------------------------------------------
union_sentinel = Sentinel[str | int]()
typing.reveal_type(union_sentinel)

complex_union_sentinel = Sentinel[str | tuple[str, dict[str, str | tuple[str, ...]]]]()
typing.reveal_type(complex_union_sentinel)
