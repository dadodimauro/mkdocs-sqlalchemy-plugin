import importlib
import sys
from pathlib import Path

from mkdocs.config import base
from mkdocs.config import config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from sqlalchemy.orm import DeclarativeBase

from mkdocs_sqlalchemy_plugin.config import (
    DEFAULT_CROSS,
    DEFAULT_FIELDS,
    DEFAULT_TICK,
    TAG_PATTERN,
    DisplayConfig,
    FilterConfig,
)
from mkdocs_sqlalchemy_plugin.config import (
    PluginConfig as DataclassPluginConfig,
)
from mkdocs_sqlalchemy_plugin.config import (
    TableStyleConfig as DataclassTableStyleConfig,
)
from mkdocs_sqlalchemy_plugin.markdown import (
    SqlAlchemyPluginContext,
    generate_content_from_params,
)
from mkdocs_sqlalchemy_plugin.utils import match_tag_regex, parse_tag_parameters

logger = get_plugin_logger(__name__)


class TableStyleConfig(base.Config):
    """MkDocs config schema for table styling."""

    tick = c.Type(str, default=DEFAULT_TICK)
    cross = c.Type(str, default=DEFAULT_CROSS)
    fields = c.ListOfItems(c.Type(str), default=DEFAULT_FIELDS)
    heading_level = c.Type(int, default=3)
    schema_heading_level = c.Type(int, default=2)
    text_align = c.Type(str, default="left")


class FilterConfigSchema(base.Config):
    """MkDocs config schema for filtering."""

    include_tables = c.Optional(c.ListOfItems(c.Type(str)))
    exclude_tables = c.Optional(c.ListOfItems(c.Type(str)))


class DisplayConfigSchema(base.Config):
    """MkDocs config schema for display options."""

    show_indexes = c.Type(bool, default=True)
    show_constraints = c.Type(bool, default=True)
    show_sql = c.Type(bool, default=False)
    group_by_schema = c.Type(bool, default=False)


class SqlAlchemyPluginConfig(base.Config):
    """MkDocs config schema for the SQLAlchemy plugin."""

    base_class = c.Type(str)
    app_path = c.Optional(c.Type(str))
    python_path = c.Optional(c.ListOfItems(c.Type(str)))
    table_style = c.SubConfig(TableStyleConfig)
    filter = c.SubConfig(FilterConfigSchema)
    display = c.SubConfig(DisplayConfigSchema)


class SqlAlchemyPlugin(BasePlugin[SqlAlchemyPluginConfig]):  # pragma: no cover
    """MkDocs plugin for documenting SQLAlchemy models."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Load the SQLAlchemy base class during configuration."""
        logger.info("Initializing SQLAlchemy documentation plugin")

        if not self.config.base_class:
            logger.error(
                "No base_class specified in plugin configuration - plugin will be disabled"
            )
            self._context = None
            return config

        logger.debug(f"Configured base_class: {self.config.base_class}")

        # Setup Python paths
        self._setup_python_paths()

        # Load base class
        base_class = self._load_base_class()
        if not base_class:
            logger.error("Failed to load base class - plugin will be disabled")
            self._context = None
            return config

        # Create dataclass config from MkDocs config
        plugin_config = self._create_dataclass_config()

        # Log configuration summary
        self._log_config_summary(plugin_config)

        # Create context
        self._context = SqlAlchemyPluginContext(
            base_class=base_class,
            plugin_config=plugin_config,
        )

        # Log discovered tables
        self._log_discovered_tables(base_class)

        logger.info("SQLAlchemy plugin initialization completed successfully")
        return config

    def _log_config_summary(self, config: DataclassPluginConfig) -> None:
        """Log a summary of the plugin configuration."""
        logger.debug("Plugin configuration:")
        logger.debug(f"  - Table style fields: {config.table_style.fields}")
        logger.debug(f"  - Show indexes: {config.display.show_indexes}")
        logger.debug(f"  - Show constraints: {config.display.show_constraints}")
        logger.debug(f"  - Show SQL: {config.display.show_sql}")
        logger.debug(f"  - Group by schema: {config.display.group_by_schema}")

        if config.filter.include_tables:
            logger.debug(f"  - Include tables: {config.filter.include_tables}")
        if config.filter.exclude_tables:
            logger.debug(f"  - Exclude tables: {config.filter.exclude_tables}")

    def _log_discovered_tables(self, base_class: type[DeclarativeBase]) -> None:
        """Log information about discovered tables."""
        tables = base_class.metadata.sorted_tables
        table_names = [t.name for t in tables]

        logger.info(
            f"Discovered {len(tables)} table(s) in metadata: {', '.join(table_names)}"
        )

        for table in tables:
            logger.debug(
                f"  Table '{table.name}': {len(table.columns)} column(s), "
                f"{len(table.indexes)} index(es), {len(table.constraints)} constraint(s)"
            )

    def _create_dataclass_config(self) -> DataclassPluginConfig:
        """Convert MkDocs config to dataclass config."""
        logger.debug("Converting MkDocs config to dataclass config")

        return DataclassPluginConfig(
            base_class=self.config.base_class,
            app_path=self.config.app_path,
            python_path=self.config.python_path,
            table_style=DataclassTableStyleConfig(
                tick=self.config.table_style.tick,
                cross=self.config.table_style.cross,
                fields=list(self.config.table_style.fields),
                heading_level=self.config.table_style.heading_level,
                schema_heading_level=self.config.table_style.schema_heading_level,
                text_align=self.config.table_style.text_align,
            ),
            filter=FilterConfig(
                include_tables=self.config.filter.include_tables,
                exclude_tables=self.config.filter.exclude_tables,
            ),
            display=DisplayConfig(
                show_indexes=self.config.display.show_indexes,
                show_constraints=self.config.display.show_constraints,
                show_sql=self.config.display.show_sql,
                group_by_schema=self.config.display.group_by_schema,
            ),
        )

    def _setup_python_paths(self) -> None:
        """Add configured paths to sys.path."""
        logger.debug("Setting up Python paths")
        paths_to_add = []

        # Collect python_path entries
        if self.config.python_path:
            logger.debug(
                f"Processing {len(self.config.python_path)} configured Python path(s)"
            )
            for path_str in self.config.python_path:
                path = Path(path_str)
                if not path.exists():
                    logger.warning(f"Python path does not exist: {path}")
                    continue
                if not path.is_dir():
                    logger.warning(f"Python path is not a directory: {path}")
                    continue
                paths_to_add.append(path)
                logger.debug(f"  Valid Python path: {path}")

        # Collect app_path
        if self.config.app_path:
            logger.debug(f"Processing configured app_path: {self.config.app_path}")
            app_path = Path(self.config.app_path)
            if not app_path.exists():
                logger.warning(f"App path does not exist: {app_path}")
            elif not app_path.is_dir():
                logger.warning(f"App path is not a directory: {app_path}")
            else:
                paths_to_add.append(app_path)
                logger.debug(f"  Valid app path: {app_path}")

        # Add all valid paths to sys.path
        added_count = 0
        for path in paths_to_add:
            path_str = str(path.resolve())
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                logger.debug(f"Added to sys.path: {path_str}")
                added_count += 1
            else:
                logger.debug(f"Path already in sys.path: {path_str}")

        if added_count > 0:
            logger.info(f"Added {added_count} path(s) to Python path")
        else:
            logger.debug("No new paths added to sys.path")

    def _load_base_class(self) -> type[DeclarativeBase] | None:
        """Load the SQLAlchemy base class from the configured module path."""
        logger.info(f"Loading SQLAlchemy base class: {self.config.base_class}")

        try:
            module_path, class_name = self.config.base_class.rsplit(".", 1)
            logger.debug(
                f"Parsed module path: '{module_path}', class name: '{class_name}'"
            )
        except ValueError as e:
            logger.error(
                f"Invalid base_class format '{self.config.base_class}'. "
                f"Expected format: 'module.path.ClassName'. Error: {e}"
            )
            return None

        try:
            logger.debug(f"Importing module: {module_path}")
            module = importlib.import_module(module_path)
            logger.debug(f"Successfully imported module: {module_path}")
        except Exception as e:
            logger.error(
                f"Failed to import module '{module_path}'. "
                f"The module may contain syntax errors or missing dependencies.\n"
                f"Error details: {type(e).__name__}: {e}"
            )
            return None

        logger.debug(f"Looking for class '{class_name}' in module '{module_path}'")
        base_class = getattr(module, class_name, None)

        if not base_class:
            available = [name for name in dir(module) if not name.startswith("_")]
            logger.error(
                f"Class '{class_name}' not found in module '{module_path}'. "
                f"Available classes: {available}"
            )
            return None

        if not isinstance(base_class, type):
            logger.error(
                f"'{class_name}' in module '{module_path}' is not a class "
                f"(type: {type(base_class).__name__})."
            )
            return None

        if not issubclass(base_class, DeclarativeBase):
            logger.error(
                f"Class '{class_name}' in module '{module_path}' is not a "
                f"subclass of DeclarativeBase. Base classes: {base_class.__bases__}"
            )
            return None

        logger.info(
            f"Successfully loaded SQLAlchemy base class: {self.config.base_class}"
        )
        return base_class

    def on_page_markdown(
        self, markdown: str, /, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        """Process SQLAlchemy tags in markdown content."""
        if self._context is None:
            logger.debug(
                f"Skipping page '{page.file.src_path}' - plugin context is None"
            )
            return None

        logger.debug(f"Processing page: {page.file.src_path}")
        matches = match_tag_regex(markdown, TAG_PATTERN)

        if not matches:
            logger.debug(f"No SQLAlchemy tags found in page: {page.file.src_path}")
            return None

        logger.info(
            f"Found {len(matches)} SQLAlchemy tag(s) in page: {page.file.src_path}"
        )

        updated_markdown = markdown
        success_count = 0
        error_count = 0

        # Process matches in reverse order to avoid index shifting
        for idx, match in enumerate(reversed(matches), 1):
            tag_params_str = match.group(1)
            logger.debug(f"Processing tag {idx}/{len(matches)}: {tag_params_str}")

            try:
                tag_params = parse_tag_parameters(tag_params_str)
                logger.debug(f"  Parsed parameters: {tag_params}")

                replacement = generate_content_from_params(self._context, tag_params)
                start, end = match.span()
                updated_markdown = (
                    updated_markdown[:start] + replacement + updated_markdown[end:]
                )
                success_count += 1
                logger.debug(f"  Successfully generated documentation for tag {idx}")

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error processing tag {idx}/{len(matches)} with parameters '{tag_params_str}': {e}",
                    exc_info=True,
                )
                # Add error comment in place of tag
                error_comment = (
                    f"<!-- Error generating SQLAlchemy documentation: {e} -->"
                )
                start, end = match.span()
                updated_markdown = (
                    updated_markdown[:start] + error_comment + updated_markdown[end:]
                )
                continue

        if success_count > 0:
            logger.info(
                f"Successfully processed {success_count}/{len(matches)} tag(s) in page: {page.file.src_path}"
            )
        if error_count > 0:
            logger.warning(
                f"Failed to process {error_count}/{len(matches)} tag(s) in page: {page.file.src_path}"
            )

        return updated_markdown
