"""Common test fixtures for the SQLFluff constraint naming rules."""

import pytest
from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture
def pk_linter():
    """Create a linter with the PRIMARY KEY constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "CR01": {"enabled": True}
        },
        "include_rules": ["CR01"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def fk_linter():
    """Create a linter with the FOREIGN KEY constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "CR02": {"enabled": True}
        },
        "include_rules": ["CR02"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def chk_linter():
    """Create a linter with the CHECK constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "CR03": {"enabled": True}
        },
        "include_rules": ["CR03"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def uc_linter():
    """Create a linter with the UNIQUE constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "CR04": {"enabled": True}
        },
        "include_rules": ["CR04"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def df_linter():
    """Create a linter with the DEFAULT constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "CR05": {"enabled": True}
        },
        "include_rules": ["CR05"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def all_constraints_linter():
    """Create a linter with all constraint rules enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "CR01": {"enabled": True},
            "CR02": {"enabled": True},
            "CR03": {"enabled": True},
            "CR04": {"enabled": True},
            "CR05": {"enabled": True}
        },
        "include_rules": ["CR01", "CR02", "CR03", "CR04", "CR05"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def fn_linter():
    """Create a linter with the function naming rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            "FN01": {"enabled": True}
        },
        "include_rules": ["FN01"],
        "exclude_rules": ["all"]
    })
    return Linter(config=config)
