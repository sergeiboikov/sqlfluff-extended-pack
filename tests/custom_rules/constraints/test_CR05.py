"""Tests for the CR05 rule (DEFAULT constraint naming)."""

import pytest
from tests.fixtures import df_linter

class TestDefaultConstraintRule:
    """Tests for the default constraint naming rule (CR05)."""

    def test_default_constraint_valid(self, df_linter):
        """Test that a valid default constraint name passes."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            created_at TIMESTAMP CONSTRAINT df_person_created_at DEFAULT (CURRENT_TIMESTAMP)
        );
        """
        result = df_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR05"]
        assert len(violations) == 0

    def test_default_constraint_invalid(self, df_linter):
        """Test that an invalid default constraint name fails."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            created_at TIMESTAMP CONSTRAINT default_created_at DEFAULT (CURRENT_TIMESTAMP)
        );
        """
        result = df_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR05"]
        assert len(violations) == 1
        assert "should start with 'df_'" in violations[0].description.lower()

    def test_add_default_constraint(self, df_linter):
        """Test adding a default constraint with ALTER TABLE."""
        sql = """
        ALTER TABLE public.person
        ADD CONSTRAINT df_person_active DEFAULT (TRUE) FOR is_active;
        """
        result = df_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR05"]
        assert len(violations) == 0
