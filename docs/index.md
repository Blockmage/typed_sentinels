# typed-sentinels

Statically-typed sentinel objects for Python 3.9+.

## Overview

`Sentinel` instances provide unique placeholder objects for a given type. They enable type-safe default values when
`None` isn't suitable, especially for custom or complex types that require runtime parameters.

### Key Features

- **Type safety**: Sentinels always appear as their target type to static type checkers.
- **Singleton behavior**: Only one instance per type, ensuring identity consistency.
- **Always falsy**: Natural `if not` patterns work as expected.
- **Lightweight & thread-safe**: Minimal memory footprint and overhead, while remaining thread-safe.
- **No external dependencies**: Written entirely using Python's standard libary.

## Installation

### Installation using [`pip`](https://pip.pypa.io/en/stable/index.html)

```bash
pip install typed-sentinels
```

### Installation using [`uv`](https://docs.astral.sh/uv/)

```bash
uv add typed-sentinels
```

## Usage

### Basic Usage

```python
--8<-- "docs/snippets/snippets.py:basic-usage"
```

### Custom Classes

Perfect for types requiring runtime parameters:

```python
--8<-- "docs/snippets/snippets.py:adv-usage"
```

## Syntax Variants

```python
--8<-- "docs/snippets/snippets.py:syntax-variants"
```

## A Note on Linting

To avoid linter warnings (like [Ruff B008](https://docs.astral.sh/ruff/rules/function-call-in-default-argument)), always
define sentinels at module level rather than in-line:

```python
--8<-- "docs/snippets/snippets.py:note-on-linting-good"
```

Rather than doing it this way, with the `Sentinel` instance being created in-line as the parameter default:

```python
--8<-- "docs/snippets/snippets.py:note-on-linting-bad"
```

Note, however, that this will technically work fine, without linter complaints, in cases where the type itself is
considered to be immutable, e.g., `tuple`.

## Reference

For complete API documentation, see the [API Reference](reference/index.md).
