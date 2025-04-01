"""Rules for enforcing constraint naming conventions."""

from typing import Optional

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
    description = "Enforces CHECK constraints to start with 'chk_' prefix."
    groups = ("all", "custom", "constraints")
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "object_reference"})

    # The expected prefix for CHECK constraint
    _EXPECTED_PREFIX = "chk_"

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate CHECK constraint name prefixes."""
        try:
            segment = context.segment
            # Check if we have a constraint name by looking at the parent segment
            is_constraint_name = False

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
                                is_constraint_name = True
                                self.logger.debug(f"Found constraint name: {segment.raw}")
                                break
                            elif not prev.is_type("whitespace"):
                                break
                            prev_idx -= 1
                        break

            if is_constraint_name:
                # Get the constraint name
                constraint_name = segment.raw.lower()
                self.logger.debug(f"Processing constraint name: {constraint_name}")

                # Find if this is a CHECK constraint
                is_check = False
                # Look at siblings in the parent segment
                if parent:
                    # This improved implementation is more flexible with inline SQL
                    for i, child in enumerate(parent.segments):
                        if child is segment:
                            # Found our segment, now look ahead for CHECK keyword
                            # within a reasonable distance, allowing for whitespace and other content
                            idx = i + 1
                            max_lookahead = 10  # Increase lookahead for compressed SQL

                            while idx < len(parent.segments) and idx - i <= max_lookahead:
                                next_seg = parent.segments[idx]

                                # Look for CHECK keyword
                                if next_seg.is_type("keyword") and next_seg.raw.upper() == "CHECK":
                                    is_check = True
                                    self.logger.debug("Found CHECK constraint")
                                    break

                                idx += 1
                            break

                if is_check and not constraint_name.startswith(self._EXPECTED_PREFIX):
                    self.logger.debug(f"CHECK constraint name '{constraint_name}' violates naming convention")
                    return LintResult(
                        anchor=segment,
                        description=(
                            f"CHECK constraint name '{constraint_name}' should start with "
                            f"'{self._EXPECTED_PREFIX}'."
                        )
                    )
            return None
        except Exception as e:
            self.logger.error(f"Exception in CHECK constraint naming rule: {str(e)}")
            return None