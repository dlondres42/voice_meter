"""
Service interfaces.

Abstract base classes defining contracts for application services.
Using Protocol for structural subtyping (duck typing support).
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Protocol, runtime_checkable

from app.dto.analysis import (
    AdvancedAnalysisResult,
    LanguageDetectionResult,
)


@runtime_checkable
class TranscriptionServiceInterface(Protocol):
    """
    Interface for audio transcription services.
    
    Implementations must provide audio-to-text transcription capability.
    Examples: OpenAI Whisper, Google Speech-to-Text, Azure Speech.
    """
    
    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Optional language hint (ISO code)
            
        Returns:
            Dictionary with:
                - text: Transcribed text
                - language: Detected language
                - duration: Audio duration in seconds
                - segments: Optional word-level timing
        """
        ...


@runtime_checkable
class TextComparisonServiceInterface(Protocol):
    """
    Interface for text comparison services.
    
    Implementations must provide text similarity analysis.
    """
    
    def compare_texts(
        self,
        original: str,
        transcribed: str
    ) -> Dict[str, Any]:
        """
        Compare original text with transcribed text.
        
        Args:
            original: Original/expected text
            transcribed: Transcribed/actual text
            
        Returns:
            Dictionary with:
                - similarity_ratio: Overall similarity (0-1)
                - matching_words: Number of matching words
                - differences: List of differences found
        """
        ...


@runtime_checkable
class AnalysisServiceInterface(Protocol):
    """
    Interface for speech analysis services.
    
    Implementations must provide comprehensive speech quality analysis.
    """
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetectionResult with language code and confidence
        """
        ...
    
    def analyze_comprehensive(
        self,
        text: str,
        duration_seconds: float,
        language: Optional[str] = None
    ) -> AdvancedAnalysisResult:
        """
        Perform comprehensive speech analysis.
        
        Args:
            text: Transcribed text
            duration_seconds: Audio duration
            language: Optional language code (auto-detect if not provided)
            
        Returns:
            AdvancedAnalysisResult with all metrics and feedback
        """
        ...


class BaseService(ABC):
    """
    Abstract base class for all services.
    
    Provides common functionality and lifecycle management.
    """
    
    def __init__(self):
        """Initialize the service."""
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the service.
        
        Called before first use. Should set up connections,
        load models, etc.
        """
        pass
    
    async def shutdown(self) -> None:
        """
        Shutdown the service.
        
        Called during application shutdown. Should clean up
        resources, close connections, etc.
        """
        self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        return self._initialized


class BaseAnalyzer(ABC):
    """
    Abstract base class for individual analyzers.
    
    Each analyzer focuses on a specific aspect of speech analysis.
    """
    
    def __init__(self, language: str = "pt-BR"):
        """
        Initialize analyzer with language configuration.
        
        Args:
            language: Language code for analysis
        """
        self.language = language
    
    @abstractmethod
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Perform analysis on the given text.
        
        Args:
            text: Text to analyze
            **kwargs: Additional analysis parameters
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def set_language(self, language: str) -> None:
        """
        Update the analysis language.
        
        Args:
            language: New language code
        """
        self.language = language
