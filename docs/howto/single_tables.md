# Document Single Tables

This recipe shows how to document specific tables on different pages or sections, rather than listing all tables at once.

## Configuration

In your `mkdocs.yml`:

```yaml
plugins:
  - sqlalchemy:
      base_class: "single_tables.models.Base"
      app_path: "src"
```

## Usage

You can document individual tables by specifying the `table` parameter in the tag.

**`users.md`**:
```markdown
# User Documentation

{% sqlalchemy table="users" %}
```

**`posts.md`**:
```markdown
# Post Documentation

{% sqlalchemy table="posts" %}
```

## Result
