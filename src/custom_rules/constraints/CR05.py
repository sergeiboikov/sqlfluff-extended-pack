"""Rules for enforcing constraint naming conventions."""

from typing import Optional, Tuple, List

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

        In PostgreSQL, named DEFAULT constraints can appear in two ways:
        1. In a column definition with CONSTRAINT keyword before DEFAULT
        2. Using ALTER TABLE ... ADD CONSTRAINT ... DEFAULT ... FOR column
        """
        try:
            segment = context.segment

            # Check if this segment is a constraint name
            is_constraint_name, constraint_name = self._is_constraint_name(context)

            if is_constraint_name:
                # Find if this is a DEFAULT constraint
                is_default = self._is_constraint_type(context, ["DEFAULT"])

                if is_default and not constraint_name.startswith(self.expected_prefix):
                    return self._create_lint_result(segment, constraint_name, self.expected_prefix)
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

    def _is_constraint_type(self, context: RuleContext, keywords: List[str]) -> bool:
        """
        Check if the constraint is of a specific type by looking for a sequence of keywords.

        Args:
            context: The rule context
            keywords: List of keywords to look for in sequence

        Returns:
            bool: True if the constraint is of the specified type
        """
        segment = context.segment
        parent = context.parent_stack[-1] if context.parent_stack else None

        if not parent:
            return False

        for i, child in enumerate(parent.segments):
            if child is segment:
                # Found our segment, now look ahead for the specified keywords
                idx = i + 1
                max_lookahead = 10  # Reasonable distance for compressed SQL

                # Search for the first keyword
                first_keyword_found = False

                while idx < len(parent.segments) and idx - i <= max_lookahead:
                    next_seg = parent.segments[idx]

                    if next_seg.is_type("keyword") and next_seg.raw.upper() == keywords[0]:
                        first_keyword_found = True
                        self.logger.debug("Found DEFAULT constraint")
                        break

                    idx += 1

                # If we found the keyword
                return first_keyword_found

        return False

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
