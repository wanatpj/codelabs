"""Structured logging configuration shared by CLI commands."""

import sys

import structlog

logger = structlog.get_logger()


def configure_logging() -> None:
    structlog.configure(
        processors=[structlog.processors.add_log_level, structlog.processors.JSONRenderer()],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )
