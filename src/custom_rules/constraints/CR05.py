"""Rules for enforcing constraint naming conventions."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CR05(BaseRule):
    """
    DEFAULT constraint names should use "df_" prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.product (
            product_id INT,
            is_active BIT,
            CONSTRAINT active_default DEFAULT (1) FOR is_active
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.product (
            product_id INT,
            is_active BIT,
            CONSTRAINT df_active DEFAULT (1) FOR is_active
        );
    """

    name = "constraints.df_constraint_naming"
    description = "Enforces DEFAULT constraints to start with 'df_' prefix."
    groups = ("all", "custom", "constraints")
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "object_reference"})

    # The expected prefix for DEFAULT constraint
    _EXPECTED_PREFIX = "df_"

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate DEFAULT constraint name prefixes."""
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

                # Find if this is a DEFAULT constraint
                is_default = False
                # Look at siblings in the parent segment
                if parent:
                    # This improved implementation is more flexible with inline SQL
                    for i, child in enumerate(parent.segments):
                        if child is segment:
                            # Found our segment, now look ahead for DEFAULT keyword
                            # within a reasonable distance, allowing for whitespace and other content
                            idx = i + 1
                            max_lookahead = 10  # Increase lookahead for compressed SQL

                            while idx < len(parent.segments) and idx - i <= max_lookahead:
                                next_seg = parent.segments[idx]

                                # Look for DEFAULT keyword
                                if next_seg.is_type("keyword") and next_seg.raw.upper() == "DEFAULT":
                                    is_default = True
                                    self.logger.debug("Found DEFAULT constraint")
                                    break

                                idx += 1
                            break

                if is_default and not constraint_name.startswith(self._EXPECTED_PREFIX):
                    self.logger.debug(f"DEFAULT constraint name '{constraint_name}' violates naming convention")
                    return LintResult(
                        anchor=segment,
                        description=(
                            f"DEFAULT constraint name '{constraint_name}' should start with "
                            f"'{self._EXPECTED_PREFIX}'."
                        )
                    )
            return None
        except Exception as e:
            self.logger.error(f"Exception in DEFAULT constraint naming rule: {str(e)}")
            return None