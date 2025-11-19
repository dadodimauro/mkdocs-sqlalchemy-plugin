from mkdocs_sqlalchemy_plugin.config import (
    DisplayConfig,
    FilterConfig,
    PluginConfig,
    TableGenerationOptions,
    TableStyleConfig,
)


class TestTableGenerationOptions:
    """Tests for TableGenerationOptions dataclass."""

    def test_from_style_and_display(self):
        """Test creating options from style and display configs."""
        style = TableStyleConfig(
            tick="✓", cross="✗", fields=["name", "type", "nullable"]
        )
        display = DisplayConfig(show_indexes=False, show_constraints=True)

        options = TableGenerationOptions.from_style_and_display(style, display)

        assert options.fields == ["name", "type", "nullable"]
        assert options.show_indexes is False
        assert options.show_constraints is True

    def test_merge_with_tag_params(self):
        """Test merging options with tag parameters."""
        initial_options = TableGenerationOptions(
            fields=["column", "type"], show_indexes=True, show_constraints=False
        )

        tag_params = {
            "fields": "column,type,nullable",
            "show_indexes": False,
            "heading_level": 3,
            "text_align": "center",
        }

        merged_options = initial_options.merge_with_tag_params(tag_params)

        assert merged_options.fields == ["column", "type", "nullable"]
        assert merged_options.show_indexes is False
        assert merged_options.show_constraints is False  # unchanged
        assert merged_options.heading_level.value == 3
        assert merged_options.text_align == "center"

    def test_merge_with_tag_params_error_heading_level(self):
        """Test merging options with invalid heading level in tag parameters."""
        initial_options = TableGenerationOptions(
            fields=["column", "type"], show_indexes=True, show_constraints=False
        )

        tag_params: dict[str, int | str | bool] = {"heading_level": 0}

        merged_options = initial_options.merge_with_tag_params(tag_params)

        assert merged_options.heading_level == initial_options.heading_level

    def test_merge_with_tag_params_error_text_align(self):
        """Test merging options with invalid text alignment in tag parameters."""
        initial_options = TableGenerationOptions(
            fields=["column", "type"], show_indexes=True, show_constraints=False
        )

        tag_params: dict[str, int | str | bool] = {"text_align": "invalid"}

        merged_options = initial_options.merge_with_tag_params(tag_params)

        assert merged_options.heading_level == initial_options.heading_level


class TestPluginConfig:
    """Tests for PluginConfig dataclass."""

    def test_get_generation_options(self):
        """Test getting default table generation options from plugin config."""
        plugin_config = PluginConfig(
            base_class="Base",
            table_style=TableStyleConfig(
                tick="✓", cross="✗", fields=["column", "type", "default"]
            ),
            display=DisplayConfig(show_indexes=True, show_constraints=False),
        )

        options = plugin_config.get_generation_options()

        assert options.fields == ["column", "type", "default"]
        assert options.show_indexes is True
        assert options.show_constraints is False

    def test_should_include_table(self):
        """Test table inclusion/exclusion logic."""
        plugin_config = PluginConfig(
            base_class="Base",
            filter=FilterConfig(
                include_tables=["users", "orders"], exclude_tables=["logs"]
            ),
        )

        assert plugin_config.should_include_table("users") is True
        assert plugin_config.should_include_table("products") is False
        assert plugin_config.should_include_table("logs") is False
