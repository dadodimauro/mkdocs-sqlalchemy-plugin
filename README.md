# mkdocs-sqlalchemy-plugin

[![tests](https://github.com/dadodimauro/mkdocs-sqlalchemy-plugin/actions/workflows/test.yml/badge.svg)](https://github.com/dadodimauro/mkdocs-sqlalchemy-plugin/actions/workflows/test.yml) [![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)]() [![codecov](https://codecov.io/github/dadodimauro/mkdocs-sqlalchemy-plugin/graph/badge.svg?token=OZFLQ0U2B6)](https://codecov.io/github/dadodimauro/mkdocs-sqlalchemy-plugin) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-sqlalchemy-plugin) ![PyPI](https://img.shields.io/pypi/v/mkdocs-sqlalchemy-plugin) ![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-sqlalchemy-plugin)


[MkDocs](https://www.mkdocs.org/) plugin to generate docs from SQLAlchemy models.

## Installation

Install the plugin using `pip`:

```bash
pip install mkdocs-sqlalchemy-plugin
```

Next, configure the plugin in your `mkdocs.yml` file:

```yml
plugins:
  - sqlalchemy:
      base_class: "my_app.models.Base"
      app_path: "src"
```

- `base_class`: The Python import path to your SQLAlchemy `DeclarativeBase` class (e.g., `my_app.models.Base`). This class contains the `metadata` object with your table definitions.
- `app_path`: The directory containing your application code (e.g., `src` or `.`). This path is added to Python's `sys.path` to allow the plugin to import your `base_class`.

## Usage

Now in your markdown file you can use the `sqlalchemy` tag to generate documentation.

### Basic Usage

Generate documentation for all tables found in the metadata:

```html
{% sqlalchemy %}
```

### Advanced Usage

For more advanced usage please refer to the documentation of this [project]().