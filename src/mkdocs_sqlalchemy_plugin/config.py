"""Configuration models for the SQLAlchemy plugin."""

from dataclasses import dataclass, field
from typing import Literal, cast

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
DEFAULT_TICK = "✔️"
DEFAULT_CROSS = "❌"
DEFAULT_FIELDS: list[str] = [
    "column",
    "type",
    "nullable",
    "default",
    "primary_key",
    "unique",
    "foreign_key",
]
TAG_PATTERN = r"\{%\s*sqlalchemy(?:\s+([^%]+?))?\s*%\}"
"""
Regex pattern for matching SQLAlchemy tags.

Captures everything between {% sqlalchemy and %}.
This pattern enforces that:
- String parameters must have quotes: key="value"
- Boolean parameters must not have quotes: key=true or key=false
- The tag must be properly formatted: {% sqlalchemy ... %}
"""


@dataclass
class TableStyleConfig:
    """
    Configuration for table styling.

    These settings control how tables are rendered in the documentation.
    Can be overridden at tag level.

    Attributes:
        tick (str): Symbol for true/yes values.
        cross (str): Symbol for false/no values.
        fields (list[str]): List of fields to include in the table.
    """

    tick: str = DEFAULT_TICK
    cross: str = DEFAULT_CROSS
    fields: list[str] = field(default_factory=lambda: DEFAULT_FIELDS.copy())


@dataclass
class FilterConfig:
    """
    Configuration for table filtering.

    These settings control which tables are included/excluded.
    Can be overridden at tag level.

    Attributes:
        include_tables (list[str] | None): List of table names to include.
        exclude_tables (list[str] | None): List of table names to exclude.
    """

    include_tables: list[str] | None = None
    exclude_tables: list[str] | None = None


@dataclass
class DisplayConfig:
    """
    Configuration for what to display in documentation.

    These settings control which additional information is shown.
    Can be overridden at tag level.

    Attributes:
        show_indexes (bool): Whether to show indexes.
        show_constraints (bool): Whether to show constraints.
        group_by_schema (bool): Whether to group tables by schema.
    """

    show_indexes: bool = True
    show_constraints: bool = True
    group_by_schema: bool = False


@dataclass
class TableGenerationOptions:
    """
    Options for generating a single table's documentation.

    This combines all settings that can be customized per table.
    Tag-level settings take precedence over plugin-level settings.

    Attributes:
        fields (list[str]): List of fields to include in the table.
        show_indexes (bool): Whether to show indexes.
        show_constraints (bool): Whether to show constraints.

    Methods:
        from_style_and_display: Create options from style and display configs.
        merge_with_tag_params: Create new options by merging with tag parameters.
    """

    fields: list[str] = field(default_factory=lambda: DEFAULT_FIELDS.copy())
    show_indexes: bool = True
    show_constraints: bool = True

    @classmethod
    def from_style_and_display(
        cls, style: TableStyleConfig, display: DisplayConfig
    ) -> "TableGenerationOptions":
        """Create options from style and display configs."""
        return cls(
            fields=style.fields.copy(),
            show_indexes=display.show_indexes,
            show_constraints=display.show_constraints,
        )

    def merge_with_tag_params(
        self, params: dict[str, str | bool]
    ) -> "TableGenerationOptions":
        """
        Create new options by merging with tag parameters.

        Tag parameters take precedence over existing options.
        """
        from mkdocs_sqlalchemy_plugin.utils import parse_fields

        new_fields = self.fields
        if "fields" in params:
            parsed = parse_fields(str(params["fields"]))
            if parsed:
                new_fields = parsed

        return TableGenerationOptions(
            fields=cast(list[str], new_fields),
            show_indexes=bool(params.get("show_indexes", self.show_indexes)),
            show_constraints=bool(
                params.get("show_constraints", self.show_constraints)
            ),
        )


@dataclass
class PluginConfig:
    """
    Main plugin configuration.

    This is the top-level configuration loaded from mkdocs.yml.

    Attributes:
        base_class (str): The SQLAlchemy base class to document
        app_path (str | None): Optional path to the application module.
        python_path (list[str] | None): Optional list of paths to add to sys.path
        table_style (TableStyleConfig): Table styling configuration.
        filter (FilterConfig): Table filtering configuration.
        display (DisplayConfig): Display options configuration.

    Methods:
        get_generation_options: Get default table generation options from this config.
        should_include_table: Check if a table should be included based on filter config.
    """

    base_class: str
    app_path: str | None = None
    python_path: list[str] | None = None

    table_style: TableStyleConfig = field(default_factory=TableStyleConfig)
    filter: FilterConfig = field(default_factory=FilterConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)

    def get_generation_options(self) -> TableGenerationOptions:
        """Get default table generation options from this config."""
        return TableGenerationOptions.from_style_and_display(
            self.table_style, self.display
        )

    def should_include_table(self, tablename: str) -> bool:
        """Check if a table should be included based on filter config."""
        if self.filter.exclude_tables and tablename in self.filter.exclude_tables:
            return False

        if self.filter.include_tables and tablename not in self.filter.include_tables:
            return False

        return True
