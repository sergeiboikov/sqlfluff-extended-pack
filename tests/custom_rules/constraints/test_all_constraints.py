"""Tests for all constraint naming rules together."""

import pytest
from tests.fixtures import all_constraints_linter


class TestAllConstraintRules:
    """Tests for all constraint naming rules together."""

    def test_all_valid_constraints(self, all_constraints_linter):
        """Test all constraint types with valid names."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            email VARCHAR(255),
            age INT,
            created_at TIMESTAMP CONSTRAINT df_person_created_at DEFAULT (CURRENT_TIMESTAMP),
            CONSTRAINT pk_person PRIMARY KEY (person_id),
            CONSTRAINT uc_person_email UNIQUE (email),
            CONSTRAINT chk_person_age CHECK (age > 0)
        );

        CREATE TABLE public.orders (
            order_id INT,
            person_id INT,
            CONSTRAINT pk_orders PRIMARY KEY (order_id),
            CONSTRAINT fk_orders_person FOREIGN KEY (person_id) REFERENCES public.person(person_id)
        );
        """
        result = all_constraints_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("CR0")]
        assert len(violations) == 0

    def test_all_invalid_constraints(self, all_constraints_linter):
        """Test all constraint types with invalid names."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            email VARCHAR(255),
            age INT,
            created_at TIMESTAMP CONSTRAINT default_created_at DEFAULT (CURRENT_TIMESTAMP),
            CONSTRAINT person_pk PRIMARY KEY (person_id),
            CONSTRAINT unique_email UNIQUE (email),
            CONSTRAINT age_check CHECK (age > 0)
        );

        CREATE TABLE public.orders (
            order_id INT,
            person_id INT,
            CONSTRAINT orders_pk PRIMARY KEY (order_id),
            CONSTRAINT orders_person_fk FOREIGN KEY (person_id) REFERENCES public.person(person_id)
        );
        """
        result = all_constraints_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("CR0")]
        assert len(violations) == 6  # All constraints have invalid names

    def test_complex_sql_file(self, all_constraints_linter):
        """Test a more complex SQL file with multiple schema-qualified tables and constraints."""
        sql = """
        CREATE TABLE public.department (
            dept_id INT,
            name VARCHAR(100),
            CONSTRAINT pk_department PRIMARY KEY (dept_id)
        );

        CREATE TABLE public.employee (
            emp_id INT,
            dept_id INT,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(100),
            birth_date DATE CONSTRAINT df_employee_birth_date DEFAULT ('1900-01-01'),
            CONSTRAINT pk_employee PRIMARY KEY (emp_id),
            CONSTRAINT fk_employee_department FOREIGN KEY (dept_id) REFERENCES public.department(dept_id),
            CONSTRAINT uc_employee_email UNIQUE (email),
            CONSTRAINT chk_employee_birth_date CHECK (birth_date > '1900-01-01')
        );

        CREATE TABLE public.project (
            project_id INT,
            name VARCHAR(100),
            start_date DATE,
            CONSTRAINT pk_project PRIMARY KEY (project_id),
            CONSTRAINT chk_project_name CHECK (LENGTH(name) > 0)
        );

        CREATE TABLE public.employee_project (
            emp_id INT,
            project_id INT,
            role VARCHAR(50),
            CONSTRAINT pk_employee_project PRIMARY KEY (emp_id, project_id),
            CONSTRAINT fk_emp_proj_employee FOREIGN KEY (emp_id) REFERENCES public.employee(emp_id),
            CONSTRAINT fk_emp_proj_project FOREIGN KEY (project_id) REFERENCES public.project(project_id)
        );
        """
        result = all_constraints_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("CR0")]
        assert len(violations) == 0

    def test_mixed_valid_invalid_constraints(self, all_constraints_linter):
        """Test mix of valid and invalid constraint names."""
        sql = """
        CREATE TABLE public.person (
            person_id INT,
            email VARCHAR(255),
            age INT,
            created_at TIMESTAMP CONSTRAINT default_created_at DEFAULT (CURRENT_TIMESTAMP),
            CONSTRAINT pk_person PRIMARY KEY (person_id),
            CONSTRAINT email_unique UNIQUE (email),
            CONSTRAINT chk_age CHECK (age > 0)
        );
        """
        result = all_constraints_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("CR0")]
        assert len(violations) == 2
        violation_descriptions = [v.description.lower() for v in violations]
        assert any("should start with 'uc_'" in desc for desc in violation_descriptions)
        assert any("should start with 'df_'" in desc for desc in violation_descriptions)

    def test_mixed_constraints(self, all_constraints_linter):
        """Test a mix of valid and invalid constraint names on various public schema tables."""
        sql = """
        CREATE TABLE public.department (
            dept_id INT,
            CONSTRAINT pk_department PRIMARY KEY (dept_id)
        );

        CREATE TABLE public.employee (
            emp_id INT,
            name VARCHAR(100),
            dept_id INT,
            salary DECIMAL(10,2),
            CONSTRAINT pk_employee PRIMARY KEY (emp_id),
            CONSTRAINT fk_employee_department FOREIGN KEY (dept_id) REFERENCES public.department(dept_id),
            CONSTRAINT employee_salary_check CHECK (salary > 0), -- Invalid name for public.employee table
            CONSTRAINT uc_employee_name UNIQUE (name)
        );

        CREATE TABLE public.project (
            project_id INT,
            name VARCHAR(100),
            CONSTRAINT project_pk PRIMARY KEY (project_id), -- Invalid name for public.project table
            CONSTRAINT uc_project_name UNIQUE (name)
        );

        CREATE TABLE public.employee_project (
            emp_id INT,
            project_id INT,
            role VARCHAR(50),
            CONSTRAINT pk_emp_proj PRIMARY KEY (emp_id, project_id),
            CONSTRAINT fk_emp_proj_employee FOREIGN KEY (emp_id) REFERENCES public.employee(emp_id),
            CONSTRAINT fk_emp_proj_project FOREIGN KEY (project_id) REFERENCES public.project(project_id)
        );
        """
        result = all_constraints_linter.lint_string(sql)
        print(f"Result: {result}")
        violations = [v for v in result.violations if v.rule_code().startswith("CR0")]
        assert len(violations) == 2  # Two invalid names

    def test_compact_style(self, all_constraints_linter):
        """Test compact style SQL with constraints on public.person table."""
        sql = """
        CREATE TABLE public.person (person_id INT, CONSTRAINT person_pk PRIMARY KEY (person_id));
        """
        result = all_constraints_linter.lint_string(sql)
        violations = [v for v in result.violations if v.rule_code().startswith("CR0")]
        assert len(violations) == 1  # Invalid primary key name
