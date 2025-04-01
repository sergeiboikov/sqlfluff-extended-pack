"""Rules for enforcing constraint naming conventions."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CR01(BaseRule):
    """
    PRIMARY KEY constraint names should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.person (
            person_id INT,
            CONSTRAINT person_pk PRIMARY KEY (person_id)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.person (
            person_id INT,
            CONSTRAINT pk_person PRIMARY KEY (person_id)
        );
    """

    name = "constraints.pk_constraint_naming"
    code = "CR01"
    description = "Enforces PRIMARY KEY constraints to start with expected prefix."
    groups = ("all", "custom", "constraints")
    config_keywords = [
        "expected_prefix",
    ]
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "object_reference"})

    # The expected prefix for PRIMARY KEY constraint
    _DEFAULT_EXPECTED_PREFIX = "pk_"

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate PRIMARY KEY constraint name prefixes."""
        self.expected_prefix: str
        try:
            expected_prefix = self.expected_prefix if self.expected_prefix else self._DEFAULT_EXPECTED_PREFIX
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

                # Find if this is a PRIMARY KEY constraint
                is_primary_key = False
                # Look at siblings in the parent segment
                if parent:
                    # This improved implementation is more flexible with inline SQL
                    for i, child in enumerate(parent.segments):
                        if child is segment:
                            # Found our segment, now look ahead for PRIMARY and KEY keywords
                            # within a reasonable distance, allowing for whitespace and other content
                            idx = i + 1
                            max_lookahead = 10  # Increase lookahead for compressed SQL

                            while idx < len(parent.segments) and idx - i <= max_lookahead:
                                next_seg = parent.segments[idx]

                                # Look for PRIMARY keyword
                                if next_seg.is_type("keyword") and next_seg.raw.upper() == "PRIMARY":
                                    # Now look for KEY keyword, which might be right after PRIMARY
                                    key_idx = idx + 1
                                    while key_idx < len(parent.segments) and key_idx - idx <= 3:
                                        key_seg = parent.segments[key_idx]
                                        if key_seg.is_type("keyword") and key_seg.raw.upper() == "KEY":
                                            is_primary_key = True
                                            self.logger.debug("Found PRIMARY KEY constraint")
                                            break
                                        # Skip whitespace
                                        if not key_seg.is_type("whitespace"):
                                            # If we hit something other than whitespace and it's not KEY,
                                            # then this PRIMARY isn't followed by KEY
                                            break
                                        key_idx += 1
                                    if is_primary_key:
                                        break

                                idx += 1
                            break

                if is_primary_key and not constraint_name.startswith(expected_prefix):
                    self.logger.debug(f"PRIMARY KEY constraint name '{constraint_name}' violates naming convention")
                    return LintResult(
                        anchor=segment,
                        description=(
                            f"PRIMARY KEY constraint name '{constraint_name}' should start with "
                            f"'{expected_prefix}'."
                        )
                    )
            return None
        except Exception as e:
            self.logger.error(f"Exception in PRIMARY KEY constraint naming rule: {str(e)}")
            return None
