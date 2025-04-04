"""Tests for all view naming rules together."""


def test_all_view_rules(view_linter):
    """Test that all view naming rules work together."""
    sql = """
    -- Regular view with incorrect naming
    CREATE OR REPLACE VIEW public.user_details AS
    SELECT id, name, email FROM public.users;

    -- Regular view with correct naming
    CREATE OR REPLACE VIEW public.v_user_details AS
    SELECT id, name, email FROM public.users;

    -- Materialized view with incorrect naming
    CREATE MATERIALIZED VIEW public.user_stats AS
    SELECT count(*) as user_count FROM public.users;

    -- Materialized view with correct naming
    CREATE MATERIALIZED VIEW public.v_user_stats AS
    SELECT count(*) as user_count FROM public.users;
    """
    result = view_linter.lint_string(sql)

    # Should find 2 violations - one for each incorrectly named view
    violations = [v for v in result.violations if v.rule_code() == "VW01"]
    assert len(violations) == 2

    # Check that the violations are for the expected view names
    violation_descriptions = [v.description for v in violations]
    assert any("'user_details'" in desc for desc in violation_descriptions)
    assert any("'user_stats'" in desc for desc in violation_descriptions)


def test_real_world_examples(view_linter):
    """Test with more complex real-world view examples."""
    sql = """
    -- Complex view with incorrect naming
    CREATE OR REPLACE VIEW public.sales_by_region AS
    WITH regional_sales AS (
        SELECT region, SUM(amount) as total_sales
        FROM orders
        GROUP BY region
    )
    SELECT
        region,
        total_sales,
        total_sales * 100.0 / (SELECT SUM(total_sales) FROM regional_sales) AS percentage
    FROM public.regional_sales
    ORDER BY total_sales DESC;

    -- Complex materialized view with correct naming
    CREATE MATERIALIZED VIEW public.v_product_analytics AS
    SELECT
        p.product_id,
        p.product_name,
        p.category_id,
        c.category_name,
        COUNT(o.order_id) AS order_count,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM
        public.products AS p
    INNER JOIN
        public.categories AS c ON p.category_id = c.category_id
    LEFT JOIN
        public.order_items AS oi ON p.product_id = oi.product_id
    LEFT JOIN
        public.orders AS o ON oi.order_id = o.order_id
    WHERE
        o.order_date >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY
        p.product_id, p.product_name, p.category_id, c.category_name
    ORDER BY
        total_revenue DESC;
    """
    result = view_linter.lint_string(sql)

    # Should find 1 violation for the incorrectly named complex view
    violations = [v for v in result.violations if v.rule_code() == "VW01"]
    assert len(violations) == 1
    assert "sales_by_region" in violations[0].description
