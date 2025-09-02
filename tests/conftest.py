import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from typed_sentinels import is_sentinel

from . import _objects as test_cases


@dataclass
class ExpectedType:
    """Expected type information for a variable."""

    variable_name: str
    expected_type: str
    runtime_validator: Callable[[Any], bool] | None = None


class BatchPyrightRunner:
    """Runner for batch Pyright testing over a single file."""

    def __init__(self):
        self.test_cases_file = Path(__file__).parent / '_objects.py'
        self._pyright_output: dict[str, Any] | None = None
        self._variable_types: dict[str, str] | None = None

    @property
    def pyright_output(self) -> dict[str, Any]:
        """Cached Pyright output."""

        if self._pyright_output is None:
            self._pyright_output = self._run_pyright()
        return self._pyright_output

    @property
    def variable_types(self) -> dict[str, str]:
        """Cached variable types."""

        if self._variable_types is None:
            self._variable_types = self._extract_variable_types()
        return self._variable_types

    def _run_pyright(self) -> dict[str, Any]:  # pragma: no cover
        """Run Pyright on the test cases file."""

        try:
            result = subprocess.run(
                ['pyright', '--outputjson', str(self.test_cases_file)],
                capture_output=True,
                check=False,
                text=True,
            )

            if result.stdout:
                return json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            pytest.fail(f'Failed to run Pyright: {e}')
        else:
            return {}

    def _extract_variable_types(self) -> dict[str, str]:  # pragma: no cover
        """Extract variable type information from Pyright output."""

        types: dict[str, str] = {}

        for diagnostic in self.pyright_output.get('generalDiagnostics', []):
            if diagnostic.get('severity') == 'information':
                message = diagnostic.get('message', '')
                if 'Type of' in message and 'is' in message:
                    parts = message.split('"')
                    if len(parts) >= 4:
                        var_name = parts[1]
                        type_str = parts[3]
                        types[var_name] = type_str

        return types

    def check_type_expectation(self, expectation: ExpectedType) -> tuple[bool, str]:  # pragma: no cover
        """Check a single type expectation."""

        var_name = expectation.variable_name
        expected_type = expectation.expected_type

        if var_name not in self.variable_types:
            return False, f"Variable '{var_name}' not found in Pyright output"

        actual_type = self.variable_types[var_name]
        if actual_type != expected_type:
            return False, f"Static type mismatch for '{var_name}': expected '{expected_type}', got '{actual_type}'"

        if expectation.runtime_validator:
            try:
                runtime_obj = getattr(test_cases, var_name, None)

                if runtime_obj is None:
                    return False, f"Runtime object '{var_name}' not found"

                if not expectation.runtime_validator(runtime_obj):
                    return False, f"Runtime validation failed for '{var_name}'"

            except Exception as e:  # noqa: BLE001
                return False, f"Runtime validation error for '{var_name}': {e}"

        return True, f'✅ {var_name} passed'


@pytest.fixture(scope='session')
def pyright_runner():
    return BatchPyrightRunner()


EXPECTED_TYPES = [
    ExpectedType(
        'basic_str_sentinel',
        'str',
        lambda x: is_sentinel(x, str),
    ),
    ExpectedType(
        'basic_int_sentinel',
        'int',
        lambda x: is_sentinel(x, int),
    ),
    ExpectedType(
        'subscripted_str_sentinel',
        'str',
        lambda x: is_sentinel(x, str),
    ),
    ExpectedType(
        'any_sentinel',
        'Any',
        lambda x: is_sentinel(x),
    ),
    ExpectedType(
        'callable_sentinel',
        '(...) -> str',
        lambda x: is_sentinel(x),
    ),
    ExpectedType(
        'nested_dict_sentinel',
        'dict[str, tuple[str, ...]]',
        lambda x: is_sentinel(x),
    ),
    ExpectedType(
        'list_sentinel',
        'list[int]',
        lambda x: is_sentinel(x),
    ),
    ExpectedType(
        'simple_custom_sentinel',
        'SimpleDummy',
        lambda x: is_sentinel(x) and hasattr(x.hint, '__name__') and x.hint.__name__ == 'SimpleDummy',
    ),
    ExpectedType(
        'complex_custom_sentinel',
        'ComplexDummy',
        lambda x: is_sentinel(x) and hasattr(x.hint, '__name__') and x.hint.__name__ == 'ComplexDummy',
    ),
    ExpectedType(
        'union_sentinel',
        'str | int',
        lambda x: is_sentinel(x),
    ),
    ExpectedType(
        'complex_union_sentinel',
        'str | tuple[str, dict[str, str | tuple[str, ...]]]',
        lambda x: is_sentinel(x),
    ),
]
