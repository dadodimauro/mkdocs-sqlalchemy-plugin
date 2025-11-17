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


def match_tag_regex(
    markdown: str, pattern: str = r"\{%\s*sqlalchemy(?:\s+([^%]+))?\s*%\}"
) -> list[re.Match]:
    """Match all occurrences of the given tag pattern in the markdown."""
    return list(re.finditer(pattern, markdown))


def parse_fields(fields_str: str | None) -> list[FIELD] | None:
    """Parse comma-separated fields string."""
    if not fields_str:
        return None
    return [
        field.strip()
        for field in str(fields_str).split(",")
        if field.strip() in FIELD_NAMES
    ]  # type: ignore


def parse_table_list(tables_str: str | None) -> list[str] | None:
    """Parse comma-separated table names string."""
    if not tables_str:
        return None
    return [table.strip() for table in str(tables_str).split(",")]


def parse_tag_parameters(params_str: str | None) -> dict[str, str | bool]:
    """Parse tag parameters from string like 'table="users" fields="column,type"'."""
    if not params_str:
        return {}

    params = {}

    # Match key="value" patterns
    for match in re.finditer(r'(\w+)="([^"]*)"', params_str):
        key, value = match.groups()
        params[key] = value

    # Match key=true/false patterns
    for match in re.finditer(r"(\w+)=(true|false)", params_str):
        key, value = match.groups()
        params[key] = value.lower() == "true"

    return params
