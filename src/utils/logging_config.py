import logging
import sys
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


@dataclass
class LogConfig:
    level: str = "INFO"
    filename: Optional[str] = "bot_manager.log"
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    logs_directory: str = "logs"
    format_pattern: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class LoggingSetup:
    def __init__(self, config: LogConfig):
        self.config = config
        self.root_logger = logging.getLogger()
        self.log_path = self._prepare_log_directory() if config.filename else None

    def configure(self) -> None:
        self._set_root_logger_level()
        self._clear_existing_handlers()
        self._add_console_handler()
        self._add_file_handler()
        self._configure_third_party_loggers()
        self._log_completion()

    def _prepare_log_directory(self) -> Path:
        log_dir = Path(self.config.logs_directory)
        log_dir.mkdir(exist_ok=True)
        return log_dir / self.config.filename

    def _set_root_logger_level(self) -> None:
        self.root_logger.setLevel(self.config.level)

    def _clear_existing_handlers(self) -> None:
        self.root_logger.handlers.clear()

    def _create_formatter(self) -> logging.Formatter:
        return logging.Formatter(self.config.format_pattern)

    def _add_console_handler(self) -> None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._create_formatter())
        self.root_logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        if not self.log_path:
            return

        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count
        )
        file_handler.setFormatter(self._create_formatter())
        self.root_logger.addHandler(file_handler)

    def _configure_third_party_loggers(self) -> None:
        third_party_loggers = ['urllib3', 'sqlalchemy']
        for logger_name in third_party_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    def _log_completion(self) -> None:
        self.root_logger.info("Logging configuration completed")


def setup_logging(
        level: str = "INFO",
        filename: Optional[str] = "bot_manager.log",
        max_file_size: int = 10 * 1024 * 1024,
        backup_count: int = 5
) -> None:
    """
    Configure application logging with console and optional file output.
    """
    config = LogConfig(
        level=level,
        filename=filename,
        max_file_size=max_file_size,
        backup_count=backup_count
    )
    LoggingSetup(config).configure()
