import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mdutils.tools.Header import AtxHeaderLevel, Header
from mdutils.tools.Table import Table
from mdutils.tools.TextUtils import TextUtils

from mkdocs_sqlalchemy_plugin.config import (
    PluginConfig,
    TableGenerationOptions,
)
from mkdocs_sqlalchemy_plugin.utils import parse_table_list

if TYPE_CHECKING:
    from sqlalchemy import Column as SaColumn
    from sqlalchemy import Table as SaTable
    from sqlalchemy.orm import DeclarativeBase
    from sqlalchemy.sql.schema import DefaultGenerator


class PluginLogFilter(logging.Filter):
    """Add a prefix to all log messages."""

    def __init__(self, prefix: str = "mkdocs_sqlalchemy_plugin"):
        super().__init__()
        self.prefix = prefix

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = f"{self.prefix}: {record.msg}"
        return True


logger = logging.getLogger("mkdocs.plugins.mkdocs_sqlalchemy_plugin")
logger.addFilter(PluginLogFilter())


@dataclass
class SqlAlchemyPluginContext:
    """
    Context for SQLAlchemy plugin operations.

    Attributes:
        base_class (DeclarativeBase): The SQLAlchemy base class containing metadata.
        plugin_config (PluginConfig): The plugin configuration.

    Methods:
        get_filtered_tables: Get tables filtered by include/exclude lists.
    """

    base_class: type[DeclarativeBase]
    plugin_config: PluginConfig

    def get_filtered_tables(
        self,
        include_tables: list[str] | None = None,
        exclude_tables: list[str] | None = None,
    ) -> list[SaTable]:
        """Get tables filtered by include/exclude lists.

        Args:
            include_tables: If provided, only include these tables (overrides config)
            exclude_tables: If provided, also exclude these tables (merged with config)

        Returns:
            List of filtered tables
        """
        logger.debug("Filtering tables from metadata")
        all_tables = self.base_class.metadata.sorted_tables
        logger.debug(f"Total tables in metadata: {len(all_tables)}")

        # Determine final include list (tag overrides config)
        final_include = (
            include_tables
            if include_tables
            else self.plugin_config.filter.include_tables
        )

        # Determine final exclude list (merge tag and config)
        final_exclude = set(exclude_tables or [])
        if self.plugin_config.filter.exclude_tables:
            final_exclude.update(self.plugin_config.filter.exclude_tables)

        if final_include:
            logger.debug(f"Include filter: {final_include}")
        if final_exclude:
            logger.debug(f"Exclude filter: {final_exclude}")

        filtered = []
        excluded_count = 0
        for table in all_tables:
            # Check include list
            if final_include and table.name not in final_include:
                logger.debug(f"  Skipping table '{table.name}' (not in include list)")
                excluded_count += 1
                continue

            # Check exclude list
            if table.name in final_exclude:
                logger.debug(f"  Skipping table '{table.name}' (in exclude list)")
                excluded_count += 1
                continue

            filtered.append(table)
            logger.debug(f"  Including table '{table.name}'")

        logger.info(
            f"Filtered tables: {len(filtered)} included, {excluded_count} excluded "
            f"(total: {len(all_tables)})"
        )
        if filtered:
            logger.debug(f"Included table names: {[t.name for t in filtered]}")

        return filtered


def generate_table(
    context: SqlAlchemyPluginContext,
    tablename: str,
    options: TableGenerationOptions | None = None,
) -> str:
    """Generate documentation for a single table.

    Args:
        context: Plugin context with configuration
        tablename: Name of the table to document
        options: Generation options (if None, uses defaults from context)

    Returns:
        Markdown documentation for the table
    """
    logger.info(f"Generating documentation for table: '{tablename}'")

    # Use default options if not provided
    if options is None:
        options = context.plugin_config.get_generation_options()
        logger.debug("Using default generation options from config")
    else:
        logger.debug(f"Using custom generation options: {options}")

    # Get the table
    if tablename not in context.base_class.metadata.tables:
        available_tables = list(context.base_class.metadata.tables.keys())
        logger.error(
            f"Table '{tablename}' not found in metadata. "
            f"Available tables: {available_tables}"
        )
        return f"<!-- Table '{tablename}' not found -->"

    table = context.base_class.metadata.tables[tablename]
    logger.debug(
        f"Table '{tablename}': {len(table.columns)} column(s), "
        f"{len(table.indexes)} index(es), {len(table.constraints)} constraint(s)"
    )

    # Get style config
    style = context.plugin_config.table_style
    logger.debug(f"Using style config: fields={options.fields}")

    output = []

    # Table header
    logger.debug(f"Generating header for table '{tablename}'")
    output.append(
        Header.atx(
            level=AtxHeaderLevel.HEADING,
            title=f"Table: {TextUtils.inline_code(table.name)}",
        )
    )

    # Generate table
    logger.debug(f"Generating column table for '{tablename}'")
    text_list = list(options.fields)
    for column in table.columns:
        text_list += _generate_column_values(
            column, options.fields, style.tick, style.cross
        )

    output.append(
        Table().create_table(
            columns=len(options.fields),
            rows=len(table.columns) + 1,
            text=text_list,
            text_align="center",
        )
    )

    # Optional sections
    if options.show_indexes:
        logger.debug(f"Generating indexes section for '{tablename}'")
        output.append(_generate_indexes_section(table))

    if options.show_constraints:
        logger.debug(f"Generating constraints section for '{tablename}'")
        output.append(_generate_constraints_section(table))

    result = "\n".join(output).rstrip("\n")
    logger.debug(
        f"Generated {len(result)} characters of documentation for '{tablename}'"
    )
    return result


def _generate_column_values(
    column: SaColumn, fields: list[str], tick: str, cross: str
) -> list[str]:
    """Generate values for each field in a column row."""
    fk_list = (
        [f"{fk.column.table.name}.{fk.column.name}" for fk in column.foreign_keys]
        if column.foreign_keys
        else []
    )
    fk_string = (
        TextUtils.italics(", ".join(fk_list).replace(".", "&period;"))
        if fk_list
        else ""
    )

    default_value = _format_default_value(column.default)

    field_values: dict[str, str] = {
        "column": TextUtils.inline_code(column.name),
        "type": str(column.type),
        "nullable": tick if column.nullable else cross,
        "default": default_value,
        "primary_key": tick if column.primary_key else cross,
        "unique": tick if column.unique else cross,
        "foreign_key": fk_string,
    }

    logger.debug(
        f"  Column '{column.name}': type={column.type}, "
        f"nullable={column.nullable}, pk={column.primary_key}, "
        f"unique={column.unique}, fks={len(fk_list)}"
    )

    return [field_values.get(field, "") for field in fields]


def _format_default_value(default: DefaultGenerator | None) -> str:
    """Format a column default value for display."""
    if default is None:
        return ""

    if hasattr(default, "arg"):
        default_val = default.arg  # type: ignore
        if callable(default_val):
            return default_val.__name__
        return str(default_val)

    return str(default)


def _generate_indexes_section(table: SaTable) -> str:
    """Generate the indexes section for a table."""
    if not table.indexes:
        logger.debug(f"  No indexes for table '{table.name}'")
        return f"\n{TextUtils.bold('Indexes:')} None\n"

    logger.debug(f"  Found {len(table.indexes)} index(es) for table '{table.name}'")
    lines = [f"\n{TextUtils.bold('Indexes:')}\n"]
    for idx in table.indexes:
        columns = ", ".join(TextUtils.inline_code(col) for col in idx.columns.keys())
        idx_name = str(idx.name) if idx.name else str(id(idx))
        lines.append(f"- {TextUtils.inline_code(idx_name)}: {columns}")
        logger.debug(
            f"    Index '{idx_name}': columns=[{', '.join(idx.columns.keys())}]"
        )

    return "\n".join(lines) + "\n"


def _generate_constraints_section(table: SaTable) -> str:
    """Generate the constraints section for a table."""
    constraints = [
        c for c in table.constraints if str(c.name) and not str(c.name).startswith("_")
    ]

    if not constraints:
        logger.debug(f"  No named constraints for table '{table.name}'")
        return f"\n{TextUtils.bold('Constraints:')} None\n"

    logger.debug(f"  Found {len(constraints)} constraint(s) for table '{table.name}'")
    lines = [f"\n{TextUtils.bold('Constraints:')}\n"]
    for constraint in constraints:
        constraint_type = type(constraint).__name__
        constraint_name = str(constraint.name or "Unknown")
        lines.append(f"- {TextUtils.inline_code(constraint_name)} ({constraint_type})")
        logger.debug(f"    Constraint '{constraint_name}': type={constraint_type}")

    return "\n".join(lines) + "\n"


def generate_tables(
    context: SqlAlchemyPluginContext,
    include_tables: list[str] | None = None,
    exclude_tables: list[str] | None = None,
    options: TableGenerationOptions | None = None,
    sort_by: str = "name",
) -> str:
    """Generate documentation for multiple tables.

    Args:
        context: Plugin context
        include_tables: Only include these tables (overrides config)
        exclude_tables: Also exclude these tables (merged with config)
        options: Generation options for each table
        sort_by: How to sort tables ('name' supported)

    Returns:
        Markdown documentation for all filtered tables
    """
    logger.info("Generating documentation for multiple tables")
    logger.debug(f"Sort by: {sort_by}")

    filtered_tables = context.get_filtered_tables(include_tables, exclude_tables)

    if not filtered_tables:
        logger.warning("No tables match the filter criteria")
        return "<!-- No tables to document -->"

    if sort_by == "name":
        filtered_tables.sort(key=lambda t: t.name)
        logger.debug("Tables sorted by name")

    if options is None:
        options = context.plugin_config.get_generation_options()
        logger.debug("Using default generation options")

    logger.info(f"Generating documentation for {len(filtered_tables)} table(s)")
    output = []
    for idx, table in enumerate(filtered_tables, 1):
        logger.debug(f"Processing table {idx}/{len(filtered_tables)}: '{table.name}'")
        try:
            table_doc = generate_table(context, table.name, options)
            output.append(table_doc)
        except Exception as e:  # pragma: no cover
            logger.error(
                f"Failed to generate documentation for table '{table.name}': {e}",
                exc_info=True,
            )
            output.append(
                f"<!-- Error generating documentation for table '{table.name}': {e} -->"
            )

    result = "\n\n".join(output)
    logger.info(
        f"Successfully generated documentation for {len(output)} table(s) ({len(result)} characters)"
    )
    return result


def generate_content_from_params(
    context: SqlAlchemyPluginContext, params: dict[str, str | bool]
) -> str:
    """Generate markdown content based on tag parameters.

    Tag parameters override plugin-level configuration.

    Args:
        context: Plugin context with base config
        params: Parameters from the tag

    Returns:
        Generated markdown content
    """
    logger.debug(f"Generating content from parameters: {params}")

    # Get base generation options from config
    base_options = context.plugin_config.get_generation_options()

    # Merge with tag parameters (tag takes precedence)
    options = base_options.merge_with_tag_params(params)
    logger.debug(f"Merged generation options: {options}")

    # Handle specific table
    if "table" in params:
        table_name = str(params["table"])
        logger.info(f"Generating documentation for single table: '{table_name}'")
        return generate_table(context, table_name, options)

    # Handle multiple tables with filtering
    include_tables = parse_table_list(str(params.get("include_tables", "")))
    exclude_tables = parse_table_list(str(params.get("exclude_tables", "")))
    sort_by = str(params.get("sort_by", "name"))

    if include_tables:
        logger.debug(f"Tag-level include_tables: {include_tables}")
    if exclude_tables:
        logger.debug(f"Tag-level exclude_tables: {exclude_tables}")

    return generate_tables(
        context,
        include_tables=include_tables,
        exclude_tables=exclude_tables,
        options=options,
        sort_by=sort_by,
    )
