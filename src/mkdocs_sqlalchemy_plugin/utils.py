import re
from typing import Literal

FIELD = Literal[
    "column", "type", "nullable", "default", "primary_key", "unique", "foreign_key"
]
FIELD_NAMES = [
    "column",
    "type",
    "nullable",
    "default",
    "primary_key",
    "unique",
    "foreign_key",
]


def match_tag_regex(markdown: str, pattern: str) -> list[re.Match]:
    """
    Match all occurrences of the given tag pattern in the markdown.

    Args:
        markdown (str): The markdown content to search.
        pattern (str): The regex pattern to match.

    Returns:
        List of regex match objects.
    """
    return list(re.finditer(pattern, markdown))


def parse_fields(fields_str: str | None) -> list[FIELD] | None:
    """
    Parse comma-separated fields string.

    Args:
        fields_str (str | None): Comma-separated string of field names.

    Returns:
        List of FIELD literals or None.
    """
    if not fields_str:
        return None
    return [
        field.strip()
        for field in str(fields_str).split(",")
        if field.strip() in FIELD_NAMES
    ]  # type: ignore


def parse_table_list(tables_str: str | None) -> list[str] | None:
    """
    Parse comma-separated table names string.

    Args:
        tables_str (str | None): Comma-separated string of table names.

    Returns:
        List of table names or None.
    """
    if not tables_str:
        return None
    return [table.strip() for table in str(tables_str).split(",")]


def parse_tag_parameters(params_str: str | None) -> dict[str, int | str | bool]:
    """
    Parse tag parameters from string.

    Supports two parameter formats:
    - String parameters: key="value" (quotes are REQUIRED)
    - Boolean parameters: key=true or key=false (no quotes)

    Invalid formats are ignored.

    Args:
        params_str: Parameter string like 'table="users" show_indexes=true'

    Returns:
        Dictionary of parsed parameters

    Examples:
        >>> parse_tag_parameters('table="users" fields="column,type"')
        {'table': 'users', 'fields': 'column,type'}

        >>> parse_tag_parameters("show_indexes=true show_constraints=false")
        {'show_indexes': True, 'show_constraints': False}

        >>> parse_tag_parameters("table=users")  # Missing quotes - ignored
        {}
    """
    if not params_str:
        return {}

    params: dict[str, int | str | bool] = {}

    # Match key="value" patterns (string parameters with quotes)
    for match in re.finditer(r'(\w+)="([^"]*)"', params_str):
        key, value = match.groups()
        params[key] = value

    # Match key=true/false patterns (boolean parameters without quotes)
    for match in re.finditer(r"(\w+)=(true|false)(?:\s|$)", params_str):
        key, value = match.groups()
        params[key] = value == "true"

    return params
