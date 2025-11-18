from sqlalchemy import Column, Index, Integer, MetaData, String, Table

from mkdocs_sqlalchemy_plugin.config import (
    DEFAULT_CROSS,
    DEFAULT_FIELDS,
    DEFAULT_TICK,
    FilterConfig,
    PluginConfig,
)
from mkdocs_sqlalchemy_plugin.markdown import (
    SqlAlchemyPluginContext,
    _format_default_value,
    _generate_column_values,
    _generate_constraints_section,
    _generate_indexes_section,
    generate_content_from_params,
    generate_table,
    generate_tables,
)

from .fixtures.models import Base, User


class TestSqlAlchemyPluginContext:
    """Tests for SqlAlchemyPluginContext dataclass."""

    def test_get_filtered_tables(self):
        """Test filtering tables with no filters."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        filtered_tables = context.get_filtered_tables()

        table_names = [table.name for table in filtered_tables]
        assert ["users", "posts", "user_profiles"] == table_names

    def test_get_filtered_tables_with_include(self):
        """Test filtering tables with include list."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        filtered_tables = context.get_filtered_tables(include_tables=["users", "posts"])

        table_names = [table.name for table in filtered_tables]
        assert ["users", "posts"] == table_names

    def test_get_filtered_tables_with_exclude(self):
        """Test filtering tables with exclude list."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        filtered_tables = context.get_filtered_tables(exclude_tables=["user_profiles"])

        table_names = [table.name for table in filtered_tables]
        assert ["users", "posts"] == table_names

    def test_get_filtered_tables_merge(self):
        """Test filtering tables with base exclude and tag include/exclude."""

        plugin_config = PluginConfig(
            base_class="Base", filter=FilterConfig(exclude_tables=["posts"])
        )

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        filtered_tables = context.get_filtered_tables(
            include_tables=None, exclude_tables=["user_profiles"]
        )

        table_names = [table.name for table in filtered_tables]
        assert ["users"] == table_names


class TestGenerateTable:
    """Tests for generate_table function."""

    def test_generate_table_basic(self):
        """Test basic table generation."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        tables_markdown = generate_table(context=context, tablename="users")

        assert "## Table: ``users``" in tables_markdown
        assert "## Table: ``posts``" not in tables_markdown

    def test_generate_table_nonexistent(self):
        """Test generating a table that does not exist."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        tables_markdown = generate_table(context=context, tablename="nonexistent")

        assert "Table 'nonexistent' not found" in tables_markdown


class TestGenerateColumnValues:
    """Tests for _generate_column_values function."""

    def test_generate_column_values(self):
        """Test generating column values for a table."""
        columns_markdown = _generate_column_values(
            column=User.username,
            fields=DEFAULT_FIELDS,
            tick=DEFAULT_TICK,
            cross=DEFAULT_CROSS,
        )

        assert [
            "``username``",
            "VARCHAR(50)",
            DEFAULT_CROSS,
            "",
            DEFAULT_CROSS,
            DEFAULT_TICK,
            "",
        ] == columns_markdown

    def test_generate_column_values_subset(self):
        """Test generating column values with a subset of fields."""
        columns_markdown = _generate_column_values(
            column=User.username,
            fields=["column", "type", "nullable"],
            tick=DEFAULT_TICK,
            cross=DEFAULT_CROSS,
        )

        assert [
            "``username``",
            "VARCHAR(50)",
            DEFAULT_CROSS,
        ] == columns_markdown


class TestFormatDefaultValue:
    """Tests for _format_default_value function."""

    def test_format_default_value_none(self):
        """Test formatting None default value."""
        assert _format_default_value(None) == ""

    def test_format_default_value_string(self):
        """Test formatting string default value."""
        assert _format_default_value("default") == "default"  # type: ignore

    def test_format_default_value_number(self):
        """Test formatting numeric default value."""
        assert _format_default_value(42) == "42"  # type: ignore

    def test_format_default_value_boolean(self):
        """Test formatting boolean default value."""
        assert _format_default_value(True) == "True"  # type: ignore
        assert _format_default_value(False) == "False"  # type: ignore


class TestGenerateIndexesSection:
    """Tests for _generate_indexes_section function."""

    def test_generate_indexes_section_with_indexes(self):
        """Test generating indexes section for a table with indexes."""

        metadata = MetaData()
        test_table = Table(
            "test_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String),
        )
        Index("ix_name", test_table.c.name)

        indexes_markdown = _generate_indexes_section(test_table)

        assert "Indexes:" in indexes_markdown
        assert "- ``ix_name``: ``name``" in indexes_markdown

    def test_generate_indexes_section_no_indexes(self):
        """Test generating indexes section for a table with no indexes."""

        metadata = MetaData()
        test_table = Table(
            "test_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String),
        )

        indexes_markdown = _generate_indexes_section(test_table)

        assert "**Indexes:** None" in indexes_markdown


class TestGenerateConstraintsSection:
    """Tests for _generate_constraints_section function."""

    def test_generate_constraints_section_with_constraints(self):
        """Test generating constraints section for a table with constraints and a naming convention"""

        metadata = MetaData(
            naming_convention={
                "ix": "ix_%(column_0_label)s",
                "uq": "uq_%(table_name)s_%(column_0_name)s",
                "ck": "ck_%(table_name)s_%(constraint_name)s",
                "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
                "pk": "pk_%(table_name)s",
            }
        )
        test_table = Table(
            "test_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True),
        )

        constraints_markdown = _generate_constraints_section(test_table)

        assert "Constraints:" in constraints_markdown
        assert "- ``uq_test_table_name`` (UniqueConstraint)" in constraints_markdown
        assert "- ``pk_test_table`` (PrimaryKeyConstraint)" in constraints_markdown
        assert "Unknown" not in constraints_markdown

    def test_generate_constraints_no_naming_convention(self):
        """Test generating constraints section for a table with no naming convention."""

        metadata = MetaData()
        test_table = Table(
            "test_table",
            metadata,
            Column("id", Integer),
            Column("name", String),
        )

        constraints_markdown = _generate_constraints_section(test_table)

        assert "Unknown" in constraints_markdown

    def test_generate_constraints_section_no_constraints(self):
        """Test generating constraints section for a table with no constraints."""

        metadata = MetaData()
        test_table = Table(
            "test_table",
            metadata,
            Column("id", Integer),
            Column("name", String),
        )
        test_table.constraints.clear()

        constraints_markdown = _generate_constraints_section(test_table)

        assert "**Constraints:** None" in constraints_markdown


class TestGenerateTables:
    """Tests for generate_tables function."""

    def test_generate_tables(self):
        """Test generating markdown for all tables."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        tables_markdown = generate_tables(context=context)

        assert "## Table: ``users``" in tables_markdown
        assert "## Table: ``posts``" in tables_markdown
        assert "## Table: ``user_profiles``" in tables_markdown

    def test_generate_tables_all_unfiltered(self):
        """Test generating markdown for all tables with filters that exclude all."""

        plugin_config = PluginConfig(
            base_class="Base",
            filter=FilterConfig(exclude_tables=["users", "posts", "user_profiles"]),
        )

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        tables_markdown = generate_tables(context=context)

        assert "<!-- No tables to document -->" in tables_markdown


class TestGenerateContentFromParams:
    """Tests for generate_content_from_params function."""

    def test_generate_content_from_params(self):
        """Test generating content from tag parameters."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        params = {
            "include_tables": "users,posts",
            "exclude_tables": "user_profiles",
            "fields": "column,type,nullable",
            "show_indexes": True,
            "show_constraints": False,
        }

        content_markdown = generate_content_from_params(
            context=context,
            params=params,
        )

        assert "## Table: ``users``" in content_markdown
        assert "## Table: ``posts``" in content_markdown
        assert "## Table: ``user_profiles``" not in content_markdown
        assert "|column|type|nullable|" in content_markdown
        assert "Constraints:" not in content_markdown

    def test_generate_content_from_params_single_table(self):
        """Test generating content for a single table from tag parameters."""

        plugin_config = PluginConfig(base_class="Base")

        context = SqlAlchemyPluginContext(
            base_class=Base,
            plugin_config=plugin_config,
        )

        params = {
            "table": "users",
            "fields": "column,type,default",
            "show_indexes": False,
            "show_constraints": True,
        }

        content_markdown = generate_content_from_params(
            context=context,
            params=params,
        )

        assert "## Table: ``users``" in content_markdown
        assert "|column|type|default|" in content_markdown
        assert "Indexes:" not in content_markdown
        assert "Constraints:" in content_markdown
