from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, TypedDict
from mkdocs_sqlalchemy_plugin.utils import parse_fields, FIELD, parse_table_list

logger = logging.getLogger("mkdocs.plugins")

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


class TableStyleConfig(TypedDict):
    tick: str
    cross: str
    fields: list[FIELD]


class PluginConfig(TypedDict):
    base_class: str
    app_path: str | None
    python_path: list[str] | None
    table_style: TableStyleConfig
    include_tables: list[str] | None
    exclude_tables: list[str] | None
    group_by_schema: bool
    show_indexes: bool
    show_constraints: bool


@dataclass
class SqlAlchemyPluginContext:
    base_class: DeclarativeBase
    plugin_config: PluginConfig

    def get_table_style(self) -> TableStyleConfig:
        """Get table style configuration."""
        return self.plugin_config["table_style"]

    def should_include_table(self, tablename: str) -> bool:
        """Check if a table should be included in documentation."""
        include_tables = self.plugin_config.get("include_tables")
        exclude_tables = self.plugin_config.get("exclude_tables")

        if include_tables and tablename not in include_tables:
            return False

        if exclude_tables and tablename in exclude_tables:
            return False

        return True

    def get_filtered_tables(self):
        """Get all tables filtered by include/exclude configuration."""
        all_tables = self.base_class.metadata.sorted_tables
        return [t for t in all_tables if self.should_include_table(t.name)]


def generate_table(
    context: SqlAlchemyPluginContext,
    tablename: str,
    fields: list[FIELD] | None = None,
    show_indexes: bool | None = None,
    show_constraints: bool | None = None,
) -> str:
    """
    Generate documentation for a single table.

    Args:
        context: Plugin context with configuration
        tablename: Name of the table to document
        fields: List of fields to include (overrides config)
        show_indexes: Whether to show indexes (overrides config)
        show_constraints: Whether to show constraints (overrides config)

    Returns:
        Markdown documentation for the table
    """
    # Get configuration values with fallbacks
    style = context.get_table_style()
    tick = style["tick"]
    cross = style["cross"]

    if fields is None:
        fields = style["fields"]
    if show_indexes is None:
        show_indexes = context.plugin_config.get("show_indexes", True)
    if show_constraints is None:
        show_constraints = context.plugin_config.get("show_constraints", True)
    if tablename not in context.base_class.metadata.tables:
        logger.error(f"Table '{tablename}' not found in metadata")
        raise ValueError(f"Table '{tablename}' not found in metadata")

    table = context.base_class.metadata.tables[tablename]
    logger.debug(f"Generating documentation for table: {tablename}")

    output = []

    output.append(f"## `{table.name}`\n")

    header = " | ".join(fields)
    separator = "|".join(["-" * (len(field) + 2) for field in fields])
    output.append(f"| {header} |")
    output.append(f"|{separator}|")

    for column in table.columns:
        row_values = _generate_column_values(column, fields, tick, cross)
        row = " | ".join(row_values)
        output.append(f"| {row} |")

    if show_indexes:
        output.append(_generate_indexes_section(table))

    if show_constraints:
        output.append(_generate_constraints_section(table))

    return "\n".join(output).rstrip("\n")


def _generate_column_values(
    column, fields: list[FIELD], tick: str, cross: str
) -> list[str]:
    """Generate values for each field in a column row."""
    fk_list = (
        [f"{fk.column.table.name}.{fk.column.name}" for fk in column.foreign_keys]
        if column.foreign_keys
        else []
    )
    fk_string = f"*{', '.join(fk_list).replace('.', '&period;')}*" if fk_list else ""

    default_value = _format_default_value(column.default)

    field_values = {
        "column": f"`{column.name}`",
        "type": str(column.type),
        "nullable": tick if column.nullable else cross,
        "default": default_value,
        "primary_key": tick if column.primary_key else cross,
        "unique": tick if column.unique else cross,
        "foreign_key": fk_string,
    }

    return [field_values.get(field, "") for field in fields]


def _format_default_value(default) -> str:
    """Format a column default value for display."""
    if default is None:
        return ""

    if hasattr(default, "arg"):
        default_val = default.arg
        # If it's a callable, show its name
        if callable(default_val):
            return default_val.__name__
        return str(default_val)

    return str(default)


def _generate_indexes_section(table) -> str:
    """Generate the indexes section for a table."""
    if not table.indexes:
        return "\n**Indexes:** None\n"

    lines = ["\n**Indexes:**\n"]
    for idx in table.indexes:
        columns = ", ".join(f"`{col}`" for col in idx.columns.keys())
        lines.append(f"- `{idx.name}`: {columns}")

    return "\n".join(lines) + "\n"


def _generate_constraints_section(table) -> str:
    """Generate the constraints section for a table."""
    # Filter constraints: must have a name and not start with underscore
    constraints = [
        c for c in table.constraints if c.name and not c.name.startswith("_")
    ]

    if not constraints:
        return "\n**Constraints:** None\n"

    lines = ["\n**Constraints:**\n"]
    for constraint in constraints:
        constraint_type = type(constraint).__name__
        lines.append(f"- `{constraint.name}` ({constraint_type})")

    return "\n".join(lines) + "\n"


def generate_tables(
    context: SqlAlchemyPluginContext,
    include_tables: list[str] | None = None,
    exclude_tables: list[str] | None = None,
    sort_by: str = "name",
    **kwargs,
) -> str:
    """Generate documentation for multiple tables."""
    all_tables = context.base_class.metadata.sorted_tables

    filtered_tables = []
    for table in all_tables:
        if include_tables and table.name not in include_tables:
            continue
        if exclude_tables and table.name in exclude_tables:
            continue
        if not context.should_include_table(table.name):
            continue
        filtered_tables.append(table)

    if sort_by == "name":
        filtered_tables.sort(key=lambda t: t.name)

    output = []
    for table in filtered_tables:
        output.append(generate_table(context, table.name))

    return "\n".join(output).rstrip("\n")


def generate_single_table(
    context: SqlAlchemyPluginContext, table_name: str, params: dict[str, str | bool]
) -> str:
    """Generate documentation for a single table with parameters."""
    table_options = {
        "fields": parse_fields(params.get("fields")),  # type: ignore
        "show_indexes": params.get(
            "show_indexes", context.plugin_config.get("show_indexes", True)
        ),
        "show_constraints": params.get(
            "show_constraints", context.plugin_config.get("show_constraints", True)
        ),
    }

    return generate_table(context, table_name, **table_options)


def generate_filtered_tables(
    context: SqlAlchemyPluginContext, params: dict[str, str | bool]
) -> str:
    """Generate documentation for filtered tables."""
    tag_include = parse_table_list(params.get("include"))  # type: ignore
    tag_exclude = parse_table_list(params.get("exclude"))  # type: ignore

    # Merge with global config
    # Tag-level include/exclude takes precedence
    final_include = tag_include if tag_include else None

    global_exclude = context.plugin_config.get("exclude_tables")
    if tag_exclude and global_exclude:
        final_exclude = list(set(tag_exclude) | set(global_exclude))
    elif tag_exclude:
        final_exclude = tag_exclude
    else:
        final_exclude = list(global_exclude) if global_exclude else None

    return generate_tables(
        context,
        include_tables=final_include,
        exclude_tables=final_exclude,
        sort_by=str(params.get("sort_by", "name")),
    )


def generate_content_from_params(
    context: SqlAlchemyPluginContext, params: dict[str, str | bool]
) -> str:
    """Generate markdown content based on tag parameters."""

    if "table" in params:
        table_name = str(params["table"])
        return generate_single_table(context, table_name, params)
    else:
        return generate_filtered_tables(context, params)
