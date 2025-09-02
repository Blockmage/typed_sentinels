# typed-sentinels

Statically-typed sentinel objects with singleton qualities.

![Example of Sentinel class mimicking parameterized type](./images/sentinel.png)

## Why `typed-sentinels`?

`Sentinel` instances provide unique placeholder objects that maintain singleton behavior for a given type. They are
particularly well-suited for use with types requiring parameters which are only available at runtime, where creating
a default instance of the type may not be possible in advance, but the structural contract of the type is otherwise
guaranteed to be fulfilled once present.

### Key Benefits

- **Type safety**: `Sentinel` objects appear as their target type to static type checkers.
- **Versatile**: Emulate complex, user-defined types, even those which require parameters on instantiation.
- **Natural usage**: `Sentinel` instances are always falsey, enabling natural `if not: ...` patterns.
- **Lightweight singleton**: `Sentinel` objects are incredibly lightweight, with only one instance per assigned type.

## Installation

```bash
pip install typed-sentinels
```

## Examples

Basic usage:

```python
from typed_sentinels import Sentinel

SNTL = Sentinel(str)  # Appears to be a string to the type checker


def process_data(value: str = SNTL) -> str:
    if not value:
        return 'No value provided'
    return f'Processing: {value}'
```

Perfect for types requiring runtime parameters:

```python
class DatabaseConfig:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port


# Appears to the type-checker as an *instance* of `DatabaseConfig`
SNTL_CFG = Sentinel(DatabaseConfig)


def connect(config: DatabaseConfig = SNTL_CFG) -> str:
    if config is SNTL_CFG:
        config = DatabaseConfig('localhost', 5432)
    return f'Connected to {config.host}:{config.port}'
```

## Singleton Behavior

`Sentinel` objects parameterized with the same type `hint` are always the same instance:

```python
S1 = Sentinel(dict[str, Any])
S2 = Sentinel(dict[str, Any])
S3 = Sentinel(dict[str, bytes])

assert S1 is S2  # True - Same type, same instance
assert S2 is not S3  # True - Different types, different instances
```
