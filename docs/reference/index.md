# Code Reference

This section contains the complete API documentation for the typed_sentinels package.

## Overview

The `typed_sentinels` package provides statically-typed sentinel objects with singleton
qualities. The main components are:

- **[Sentinel](typed_sentinels/index.md)** - The main class for creating sentinel objects
- **[Core Functions](typed_sentinels/_core.md)** - Core implementation details
- **[Exceptions](typed_sentinels/_exceptions.md)** - Exception classes used by the package

## Quick Start

The most common use case is creating sentinel values for function parameters:

```python
from typed_sentinels import Sentinel

UNSET: str = Sentinel(str)


def process(value: str = UNSET) -> str:
    if not value:  # Sentinels are always falsy
        return 'No value provided'
    return f'Processing: {value}'
```

## Navigation

Use the navigation menu to explore the different modules:

- Start with the main [typed_sentinels module](typed_sentinels/index.md) for an overview
- Check [core implementation](typed_sentinels/_core.md) for detailed class documentation
- Review [exceptions](typed_sentinels/_exceptions.md) for error handling
