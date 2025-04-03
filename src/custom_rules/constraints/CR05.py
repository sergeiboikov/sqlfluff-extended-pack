"""Rules for enforcing constraint naming conventions."""

from typing import Optional, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CR05(BaseRule):
    """
    DEFAULT constraint names should use "df_" prefix.

    In PostgreSQL, DEFAULT can be used in two ways:
    1. As a column property without a name (most common)
    2. As a named constraint with the CONSTRAINT keyword (less common)

    This rule only applies when DEFAULT is used with the CONSTRAINT keyword.

    **Anti-pattern**

    .. code-block:: sql

        -- Named DEFAULT constraints should use the df_ prefix
        CREATE TABLE public.person (
            person_id INT,
            created_at TIMESTAMP CONSTRAINT default_created_at DEFAULT (CURRENT_TIMESTAMP)
        );

    **Best practice**

    .. code-block:: sql

        -- Use the df_ prefix for named DEFAULT constraints
        CREATE TABLE public.person (
            person_id INT,
            created_at TIMESTAMP CONSTRAINT df_created_at DEFAULT (CURRENT_TIMESTAMP)
        );

        -- DEFAULT without CONSTRAINT keyword is not checked by this rule
        CREATE TABLE public.employee (
            employee_id INT,
            is_active BOOLEAN DEFAULT FALSE
        );

        -- ALTER COLUMN SET DEFAULT is also not checked by this rule
        ALTER TABLE public.employee
        ALTER COLUMN is_active SET DEFAULT TRUE;
    """

    name = "constraints.df_constraint_naming"
    code = "CR05"
    description = "Enforces named DEFAULT constraints to start with expected prefix."
    groups = ("all", "custom", "constraints")
    config_keywords = []  # Intentionally empty to bypass validation
    # DEFAULT constraints can be part of column definitions, so we need to look at naked_identifier segments
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "object_reference"})

    # The expected prefix for DEFAULT constraint
    _DEFAULT_EXPECTED_PREFIX = "df_"

    def __init__(self, code="CR05", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get("expected_prefix", self._DEFAULT_EXPECTED_PREFIX)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """
        Validate DEFAULT constraint name prefixes.

        This rule only checks explicitly named DEFAULT constraints with the CONSTRAINT keyword.
        DEFAULT as a column property (without a name) is not checked.
        """
        try:
            segment = context.segment
            constraint_name = segment.raw.lower()

            # Check if this segment is a constraint name
            is_constraint_name, constraint_name = self._is_constraint_name(context)

            if is_constraint_name:
                # Check for DEFAULT keyword after constraint name
                parent = context.parent_stack[-1] if context.parent_stack else None
                if parent:
                    for i, child in enumerate(parent.segments):
                        if child is segment:
                            # Look ahead for DEFAULT keyword
                            for j in range(i + 1, min(i + 10, len(parent.segments))):
                                next_seg = parent.segments[j]
                                if next_seg.is_type("keyword") and next_seg.raw.upper() == "DEFAULT":
                                    if not constraint_name.startswith(self.expected_prefix):
                                        return self._create_lint_result(segment, constraint_name, self.expected_prefix)
                                    break
                                elif not next_seg.is_type("whitespace") and not next_seg.is_type("type"):
                                    # If we hit something other than whitespace or a type definition
                                    # and it's not DEFAULT, this is not a DEFAULT constraint
                                    break

            return None
        except Exception as e:
            self.logger.error(f"Exception in constraint naming rule: {str(e)}")
            return None

    def _is_constraint_name(self, context: RuleContext) -> Tuple[bool, str]:
        """
        Check if the current segment is a constraint name.

        Only identifies constraint names that follow the CONSTRAINT keyword.

        Returns:
            Tuple[bool, str]: A tuple containing (is_constraint_name, constraint_name)
        """
        segment = context.segment
        constraint_name = segment.raw.lower()

        # Get the parent and check if it has a keyword before this segment
        parent = context.parent_stack[-1] if context.parent_stack else None
        if parent:
            # Check for a simple case - this segment is preceded by the CONSTRAINT keyword
            for i, child in enumerate(parent.segments):
                if child is segment and i > 0:
                    # Look at previous segment(s)
                    prev_idx = i - 1
                    while prev_idx >= 0:
                        prev = parent.segments[prev_idx]
                        if prev.is_type("keyword") and prev.raw.upper() == "CONSTRAINT":
                            self.logger.debug(f"Found constraint name: {segment.raw}")
                            return True, constraint_name
                        elif not prev.is_type("whitespace"):
                            break
                        prev_idx -= 1
                    break

        return False, constraint_name

    def _create_lint_result(self, segment, constraint_name: str, expected_prefix: str) -> LintResult:
        """
        Create a lint result for a constraint naming violation.

        Args:
            segment: The segment to anchor the lint result to
            constraint_name: The name of the constraint
            expected_prefix: The expected prefix for the constraint

        Returns:
            LintResult: The lint result object
        """
        self.logger.debug(f"DEFAULT constraint name '{constraint_name}' violates naming convention")
        return LintResult(
            anchor=segment,
            description=(
                f"DEFAULT constraint name '{constraint_name}' should start with "
                f"'{expected_prefix}'."
            )
        )
