"""Tests for all function naming rules together."""


class TestAllFunctionRules:
    """Tests for all function naming rules together."""

    def test_all_valid_functions(self, fn_linter):
        """Test all function types with valid names."""
        sql = """
        CREATE OR REPLACE FUNCTION public.fun_configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM configuration
        $$;

        CREATE OR REPLACE FUNCTION public.fun_get_user_by_id(user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM users WHERE id = user_id
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]
        assert len(violations) == 0

    def test_all_invalid_functions(self, fn_linter):
        """Test all function types with invalid names."""
        sql = """
        CREATE OR REPLACE FUNCTION public.configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM configuration
        $$;

        CREATE OR REPLACE FUNCTION public.get_user_by_id(user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM users WHERE id = user_id
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]
        assert len(violations) == 2  # All functions have invalid names

    def test_mixed_functions(self, fn_linter):
        """Test a mix of valid and invalid function names."""
        sql = """
        CREATE OR REPLACE FUNCTION public.fun_configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM configuration
        $$;

        CREATE OR REPLACE FUNCTION public.get_user_by_id(user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM users WHERE id = user_id
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]
        assert len(violations) == 1
        assert "should start with 'fun_'" in violations[0].description.lower()
