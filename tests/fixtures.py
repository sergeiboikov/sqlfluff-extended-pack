"""Common test fixtures for the SQLFluff constraint naming rules."""

import pytest
from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig

# Import rules directly to avoid registration issues
from custom_rules.constraints.CR01 import Rule_CR01
from custom_rules.constraints.CR02 import Rule_CR02
from custom_rules.constraints.CR03 import Rule_CR03
from custom_rules.constraints.CR04 import Rule_CR04
from custom_rules.constraints.CR05 import Rule_CR05


@pytest.fixture
def pk_linter():
    """Create a linter with the PRIMARY KEY constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        # Use the actual rule name from the class
        "rules": {
            Rule_CR01.name: {
                "enabled": True,
                "expected_prefix": "pk_"
            }
        },
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def fk_linter():
    """Create a linter with the FOREIGN KEY constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        # Use the actual rule name from the class
        "rules": {
            Rule_CR02.name: {
                "enabled": True,
                "expected_prefix": "fk_"
            }
        },
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def chk_linter():
    """Create a linter with the CHECK constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        # Use the actual rule name from the class
        "rules": {
            Rule_CR03.name: {
                "enabled": True,
                "expected_prefix": "chk_"
            }
        },
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def uc_linter():
    """Create a linter with the UNIQUE constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        # Use the actual rule name from the class
        "rules": {
            Rule_CR04.name: {
                "enabled": True,
                "expected_prefix": "uc_"
            }
        },
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def df_linter():
    """Create a linter with the DEFAULT constraint rule enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        # Use the actual rule name from the class
        "rules": {
            Rule_CR05.name: {
                "enabled": True,
                "expected_prefix": "df_"
            }
        },
        "exclude_rules": ["all"]
    })
    return Linter(config=config)


@pytest.fixture
def all_constraints_linter():
    """Create a linter with all constraint rules enabled."""
    config = FluffConfig(configs={
        "core": {"dialect": "postgres"},
        "rules": {
            Rule_CR01.name: {"enabled": True, "expected_prefix": "pk_"},
            Rule_CR02.name: {"enabled": True, "expected_prefix": "fk_"},
            Rule_CR03.name: {"enabled": True, "expected_prefix": "chk_"},
            Rule_CR04.name: {"enabled": True, "expected_prefix": "uc_"},
            Rule_CR05.name: {"enabled": True, "expected_prefix": "df_"}
        },
        "exclude_rules": ["all"]
    })
    return Linter(config=config)
