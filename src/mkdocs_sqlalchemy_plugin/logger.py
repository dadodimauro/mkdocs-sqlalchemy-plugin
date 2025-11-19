import logging


class PluginLogFilter(logging.Filter):
    """Add a prefix to all log messages."""

    def __init__(self, prefix: str = "mkdocs_sqlalchemy_plugin"):
        super().__init__()
        self.prefix = prefix

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = f"{self.prefix}: {record.msg}"
        return True


logger = logging.getLogger("mkdocs.plugins.mkdocs_sqlalchemy_plugin")
logger.addFilter(PluginLogFilter())
