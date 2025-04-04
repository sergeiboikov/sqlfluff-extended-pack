"""Tests for the FN02 rule (function parameter naming)."""


class TestFunctionParameterNamingRule:
    """Tests for the function parameter naming rule (FN02)."""

    def test_function_param_valid(self, fn_param_linter):
        """Test that valid function parameters pass when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.get_user(p_user_id INT)
        RETURNS SETOF users
        LANGUAGE SQL
        AS $$
            SELECT * FROM users WHERE user_id = p_user_id;
        $$;
        """
        result = fn_param_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN02"]
        assert len(violations) == 0

    def test_function_param_invalid(self, fn_param_linter):
        """Test that invalid function parameters fail when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.get_user(user_id INT)
        RETURNS SETOF users
        LANGUAGE SQL
        AS $$
            SELECT * FROM users WHERE user_id = user_id;
        $$;
        """
        result = fn_param_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN02"]
        assert len(violations) == 1
        assert "should start with 'p_'" in violations[0].description.lower()

    def test_multiple_params_valid(self, fn_param_linter):
        """Test that multiple valid parameters pass when creating a function."""
        sql = """
        CREATE OR REPLACE FUNCTION public.get_filtered_users(
            p_min_age INT,
            p_max_age INT,
            p_active BOOLEAN
        )
        RETURNS SETOF users
        LANGUAGE SQL
        AS $$
            SELECT * FROM users
            WHERE age BETWEEN p_min_age AND p_max_age
                AND is_active = p_active;
        $$;
        """
        result = fn_param_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN02"]
        assert len(violations) == 0

    def test_multiple_params_mixed(self, fn_param_linter):
        """Test that mixed valid/invalid parameters report the first violation."""
        sql = """
        CREATE OR REPLACE FUNCTION public.get_filtered_users(
            p_min_age INT,
            max_age INT,
            p_active BOOLEAN
        )
        RETURNS SETOF users
        LANGUAGE SQL
        AS $$
            SELECT * FROM users
            WHERE age BETWEEN p_min_age AND max_age
                AND is_active = p_active;
        $$;
        """
        result = fn_param_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN02"]
        assert len(violations) == 1
        assert "max_age" in violations[0].description.lower()

    def test_function_with_no_params(self, fn_param_linter):
        """Test that functions with no parameters pass."""
        sql = """
        CREATE OR REPLACE FUNCTION public.get_all_users()
        RETURNS SETOF users
        LANGUAGE SQL
        AS $$
            SELECT * FROM users;
        $$;
        """
        result = fn_param_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "FN02"]
        assert len(violations) == 0
