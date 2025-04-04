"""SQLFluff Extended Rules Pack.

A SQLFluff plugin providing extended rules for SQL best practices.
"""

__version__ = "0.2.0"

from typing import List, Type, Dict, Any
from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_configs_info() -> Dict[str, Any]:
    """Get additional rule config validations and descriptions."""
    return {
        "expected_prefix": {
            "definition": (
                "Expected prefix for PRIMARY KEY constraints. "
                "Example: pk_ "
            ),
        },
    }


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules.

    Returns:
        A list of rule classes to be registered with SQLFluff.
    """
    # Import directly from modules to avoid registration conflicts
    print("Loading rules from custom_rules...")

    # Import rules directly
    from custom_rules.constraints.CR01 import Rule_CR01
    from custom_rules.constraints.CR02 import Rule_CR02
    from custom_rules.constraints.CR03 import Rule_CR03
    from custom_rules.constraints.CR04 import Rule_CR04
    from custom_rules.constraints.CR05 import Rule_CR05
    from custom_rules.functions.FN01 import Rule_FN01
    from custom_rules.functions.FN02 import Rule_FN02
    from custom_rules.views.VW01 import Rule_VW01

    # Return the rules as a list
    rules = [Rule_CR01, Rule_CR02, Rule_CR03, Rule_CR04, Rule_CR05, Rule_FN01, Rule_FN02, Rule_VW01]
    print(f"Loaded {len(rules)} rules: {[r.code for r in rules]}")
    return rules
