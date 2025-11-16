import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


# --- Custom JSON Formatter ---
class JsonFormatter(logging.Formatter):
    """Formats log records as JSON strings."""

    def format(self, record):
        # Create a base log dictionary
        log_data = {
            "level": record.levelname,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add any extra fields passed to the logger
        # This is where our 'audit_details' will go
        if record.args and isinstance(record.args, dict):
            log_data.update(record.args)

        return json.dumps(log_data)


def setup_logging():
    """Configures the loggers for the application."""
    LOGS_DIR = "logs"
    os.makedirs(LOGS_DIR, exist_ok=True)

    # --- 1. Configure the "audit" logger ---
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    # Stop audit logs from bubbling up to the default uvicorn logger
    audit_logger.propagate = False

    # Create a rotating file handler for audit logs
    audit_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "audit.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB per file
        backupCount=5,  # Keep 5 old files
    )

    # Use our custom JSON formatter
    audit_handler.setFormatter(JsonFormatter())
    audit_logger.addHandler(audit_handler)

    # --- 2. Configure the general "uvicorn.error" logger ---
    app_logger = logging.getLogger("uvicorn.error")
    app_logger.propagate = False
    app_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    )

    app_logger.addHandler(console_handler)

    # Also log general app errors to a file
    app_error_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "app_error.log"), maxBytes=10 * 1024 * 1024, backupCount=3
    )
    app_error_handler.setLevel(logging.WARNING)  # Only log warnings and errors
    app_error_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    app_logger.addHandler(app_error_handler)

    app_logger.info("Logging configured.")
