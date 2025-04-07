"""Rules for enforcing view naming conventions."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_VW01(BaseRule):
    """
    View names should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE OR REPLACE VIEW public.configuration_view ()...

    **Best practice**

    .. code-block:: sql

        CREATE OR REPLACE VIEW public.v_configuration ()...
    """

    name = "views.view_naming"
    code = "VW01"
    description = "Enforces view names to start with expected prefix."
    groups = ("all", "custom", "views")
    config_keywords = []  # Intentionally empty to bypass validation
    crawl_behaviour = SegmentSeekerCrawler(
        {"create_view_statement", "create_materialized_view_statement"}
    )

    # The expected prefix for view names
    _DEFAULT_EXPECTED_PREFIX = "v_"

    def __init__(self, code="VW01", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get(
            "expected_prefix", self._DEFAULT_EXPECTED_PREFIX
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate view names."""
        try:
            segment = context.segment

            # Handle the structure of a view definition more carefully
            view_name = self._extract_view_name(segment)

            if view_name:
                # Extract just the view name if it's a fully qualified name
                if "." in view_name:
                    parts = view_name.split(".")
                    view_name = parts[-1]

                if not view_name.lower().startswith(self.expected_prefix):
                    self.logger.debug(
                        f"View name violates naming convention: {view_name}"
                    )
                    return self._create_lint_result(
                        segment, view_name, self.expected_prefix
                    )

            return None
        except Exception as e:
            self.logger.error(f"Exception in view naming rule: {str(e)}")
            return None

    def _extract_view_name(self, segment) -> Optional[str]:
        """Extract the view name from a view definition segment."""
        # Look for the schema qualified name segment
        schema_qualified_name = segment.get_child("schema_qualified_name")
        if schema_qualified_name:
            # The last identifier is the view name
            identifiers = schema_qualified_name.get_children("naked_identifier")
            if identifiers:
                return identifiers[-1].raw

        # If no schema qualified name found, try to find standalone view name
        view_name_seg = segment.get_child("view_name")
        if view_name_seg:
            return view_name_seg.raw

        # Try to find object reference (could be a view name in some dialects)
        object_ref = segment.get_child("object_reference")
        if object_ref:
            return object_ref.raw

        # If we can't find the view name using specific types, try a more general approach
        # Look for segments after CREATE [OR REPLACE] VIEW or CREATE MATERIALIZED VIEW keywords
        create_view_idx = None
        for i, child in enumerate(segment.segments):
            if child.is_type("keyword") and child.raw.upper() in [
                "VIEW",
                "MATERIALIZED",
            ]:
                # For "VIEW", it could be directly after CREATE
                # For "MATERIALIZED", the next keyword should be "VIEW"
                if child.raw.upper() == "VIEW":
                    create_view_idx = i
                    break
                elif (
                    i + 1 < len(segment.segments)
                    and segment.segments[i + 1].is_type("keyword")
                    and segment.segments[i + 1].raw.upper() == "VIEW"
                ):
                    create_view_idx = i + 1  # Set to the VIEW keyword position
                    break

        if create_view_idx is not None and create_view_idx + 1 < len(segment.segments):
            # Try to find the view name after the VIEW keyword
            for i in range(
                create_view_idx + 1, min(create_view_idx + 5, len(segment.segments))
            ):
                child = segment.segments[i]
                if not child.is_type("whitespace") and not child.is_type("comment"):
                    # This is likely the view name or schema.view_name
                    return child.raw

        return None

    def _create_lint_result(
        self, segment, view_name: str, expected_prefix: str
    ) -> LintResult:
        """
        Create a lint result for a view naming violation.

        Args:
            segment: The segment to anchor the lint result to
            view_name: The name of the view
            expected_prefix: The expected prefix for the view

        Returns:
            LintResult: The lint result object
        """
        self.logger.debug(f"View name '{view_name}' violates naming convention")
        return LintResult(
            anchor=segment,
            description=(
                f"View name '{view_name}' should start with " f"'{expected_prefix}'."
            ),
        )
