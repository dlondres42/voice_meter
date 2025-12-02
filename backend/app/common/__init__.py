"""
Common module - Shared utilities, constants, and base classes.

This module contains reusable components that are shared across the application.
"""

from app.common.constants import *
from app.common.exceptions import *

__all__ = [
    # Constants
    "SUPPORTED_LANGUAGES",
    "DEFAULT_LANGUAGE",
    # Exceptions
    "VoiceMeterException",
    "AudioProcessingError",
    "TranscriptionError",
    "LanguageDetectionError",
    "ValidationError",
]
