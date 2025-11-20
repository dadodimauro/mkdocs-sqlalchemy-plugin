# Custom Table Styling

This recipe demonstrates how to customize the visual appearance of the tables, such as changing the symbols for boolean values and text alignment.

## Configuration

In your `mkdocs.yml`:

```yaml
plugins:
  - sqlalchemy:
      base_class: "table_style.models.Base"
      app_path: "src"
      table_style:
        tick: "y"
        cross: "n"
        heading_level: 2
        text_align: left
```

## Usage

In your markdown file:

```markdown
# MkDocs SqlAlchemy Plugin

{% sqlalchemy %}
```

This will render tables with "y" and "n" instead of icons, use level 2 headings for table names, and left-align text.

## Result
