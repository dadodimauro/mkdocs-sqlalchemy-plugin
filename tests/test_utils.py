import re

import pytest

from mkdocs_sqlalchemy_plugin.config import TAG_PATTERN
from mkdocs_sqlalchemy_plugin.utils import (
    FIELD_NAMES,
    match_tag_regex,
    parse_fields,
    parse_table_list,
    parse_tag_parameters,
)


class TestMatchTagRegex:
    """Tests for match_tag_regex function."""

    @pytest.mark.parametrize(
        "markdown,expected_matches,expected_count",
        [
            (
                'Some text {% sqlalchemy table="users" %} more text',
                ['{% sqlalchemy table="users" %}'],
                1,
            ),
            ("No tags here", [], 0),
            (
                '{% sqlalchemy %} and {% sqlalchemy table="orders" %}',
                ["{% sqlalchemy %}", '{% sqlalchemy table="orders" %}'],
                2,
            ),
            ("{% sqlalchemy %}", ["{% sqlalchemy %}"], 1),
            (
                '{% sqlalchemy table="users" fields="column,type" show_indexes=true %}',
                [
                    '{% sqlalchemy table="users" fields="column,type" show_indexes=true %}'
                ],
                1,
            ),
            ("{%sqlalchemy%}", ["{%sqlalchemy%}"], 1),
            ("{%  sqlalchemy  %}", ["{%  sqlalchemy  %}"], 1),
            (
                '{% sqlalchemy table="users" %} {% sqlalchemy table="products" %}',
                ['{% sqlalchemy table="users" %}', '{% sqlalchemy table="products" %}'],
                2,
            ),
            (
                "{% sqlalchemy show_indexes=false show_constraints=true %}",
                ["{% sqlalchemy show_indexes=false show_constraints=true %}"],
                1,
            ),
            ("{% sqlalchemy table=users %}", ["{% sqlalchemy table=users %}"], 1),
            ("{ sqlalchemy }", [], 0),
            ("{sqlalchemy}", [], 0),
        ],
        ids=[
            "single_tag_with_params",
            "no_tags",
            "multiple_tags",
            "tag_without_params",
            "tag_with_multiple_params",
            "tag_with_whitespace_variations_1",
            "tag_with_whitespace_variations_2",
            "multiple_tags_same_line",
            "tag_with_boolean_params",
            "tag_without_quotes",
            "missing_percent_signs",
            "missing_percent_and_spaces",
        ],
    )
    def test_match_tag_regex(
        self, markdown: str, expected_matches: list[str], expected_count: int
    ):
        """Test matching SQLAlchemy tags in markdown."""
        result = match_tag_regex(markdown, TAG_PATTERN)

        assert len(result) == expected_count, (
            f"Expected {expected_count} matches, got {len(result)}"
        )

        if expected_count > 0:
            matched_strings = [match.group(0) for match in result]
            assert matched_strings == expected_matches, (
                f"Expected matches {expected_matches}, got {matched_strings}"
            )

    def test_match_tag_regex_returns_match_objects(self):
        """Test that match_tag_regex returns proper Match objects."""
        markdown = '{% sqlalchemy table="users" %}'
        result = match_tag_regex(markdown, TAG_PATTERN)

        assert len(result) == 1
        assert isinstance(result[0], re.Match)
        assert result[0].group(0) == '{% sqlalchemy table="users" %}'
        assert result[0].group(1) == 'table="users"'  # Captured group

    def test_match_tag_regex_with_multiline(self):
        """Test matching tags across multiple lines."""
        markdown = """
        # Title
        
        {% sqlalchemy %}
        
        Some content
        
        {% sqlalchemy table="products" %}
        """
        result = match_tag_regex(markdown, TAG_PATTERN)

        assert len(result) == 2


class TestParseFields:
    """Tests for parse_fields function."""

    @pytest.mark.parametrize(
        "fields_str,expected",
        [
            ("column", ["column"]),
            ("column,type,nullable", ["column", "type", "nullable"]),
            ("column, type, nullable", ["column", "type", "nullable"]),
            (
                "column,type,nullable,default,primary_key,unique,foreign_key",
                [
                    "column",
                    "type",
                    "nullable",
                    "default",
                    "primary_key",
                    "unique",
                    "foreign_key",
                ],
            ),
            ("", None),
            (None, None),
            ("column,invalid,type", ["column", "type"]),
            ("invalid,bad,wrong", []),
            ("  column  ,  type  ", ["column", "type"]),
        ],
        ids=[
            "single_field",
            "multiple_fields",
            "fields_with_spaces",
            "all_valid_fields",
            "empty_string",
            "none_input",
            "mixed_valid_invalid_fields",
            "only_invalid_fields",
            "fields_with_extra_whitespace",
        ],
    )
    def test_parse_fields(self, fields_str: str | None, expected: list[str] | None):
        """Test parsing comma-separated field strings."""
        result = parse_fields(fields_str)

        if expected is None:
            assert result is None
        else:
            assert result == expected

    def test_parse_fields_returns_valid_field_types(self):
        """Test that parse_fields only returns valid FIELD types."""
        result = parse_fields("column,type,invalid_field,nullable")

        assert result is not None
        for field in result:
            assert field in FIELD_NAMES


class TestParseTableList:
    """Tests for parse_table_list function."""

    @pytest.mark.parametrize(
        "tables_str,expected",
        [
            ("users", ["users"]),
            ("users,products,orders", ["users", "products", "orders"]),
            ("users, products, orders", ["users", "products", "orders"]),
            ("", None),
            (None, None),
            ("user_profiles,order_items", ["user_profiles", "order_items"]),
            ("  users  ,  products  ", ["users", "products"]),
            ("  users  ", ["users"]),
        ],
        ids=[
            "single_table",
            "multiple_tables",
            "tables_with_spaces",
            "empty_string",
            "none_input",
            "tables_with_underscores",
            "tables_with_extra_whitespace",
            "single_table_with_whitespace",
        ],
    )
    def test_parse_table_list(self, tables_str: str | None, expected: list[str] | None):
        """Test parsing comma-separated table name strings."""
        result = parse_table_list(tables_str)

        if expected is None:
            assert result is None
        else:
            assert result == expected


class TestParseTagParameters:
    """Tests for parse_tag_parameters function."""

    @pytest.mark.parametrize(
        "params_str,expected",
        [
            ('table="users"', {"table": "users"}),
            (
                'table="users" fields="column,type"',
                {"table": "users", "fields": "column,type"},
            ),
            (
                "show_indexes=true show_constraints=false",
                {"show_indexes": True, "show_constraints": False},
            ),
            (
                'table="users" show_indexes=true fields="column,type" show_constraints=false',
                {
                    "table": "users",
                    "show_indexes": True,
                    "fields": "column,type",
                    "show_constraints": False,
                },
            ),
            ("", {}),
            (None, {}),
            ('table="user profiles"', {"table": "user profiles"}),
            ('table=""', {"table": ""}),
            ('include_tables="users,products"', {"include_tables": "users,products"}),
            ('table="users"  fields="column"', {"table": "users", "fields": "column"}),
        ],
        ids=[
            "single_string_parameter",
            "multiple_string_parameters",
            "boolean_parameters",
            "mixed_parameters",
            "empty_string",
            "none_input",
            "parameter_with_spaces_in_value",
            "empty_string_value",
            "parameters_with_underscores",
            "multiple_spaces_between_parameters",
        ],
    )
    def test_parse_tag_parameters(
        self, params_str: str | None, expected: dict[str, str | bool]
    ):
        """Test parsing tag parameter strings."""
        result = parse_tag_parameters(params_str)
        assert result == expected

    def test_parse_tag_parameters_ignores_invalid_syntax(self):
        """Test that invalid parameter syntax is ignored."""
        # Missing quotes - should be ignored
        result = parse_tag_parameters('table=users fields="column"')
        assert result == {"fields": "column"}
        assert "table" not in result

        # Invalid boolean - should be ignored
        result = parse_tag_parameters("show_indexes=yes")
        assert result == {}

    def test_parse_tag_parameters_requires_quotes_for_strings(self):
        """Test that string parameters require quotes."""
        # Without quotes - should be ignored
        result = parse_tag_parameters("table=users")
        assert "table" not in result
        assert result == {}

        # With quotes - should work
        result = parse_tag_parameters('table="users"')
        assert result == {"table": "users"}

    def test_parse_tag_parameters_handles_complex_values(self):
        """Test parsing parameters with complex values."""
        params_str = (
            'fields="column,type,nullable,default" exclude="migrations,alembic"'
        )
        result = parse_tag_parameters(params_str)

        assert result == {
            "fields": "column,type,nullable,default",
            "exclude": "migrations,alembic",
        }

    def test_parse_tag_parameters_case_sensitivity(self):
        """Test that boolean values are case-sensitive."""
        # Should match (lowercase)
        result = parse_tag_parameters("show_indexes=true")
        assert result == {"show_indexes": True}

        # Should not match (capital T)
        result = parse_tag_parameters("show_indexes=True")
        assert result == {}


class TestUtilsIntegration:
    """Integration tests combining multiple utility functions."""

    def test_full_tag_parsing_workflow(self):
        """Test the complete workflow of parsing a tag."""
        # Simulate a markdown document with a tag
        markdown = 'Text before {% sqlalchemy table="users" fields="column,type" show_indexes=true %} text after'

        # Step 1: Find the tag
        matches = match_tag_regex(markdown, TAG_PATTERN)
        assert len(matches) == 1

        # Step 2: Extract parameters
        params_str = matches[0].group(1)
        params = parse_tag_parameters(params_str)

        # Step 3: Parse individual parameter values
        assert params["table"] == "users"
        assert params["show_indexes"] is True

        fields = parse_fields(params["fields"])  # type: ignore
        assert fields == ["column", "type"]

    def test_multiple_tags_workflow(self):
        """Test parsing multiple tags in one document."""
        markdown = """
        # Database
        
        {% sqlalchemy table="users" %}
        
        {% sqlalchemy table="products" fields="column,type,foreign_key" %}
        
        {% sqlalchemy exclude="migrations,test_tables" %}
        """

        matches = match_tag_regex(markdown, TAG_PATTERN)
        assert len(matches) == 3

        # Parse each tag
        all_params = [parse_tag_parameters(match.group(1)) for match in matches]

        assert all_params[0] == {"table": "users"}
        assert all_params[1] == {
            "table": "products",
            "fields": "column,type,foreign_key",
        }
        assert all_params[2] == {"exclude": "migrations,test_tables"}

    def test_malformed_parameters_are_rejected(self):
        """Test that malformed parameters are properly rejected."""
        # Tag matches but parameters without quotes are rejected
        markdown = "{% sqlalchemy table=users %}"

        matches = match_tag_regex(markdown, TAG_PATTERN)
        assert len(matches) == 1  # Tag structure is valid

        params = parse_tag_parameters(matches[0].group(1))
        assert params == {}  # But parameters are rejected
