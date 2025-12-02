"""
Analysis DTOs.

Data Transfer Objects for speech analysis results.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.enums.analysis import (
    SpeechRateClassification,
    FeedbackSeverity,
    VocabularyLevel,
)
from app.enums.language import LanguageCode


@dataclass
class FeedbackItem:
    """
    Individual feedback item with message and severity.
    
    Attributes:
        message: Human-readable feedback message
        severity: Severity level of the feedback
        category: Category of feedback (speech_rate, pauses, vocabulary, fluency)
        metric_value: Optional numeric value related to the feedback
    """
    message: str
    severity: FeedbackSeverity = FeedbackSeverity.INFO
    category: str = "general"
    metric_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category,
            "metric_value": self.metric_value,
        }


@dataclass
class SpeechRateMetrics:
    """
    Metrics related to speech rate and pacing.
    
    Based on research: optimal range is 140-180 WPM with 150-165 preferred.
    
    Attributes:
        words_per_minute: Average words per minute
        syllables_per_second: Average syllables per second
        total_words: Total word count
        total_syllables: Total syllable count
        speaking_duration: Duration in seconds (excluding long pauses)
        classification: Classification of the speech rate
        score: Quality score (0-100)
    """
    words_per_minute: float
    syllables_per_second: float
    total_words: int
    total_syllables: int
    speaking_duration: float
    classification: SpeechRateClassification = field(default=SpeechRateClassification.OPTIMAL)
    score: float = 0.0
    
    def __post_init__(self):
        """Set classification based on WPM if not provided."""
        if self.words_per_minute > 0:
            self.classification = SpeechRateClassification.from_wpm(self.words_per_minute)
    
    def is_optimal(self) -> bool:
        """Check if speech rate is within optimal range."""
        return self.classification.is_optimal()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "words_per_minute": round(self.words_per_minute, 2),
            "syllables_per_second": round(self.syllables_per_second, 2),
            "total_words": self.total_words,
            "total_syllables": self.total_syllables,
            "speaking_duration": round(self.speaking_duration, 2),
            "classification": self.classification.value,
            "is_optimal": self.is_optimal(),
            "score": round(self.score, 2),
        }


@dataclass
class PauseMetrics:
    """
    Metrics related to pauses in speech.
    
    Attributes:
        total_pauses: Total number of detected pauses
        short_pauses: Pauses < 0.5s
        medium_pauses: Pauses 0.5s - 1.0s
        long_pauses: Pauses 1.0s - 2.0s
        extended_pauses: Pauses > 2.0s
        average_pause_duration: Average pause duration in seconds
        total_pause_time: Total time spent pausing in seconds
        pause_ratio: Ratio of pause time to total time
        score: Quality score (0-100)
    """
    total_pauses: int
    short_pauses: int
    medium_pauses: int
    long_pauses: int
    extended_pauses: int
    average_pause_duration: float
    total_pause_time: float
    pause_ratio: float
    score: float = 0.0
    
    @property
    def effective_pauses(self) -> int:
        """Get count of effective pauses (short + medium)."""
        return self.short_pauses + self.medium_pauses
    
    @property
    def problematic_pauses(self) -> int:
        """Get count of problematic pauses (extended)."""
        return self.extended_pauses
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_pauses": self.total_pauses,
            "short_pauses": self.short_pauses,
            "medium_pauses": self.medium_pauses,
            "long_pauses": self.long_pauses,
            "extended_pauses": self.extended_pauses,
            "average_pause_duration": round(self.average_pause_duration, 3),
            "total_pause_time": round(self.total_pause_time, 2),
            "pause_ratio": round(self.pause_ratio, 3),
            "effective_pauses": self.effective_pauses,
            "problematic_pauses": self.problematic_pauses,
            "score": round(self.score, 2),
        }


@dataclass
class VocabularyMetrics:
    """
    Metrics related to vocabulary usage.
    
    Attributes:
        unique_words: Number of unique words used
        total_content_words: Total content words (excluding stopwords)
        type_token_ratio: Lexical diversity measure
        complex_words: Number of complex words (4+ syllables PT, 3+ EN)
        complex_word_ratio: Ratio of complex words to total
        vocabulary_level: Classification of vocabulary sophistication
        average_word_length: Average word length in characters
        score: Quality score (0-100)
    """
    unique_words: int
    total_content_words: int
    type_token_ratio: float
    complex_words: int
    complex_word_ratio: float
    vocabulary_level: VocabularyLevel = field(default=VocabularyLevel.INTERMEDIATE)
    average_word_length: float = 0.0
    score: float = 0.0
    
    def __post_init__(self):
        """Set vocabulary level if not provided."""
        if self.type_token_ratio > 0:
            self.vocabulary_level = VocabularyLevel.from_diversity_score(self.type_token_ratio)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "unique_words": self.unique_words,
            "total_content_words": self.total_content_words,
            "type_token_ratio": round(self.type_token_ratio, 3),
            "complex_words": self.complex_words,
            "complex_word_ratio": round(self.complex_word_ratio, 3),
            "vocabulary_level": self.vocabulary_level.value,
            "average_word_length": round(self.average_word_length, 2),
            "score": round(self.score, 2),
        }


@dataclass
class FluencyMetrics:
    """
    Metrics related to speech fluency.
    
    Attributes:
        filler_words_count: Number of filler words detected
        filler_words_list: List of specific fillers found
        filler_ratio: Ratio of fillers to total words
        repetitions_count: Number of word/phrase repetitions
        repetition_ratio: Ratio of repetitions to total words
        false_starts: Number of false starts/corrections
        score: Quality score (0-100)
    """
    filler_words_count: int
    filler_words_list: List[str] = field(default_factory=list)
    filler_ratio: float = 0.0
    repetitions_count: int = 0
    repetition_ratio: float = 0.0
    false_starts: int = 0
    score: float = 0.0
    
    @property
    def is_fluent(self) -> bool:
        """Check if speech is considered fluent (low fillers/repetitions)."""
        return self.filler_ratio < 0.03 and self.repetition_ratio < 0.02
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filler_words_count": self.filler_words_count,
            "filler_words_list": self.filler_words_list[:10],  # Limit to top 10
            "filler_ratio": round(self.filler_ratio, 3),
            "repetitions_count": self.repetitions_count,
            "repetition_ratio": round(self.repetition_ratio, 3),
            "false_starts": self.false_starts,
            "is_fluent": self.is_fluent,
            "score": round(self.score, 2),
        }


@dataclass
class LanguageDetectionResult:
    """
    Result of language detection.
    
    Attributes:
        detected_language: Detected language code
        confidence: Confidence score (0-1)
        language_name: Human-readable language name
        is_reliable: Whether detection is considered reliable
    """
    detected_language: LanguageCode
    confidence: float
    language_name: str = ""
    is_reliable: bool = True
    
    def __post_init__(self):
        """Set language name from code if not provided."""
        if not self.language_name:
            from app.enums.language import Language
            try:
                self.language_name = Language.from_code(self.detected_language).value
            except (KeyError, ValueError):
                self.language_name = self.detected_language.value
        
        # Set reliability based on confidence
        self.is_reliable = self.confidence >= 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "detected_language": self.detected_language.value,
            "confidence": round(self.confidence, 3),
            "language_name": self.language_name,
            "is_reliable": self.is_reliable,
        }


@dataclass
class AdvancedAnalysisResult:
    """
    Complete advanced speech analysis result.
    
    Aggregates all analysis components with overall scoring.
    
    Attributes:
        language: Detected language information
        speech_rate: Speech rate metrics
        pauses: Pause metrics
        vocabulary: Vocabulary metrics
        fluency: Fluency metrics
        overall_score: Aggregate quality score (0-100)
        feedback: List of feedback items
        analyzed_at: Timestamp of analysis
    """
    language: LanguageDetectionResult
    speech_rate: SpeechRateMetrics
    pauses: PauseMetrics
    vocabulary: VocabularyMetrics
    fluency: FluencyMetrics
    overall_score: float = 0.0
    feedback: List[FeedbackItem] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_overall_score(self) -> float:
        """Calculate overall score from component scores."""
        from app.utils.metrics import calculate_overall_score
        
        self.overall_score = calculate_overall_score(
            self.speech_rate.score,
            self.pauses.score,
            self.vocabulary.score,
            self.fluency.score,
        )
        return self.overall_score
    
    def get_feedback_by_severity(self, severity: FeedbackSeverity) -> List[FeedbackItem]:
        """Get feedback items of a specific severity."""
        return [f for f in self.feedback if f.severity == severity]
    
    def get_critical_feedback(self) -> List[FeedbackItem]:
        """Get critical feedback items that need immediate attention."""
        return self.get_feedback_by_severity(FeedbackSeverity.CRITICAL)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "language": self.language.to_dict(),
            "speech_rate": self.speech_rate.to_dict(),
            "pauses": self.pauses.to_dict(),
            "vocabulary": self.vocabulary.to_dict(),
            "fluency": self.fluency.to_dict(),
            "overall_score": round(self.overall_score, 2),
            "feedback": [f.to_dict() for f in self.feedback],
            "analyzed_at": self.analyzed_at.isoformat(),
        }
