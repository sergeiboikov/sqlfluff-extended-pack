"""Rules for enforcing function parameter naming conventions."""

from typing import Optional, List, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_FN02(BaseRule):
    """
    Function parameters should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE OR REPLACE FUNCTION public.configuration_get (configuration_key TEXT)...

    **Best practice**

    .. code-block:: sql

        CREATE OR REPLACE FUNCTION public.configuration_get (p_configuration_key TEXT)...
    """

    name = "functions.function_parameter_naming"
    code = "FN02"
    description = "Enforces function parameters to start with expected prefix."
    groups = ("all", "custom", "functions")
    config_keywords = []  # Intentionally empty to bypass validation
    # PostgreSQL uses CREATE FUNCTION statements rather than function_definition
    crawl_behaviour = SegmentSeekerCrawler(
        {
            "function_definition",
            "create_function_statement",
            "statement",
            "create_statement",
        }
    )

    # The expected prefix for function parameter names
    _DEFAULT_EXPECTED_PREFIX = "p_"
    COMMON_TYPES = [
        "INT",
        "INTEGER",
        "TEXT",
        "VARCHAR",
        "CHAR",
        "BOOLEAN",
        "DATE",
        "TIMESTAMP",
        "NUMERIC",
        "DECIMAL",
        "FLOAT",
        "REAL",
        "JSON",
        "JSONB",
        "UUID",
        "ARRAY",
        "SETOF",
    ]

    def __init__(self, code="FN02", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get(
            "expected_prefix", self._DEFAULT_EXPECTED_PREFIX
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate function parameters."""
        try:
            segment = context.segment

            # We only care about CREATE FUNCTION statements
            if not self._is_create_function(segment):
                return None

            # Extract function parameters from the segment
            parameters = self._extract_function_parameters(segment)

            if parameters:
                # Check if any parameter violates the naming convention
                for param_segment, param_name in parameters:
                    if not param_name.lower().startswith(self.expected_prefix):
                        return self._create_lint_result(
                            param_segment, param_name, self.expected_prefix
                        )

            return None
        except Exception as e:
            self.logger.error(f"Exception in function parameter naming rule: {str(e)}")
            return None

    def _is_create_function(self, segment) -> bool:
        """Check if the segment is a CREATE FUNCTION statement."""
        # If it's already a function_definition or create_function_statement, we're good
        if segment.is_type("function_definition") or segment.is_type(
            "create_function_statement"
        ):
            return True

        # Otherwise, check if it's a generic statement that is a CREATE FUNCTION
        if segment.is_type("statement") or segment.is_type("create_statement"):
            # Look for CREATE and FUNCTION keywords in sequence
            keywords = []
            for child in segment.segments:
                if child.is_type("keyword"):
                    keywords.append(child.raw.upper())

            # Check if CREATE and FUNCTION appear in sequence
            for i in range(len(keywords) - 1):
                if keywords[i] == "CREATE" and keywords[i + 1] == "FUNCTION":
                    return True

            # Also check for CREATE OR REPLACE FUNCTION
            for i in range(len(keywords) - 3):
                if (
                    keywords[i] == "CREATE"
                    and keywords[i + 1] == "OR"
                    and keywords[i + 2] == "REPLACE"
                    and keywords[i + 3] == "FUNCTION"
                ):
                    return True

        return False

    def _extract_function_parameters(self, segment) -> List[Tuple]:
        """
        Extract function parameters from a function definition segment.

        Returns:
            List of tuples containing (parameter_segment, parameter_name)
        """
        parameters = []

        # First try to find a parenthesized segment that likely contains the parameters
        parenthesized = None

        # Method 1: Look for a dedicated function_parameter_list segment
        param_list = segment.get_child("function_parameter_list")
        if param_list:
            parenthesized = param_list

        # Method 2: Look for bracketed/parenthesized segments right after the function name
        if not parenthesized:
            # Find the function name first
            func_name_found = False
            for _, child in enumerate(segment.segments):
                # If we've already found the function name, look for parentheses
                if func_name_found and (
                    child.is_type("bracketed") or child.is_type("parenthesized")
                ):
                    parenthesized = child
                    break

                # Look for function name indicators
                if child.is_type("function_name") or child.is_type("object_reference"):
                    func_name_found = True
                elif child.is_type("keyword") and child.raw.upper() == "FUNCTION":
                    func_name_found = (
                        True  # The next non-whitespace might be the function name
                    )

        # Method 3: Just look for any parenthesized segment
        if not parenthesized:
            for child in segment.segments:
                if child.is_type("bracketed") or child.is_type("parenthesized"):
                    # Make sure it's not some other bracketed content like the function body
                    if "(" in child.raw and not child.raw.startswith("$$"):
                        parenthesized = child
                        break

        # Process the parenthesized segment to extract parameters
        if parenthesized:
            # Method 1: Look for dedicated parameter_definition segments
            param_defs = parenthesized.get_children("parameter_definition")
            if param_defs:
                for param_def in param_defs:
                    # Try different ways to extract the parameter name
                    param_name = self._extract_parameter_name_from_definition(param_def)
                    if param_name:
                        parameters.append((param_def, param_name))

            # Method 2: Parse the raw content directly
            if not parameters:
                # Parse the raw content, which might look like "(param1 TYPE, param2 TYPE)"
                raw_content = parenthesized.raw

                # Remove outer parentheses
                if raw_content.startswith("(") and raw_content.endswith(")"):
                    raw_content = raw_content[1:-1].strip()

                # Split by commas to get individual parameter definitions
                raw_params = raw_content.split(",")

                for raw_param in raw_params:
                    raw_param = raw_param.strip()
                    if not raw_param:
                        continue

                    # Extract the parameter name (typically the first word)
                    parts = raw_param.split()
                    if parts:
                        param_name = parts[0]
                        # Make sure we're not picking up a type name as a parameter
                        if param_name.upper() not in self.COMMON_TYPES:
                            parameters.append((parenthesized, param_name))

            # Method 3: Use recursive identifier search as a last resort
            if not parameters:
                id_segments = []
                self._collect_identifiers(parenthesized, id_segments)

                for id_seg in id_segments:
                    # Skip if it's a known type name
                    if id_seg.raw.upper() in self.COMMON_TYPES:
                        continue

                    # Consider this a parameter name
                    parameters.append((id_seg, id_seg.raw))

        return parameters

    def _extract_parameter_name_from_definition(self, param_def) -> Optional[str]:
        """Extract parameter name from a parameter definition segment."""
        # Try to find an explicit identifier
        param_name = param_def.get_child("identifier")
        if param_name:
            return param_name.raw

        # Try naked_identifier
        param_name = param_def.get_child("naked_identifier")
        if param_name:
            return param_name.raw

        # Try looking at the direct children
        for child in param_def.segments:
            if child.is_type("identifier") or child.is_type("naked_identifier"):
                return child.raw

        # If all else fails, parse the raw content
        raw_def = param_def.raw.strip()
        if raw_def:
            # Parameter name is typically the first word
            parts = raw_def.split()
            if parts:
                return parts[0]

        return None

    def _collect_identifiers(self, segment, result_list):
        """Recursively collect all identifier segments."""
        if segment.is_type("identifier") or segment.is_type("naked_identifier"):
            result_list.append(segment)

        # Recursively check all child segments
        if hasattr(segment, "segments") and segment.segments:
            for child in segment.segments:
                self._collect_identifiers(child, result_list)

    def _create_lint_result(
        self, segment, parameter_name: str, expected_prefix: str
    ) -> LintResult:
        """
        Create a lint result for a function parameter naming violation.

        Args:
            segment: The segment to anchor the lint result to
            parameter_name: The name of the function parameter
            expected_prefix: The expected prefix for the function parameter

        Returns:
            LintResult: The lint result object
        """
        return LintResult(
            anchor=segment,
            description=(
                f"Function parameter '{parameter_name}' should start with "
                f"'{expected_prefix}'."
            ),
        )
