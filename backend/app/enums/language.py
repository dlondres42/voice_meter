"""
Language enumeration module.

Defines supported languages and their codes.
"""

from enum import Enum


class LanguageCode(str, Enum):
    """ISO language codes supported by the application."""
    
    PORTUGUESE_BR = "pt-BR"
    ENGLISH_US = "en-US"
    
    @classmethod
    def from_string(cls, value: str) -> "LanguageCode":
        """
        Convert a string to LanguageCode enum.
        
        Args:
            value: String representation of language code
            
        Returns:
            LanguageCode enum value
            
        Raises:
            ValueError: If language code is not supported
        """
        value_lower = value.lower().replace("_", "-")
        for lang in cls:
            if lang.value.lower() == value_lower:
                return lang
        raise ValueError(f"Unsupported language code: {value}")
    
    def is_portuguese(self) -> bool:
        """Check if this is a Portuguese variant."""
        return self == LanguageCode.PORTUGUESE_BR
    
    def is_english(self) -> bool:
        """Check if this is an English variant."""
        return self == LanguageCode.ENGLISH_US


class Language(str, Enum):
    """
    Language names for display purposes.
    
    Each language has a display name and corresponding code.
    """
    
    PORTUGUESE = "Português (Brasil)"
    ENGLISH = "English (US)"
    
    @property
    def code(self) -> LanguageCode:
        """Get the language code for this language."""
        mapping = {
            Language.PORTUGUESE: LanguageCode.PORTUGUESE_BR,
            Language.ENGLISH: LanguageCode.ENGLISH_US,
        }
        return mapping[self]
    
    @classmethod
    def from_code(cls, code: LanguageCode) -> "Language":
        """Get Language from LanguageCode."""
        mapping = {
            LanguageCode.PORTUGUESE_BR: Language.PORTUGUESE,
            LanguageCode.ENGLISH_US: Language.ENGLISH,
        }
        return mapping[code]
