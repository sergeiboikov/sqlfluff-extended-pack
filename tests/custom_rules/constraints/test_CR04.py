"""Tests for the CR04 rule (UNIQUE constraint naming)."""


class TestUniqueConstraintRule:
    """Tests for the unique constraint naming rule (CR04)."""

    def test_unique_constraint_valid(self, uc_linter):
        """Test that a valid unique constraint name passes."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            email VARCHAR(255),
            CONSTRAINT uc_person_email UNIQUE (email)
        );
        """
        result = uc_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR04"]
        assert len(violations) == 0

    def test_unique_constraint_invalid(self, uc_linter):
        """Test that an invalid unique constraint name fails."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            email VARCHAR(255),
            CONSTRAINT unique_email UNIQUE (email)
        );
        """
        result = uc_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR04"]
        assert len(violations) == 1
        assert "should start with 'uc_'" in violations[0].description.lower()

    def test_inline_unique_constraint(self, uc_linter):
        """Test inline unique constraint."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            email VARCHAR(255) CONSTRAINT uc_person_email UNIQUE
        );
        """
        result = uc_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR04"]
        assert len(violations) == 0

    def test_add_unique_constraint(self, uc_linter):
        """Test adding a unique constraint with ALTER TABLE."""
        sql = """
        ALTER TABLE public.person
        ADD CONSTRAINT uc_person_email UNIQUE (email);
        """
        result = uc_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR04"]
        assert len(violations) == 0
