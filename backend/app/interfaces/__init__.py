"""
Interfaces module - Abstract base classes and protocols.

Defines contracts for services and components.
"""

from app.interfaces.services import (
    TranscriptionServiceInterface,
    AnalysisServiceInterface,
    TextComparisonServiceInterface,
)

__all__ = [
    "TranscriptionServiceInterface",
    "AnalysisServiceInterface",
    "TextComparisonServiceInterface",
]
