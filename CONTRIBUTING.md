# Contributing to SQLFluff Extended Pack

Thank you for your interest in contributing to the SQLFluff Extended Pack project! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sergeiboikov/sqlfluff-extended-pack.git
   cd sqlfluff-extended-pack
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   pip install pytest pre-commit
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Creating a New Rule

To create a new rule:

1. Decide on a rule code (e.g., VW02 for a new view rule).
2. Create a new file in the appropriate directory:
   - `src/custom_rules/constraints/` for constraint rules
   - `src/custom_rules/functions/` for function rules
   - `src/custom_rules/views/` for view rules

3. Implement your rule class following the examples of existing rules.
4. Register your rule in `src/custom_rules/__init__.py`.
5. Create tests for your rule in the `tests/custom_rules/` directory.
6. Update the README.md to document your new rule.

## Running Tests

```bash
# Run all tests
pytest

# Run tests for a specific rule
pytest tests/custom_rules/views/test_VW01.py

# Run a specific test
pytest tests/custom_rules/views/test_VW01.py::TestViewNamingRule::test_view_valid
```

## Code Style

This project uses flake8 for code style checking. Run it with:

```bash
flake8 src tests
```

## Release Process

When preparing a new release:

1. Update version numbers in:
   - `src/custom_rules/__init__.py`
   - `pyproject.toml`

2. Update the `CHANGELOG.md` file with your changes.

3. Make sure all tests pass:
   ```bash
   pytest
   ```

4. Create a git tag for the new version:
   ```bash
   git tag -a v0.x.y -m "Version 0.x.y"
   git push origin v0.x.y
   ```

5. Update the README.md with the new version in the installation instructions.

## Pull Request Process

1. Create a new branch for your feature or fix from the `dev` branch.
2. Add tests for your changes.
3. Ensure all tests pass and code style checks pass.
4. Update documentation as needed.
5. Submit a pull request with a clear description of the changes and any relevant issue numbers to the `dev` branch.
