"""
Audio utility functions.

Provides audio processing utilities for speech analysis.
"""

import os
from typing import Tuple, Optional

# Supported audio formats and their MIME types
SUPPORTED_FORMATS = {
    ".mp3": "audio/mpeg",
    ".mp4": "audio/mp4",
    ".m4a": "audio/mp4",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
}

# Size limits
MIN_AUDIO_SIZE_BYTES = 1000  # 1 KB minimum
MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB (Whisper API limit)

# Duration limits (in seconds)
MIN_AUDIO_DURATION = 0.5
MAX_AUDIO_DURATION = 7200  # 2 hours


def validate_audio_format(
    file_path: str,
    check_size: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Validate audio file format and size.
    
    Args:
        file_path: Path to audio file
        check_size: Whether to check file size
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file exists
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    # Check extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        return False, f"Unsupported format '{ext}'. Supported: {supported}"
    
    # Check size
    if check_size:
        file_size = os.path.getsize(file_path)
        
        if file_size < MIN_AUDIO_SIZE_BYTES:
            return False, f"File too small ({file_size} bytes). Minimum: {MIN_AUDIO_SIZE_BYTES} bytes"
        
        if file_size > MAX_AUDIO_SIZE_BYTES:
            max_mb = MAX_AUDIO_SIZE_BYTES / (1024 * 1024)
            return False, f"File too large. Maximum: {max_mb:.1f} MB"
    
    return True, None


def get_audio_duration(file_path: str) -> Optional[float]:
    """
    Get audio file duration in seconds.
    
    Note: This requires additional libraries like mutagen or pydub.
    For now, returns None (duration will be provided by Whisper API).
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds, or None if cannot be determined
    """
    # TODO: Implement using mutagen or pydub if needed
    # For now, the Whisper API response provides duration
    return None


def get_mime_type(file_path: str) -> Optional[str]:
    """
    Get MIME type for audio file.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        MIME type string, or None if unknown
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    return SUPPORTED_FORMATS.get(ext)


def estimate_duration_from_size(
    file_size_bytes: int,
    format_ext: str = ".mp3"
) -> float:
    """
    Estimate audio duration from file size.
    
    This is a rough estimate based on typical bitrates.
    
    Args:
        file_size_bytes: File size in bytes
        format_ext: Audio format extension
        
    Returns:
        Estimated duration in seconds
    """
    # Typical bitrates (kbps) for different formats
    typical_bitrates = {
        ".mp3": 128,
        ".m4a": 128,
        ".wav": 1411,  # 16-bit 44.1kHz stereo
        ".ogg": 96,
        ".flac": 900,  # Variable, rough estimate
        ".webm": 128,
    }
    
    bitrate_kbps = typical_bitrates.get(format_ext.lower(), 128)
    bitrate_bps = bitrate_kbps * 1000 / 8  # Convert to bytes per second
    
    return file_size_bytes / bitrate_bps
