import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest


class PyrightTestCase:
    def __init__(self, code: str, expected_types: dict[str, str], line_offset: int = 0):
        self.code = code
        self.expected_types = expected_types
        self.line_offset = line_offset


def run_pyright_on_code(code: str) -> dict[str, Any]:
    """Run Pyright on the given code and return JSON output."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(code)
        tf.flush()

        try:
            result = subprocess.run(
                ['pyright', '--outputjson', tf.name],
                capture_output=True,
                check=False,
                text=True,
            )

            if result.stdout:
                return json.loads(result.stdout)
            return {}
        finally:
            Path(tf.name).unlink()


def extract_variable_types(pyright_output: dict[str, Any]) -> dict[str, str]:
    """Extract variable type information from Pyright JSON output."""

    types: dict[str, str] = {}

    for diagnostic in pyright_output.get('generalDiagnostics', []):
        if diagnostic.get('severity') == 'information':
            message = diagnostic.get('message', '')
            if 'Type of' in message and 'is' in message:
                parts = message.split('"')
                if len(parts) >= 4:
                    var_name = parts[1]
                    type_str = parts[3]
                    types[var_name] = type_str

    return types


class TestPyrightIntegration:
    """Test that Pyright correctly infers types for Sentinel instances."""

    def test_basic_sentinel_types(self):
        """Test basic Sentinel type inference scenarios."""
        test_code = """
import typing
from collections.abc import Callable
from typed_sentinels import Sentinel

s0 = Sentinel[Callable[..., str]](Callable[..., str])
s0_t = typing.reveal_type(s0)

s1 = Sentinel[Callable[..., tuple[str, ...]]]()
s1_t = typing.reveal_type(s1)

s2 = Sentinel(Callable[..., str])
s2_t = typing.reveal_type(s2)

s4 = Sentinel(str)
s4_t = typing.reveal_type(s4)

s5 = Sentinel[str]()
s5_t = typing.reveal_type(s5)

s6 = Sentinel()
s6_t = typing.reveal_type(s6)
"""

        expected_types = {
            's0': 'Any',
            's1': '(...) -> tuple[str, ...]',
            's2': 'Any',
            's4': 'str',
            's5': 'str',
            's6': 'Any',
        }

        pyright_output = run_pyright_on_code(test_code)
        actual_types = extract_variable_types(pyright_output)

        for var_name, expected_type in expected_types.items():
            assert var_name in actual_types, f'Variable {var_name} not found in Pyright output'
            assert actual_types[var_name] == expected_type, (
                f'Type mismatch for {var_name}: expected {expected_type}, got {actual_types[var_name]}'
            )

    def test_complex_sentinel_types(self):
        """Test more complex type scenarios."""
        test_code = """
import typing
from typed_sentinels import Sentinel

s3b = Sentinel[dict[str, tuple[str, ...]]]()
s3b_t = typing.reveal_type(s3b)

s3c = Sentinel(dict[str, tuple[str, ...]])
s3c_t = typing.reveal_type(s3c)

s7: str = Sentinel()
s7_t = typing.reveal_type(s7)
"""

        expected_types = {'s3b': 'dict[str, tuple[str, ...]]', 's3c': 'dict[str, tuple[str, ...]]', 's7': 'str'}

        pyright_output = run_pyright_on_code(test_code)
        actual_types = extract_variable_types(pyright_output)

        for var_name, expected_type in expected_types.items():
            assert var_name in actual_types, f'Variable {var_name} not found in Pyright output'
            assert actual_types[var_name] == expected_type, (
                f'Type mismatch for {var_name}: expected {expected_type}, got {actual_types[var_name]}'
            )

    def test_runtime_type_consistency(self):
        """Test that runtime types are always Sentinel regardless of static type."""

        test_cases = [
            'Sentinel(str)',
            'Sentinel[str]()',
            'Sentinel[dict[str, int]]()',
            'Sentinel()',
        ]

        for case in test_cases:
            test_code = f"""
from typed_sentinels import Sentinel

s = {case}
runtime_type = type(s).__name__
"""

            globals_dict: dict[str, Any] = {}
            exec(test_code, globals_dict)

            assert globals_dict['runtime_type'] == 'Sentinel', (
                f"Runtime type should be 'Sentinel' for {case}, got {globals_dict['runtime_type']}"
            )

    @pytest.mark.parametrize(
        ('sentinel_expr', 'expected_static_type'),
        [
            ('Sentinel(str)', 'str'),
            ('Sentinel[str]()', 'str'),
            ('Sentinel[int]()', 'int'),
            ('Sentinel()', 'Any'),
            ('Sentinel[list[str]]()', 'list[str]'),
        ],
    )
    def test_parametrized_type_inference(self, sentinel_expr: str, expected_static_type: str):
        """Parametrized test for various Sentinel expressions."""
        test_code = f"""
import typing
from typed_sentinels import Sentinel

s = {sentinel_expr}
s_t = typing.reveal_type(s)
"""

        pyright_output = run_pyright_on_code(test_code)
        actual_types = extract_variable_types(pyright_output)

        assert 's' in actual_types, f"Variable 's' not found in Pyright output for {sentinel_expr}"
        assert actual_types['s'] == expected_static_type, (
            f'Type mismatch for {sentinel_expr}: expected {expected_static_type}, got {actual_types["s"]}'
        )
