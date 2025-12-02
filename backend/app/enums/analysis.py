"""
Analysis enumeration module.

Defines enums related to speech analysis categories and classifications.
"""

from enum import Enum, auto


class AnalysisType(str, Enum):
    """Types of speech analysis available."""
    
    SPEECH_RATE = "speech_rate"
    PAUSES = "pauses"
    VOCABULARY = "vocabulary"
    FLUENCY = "fluency"
    COMPREHENSIVE = "comprehensive"


class FeedbackSeverity(str, Enum):
    """
    Severity levels for feedback messages.
    
    Used to categorize the importance of feedback items.
    """
    
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL = "critical"
    
    @property
    def priority(self) -> int:
        """Get numeric priority (higher = more severe)."""
        priorities = {
            FeedbackSeverity.INFO: 0,
            FeedbackSeverity.SUCCESS: 1,
            FeedbackSeverity.WARNING: 2,
            FeedbackSeverity.CRITICAL: 3,
        }
        return priorities[self]


class SpeechRateClassification(str, Enum):
    """
    Classification of speech rate based on words per minute.
    
    Based on research: optimal range is 140-180 WPM with 150-165 preferred.
    """
    
    TOO_SLOW = "too_slow"           # < 120 WPM
    SLOW = "slow"                   # 120-139 WPM
    OPTIMAL_LOW = "optimal_low"     # 140-149 WPM
    OPTIMAL = "optimal"             # 150-165 WPM (ideal)
    OPTIMAL_HIGH = "optimal_high"   # 166-180 WPM
    FAST = "fast"                   # 181-200 WPM
    TOO_FAST = "too_fast"           # > 200 WPM
    
    @classmethod
    def from_wpm(cls, wpm: float) -> "SpeechRateClassification":
        """
        Classify speech rate from words per minute.
        
        Args:
            wpm: Words per minute value
            
        Returns:
            SpeechRateClassification enum value
        """
        if wpm < 120:
            return cls.TOO_SLOW
        elif wpm < 140:
            return cls.SLOW
        elif wpm < 150:
            return cls.OPTIMAL_LOW
        elif wpm <= 165:
            return cls.OPTIMAL
        elif wpm <= 180:
            return cls.OPTIMAL_HIGH
        elif wpm <= 200:
            return cls.FAST
        else:
            return cls.TOO_FAST
    
    def is_optimal(self) -> bool:
        """Check if this classification is within optimal range."""
        return self in {
            SpeechRateClassification.OPTIMAL_LOW,
            SpeechRateClassification.OPTIMAL,
            SpeechRateClassification.OPTIMAL_HIGH,
        }
    
    @property
    def description_pt(self) -> str:
        """Get Portuguese description."""
        descriptions = {
            SpeechRateClassification.TOO_SLOW: "Muito lento",
            SpeechRateClassification.SLOW: "Lento",
            SpeechRateClassification.OPTIMAL_LOW: "Bom (mais pausado)",
            SpeechRateClassification.OPTIMAL: "Ideal",
            SpeechRateClassification.OPTIMAL_HIGH: "Bom (mais dinâmico)",
            SpeechRateClassification.FAST: "Rápido",
            SpeechRateClassification.TOO_FAST: "Muito rápido",
        }
        return descriptions[self]
    
    @property
    def description_en(self) -> str:
        """Get English description."""
        descriptions = {
            SpeechRateClassification.TOO_SLOW: "Too slow",
            SpeechRateClassification.SLOW: "Slow",
            SpeechRateClassification.OPTIMAL_LOW: "Good (more deliberate)",
            SpeechRateClassification.OPTIMAL: "Ideal",
            SpeechRateClassification.OPTIMAL_HIGH: "Good (more dynamic)",
            SpeechRateClassification.FAST: "Fast",
            SpeechRateClassification.TOO_FAST: "Too fast",
        }
        return descriptions[self]


class PauseType(str, Enum):
    """
    Types of pauses in speech.
    
    Categorized by duration and function.
    """
    
    MICRO = "micro"           # < 0.3s - natural speech rhythm
    SHORT = "short"           # 0.3-0.5s - emphasis/breathing
    MEDIUM = "medium"         # 0.5-1.0s - sentence breaks
    LONG = "long"             # 1.0-2.0s - paragraph/topic changes
    EXTENDED = "extended"     # > 2.0s - hesitation/uncertainty
    
    @classmethod
    def from_duration(cls, duration_seconds: float) -> "PauseType":
        """
        Classify pause type from duration.
        
        Args:
            duration_seconds: Pause duration in seconds
            
        Returns:
            PauseType enum value
        """
        if duration_seconds < 0.3:
            return cls.MICRO
        elif duration_seconds < 0.5:
            return cls.SHORT
        elif duration_seconds < 1.0:
            return cls.MEDIUM
        elif duration_seconds < 2.0:
            return cls.LONG
        else:
            return cls.EXTENDED
    
    def is_natural(self) -> bool:
        """Check if this pause type is natural in speech."""
        return self in {PauseType.MICRO, PauseType.SHORT, PauseType.MEDIUM}


class VocabularyLevel(str, Enum):
    """
    Vocabulary complexity levels.
    
    Based on lexical diversity and word sophistication.
    """
    
    BASIC = "basic"             # Simple, everyday vocabulary
    INTERMEDIATE = "intermediate"  # Standard vocabulary
    ADVANCED = "advanced"        # Rich, varied vocabulary
    EXPERT = "expert"           # Specialized/technical vocabulary
    
    @classmethod
    def from_diversity_score(cls, score: float) -> "VocabularyLevel":
        """
        Classify vocabulary level from diversity score.
        
        Args:
            score: Lexical diversity score (0-1)
            
        Returns:
            VocabularyLevel enum value
        """
        if score < 0.3:
            return cls.BASIC
        elif score < 0.5:
            return cls.INTERMEDIATE
        elif score < 0.7:
            return cls.ADVANCED
        else:
            return cls.EXPERT
    
    @property
    def min_score(self) -> float:
        """Get minimum diversity score for this level."""
        scores = {
            VocabularyLevel.BASIC: 0.0,
            VocabularyLevel.INTERMEDIATE: 0.3,
            VocabularyLevel.ADVANCED: 0.5,
            VocabularyLevel.EXPERT: 0.7,
        }
        return scores[self]
