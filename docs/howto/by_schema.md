# Group by Schema

This recipe demonstrates how to group tables by their database schema. This is useful for databases like PostgreSQL that use schemas to organize tables.

## Configuration

In your `mkdocs.yml`:

```yaml
plugins:
  - sqlalchemy:
      base_class: "by_schema.models.Base"
      app_path: "src"
      display:
        group_by_schema: true
```

## Usage

In your markdown file:

```markdown
# MkDocs SqlAlchemy Plugin

{% sqlalchemy %}
```

The output will be grouped by schema, with a heading for each schema.
