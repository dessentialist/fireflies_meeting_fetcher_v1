"""
Configuration module for Fireflies Meeting Fetcher

This module handles all configuration loading, validation, and default values.
It provides a centralized way to manage environment variables and application settings.
"""

import logging
import os
from datetime import datetime

from dotenv import load_dotenv


class Config:
    """
    Configuration class that loads and validates environment variables.

    This class provides a single source of truth for all configuration values,
    with proper validation and sensible defaults.
    """

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load environment variables from .env file
        load_dotenv()

        # Core API configuration
        self.api_key: str = self._get_required_env("FIREFLIES_API_KEY")
        self.api_base_url: str = os.getenv(
            "API_BASE_URL", "https://api.fireflies.ai/graphql"
        )

        # Output configuration
        self.output_directory: str = os.getenv("OUTPUT_DIRECTORY", "transcripts")

        # Query configuration
        self.months_to_fetch: int = int(os.getenv("MONTHS_TO_FETCH", "2"))
        self.max_transcripts_per_query: int = int(
            os.getenv("MAX_TRANSCRIPTS_PER_QUERY", "50")
        )

        # Validate configuration
        self._validate_config()

    def _get_required_env(self, key: str) -> str:
        """
        Get a required environment variable with proper error handling.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value

        Raises:
            ValueError: If the environment variable is not set or empty
        """
        value = os.getenv(key)
        if not value or value.strip() == "":
            raise ValueError(
                f"Required environment variable '{key}' is not set or empty. "
                f"Please check your .env file."
            )
        return value.strip()

    def _validate_config(self) -> None:
        """
        Validate configuration values and raise errors for invalid settings.

        Raises:
            ValueError: If any configuration value is invalid
        """
        # Validate API key format (basic check)
        if len(self.api_key) < 10:
            raise ValueError(
                "API key appears to be too short. Please verify your FIREFLIES_API_KEY."
            )

        # Validate months to fetch
        if self.months_to_fetch < 1 or self.months_to_fetch > 12:
            raise ValueError("MONTHS_TO_FETCH must be between 1 and 12.")

        # Validate max transcripts per query
        if self.max_transcripts_per_query < 1 or self.max_transcripts_per_query > 50:
            raise ValueError(
                "MAX_TRANSCRIPTS_PER_QUERY must be between 1 and 50 (API limit)."
            )

        # Validate API base URL
        if not self.api_base_url.startswith("https://"):
            raise ValueError("API_BASE_URL must be a valid HTTPS URL.")

    def get_date_range(self) -> tuple[datetime, datetime]:
        """
        Calculate the date range for fetching transcripts.

        Returns:
            Tuple of (start_date, end_date) in UTC timezone
        """
        # End date is current time in UTC
        end_date = datetime.utcnow()

        # Start date is months_to_fetch months ago
        # Handle different month lengths properly
        start_date = end_date
        for _ in range(self.months_to_fetch):
            # Go back one month, handling year boundaries
            if start_date.month == 1:
                start_date = start_date.replace(year=start_date.year - 1, month=12)
            else:
                start_date = start_date.replace(month=start_date.month - 1)

        return start_date, end_date

    def get_date_range_iso(self) -> tuple[str, str]:
        """
        Get date range in ISO 8601 format for GraphQL queries.

        Returns:
            Tuple of (from_date, to_date) in ISO 8601 format
        """
        start_date, end_date = self.get_date_range()

        # Convert to ISO 8601 format as required by Fireflies API
        from_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        to_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return from_date, to_date


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("fireflies_fetcher")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:  # Avoid duplicate handlers
        logger.addHandler(console_handler)

    return logger


def ensure_output_directory(output_dir: str) -> None:
    """
    Ensure the output directory exists, creating it if necessary.

    Args:
        output_dir: Path to the output directory

    Raises:
        OSError: If directory cannot be created or accessed
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create output directory '{output_dir}': {e}")
