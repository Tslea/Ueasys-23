"""
Logging configuration for Fantasy World RAG.

This module provides structured logging setup using structlog for JSON logging
and standard logging for development. Supports both file and console output.

Example:
    >>> from src.config.logging_config import setup_logging, get_logger
    >>> setup_logging()
    >>> logger = get_logger(__name__)
    >>> logger.info("Server started", port=8000)
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.types import Processor

from src.config.settings import get_settings


def setup_logging() -> None:
    """
    Configure application logging.
    
    Sets up structlog for structured logging with JSON output in production
    and human-readable output in development. Also configures standard
    library logging to work with structlog.
    
    The log level and format are determined by settings.
    """
    settings = get_settings()
    
    # Ensure log directory exists
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Common processors for structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.log_format == "json":
        # JSON format for production
        shared_processors.append(structlog.processors.format_exc_info)
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        # Human-readable format for development
        shared_processors.append(structlog.dev.set_exc_info)
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Create formatter for stdlib logging
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # File handler (if configured)
    handlers: list[logging.Handler] = [console_handler]
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = handlers
    
    # Configure specific loggers
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = handlers
        logger.propagate = False
    
    # Suppress noisy loggers
    for logger_name in ["httpx", "httpcore", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        BoundLogger: Configured structlog logger
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", request_id="abc123")
        >>> logger.error("Failed to process", error="Connection timeout", retry=3)
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables to all subsequent log messages.
    
    Useful for adding request-specific context like request_id or user_id.
    
    Args:
        **kwargs: Context variables to bind
        
    Example:
        >>> bind_context(request_id="abc123", user_id="user456")
        >>> logger.info("Processing")  # Will include request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """
    Clear all bound context variables.
    
    Should be called at the end of request processing to prevent
    context leakage between requests.
    """
    structlog.contextvars.clear_contextvars()


class LoggerMixin:
    """
    Mixin class that provides a logger attribute.
    
    Classes that inherit from this mixin will have a `logger` attribute
    automatically configured with the class name.
    
    Example:
        >>> class MyService(LoggerMixin):
        ...     def process(self):
        ...         self.logger.info("Processing started")
    """
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
