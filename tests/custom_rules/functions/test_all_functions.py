"""Tests for all function naming rules together."""


class TestAllFunctionRules:
    """Tests for all function naming rules together."""

    def test_all_valid_functions(self, all_functions_linter):
        """Test all function rules with valid names and parameters."""
        sql = """
        CREATE OR REPLACE FUNCTION public.fun_configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM configuration
        $$;

        CREATE OR REPLACE FUNCTION public.fun_get_user_by_id(p_user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM users WHERE id = p_user_id
        $$;
        """
        result = all_functions_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]
        assert len(violations) == 0

    def test_all_invalid_functions(self, all_functions_linter):
        """Test all function rules with invalid names and parameters."""
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
        result = all_functions_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]

        # Should have two FN01 and one FN02 violation
        assert len(violations) == 3
        rule_codes = [v.rule_code() for v in violations]
        assert rule_codes.count("FN01") == 2
        assert rule_codes.count("FN02") == 1

    def test_mixed_function_names(self, all_functions_linter):
        """Test with valid function names but invalid parameters."""
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
        result = all_functions_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]
        assert len(violations) == 1
        assert violations[0].rule_code() == "FN02"
        assert "should start with 'p_'" in violations[0].description.lower()

    def test_mixed_function_params(self, all_functions_linter):
        """Test with invalid function names but valid parameters."""
        sql = """
        CREATE OR REPLACE FUNCTION public.configuration_get()
        RETURNS JSON
        LANGUAGE SQL
        AS $$
            SELECT * FROM configuration
        $$;

        CREATE OR REPLACE FUNCTION public.get_user_by_id(p_user_id INT)
        RETURNS TABLE (
            id INT,
            name TEXT,
            email TEXT
        )
        LANGUAGE SQL
        AS $$
            SELECT id, name, email FROM users WHERE id = p_user_id
        $$;
        """
        result = all_functions_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("FN0")]
        assert len(violations) == 2
        rule_codes = [v.rule_code() for v in violations]
        assert rule_codes.count("FN01") == 2
        assert "should start with 'fun_'" in violations[0].description.lower()
