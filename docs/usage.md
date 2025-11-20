# Tag Usage

The `mkdocs-sqlalchemy-plugin` uses a special tag to inject documentation into your Markdown files.

## Basic Syntax

The basic tag is:

```html
{% sqlalchemy %}
```

This will generate documentation for all tables found in your SQLAlchemy models, using the global configuration defined in `mkdocs.yml`.

## Overriding Configuration

You can override almost any global configuration option directly within the tag. This allows you to have different documentation styles for different pages or sections.

### Syntax

Parameters are passed as key-value pairs.

- Strings must be quoted: `key="value"`
- Booleans and numbers should not be quoted: `key=true`, `key=1`
- Lists are not directly supported in the tag syntax for all options, but comma-separated strings might work for some (check implementation details if unsure, currently mostly simple types are supported).

### Examples

#### Filter Tables

To document only specific tables:

```html
{% sqlalchemy include_tables="users,posts" %}
```

To exclude specific tables:

```html
{% sqlalchemy exclude_tables="alembic_version" %}
```

#### Customize Display

To show SQL DDL for a specific section:

```html
{% sqlalchemy show_sql=true sql_dialect="mysql" %}
```

To hide indexes and constraints:

```html
{% sqlalchemy show_indexes=false show_constraints=false %}
```

#### Customize Styling

To change the table style for a specific page:

```html
{% sqlalchemy tick="YES" cross="NO" text_align="center" %}
```

## Supported Parameters

The following parameters can be used in the tag:

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `include_tables` | `str` | Comma-separated list of tables to include. |
| `exclude_tables` | `str` | Comma-separated list of tables to exclude. |
| `show_indexes` | `bool` | Show/hide indexes. |
| `show_constraints` | `bool` | Show/hide constraints. |
| `show_sql` | `bool` | Show/hide SQL DDL. |
| `sql_dialect` | `str` | SQL dialect for DDL. |
| `group_by_schema` | `bool` | Group tables by schema. |
| `tick` | `str` | Symbol for true values. |
| `cross` | `str` | Symbol for false values. |
| `heading_level` | `int` | Heading level for table names. |
| `schema_heading_level` | `int` | Heading level for schema names. |
| `text_align` | `str` | Text alignment (`left`, `center`, `right`). |
| `fields` | `str` | Comma-separated list of fields to include (e.g., `column,type,nullable`). |

