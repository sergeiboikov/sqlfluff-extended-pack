"""Tests for the VW01 rule (view naming)."""


class TestViewNamingRule:
    """Tests for the view naming rule (VW01)."""

    def test_view_valid(self, view_linter):
        """Test that a valid view name passes when creating a view."""
        sql = """
        CREATE OR REPLACE VIEW public.v_user_details AS
        SELECT id, name, email FROM public.users;
        """
        result = view_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "VW01"]
        assert len(violations) == 0

    def test_view_invalid(self, view_linter):
        """Test that an invalid view name fails when creating a view."""
        sql = """
        CREATE OR REPLACE VIEW public.user_details AS
        SELECT id, name, email FROM public.users;
        """
        result = view_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "VW01"]
        assert len(violations) == 1
        assert "should start with 'v_'" in violations[0].description.lower()

    def test_materialized_view_valid(self, view_linter):
        """Test that a valid materialized view name passes."""
        sql = """
        CREATE MATERIALIZED VIEW public.v_user_stats AS
        SELECT count(*) as user_count FROM public.users;
        """
        result = view_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "VW01"]
        assert len(violations) == 0

    def test_materialized_view_invalid(self, view_linter):
        """Test that an invalid materialized view name fails."""
        sql = """
        CREATE MATERIALIZED VIEW public.user_stats AS
        SELECT count(*) as user_count FROM public.users;
        """
        result = view_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "VW01"]
        assert len(violations) == 1
        assert "should start with 'v_'" in violations[0].description.lower()

    def test_alter_view_valid(self, view_linter):
        """Test that altering a view with valid name is ignored by linter."""
        sql = """
        ALTER VIEW public.v_user_details
        SET SCHEMA private;
        """
        result = view_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "VW01"]
        assert len(violations) == 0
