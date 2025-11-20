---
hide:
  - navigation
---

# MkDocs SQLAlchemy Plugin

[MkDocs](https://www.mkdocs.org/) plugin to generate documentation from SQLAlchemy models.

## Features

- **Automatic Documentation**: Generates tables documenting your SQLAlchemy models.
- **Customizable**: Configure which fields to show, table styling, and more.
- **Filtering**: Include or exclude specific tables.
- **SQL DDL**: Optionally display the SQL `CREATE TABLE` statements.
- **Schema Support**: Group tables by schema.

## Installation

Install the plugin using `pip`:

```bash
pip install mkdocs-sqlalchemy-plugin
```

## Quick Start

1. **Configure `mkdocs.yml`**:

    Add the plugin to your `mkdocs.yml` configuration file. You must specify the `base_class` which is the import path to your SQLAlchemy `DeclarativeBase`.

    ```yaml
    plugins:
      - sqlalchemy:
          base_class: "my_app.models.Base"
          app_path: "src"
    ```

2. **Add to Markdown**:

    In your markdown files, use the `sqlalchemy` tag where you want the documentation to appear.

    ```html
    {% sqlalchemy %}
    ```

3. **Build Docs**:

    Run `mkdocs serve` to see your documentation.

## Configuration

The plugin offers extensive configuration options to tailor the output to your needs. See the [Configuration Options](configuration.md) page for a full reference.

## Usage

The `{% sqlalchemy %}` tag is powerful and supports local overrides. See the [Tag Usage](usage.md) page for details.
