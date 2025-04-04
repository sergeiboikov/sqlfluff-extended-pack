"""Tests for the CR02 rule (FOREIGN KEY constraint naming)."""


class TestForeignKeyConstraintRule:
    """Tests for the foreign key constraint naming rule (CR02)."""

    def test_foreign_key_valid(self, fk_linter):
        """Test that a valid foreign key constraint name passes when creating a table."""
        sql = """
        CREATE TABLE public.orders (
            order_id INT,
            person_id INT,
            CONSTRAINT fk_orders_person FOREIGN KEY (person_id) REFERENCES public.person(person_id)
        );
        """
        result = fk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR02"]
        assert len(violations) == 0

    def test_foreign_key_invalid(self, fk_linter):
        """Test that an invalid foreign key constraint name fails when creating a table."""
        sql = """
        CREATE TABLE public.orders (
            order_id INT,
            person_id INT,
            CONSTRAINT orders_person_fk FOREIGN KEY (person_id) REFERENCES public.person(person_id)
        );
        """
        result = fk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR02"]
        assert len(violations) == 1
        assert "should start with 'fk_'" in violations[0].description.lower()

    def test_add_foreign_key_valid(self, fk_linter):
        """Test that a valid foreign key constraint name passes when altering a table."""
        sql = """
        ALTER TABLE public.orders
        ADD CONSTRAINT fk_orders_person FOREIGN KEY (person_id) REFERENCES public.person(person_id);
        """
        result = fk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR02"]
        assert len(violations) == 0

    def test_add_foreign_key_invalid(self, fk_linter):
        """Test that an invalid foreign key constraint name fails when altering a table."""
        sql = """
        ALTER TABLE public.orders
        ADD CONSTRAINT orders_person_fk FOREIGN KEY (person_id) REFERENCES public.person(person_id);
        """
        result = fk_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code() == "CR02"]
        assert len(violations) == 1
        assert "should start with 'fk_'" in violations[0].description.lower()
