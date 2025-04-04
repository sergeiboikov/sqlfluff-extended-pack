"""Fixtures for function tests."""

# Import all fixtures from the main fixtures module
from tests.fixtures import fn_linter, fn_param_linter, all_functions_linter

# Explicitly make them available to pytest
__all__ = ["fn_linter", "fn_param_linter", "all_functions_linter"]
