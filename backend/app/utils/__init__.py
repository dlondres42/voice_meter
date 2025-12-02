"""
Utils module - Utility functions and helpers.

This module contains stateless utility functions that can be used
across the application.
"""

from app.utils.text import (
    normalize_text,
    count_syllables,
    count_words,
    tokenize,
    remove_punctuation,
)
from app.utils.audio import (
    validate_audio_format,
    get_audio_duration,
)
from app.utils.metrics import (
    calculate_wpm,
    calculate_similarity,
    calculate_ttr,
)

__all__ = [
    # Text utilities
    "normalize_text",
    "count_syllables",
    "count_words",
    "tokenize",
    "remove_punctuation",
    # Audio utilities
    "validate_audio_format",
    "get_audio_duration",
    # Metrics utilities
    "calculate_wpm",
    "calculate_similarity",
    "calculate_ttr",
]
