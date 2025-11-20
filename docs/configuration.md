---
hide:
  - navigation
---

# Configuration Options

This page details all available configuration options for the `mkdocs-sqlalchemy-plugin`. These options are set in your `mkdocs.yml` file under the `plugins` section.

## Global Configuration

### `base_class`

- **Type**: `str`
- **Required**: Yes
- **Description**: The Python import path to your SQLAlchemy `DeclarativeBase` class. This class contains the `metadata` object with your table definitions.
- **Example**: `my_app.models.Base`

### `app_path`

- **Type**: `str`
- **Required**: No
- **Default**: `None`
- **Description**: The directory containing your application code. This path is added to Python's `sys.path` to allow the plugin to import your `base_class`.
- **Example**: `src`

### `python_path`

- **Type**: `list[str]`
- **Required**: No
- **Default**: `None`
- **Description**: A list of additional paths to add to Python's `sys.path`. Useful if your models depend on other modules not in the standard path.
- **Example**:

    ```yaml
    python_path:
      - "src"
      - "lib"
    ```

## Table Styling (`table_style`)

These options control the visual appearance of the generated tables.

### `tick`

- **Type**: `str`
- **Default**: `✔️`
- **Description**: The symbol used to represent boolean `True` values (e.g., for "Nullable" or "Primary Key" columns).

### `cross`

- **Type**: `str`
- **Default**: `❌`
- **Description**: The symbol used to represent boolean `False` values.

### `fields`

- **Type**: `list[str]`
- **Default**: `["column", "type", "nullable", "default", "primary_key", "unique", "foreign_key"]`
- **Description**: The list of columns to include in the generated documentation table. You can reorder or remove fields as needed.
- **Available Fields**:
  - `column`: The name of the database column.
  - `type`: The SQLAlchemy type of the column.
  - `nullable`: Whether the column allows NULL values.
  - `default`: The default value of the column.
  - `primary_key`: Whether the column is part of the primary key.
  - `unique`: Whether the column has a unique constraint.
  - `foreign_key`: Whether the column is a foreign key.

### `heading_level`

- **Type**: `int`
- **Default**: `3`
- **Description**: The Markdown heading level (e.g., 3 for `###`) used for table names.

### `schema_heading_level`

- **Type**: `int`
- **Default**: `2`
- **Description**: The Markdown heading level used for schema names when `group_by_schema` is enabled.

### `text_align`

- **Type**: `str`
- **Default**: `left`
- **Description**: The text alignment for table cells. Options are `left`, `center`, or `right`.

## Filtering (`filter`)

These options allow you to control which tables are included in the documentation.

### `include_tables`

- **Type**: `list[str]`
- **Default**: `None` (Include all)
- **Description**: A list of table names to explicitly include. If specified, only these tables will be documented.

### `exclude_tables`

- **Type**: `list[str]`
- **Default**: `None`
- **Description**: A list of table names to exclude from the documentation.

## Display Options (`display`)

These options control additional information displayed alongside the tables.

### `show_indexes`

- **Type**: `bool`
- **Default**: `True`
- **Description**: Whether to list the indexes defined on the table.

### `show_constraints`

- **Type**: `bool`
- **Default**: `True`
- **Description**: Whether to list the constraints (e.g., Unique, Check) defined on the table.

### `show_sql`

- **Type**: `bool`
- **Default**: `False`
- **Description**: Whether to display the SQL `CREATE TABLE` statement for each table.

### `sql_dialect`

- **Type**: `str`
- **Default**: `postgresql`
- **Description**: The SQL dialect to use when generating the SQL DDL (if `show_sql` is enabled).

### `group_by_schema`

- **Type**: `bool`
- **Default**: `False`
- **Description**: Whether to group tables by their database schema.

## Example Configuration

```yaml
plugins:
  - sqlalchemy:
      base_class: "my_app.models.Base"
      app_path: "src"
      table_style:
        tick: "YES"
        cross: "NO"
        fields: ["column", "type", "nullable", "primary_key"]
      filter:
        exclude_tables: ["alembic_version"]
      display:
        show_sql: true
        sql_dialect: "mysql"
```
