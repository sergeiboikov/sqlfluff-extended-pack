"""Tests for the FN01 rule (function naming)."""


class TestFunctionNamingRule:
    """Tests for the function naming rule (FN01)."""

    def test_function_valid(self, fn_linter):
        """Test that a valid function name passes when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.fun_configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM public.configuration
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN01"]
        assert len(violations) == 0

    def test_function_invalid(self, fn_linter):
        """Test that an invalid function name fails when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM public.configuration
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN01"]
        assert len(violations) == 1
        assert "should start with 'fun_'" in violations[0].description.lower()

    def test_function_with_params_valid(self, fn_linter):
        """Test that a valid function name with parameters passes when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.fun_get_user_by_id(user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM public.users WHERE id = user_id
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN01"]
        assert len(violations) == 0

    def test_function_with_params_invalid(self, fn_linter):
        """Test that an invalid function name with parameters fails when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.get_user_by_id(user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM public.users WHERE id = user_id
        $$;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN01"]
        assert len(violations) == 1
        assert "should start with 'fun_'" in violations[0].description.lower()

    def test_alter_function_valid(self, fn_linter):
        """Test that altering a function with valid name is ignored by linter."""
        sql = """
        ALTER FUNCTION public.fun_get_user_by_id(INT)
        SET SCHEMA private;
        """
        result = fn_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN01"]
        assert len(violations) == 0
