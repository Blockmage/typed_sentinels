# pyright: reportRedeclaration=none
# ruff: noqa: F811,B008

# fmt: off
# --8<-- [start:basic-usage]
from typed_sentinels import Sentinel

# Create a sentinel that appears as a `str` type to the type checker
SNTL = Sentinel(str)


def process_data(value: str = SNTL) -> str:
    if not value:  # Sentinels are always falsy
        return 'No value provided'
    return f'Processing: {value}'


# Usage
result = print(process_data())        # Prints "No value provided"
result = print(process_data('data'))  # Prints "Processing: data"
# --8<-- [end:basic-usage]
# fmt: on


# fmt: off
# --8<-- [start:adv-usage]
class DatabaseConfig:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port


# No need to instantiate the class
SNTL_DB = Sentinel(DatabaseConfig)


def connect(config: DatabaseConfig = SNTL_DB) -> str:
    if not config:
        return 'Using default connection'
    return f'Connecting to {config.host}:{config.port}'
# --8<-- [end:adv-usage]
# fmt: on

# --8<-- [start:syntax-variants]
# Equivalent ways to create the same sentinel
SNTL_A = Sentinel(tuple[str, ...])
SNTL_B = Sentinel[tuple[str, ...]]()

# Both create the same singleton instance
print(SNTL_A is SNTL_B)  # True
# --8<-- [end:syntax-variants]

# fmt: off
# --8<-- [start:note-on-linting-good]
# Module-level definition
EMPTY_LIST = Sentinel(list[str])

def process_items(items: list[str] = EMPTY_LIST) -> list[str]:
    if not items:
        return []
    return [*items, 'processed']
# --8<-- [end:note-on-linting-good]
# fmt: on


# fmt: off
# --8<-- [start:note-on-linting-bad]
# Inline definition (triggers Ruff B008)
def process_items(items: list[str] = Sentinel(list[str])) -> list[str]:
    if not items:
        return []
    return [*items, 'processed']

# --8<-- [end:note-on-linting-bad]
# fmt: on
