from typing import TYPE_CHECKING
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config import base, config_options as c
import importlib
import sys
from pathlib import Path
from mkdocs_sqlalchemy_plugin.markdown import generate_content_from_params
from mkdocs_sqlalchemy_plugin.markdown import SqlAlchemyPluginContext
from mkdocs_sqlalchemy_plugin.utils import parse_tag_parameters, match_tag_regex

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page
    from mkdocs_sqlalchemy_plugin.markdown import FIELD

logger = get_plugin_logger(__name__)

_DEFAULT_TICK = "✔️"
_DEFAULT_CROSS = "❌"
_DEFAULT_FIELDS: list[FIELD] = [
    "column",
    "type",
    "nullable",
    "default",
    "primary_key",
    "unique",
    "foreign_key",
]


class TableStyleConfig(base.Config):
    tick = c.Type(str, default=_DEFAULT_TICK)
    cross = c.Type(str, default=_DEFAULT_CROSS)
    fields = c.ListOfItems(
        c.Type(str),
        default=_DEFAULT_FIELDS,
    )


class SqlAlchemyPluginConfig(base.Config):
    base_class = c.Type(str)
    app_path = c.Optional(c.Type(str))
    python_path = c.Optional(c.ListOfItems(c.Type(str)))
    table_style = c.Type(TableStyleConfig, default=TableStyleConfig())
    include_tables = c.Optional(c.ListOfItems(c.Type(str)))
    exclude_tables = c.Optional(c.ListOfItems(c.Type(str)))
    group_by_schema = c.Type(bool, default=False)
    show_indexes = c.Type(bool, default=True)
    show_constraints = c.Type(bool, default=True)


class SqlAlchemyPlugin(BasePlugin[SqlAlchemyPluginConfig]):
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Load the SQLAlchemy base class during configuration."""
        if not self.config.base_class:
            logger.warning("No base_class specified in plugin configuration")
            self._context = None
            return config

        # Setup Python paths
        self._setup_python_paths()

        # Load base class and create context
        base_class = self._load_base_class()
        if base_class:
            self._context = self._create_context(base_class)
        else:
            self._context = None

        return config

    def _setup_python_paths(self) -> None:
        """Add configured paths to sys.path."""
        paths_to_add = []

        # Collect python_path entries
        if self.config.python_path:
            for path_str in self.config.python_path:
                path = Path(path_str)
                if not path.exists():
                    logger.warning(f"Python path does not exist: {path}")
                    continue
                if not path.is_dir():
                    logger.warning(f"Python path is not a directory: {path}")
                    continue
                paths_to_add.append(path)

        # Collect app_path
        if self.config.app_path:
            app_path = Path(self.config.app_path)
            if not app_path.exists():
                logger.warning(f"App path does not exist: {app_path}")
            elif not app_path.is_dir():
                logger.warning(f"App path is not a directory: {app_path}")
            else:
                paths_to_add.append(app_path)

        # Add all valid paths to sys.path
        for path in paths_to_add:
            path_str = str(path.resolve())
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                logger.debug(f"Added to Python path: {path_str}")

    def _load_base_class(self):
        """Load the SQLAlchemy base class from the configured module path."""
        try:
            module_path, class_name = self.config.base_class.rsplit(".", 1)
        except ValueError as e:
            logger.error(
                f"Invalid base_class format '{self.config.base_class}'. "
                f"Expected format: 'module.path.ClassName'. Error: {e}"
            )
            return None

        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.error(
                f"Failed to import module '{module_path}': {e}. "
                f"Make sure the module is in your Python path."
            )
            return None

        base_class = getattr(module, class_name, None)
        if not base_class:
            logger.error(
                f"Class '{class_name}' not found in module '{module_path}'. "
                f"Available classes: {[name for name in dir(module) if not name.startswith('_')]}"
            )
            return None

        logger.info(
            f"Successfully loaded SQLAlchemy base class: {self.config.base_class}"
        )
        return base_class

    def _create_context(self, base_class) -> SqlAlchemyPluginContext:
        """Create the plugin context with the loaded base class."""
        return SqlAlchemyPluginContext(
            base_class=base_class,
            plugin_config={
                "base_class": self.config.base_class,
                "app_path": self.config.app_path,
                "python_path": self.config.python_path,
                "table_style": {
                    "tick": self.config.table_style.tick,
                    "cross": self.config.table_style.cross,
                    "fields": self.config.table_style.fields,  # type: ignore
                },
                "include_tables": self.config.include_tables,
                "exclude_tables": self.config.exclude_tables,
                "group_by_schema": self.config.group_by_schema,
                "show_indexes": self.config.show_indexes,
                "show_constraints": self.config.show_constraints,
            },
        )

    def on_page_markdown(
        self, markdown: str, /, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        if self._context is None:
            logger.warning("Plugin context is None, skipping SQLAlchemy tag processing")
            return None

        # Enhanced pattern to match various tag options:
        # {% sqlalchemy %}
        # {% sqlalchemy table="users" %}
        # {% sqlalchemy table="users" fields="column,type,nullable" %}
        # {% sqlalchemy exclude="internal_tables,audit_log" %}
        pattern = r"\{%\s*sqlalchemy(?:\s+([^%]+))?\s*%\}"

        matches = match_tag_regex(markdown, pattern)
        if not matches:
            return None

        logger.info(f"Found {len(matches)} SQLAlchemy tag(s) to process")

        updated_markdown = markdown

        # Process matches in reverse order to avoid index shifting
        for match in reversed(matches):
            tag_params_str = match.group(1)  # Everything after 'sqlalchemy'

            try:
                tag_params = parse_tag_parameters(tag_params_str)
                replacement = generate_content_from_params(self._context, tag_params)
                start, end = match.span()
                updated_markdown = (
                    updated_markdown[:start] + replacement + updated_markdown[end:]
                )

            except Exception as e:
                logger.error(f"Error generating SQLAlchemy documentation: {e}")
                continue

        return updated_markdown
