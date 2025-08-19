# Advanced Usage

## Thread Safety

`Sentinel` object instances are thread-safe and maintain singleton guarantees across threads:

```python
import threading
from typed_sentinels import Sentinel

results = []


def create_sentinel():
    results.append(Sentinel(str))


# Create sentinels from multiple threads
threads = [threading.Thread(target=create_sentinel) for _ in range(100)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

# All results are the same instance
assert all(sentinel is results[0] for sentinel in results)
```

## Custom Classes

`Sentinel`s work with any type, including custom classes:

```python
class DatabaseConfig:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url


# No need to instantiate the classes
DB_UNSET: DatabaseConfig = Sentinel(DatabaseConfig)
API_UNSET: APIClient = Sentinel(APIClient)


def connect_db(config: DatabaseConfig = DB_UNSET) -> str:
    if not config:
        config = DatabaseConfig('localhost', 5432)
    return f'Connected to {config.host}:{config.port}'


def make_request(client: APIClient = API_UNSET) -> str:
    if client is API_UNSET:
        client = APIClient('https://api.example.com')
    return f'Making request to {client.base_url}'
```

## Complex Generic Types

`Sentinel`s work seamlessly with complex generic types:

```python
from typing import Dict, List, Tuple, Optional
from typed_sentinels import Sentinel

# Complex nested types
UNSET_MAPPING = Sentinel(dict[str, list[int]])
UNSET_TUPLE = Sentinel(tuple[str, ...])
UNSET_OPTIONAL = Sentinel(Optional[dict[str, str]])


def process_mapping(data: dict[str, list[int]] = UNSET_MAPPING) -> dict[str, int]:
    if data is UNSET_MAPPING:
        return {}
    return {key: sum(values) for key, values in data.items()}


def process_tuple(items: tuple[str, ...] = UNSET_TUPLE) -> tuple[str, ...]:
    if items is UNSET_TUPLE:
        return ()
    return tuple(item.upper() for item in items)
```

## Serialization

`Sentinel`s (theoretically) maintain their singleton qualities across pickle serialization\*:

```python
import pickle
from typed_sentinels import Sentinel

original = Sentinel(str)
serialized = pickle.dumps(original)
deserialized = pickle.loads(serialized)

assert original is deserialized  # True - singleton preserved!

# This works even with complex types
complex_sentinel = Sentinel(dict[str, list[int]])
serialized_complex = pickle.dumps(complex_sentinel)
deserialized_complex = pickle.loads(serialized_complex)

assert complex_sentinel is deserialized_complex  # True
```

\* This has only been tested within a short timeframe. It should go without saying that this is a
bit of an unexplored/undefined area, and so, not a recommended practice. Though, do [open an issue
to let us know](https://github.com/Blockmage/typed_sentinels/issues) how it goes if you should try!

## Memory Management

`Sentinel` uses a class-level [`WeakValueDictionary`](https://docs.python.org/3/library/weakref.html#weakref.WeakValueDictionary)
for caching and storing instances, providing:

1. **Automatic cleanup**: Unused `Sentinel` object instances will be discarded when no strong
    reference to the instance exists.
1. **Memory efficient**: Helps prevent memory leaks from cached instances.
1. **Singleton preservation**: Ensures that active `Sentinel` instances maintain singleton behavior.

```python
import gc

from typed_sentinels import Sentinel

s1 = Sentinel(str)
original_id = id(s1)
print(f'Cache size: {len(Sentinel._cls_cache)}')  # Cache size: 1

s2 = Sentinel(str)
print(s2 is s1)  # True - Same instance

del s1, s2
gc.collect()  # Force cleanup
print(f'Cache size after cleanup: {len(Sentinel._cls_cache)}')  # Cache size after cleanup: 0

s3 = Sentinel(str)
print(f'New instance created: {id(s3) != original_id}')  # New instance created: True
print(f'Cache size with new instance: {len(Sentinel._cls_cache)}')  # Cache size with new instance: 1

s4, s5, s6, s7 = Sentinel(str), Sentinel(str), Sentinel(str), Sentinel(str)
print(id(s3) == id(s4) == id(s5) == id(s6) == id(s7))  # True
print(f'Cache size remains: {len(Sentinel._cls_cache)}')  # Cache size remains: 1

# Will add +1 instance to the cache due to being parameterized with a new type
s8 = Sentinel(dict[str, bytes])
print(f'Cache size now: {len(Sentinel._cls_cache)}')  # Cache size now: 2
```

For more advanced usage (with threading), check out the [examples directory on GitHub](https://github.com/Blockmage/typed_sentinels/tree/main/examples).

## Type Introspection

Access the type hint of a sentinel:

```python
int_sentinel = Sentinel(int)
str_sentinel = Sentinel(str)
any_sentinel = Sentinel()  # Defaults to Any

# Note: If we were to annotate, e.g., `int_sentinel: int` here, we would be getting linter complaints due to attribute
# access issues (or so the type-checker will believe). Instead, here they will appear as `typing.Any`.
print(str_sentinel.hint)  # <class 'str'>
print(int_sentinel.hint)  # <class 'int'>
print(any_sentinel.hint)  # typing.Any


# Use in runtime type checking
def process_by_type(value):
    if hasattr(value, 'hint'):
        if value.hint is str:
            return 'String sentinel'
        if value.hint is int:
            return 'Integer sentinel'
        if value.hint is not int and value.hint is not str:
            return f'Sentinel has hint: {value.hint} of type: {type(value.hint)}'
    return 'Not a sentinel or unknown type'


if __name__ == '__main__':
    print(process_by_type(str_sentinel))  # String sentinel
    print(process_by_type(int_sentinel))  # Integer sentinel
    print(process_by_type(any_sentinel))  # Sentinel has hint: typing.Any of type: <class 'typing._AnyMeta'>
    print(process_by_type(object()))  # Not a sentinel or unknown type
```

## Integration with Type Checkers

`Sentinel`s are designed to work seamlessly with static type checkers:

```python
from typed_sentinels import Sentinel

UNSET: str = Sentinel(str)


def process(value: str = UNSET) -> str:
    # Type-checker sees `value` as a `str` instance, not, e.g., `Sentinel[str]`
    reveal_type(value)  # Revealed type is `str`; Runtime type us `Sentinel`.

    if not value:  # The idiomatic way to check
        return 'default'

    # Type-checker knows value is `str` here
    return value.upper()  # No type errors


print(process('Real string value'))  # Runtime type is 'str' -> 'REAL STRING VALUE'
print(process())  # Runtime type is 'Sentinel' -> 'default'
```
