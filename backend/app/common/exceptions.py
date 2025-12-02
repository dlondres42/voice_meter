"""
Custom exceptions module.

Defines application-specific exceptions for better error handling.
"""

from typing import Optional, Dict, Any


class VoiceMeterException(Exception):
    """
    Base exception for all VoiceMeter application errors.
    
    All custom exceptions should inherit from this class to enable
    consistent error handling throughout the application.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional error details
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class AudioProcessingError(VoiceMeterException):
    """
    Raised when audio processing fails.
    
    Examples:
        - Invalid audio format
        - Corrupted audio file
        - Audio too short/long
    """
    
    def __init__(
        self,
        message: str = "Failed to process audio file",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AUDIO_PROCESSING_ERROR", details)


class TranscriptionError(VoiceMeterException):
    """
    Raised when audio transcription fails.
    
    Examples:
        - API error from Whisper
        - Timeout during transcription
        - Unsupported language
    """
    
    def __init__(
        self,
        message: str = "Failed to transcribe audio",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "TRANSCRIPTION_ERROR", details)


class LanguageDetectionError(VoiceMeterException):
    """
    Raised when language detection fails or is uncertain.
    
    Examples:
        - Text too short for reliable detection
        - Mixed language content
        - Unsupported language detected
    """
    
    def __init__(
        self,
        message: str = "Failed to detect language",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "LANGUAGE_DETECTION_ERROR", details)


class ValidationError(VoiceMeterException):
    """
    Raised when input validation fails.
    
    Examples:
        - Missing required fields
        - Invalid parameter values
        - Constraint violations
    """
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", error_details)


class RecordingNotFoundError(VoiceMeterException):
    """
    Raised when a recording is not found.
    
    Examples:
        - Recording ID doesn't exist
        - Recording was deleted
    """
    
    def __init__(
        self,
        recording_id: int,
        message: Optional[str] = None
    ):
        msg = message or f"Recording with ID {recording_id} not found"
        super().__init__(msg, "RECORDING_NOT_FOUND", {"recording_id": recording_id})


class AnalysisError(VoiceMeterException):
    """
    Raised when speech analysis fails.
    
    Examples:
        - Insufficient data for analysis
        - Analysis algorithm error
        - Invalid analysis parameters
    """
    
    def __init__(
        self,
        message: str = "Speech analysis failed",
        analysis_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if analysis_type:
            error_details["analysis_type"] = analysis_type
        super().__init__(message, "ANALYSIS_ERROR", error_details)


class ConfigurationError(VoiceMeterException):
    """
    Raised when there's a configuration problem.
    
    Examples:
        - Missing API key
        - Invalid configuration value
        - Required service unavailable
    """
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key
        super().__init__(message, "CONFIGURATION_ERROR", error_details)


class ExternalServiceError(VoiceMeterException):
    """
    Raised when an external service (API) fails.
    
    Examples:
        - OpenAI API error
        - Network timeout
        - Rate limiting
    """
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if service_name:
            error_details["service"] = service_name
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", error_details)
