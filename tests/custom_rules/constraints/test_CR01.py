"""Tests for the CR01 rule (PRIMARY KEY constraint naming)."""

import pytest
from tests.fixtures import pk_linter

class TestPrimaryKeyConstraintRule:
    """Tests for the primary key constraint naming rule (CR01)."""

    def test_primary_key_valid(self, pk_linter):
        """Test that a valid primary key constraint name passes."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            CONSTRAINT pk_person PRIMARY KEY (person_id)
        );
        """
        result = pk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR01"]
        assert len(violations) == 0

    def test_primary_key_invalid(self, pk_linter):
        """Test that an invalid primary key constraint name fails."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            CONSTRAINT person_pk PRIMARY KEY (person_id)
        );
        """
        result = pk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR01"]
        assert len(violations) == 1
        assert "should start with 'pk_'" in violations[0].description.lower()

    def test_add_primary_key_constraint(self, pk_linter):
        """Test adding a primary key constraint with ALTER TABLE."""
        sql = """
        ALTER TABLE public.person
        ADD CONSTRAINT pk_person PRIMARY KEY (person_id);
        """
        result = pk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR01"]
        assert len(violations) == 0
