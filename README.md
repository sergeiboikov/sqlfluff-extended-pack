# SQLFluff Constraint Naming Plugin

[![Tests](https://github.com/sergeiboikov/sqlfluff-extended-pack/actions/workflows/tests.yml/badge.svg)](https://github.com/sergeiboikov/sqlfluff-extended-pack/actions/workflows/tests.yml)

A SQLFluff plugin to enforce constraint naming conventions according to the Postgres SQL Format Guidelines. The plugin validates objects to ensure they follow standardized naming patterns.1

## Rules Implemented

This plugin implements the following constraint naming rules:

- **CR01** - PRIMARY KEY constraints should use `pk_` prefix
- **CR02** - FOREIGN KEY constraints should use `fk_` prefix
- **CR03** - CHECK constraints should use `chk_` prefix
- **CR04** - UNIQUE constraints should use `uc_` prefix
- **CR05** - DEFAULT constraints should use `df_` prefix. This rule checks explicitly named DEFAULT constraints with the CONSTRAINT keyword. DEFAULT as a column property (without a name) is not checked.

### Function Naming Rules

This plugin also implements the following function naming rules:

- **FN01** - Functions should use `fun_` prefix
- **FN02** - Function parameters should use `p_` prefix

## Requirements

### Python Compatibility

This plugin requires Python 3.8 or newer. It has been tested with the following Python versions:
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### Dependencies

- SQLFluff 3.3.1 or newer
- pre-commit 3.5.0 or newer (for development)

## Installation

1. Clone the repository.

2. Install the plugin:

```bash
# Navigate to the plugin directory
cd /path/to/sqlfluff-extended-pack

# Install the plugin in development mode
pip install -e .
```

3. Verify that SQLFluff recognizes the plugin:

```bash
sqlfluff rules
```

You should see all the custom rules listed among the available rules.

## Configuration

You can customize the expected prefixes for each constraint type and function naming by creating a `.sqlfluff` configuration file:

```ini
[sqlfluff]
dialect = postgres

[sqlfluff:rules]
rule_allowlist = CR01, CR02, CR03, CR04, CR05, FN01, FN02

[sqlfluff:rules:constraints.pk_constraint_naming]
# For PRIMARY KEY constraints
expected_prefix = pk_

[sqlfluff:rules:constraints.fk_constraint_naming]
# For FOREIGN KEY constraints
expected_prefix = fk_

[sqlfluff:rules:constraints.chk_constraint_naming]
# For CHECK constraints
expected_prefix = chk_

[sqlfluff:rules:constraints.uc_constraint_naming]
# For UNIQUE constraints
expected_prefix = uc_

[sqlfluff:rules:constraints.df_constraint_naming]
# For DEFAULT constraints
expected_prefix = df_

[sqlfluff:rules:functions.function_naming]
# For function names
expected_prefix = fun_

[sqlfluff:rules:functions.function_parameter_naming]
# For function parameters
expected_prefix = p_
```

If you don't specify prefixes in your configuration, the plugin will use the default prefixes shown above.

## Using as a Library

You can use this project as a library by installing it directly from GitHub:

```bash
pip install git+https://github.com/sergeiboikov/sqlfluff-extended-pack.git
```

### Programmatic Configuration

You can set custom prefixes in the configuration file:
```ini
[sqlfluff:rules:constraints.pk_constraint_naming]
expected_prefix = pk_

[sqlfluff:rules:constraints.fk_constraint_naming]
expected_prefix = fk_

[sqlfluff:rules:constraints.chk_constraint_naming]
expected_prefix = chk_

[sqlfluff:rules:constraints.uc_constraint_naming]
expected_prefix = uc_

[sqlfluff:rules:constraints.df_constraint_naming]
expected_prefix = df_
```

## Usage

Once installed, the plugin automatically integrates with SQLFluff. Just run SQLFluff as usual.
For example:

```bash
# Lint using all constraint rules
sqlfluff lint tests/test_constraints.sql --config .sqlfluff

# Lint using a specific constraint rule
sqlfluff lint tests/test_constraints.sql --config .sqlfluff --rules CR01

# Generate detailed debug output
sqlfluff lint tests/test_constraints.sql --config .sqlfluff --rules CR01 -vvvv > debug.log
```

## Examples

The following examples demonstrate how the constraint naming rules are enforced:

### Incorrect constraint naming:

```sql
CREATE TABLE public.person (
    person_id INT,
    email TEXT,
    age INT,
    is_active BOOLEAN DEFAULT FALSE,
    CONSTRAINT person_pk PRIMARY KEY (person_id),
    CONSTRAINT email_unique UNIQUE (email),
    CONSTRAINT age_positive CHECK (age > 0)
);

ALTER TABLE public.person ALTER COLUMN is_active SET DEFAULT TRUE;

CREATE TABLE public.orders (
    order_id INT,
    person_id INT,
    CONSTRAINT orders_pk PRIMARY KEY (order_id),
    CONSTRAINT customer_order_fkey FOREIGN KEY (person_id) REFERENCES public.person(person_id)
);
```

### Correct constraint naming:

```sql
CREATE TABLE public.person (
    person_id INT,
    email TEXT,
    age INT,
    is_active BOOLEAN DEFAULT FALSE,
    CONSTRAINT pk_person PRIMARY KEY (person_id),
    CONSTRAINT uc_email UNIQUE (email),
    CONSTRAINT chk_age_positive CHECK (age > 0)
);

CREATE TABLE public.orders (
    order_id INT,
    person_id INT,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_person FOREIGN KEY (person_id) REFERENCES public.person(person_id)
);
```

### Works with inline SQL too:

```sql
CREATE TABLE public.person (person_id INT, CONSTRAINT person_pk PRIMARY KEY (person_id)); -- Will flag the PRIMARY KEY constraint on public.person table

ALTER TABLE public.person ADD CONSTRAINT email_unique UNIQUE (email); -- Will flag the UNIQUE constraint on public.person table
```

The following SQL would pass validation:

```sql
CREATE TABLE public.person (person_id INT, CONSTRAINT pk_person PRIMARY KEY (person_id)); -- Correctly named PRIMARY KEY constraint

ALTER TABLE public.person ADD CONSTRAINT uc_person_email UNIQUE (email); -- Correctly named UNIQUE constraint
```

### Incorrect function naming:

```sql
CREATE FUNCTION public.calculate_tax(amount NUMERIC) RETURNS NUMERIC AS $$
BEGIN
    RETURN amount * 0.2;
END;
$$ LANGUAGE plpgsql;
```

### Correct function naming:

```sql
CREATE FUNCTION public.fun_calculate_tax(p_amount NUMERIC) RETURNS NUMERIC AS $$
BEGIN
    RETURN p_amount * 0.2;
END;
$$ LANGUAGE plpgsql;
```
