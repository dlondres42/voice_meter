"""
Text utility functions.

Provides text processing utilities for speech analysis.
"""

import re
import unicodedata
from typing import List, Optional

from app.common.constants import STOPWORDS


def normalize_text(text: str, lowercase: bool = True) -> str:
    """
    Normalize text for analysis.
    
    Performs:
        - Unicode normalization (NFC)
        - Optional lowercasing
        - Multiple space reduction
        - Trimming
    
    Args:
        text: Input text to normalize
        lowercase: Whether to convert to lowercase
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    # Unicode normalization
    normalized = unicodedata.normalize("NFC", text)
    
    # Lowercase if requested
    if lowercase:
        normalized = normalized.lower()
    
    # Reduce multiple spaces to single space
    normalized = re.sub(r"\s+", " ", normalized)
    
    # Trim whitespace
    return normalized.strip()


def remove_punctuation(text: str, keep_apostrophes: bool = True) -> str:
    """
    Remove punctuation from text.
    
    Args:
        text: Input text
        keep_apostrophes: Whether to keep apostrophes (for contractions)
        
    Returns:
        Text with punctuation removed
    """
    if keep_apostrophes:
        # Keep apostrophes and single quotes
        pattern = r"[^\w\s']"
    else:
        pattern = r"[^\w\s]"
    
    return re.sub(pattern, "", text)


def tokenize(
    text: str,
    remove_stopwords: bool = False,
    language: str = "pt-BR"
) -> List[str]:
    """
    Tokenize text into words.
    
    Args:
        text: Input text to tokenize
        remove_stopwords: Whether to remove stopwords
        language: Language code for stopword list
        
    Returns:
        List of word tokens
    """
    # Normalize and clean
    cleaned = normalize_text(text)
    cleaned = remove_punctuation(cleaned)
    
    # Split into words
    words = cleaned.split()
    
    # Remove empty tokens
    words = [w for w in words if w]
    
    # Remove stopwords if requested
    if remove_stopwords:
        stopwords = STOPWORDS.get(language, set())
        words = [w for w in words if w not in stopwords]
    
    return words


def count_words(text: str) -> int:
    """
    Count the number of words in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of words
    """
    return len(tokenize(text))


def count_syllables(word: str, language: str = "pt-BR") -> int:
    """
    Estimate the number of syllables in a word.
    
    Uses language-specific heuristics since accurate syllable
    counting requires linguistic knowledge.
    
    Args:
        word: Word to count syllables for
        language: Language code for heuristics
        
    Returns:
        Estimated number of syllables
    """
    word = word.lower().strip()
    
    if not word:
        return 0
    
    if language.startswith("pt"):
        return _count_syllables_portuguese(word)
    else:
        return _count_syllables_english(word)


def _count_syllables_portuguese(word: str) -> int:
    """
    Count syllables in Portuguese word.
    
    Uses vowel counting with adjustments for:
    - Diphthongs (two vowels that form one syllable)
    - Hiatus (two vowels that form separate syllables)
    """
    vowels = "aeiouáàâãéêíóôõú"
    diphthongs = [
        "ai", "au", "ei", "eu", "iu", "oi", "ou", "ui",
        "ão", "ãe", "õe",
        "ai", "au", "ei", "eu", "iu", "oi", "ou", "ui"
    ]
    
    word = word.lower()
    count = 0
    prev_was_vowel = False
    i = 0
    
    while i < len(word):
        char = word[i]
        is_vowel = char in vowels
        
        if is_vowel:
            # Check for diphthong
            if i + 1 < len(word):
                pair = word[i:i+2]
                if pair in diphthongs:
                    if not prev_was_vowel:
                        count += 1
                    prev_was_vowel = True
                    i += 2
                    continue
            
            if not prev_was_vowel:
                count += 1
            prev_was_vowel = True
        else:
            prev_was_vowel = False
        
        i += 1
    
    return max(1, count)


def _count_syllables_english(word: str) -> int:
    """
    Count syllables in English word.
    
    Uses a simplified algorithm based on vowel patterns
    and common English word endings.
    """
    word = word.lower().strip()
    
    if not word:
        return 0
    
    # Common exceptions
    exceptions = {
        "the": 1, "be": 1, "are": 1, "were": 1,
        "have": 1, "give": 1, "live": 1,
        "love": 1, "move": 1, "come": 1,
    }
    
    if word in exceptions:
        return exceptions[word]
    
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    
    for i, char in enumerate(word):
        is_vowel = char in vowels
        
        if is_vowel and not prev_was_vowel:
            count += 1
        
        prev_was_vowel = is_vowel
    
    # Adjust for silent 'e' at end
    if word.endswith("e") and count > 1:
        count -= 1
    
    # Adjust for -le endings (like "table", "bubble")
    if len(word) > 2 and word.endswith("le") and word[-3] not in vowels:
        count += 1
    
    # Adjust for -ed endings
    if word.endswith("ed") and count > 1:
        if not word.endswith("ted") and not word.endswith("ded"):
            count -= 1
    
    return max(1, count)


def count_syllables_in_text(text: str, language: str = "pt-BR") -> int:
    """
    Count total syllables in a text.
    
    Args:
        text: Input text
        language: Language code
        
    Returns:
        Total syllable count
    """
    words = tokenize(text)
    return sum(count_syllables(word, language) for word in words)


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Split on sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def get_unique_words(text: str, language: str = "pt-BR") -> set:
    """
    Get set of unique words (lemmas would be better but this is simpler).
    
    Args:
        text: Input text
        language: Language code
        
    Returns:
        Set of unique words
    """
    words = tokenize(text, remove_stopwords=True, language=language)
    return set(words)


def find_repeated_patterns(
    words: List[str],
    min_length: int = 2,
    max_length: int = 4
) -> List[tuple]:
    """
    Find repeated word patterns (potential stuttering or emphasis).
    
    Args:
        words: List of words
        min_length: Minimum pattern length
        max_length: Maximum pattern length
        
    Returns:
        List of (pattern, count) tuples
    """
    patterns = {}
    
    for length in range(min_length, max_length + 1):
        for i in range(len(words) - length + 1):
            pattern = tuple(words[i:i + length])
            patterns[pattern] = patterns.get(pattern, 0) + 1
    
    # Filter to only repeated patterns
    repeated = [(p, c) for p, c in patterns.items() if c > 1]
    
    # Sort by count descending
    repeated.sort(key=lambda x: x[1], reverse=True)
    
    return repeated
