"""Rules for enforcing constraint naming conventions."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CR04(BaseRule):
    """
    UNIQUE constraint names should use "uc_" prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.person (
            person_id INT,
            email TEXT,
            CONSTRAINT email_unique UNIQUE (email)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.person (
            person_id INT,
            email TEXT,
            CONSTRAINT uc_email UNIQUE (email)
        );
    """

    name = "constraints.uc_constraint_naming"
    code = "CR04"
    description = "Enforces UNIQUE constraints to start with expected prefix."
    groups = ("all", "custom", "constraints")
    config_keywords = []  # Intentionally empty to bypass validation
    crawl_behaviour = SegmentSeekerCrawler({"table_constraint"})

    # The expected prefix for UNIQUE constraint
    _DEFAULT_EXPECTED_PREFIX = "uc_"

    def __init__(self, code="CR04", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get(
            "expected_prefix", self._DEFAULT_EXPECTED_PREFIX
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate UNIQUE constraint name prefixes."""
        try:
            segment = context.segment
            constraint_name = segment.get_child("object_reference").raw
            keywords = [keyword.raw for keyword in segment.get_children("keyword")]

            # Check if this is a UNIQUE constraint
            is_unique = "UNIQUE" in keywords

            if is_unique and not constraint_name.lower().startswith(
                self.expected_prefix
            ):
                return self._create_lint_result(
                    segment, constraint_name, self.expected_prefix
                )
            return None
        except Exception as e:
            self.logger.error(f"Exception in constraint naming rule: {str(e)}")
            return None

    def _create_lint_result(
        self, segment, constraint_name: str, expected_prefix: str
    ) -> LintResult:
        """
        Create a lint result for a constraint naming violation.

        Args:
            segment: The segment to anchor the lint result to
            constraint_name: The name of the constraint
            expected_prefix: The expected prefix for the constraint

        Returns:
            LintResult: The lint result object
        """
        self.logger.debug(
            f"UNIQUE constraint name '{constraint_name}' violates naming convention"
        )
        return LintResult(
            anchor=segment,
            description=(
                f"UNIQUE constraint name '{constraint_name}' should start with "
                f"'{expected_prefix}'."
            ),
        )
