# Getting Started

## Installation

```bash
# With `pip`:
pip install typed-sentinels

# Or if using `uv`:
uv add typed-sentinels
```

## Basic Patterns

Create `Sentinel` instances at the module level:

```python
from typed_sentinels import Sentinel

# Define once, use everywhere
SNTL_STR = Sentinel(str)


def process_name(name: str = SNTL_STR) -> str:
    if not name:
        return 'Anonymous'
    return name.title()
```

You can also parameterize `Sentinel` via subscription notation:

```python
# These are identical.
UNSET_A = Sentinel(str)
UNSET_B = Sentinel[str]()

# Both create the same singleton instance.
assert UNSET_A is UNSET_B  # True
print(repr(UNSET_A), repr(UNSET_B))  # <Sentinel: <class 'str'>> <Sentinel: <class 'str'>>

UNSET_C = Sentinel()  # Separate instance from the other two.
assert UNSET_C is not UNSET_B  # True
print(repr(UNSET_C), repr(UNSET_B))  # <Sentinel: typing.Any> <Sentinel: <class 'str'>>
```

## Singleton Behavior

`Sentinel` objects with the same type `hint` are always the same instance:

```python
# These are the exact same object
sentinel1 = Sentinel(str)
sentinel2 = Sentinel(str)
assert sentinel1 is sentinel2  # True

# Different types = different instances
str_sentinel = Sentinel(str)
int_sentinel = Sentinel(int)
assert str_sentinel is not int_sentinel  # True
```

## Why Not Just Use `None`?

While `None` works for many cases, `Sentinel` offers advantages:

1. **Type Safety**: `Sentinel`s appear as their target type to type checkers.
1. **Disambiguation**: When `None` is a valid value.
1. **Multiple Defaults**: Different sentinels for different parameters.
1. **Versatility**: `Sentinel`s can emulate the shape and structure of **any** type, even those which
    require parameterization. To the type-checker, `Sentinel(CustomType)` is seen as an *instance* of
    `CustomType` without requiring an actual instance to exist.

With `None`: Type-checker sees two distinct types possible:

```python
def process_optional(value: str | None = None) -> str:
    if value is None:
        return 'default'
    return value
```

With `Sentinel`: Type checker only sees a `str` instance:

```python
UNSET = Sentinel(str)


def process_sentinel(value: str = UNSET) -> str:
    if not value:  # or: if value is UNSET
        return 'default'
    return value
```

## Checking for `Sentinel`

You can check if a value is a sentinel in several ways:

```python
from typed_sentinels import Sentinel, is_sentinel

UNSET = Sentinel(str)


def func(value: str = UNSET) -> None:
    # Method 1: Direct comparison
    if value is UNSET:
        print('Value was not provided')

    # Method 2: Falsy check - Works because `Sentinels` are always "falsy."
    if not value:
        print('Value is falsy (could be sentinel, empty string, etc.)')

    # Method 3: `TypeGuard` function.
    if is_sentinel(value):
        print('Value is some kind of sentinel')

    # Method 4: `TypeGuard` with specific type.
    if is_sentinel(value, str):
        print('Value is a string sentinel')
```
