"""Rules for enforcing constraint naming conventions."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CR02(BaseRule):
    """
    FOREIGN KEY constraint names should use "fk_" prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.orders (
            order_id INT,
            customer_id INT,
            CONSTRAINT customer_order_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.orders (
            order_id INT,
            customer_id INT,
            CONSTRAINT fk_customer_order FOREIGN KEY (customer_id) REFERENCES public.customers(id)
        );
    """

    name = "constraints.fk_constraint_naming"
    description = "Enforces FOREIGN KEY constraints to start with 'fk_' prefix."
    groups = ("all", "custom", "constraints")
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "object_reference"})

    # The expected prefix for FOREIGN KEY constraint
    _EXPECTED_PREFIX = "fk_"

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate FOREIGN KEY constraint name prefixes."""
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

                # Find if this is a FOREIGN KEY constraint
                is_foreign_key = False
                # Look at siblings in the parent segment
                if parent:
                    # This improved implementation is more flexible with inline SQL
                    for i, child in enumerate(parent.segments):
                        if child is segment:
                            # Found our segment, now look ahead for FOREIGN and KEY keywords
                            # within a reasonable distance, allowing for whitespace and other content
                            idx = i + 1
                            max_lookahead = 10  # Increase lookahead for compressed SQL

                            while idx < len(parent.segments) and idx - i <= max_lookahead:
                                next_seg = parent.segments[idx]

                                # Look for FOREIGN keyword
                                if next_seg.is_type("keyword") and next_seg.raw.upper() == "FOREIGN":
                                    # Now look for KEY keyword, which might be right after FOREIGN
                                    key_idx = idx + 1
                                    while key_idx < len(parent.segments) and key_idx - idx <= 3:
                                        key_seg = parent.segments[key_idx]
                                        if key_seg.is_type("keyword") and key_seg.raw.upper() == "KEY":
                                            is_foreign_key = True
                                            self.logger.debug("Found FOREIGN KEY constraint")
                                            break
                                        # Skip whitespace
                                        if not key_seg.is_type("whitespace"):
                                            # If we hit something other than whitespace and it's not KEY,
                                            # then this FOREIGN isn't followed by KEY
                                            break
                                        key_idx += 1
                                    if is_foreign_key:
                                        break

                                idx += 1
                            break

                if is_foreign_key and not constraint_name.startswith(self._EXPECTED_PREFIX):
                    self.logger.debug(f"FOREIGN KEY constraint name '{constraint_name}' violates naming convention")
                    return LintResult(
                        anchor=segment,
                        description=(
                            f"FOREIGN KEY constraint name '{constraint_name}' should start with "
                            f"'{self._EXPECTED_PREFIX}'."
                        )
                    )
            return None
        except Exception as e:
            self.logger.error(f"Exception in FOREIGN KEY constraint naming rule: {str(e)}")
            return None