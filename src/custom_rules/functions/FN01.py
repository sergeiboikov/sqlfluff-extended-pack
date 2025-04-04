"""Rules for enforcing function naming conventions."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_FN01(BaseRule):
    """
    Function names should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE OR REPLACE FUNCTION public.configuration_get ()...

    **Best practice**

    .. code-block:: sql

        CREATE OR REPLACE FUNCTION public.fun_configuration_get ()...
    """

    name = "functions.function_naming"
    code = "FN01"
    description = "Enforces function names to start with expected prefix."
    groups = ("all", "custom", "functions")
    config_keywords = []  # Intentionally empty to bypass validation
    crawl_behaviour = SegmentSeekerCrawler({"function_definition", "create_function_statement"})

    # The expected prefix for function names
    _DEFAULT_EXPECTED_PREFIX = "fun_"

    def __init__(self, code="FN01", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get("expected_prefix", self._DEFAULT_EXPECTED_PREFIX)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate function names."""
        try:
            segment = context.segment

            # Handle the structure of a function definition more carefully
            function_name = self._extract_function_name(segment)

            if function_name:
                # Extract just the function name if it's a fully qualified name
                if "." in function_name:
                    parts = function_name.split(".")
                    function_name = parts[-1]

                if not function_name.lower().startswith(self.expected_prefix):
                    self.logger.debug(f"Function name violates naming convention: {function_name}")
                    return self._create_lint_result(segment, function_name, self.expected_prefix)

            return None
        except Exception as e:
            self.logger.error(f"Exception in function naming rule: {str(e)}")
            return None

    def _extract_function_name(self, segment) -> Optional[str]:
        """Extract the function name from a function definition segment."""
        # Look for the schema qualified name segment
        schema_qualified_name = segment.get_child("schema_qualified_name")
        if schema_qualified_name:
            # The last identifier is the function name
            identifiers = schema_qualified_name.get_children("naked_identifier")
            if identifiers:
                return identifiers[-1].raw

        # If no schema qualified name found, try to find standalone function name
        function_name_seg = segment.get_child("function_name")
        if function_name_seg:
            return function_name_seg.raw

        # Try to find object reference (could be a function name in some dialects)
        object_ref = segment.get_child("object_reference")
        if object_ref:
            return object_ref.raw

        # If we can't find the function name using specific types, try a more general approach
        # Look for segments after CREATE [OR REPLACE] FUNCTION keywords
        create_func_idx = None
        for i, child in enumerate(segment.segments):
            if child.is_type("keyword") and child.raw.upper() == "FUNCTION":
                create_func_idx = i
                break

        if create_func_idx is not None and create_func_idx + 1 < len(segment.segments):
            # Try to find the function name after the FUNCTION keyword
            for i in range(create_func_idx + 1, min(create_func_idx + 5, len(segment.segments))):
                child = segment.segments[i]
                if not child.is_type("whitespace") and not child.is_type("comment"):
                    # This is likely the function name or schema.function_name
                    return child.raw

        return None

    def _create_lint_result(self, segment, function_name: str, expected_prefix: str) -> LintResult:
        """
        Create a lint result for a function naming violation.

        Args:
            segment: The segment to anchor the lint result to
            function_name: The name of the function
            expected_prefix: The expected prefix for the function

        Returns:
            LintResult: The lint result object
        """
        self.logger.debug(f"Function name '{function_name}' violates naming convention")
        return LintResult(
            anchor=segment,
            description=(
                f"Function name '{function_name}' should start with "
                f"'{expected_prefix}'."
            )
        )
