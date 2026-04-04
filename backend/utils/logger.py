"""
STEP 6: LOGGING AND EXCEPTION HANDLING
Production-ready logging and error handling system
"""

import logging
import logging.handlers
import sys
from typing import Dict, Any, Optional
from pathlib import Path


class ResumeAnalyzerLogger:
    """
    STEP 6: Centralized logging system for the resume analyzer
    """

    def __init__(self, log_level: str = "INFO", log_to_file: bool = True):
        self.logger = logging.getLogger("ResumeAnalyzer")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove any existing handlers
        self.logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        # Console handler (always active)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # File handler (optional)
        if log_to_file:
            log_dir = Path("backend/logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_dir / "resume_analyzer.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)

        # Error file handler (separate file for errors)
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)

    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)


# Global logger instance
logger = ResumeAnalyzerLogger()


class SafeOperation:
    """
    STEP 6: Context manager for safe operations with automatic error handling
    """

    def __init__(self, operation_name: str, fallback_value: Any = None):
        self.operation_name = operation_name
        self.fallback_value = fallback_value
        self.logger = logger

    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error(f"Operation '{self.operation_name}' failed: {exc_val}")
            # Return True to suppress the exception (we're handling it)
            return True
        else:
            self.logger.debug(f"Operation '{self.operation_name}' completed successfully")
        return False


def safe_execute(operation_name: str, func, *args, fallback_value=None, **kwargs) -> Any:
    """
    STEP 6: Execute a function safely with automatic error handling and logging

    Args:
        operation_name: Name of the operation for logging
        func: Function to execute
        args: Positional arguments for the function
        fallback_value: Value to return if operation fails
        kwargs: Keyword arguments for the function

    Returns:
        Function result or fallback_value if failed
    """
    try:
        logger.debug(f"Executing: {operation_name}")
        result = func(*args, **kwargs)
        logger.debug(f"Successfully executed: {operation_name}")
        return result
    except Exception as e:
        logger.error(f"Failed to execute '{operation_name}': {str(e)}")
        if fallback_value is not None:
            logger.warning(f"Using fallback value for '{operation_name}': {fallback_value}")
        return fallback_value


def create_safe_response(status: str = "success", message: str = "",
                        data: Any = None, error: str = None) -> Dict[str, Any]:
    """
    STEP 6: Create a standardized response format

    Args:
        status: Response status ("success", "partial", "failed")
        message: Human-readable message
        data: Response data
        error: Error details (if any)

    Returns:
        Standardized response dictionary
    """
    response = {
        "status": status,
        "message": message,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            "response", logging.INFO, "", 0, "", (), None
        )),
    }

    if data is not None:
        response["data"] = data

    if error is not None:
        response["error"] = error
        if status == "success":
            response["status"] = "partial"  # Upgrade to partial if there's an error

    return response


def validate_response_structure(response: Dict[str, Any], required_keys: list) -> bool:
    """
    STEP 6: Validate that a response has all required keys

    Args:
        response: Response dictionary to validate
        required_keys: List of keys that must be present

    Returns:
        True if all required keys are present
    """
    missing_keys = [key for key in required_keys if key not in response]
    if missing_keys:
        logger.warning(f"Response missing required keys: {missing_keys}")
        return False
    return True


# Required response structure for different operations
RESPONSE_STRUCTURES = {
    "parsing": ["status", "skills", "sections_detected"],
    "scoring": ["status", "score", "breakdown"],
    "ml_prediction": ["probability", "decision"],
    "analysis": ["status", "parsing", "ats_analysis", "ml_prediction"],
}


def log_operation_start(operation: str, details: Dict[str, Any] = None):
    """Log the start of an operation"""
    message = f"Starting {operation}"
    if details:
        message += f" with details: {details}"
    logger.info(message)


def log_operation_end(operation: str, success: bool = True, duration: float = None):
    """Log the end of an operation"""
    status = "successfully" if success else "with errors"
    message = f"Completed {operation} {status}"
    if duration is not None:
        message += f" in {duration:.2f}s"
    logger.info(message)


def log_performance_metric(operation: str, duration: float, threshold: float = 5.0):
    """Log performance metrics with warnings for slow operations"""
    if duration > threshold:
        logger.warning(f"Slow operation: {operation} took {duration:.2f}s (threshold: {threshold}s)")
    else:
        logger.debug(f"Performance: {operation} completed in {duration:.2f}s")