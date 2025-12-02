"""
Enums module - Application enumerations.

This module contains all enum definitions used throughout the application.
"""

from app.enums.language import Language, LanguageCode
from app.enums.analysis import (
    AnalysisType,
    FeedbackSeverity,
    SpeechRateClassification,
    PauseType,
    VocabularyLevel,
)

__all__ = [
    # Language enums
    "Language",
    "LanguageCode",
    # Analysis enums
    "AnalysisType",
    "FeedbackSeverity",
    "SpeechRateClassification",
    "PauseType",
    "VocabularyLevel",
]
