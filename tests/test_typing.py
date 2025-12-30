"""Tests for Pyright type inference integration."""

import pytest

from .conftest import EXPECTED_TYPES, BatchPyrightRunner, ExpectedType


class TestPyrightIntegration:
    """Test that Pyright correctly infers types for Sentinel instances."""

    @pytest.mark.parametrize('expectation', EXPECTED_TYPES, ids=lambda e: e.variable_name)
    def test_type_expectation(self, pyright_runner: BatchPyrightRunner, expectation: ExpectedType):
        success, message = pyright_runner.check_type_expectation(expectation)
        assert success, message

    def test_all_expectations_batch(self, pyright_runner: BatchPyrightRunner):
        failures: list[str] = []

        for expectation in EXPECTED_TYPES:
            success, message = pyright_runner.check_type_expectation(expectation)
            if not success:
                failures.append(message)

        if failures:
            pytest.fail('Failed type expectations:\n' + '\n'.join(failures))

    def test_pyright_ran_successfully(self, pyright_runner: BatchPyrightRunner):
        output = pyright_runner.pyright_output
        errors = [diag for diag in output.get('generalDiagnostics', []) if diag.get('severity') == 'error']

        if errors:
            error_messages = [diag.get('message', 'Unknown error') for diag in errors]
            pytest.fail('Pyright errors:\n' + '\n'.join(error_messages))

    def test_all_expected_variables_found(self, pyright_runner: BatchPyrightRunner):
        expected_vars = {exp.variable_name for exp in EXPECTED_TYPES}
        variable_types = pyright_runner.variable_types
        found_vars = set(variable_types.keys())

        missing = expected_vars - found_vars
        if missing:
            pytest.fail(f'Missing variables in Pyright output: {sorted(missing)}')

        print(f'\n✅ Found {len(found_vars)} variables with type information')
        for var, typ in sorted(variable_types.items()):
            print(f'  {var}: {typ}')
