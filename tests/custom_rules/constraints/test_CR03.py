"""Tests for the CR03 rule (CHECK constraint naming)."""


class TestCheckConstraintRule:
    """Tests for the check constraint naming rule (CR03)."""

    def test_check_constraint_valid(self, chk_linter):
        """Test that a valid check constraint name passes."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            age INT,
            CONSTRAINT chk_person_age CHECK (age > 0)
        );
        """
        result = chk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR03"]
        assert len(violations) == 0

    def test_check_constraint_invalid(self, chk_linter):
        """Test that an invalid check constraint name fails."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            age INT,
            CONSTRAINT age_positive CHECK (age > 0)
        );
        """
        result = chk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR03"]
        assert len(violations) == 1
        assert "should start with 'chk_'" in violations[0].description.lower()

    def test_add_check_constraint(self, chk_linter):
        """Test adding a check constraint with ALTER TABLE."""
        sql = """
        ALTER TABLE public.person
        ADD CONSTRAINT chk_person_age CHECK (age > 0);
        """
        result = chk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR03"]
        assert len(violations) == 0
