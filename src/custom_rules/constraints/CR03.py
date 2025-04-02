"""Rules for enforcing constraint naming conventions."""

from typing import Optional, Tuple, List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CR03(BaseRule):
    """
    CHECK constraint names should use "chk_" prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.employee (
            employee_id INT,
            salary DECIMAL(10,2),
            CONSTRAINT salary_positive CHECK (salary > 0)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.employee (
            employee_id INT,
            salary DECIMAL(10,2),
            CONSTRAINT chk_salary_positive CHECK (salary > 0)
        );
    """

    name = "constraints.chk_constraint_naming"
    code = "CR03"
    description = "Enforces CHECK constraints to start with expected prefix."
    groups = ("all", "custom", "constraints")
    config_keywords = []  # Intentionally empty to bypass validation
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "object_reference"})

    # The expected prefix for CHECK constraint
    _DEFAULT_EXPECTED_PREFIX = "chk_"

    def __init__(self, code="CR03", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get("expected_prefix", self._DEFAULT_EXPECTED_PREFIX)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate CHECK constraint name prefixes."""
        try:
            segment = context.segment

            # Check if this segment is a constraint name
            is_constraint_name, constraint_name = self._is_constraint_name(context)

            if is_constraint_name:
                # Find if this is a CHECK constraint
                is_check = self._is_constraint_type(context, ["CHECK"])

                if is_check and not constraint_name.startswith(self.expected_prefix):
                    return self._create_lint_result(segment, constraint_name, self.expected_prefix)
            return None
        except Exception as e:
            self.logger.error(f"Exception in constraint naming rule: {str(e)}")
            return None

    def _is_constraint_name(self, context: RuleContext) -> Tuple[bool, str]:
        """
        Check if the current segment is a constraint name.

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
                        self.logger.debug("Found CHECK constraint")
                        break

                    idx += 1

                # If we only had one keyword to check or found all keywords
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
        self.logger.debug(f"CHECK constraint name '{constraint_name}' violates naming convention")
        return LintResult(
            anchor=segment,
            description=(
                f"CHECK constraint name '{constraint_name}' should start with "
                f"'{expected_prefix}'."
            )
        )