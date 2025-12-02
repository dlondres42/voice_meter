"""
Metrics utility functions.

Provides calculation utilities for speech analysis metrics.
"""

from typing import List, Set, Optional, Tuple
import difflib

from app.common.constants import (
    OPTIMAL_WPM_MIN,
    OPTIMAL_WPM_MAX,
    IDEAL_WPM_MIN,
    IDEAL_WPM_MAX,
)


def calculate_wpm(word_count: int, duration_seconds: float) -> float:
    """
    Calculate words per minute.
    
    Args:
        word_count: Number of words spoken
        duration_seconds: Duration in seconds
        
    Returns:
        Words per minute (WPM)
    """
    if duration_seconds <= 0:
        return 0.0
    
    minutes = duration_seconds / 60.0
    return word_count / minutes


def calculate_syllables_per_second(
    syllable_count: int,
    duration_seconds: float
) -> float:
    """
    Calculate syllables per second.
    
    Args:
        syllable_count: Number of syllables
        duration_seconds: Duration in seconds
        
    Returns:
        Syllables per second
    """
    if duration_seconds <= 0:
        return 0.0
    
    return syllable_count / duration_seconds


def calculate_ttr(words: List[str]) -> float:
    """
    Calculate Type-Token Ratio (lexical diversity).
    
    TTR = unique words / total words
    
    Higher TTR indicates more diverse vocabulary.
    
    Args:
        words: List of words (tokens)
        
    Returns:
        TTR value between 0 and 1
    """
    if not words:
        return 0.0
    
    unique_words = set(words)
    return len(unique_words) / len(words)


def calculate_root_ttr(words: List[str]) -> float:
    """
    Calculate Root Type-Token Ratio (Guiraud's index).
    
    Root TTR = unique words / sqrt(total words)
    
    This corrects for text length better than simple TTR.
    
    Args:
        words: List of words
        
    Returns:
        Root TTR value
    """
    if not words:
        return 0.0
    
    import math
    unique_words = set(words)
    return len(unique_words) / math.sqrt(len(words))


def calculate_similarity(
    text1: str,
    text2: str,
    method: str = "ratio"
) -> float:
    """
    Calculate text similarity between two strings.
    
    Args:
        text1: First text
        text2: Second text
        method: Similarity method ('ratio', 'quick', 'real_quick')
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
    
    if method == "quick":
        return matcher.quick_ratio()
    elif method == "real_quick":
        return matcher.real_quick_ratio()
    else:
        return matcher.ratio()


def calculate_levenshtein_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity using Levenshtein distance.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    try:
        import Levenshtein
        distance = Levenshtein.distance(text1.lower(), text2.lower())
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        return 1 - (distance / max_len)
    except ImportError:
        # Fall back to difflib if Levenshtein not available
        return calculate_similarity(text1, text2)


def calculate_wpm_score(wpm: float) -> float:
    """
    Calculate a 0-100 score based on WPM.
    
    100 = ideal range (150-165)
    Lower scores for too slow/fast
    
    Args:
        wpm: Words per minute
        
    Returns:
        Score between 0 and 100
    """
    if IDEAL_WPM_MIN <= wpm <= IDEAL_WPM_MAX:
        return 100.0
    
    if OPTIMAL_WPM_MIN <= wpm <= OPTIMAL_WPM_MAX:
        # Within optimal but not ideal
        if wpm < IDEAL_WPM_MIN:
            # Between 140-149
            distance = IDEAL_WPM_MIN - wpm
            return 100 - (distance * 2)  # -2 per WPM below ideal
        else:
            # Between 166-180
            distance = wpm - IDEAL_WPM_MAX
            return 100 - (distance * 2)
    
    # Outside optimal range
    if wpm < OPTIMAL_WPM_MIN:
        # Too slow
        distance = OPTIMAL_WPM_MIN - wpm
        return max(0, 80 - distance)
    else:
        # Too fast
        distance = wpm - OPTIMAL_WPM_MAX
        return max(0, 80 - distance)


def calculate_pause_score(
    pause_count: int,
    total_duration: float,
    long_pause_count: int = 0
) -> float:
    """
    Calculate a score for pause usage.
    
    Good pauses: ~2-4 per minute
    Long pauses (>2s) are penalized
    
    Args:
        pause_count: Total number of pauses
        total_duration: Total duration in seconds
        long_pause_count: Number of pauses > 2 seconds
        
    Returns:
        Score between 0 and 100
    """
    if total_duration <= 0:
        return 50.0
    
    minutes = total_duration / 60.0
    pauses_per_minute = pause_count / minutes
    
    # Ideal: 2-4 pauses per minute
    if 2 <= pauses_per_minute <= 4:
        base_score = 100.0
    elif 1 <= pauses_per_minute < 2:
        base_score = 80.0
    elif 4 < pauses_per_minute <= 6:
        base_score = 80.0
    else:
        base_score = 60.0
    
    # Penalize long pauses
    long_pause_penalty = long_pause_count * 5
    
    return max(0, base_score - long_pause_penalty)


def calculate_vocabulary_score(
    ttr: float,
    complex_word_ratio: float,
    content_word_count: int
) -> float:
    """
    Calculate a vocabulary richness score.
    
    Combines:
    - Type-Token Ratio (diversity)
    - Complex word usage
    - Content word count
    
    Args:
        ttr: Type-Token Ratio (0-1)
        complex_word_ratio: Ratio of complex words (0-1)
        content_word_count: Number of content words
        
    Returns:
        Score between 0 and 100
    """
    # Weight factors
    diversity_weight = 0.5
    complexity_weight = 0.3
    volume_weight = 0.2
    
    # Diversity score (TTR)
    diversity_score = min(100, ttr * 200)  # 0.5 TTR = 100
    
    # Complexity score
    # Ideal: 10-20% complex words
    if 0.1 <= complex_word_ratio <= 0.2:
        complexity_score = 100.0
    elif complex_word_ratio < 0.1:
        complexity_score = complex_word_ratio * 1000  # 0.1 = 100
    else:
        # Too complex can be hard to follow
        complexity_score = max(50, 100 - (complex_word_ratio - 0.2) * 200)
    
    # Volume score (more content = potentially richer)
    volume_score = min(100, content_word_count * 2)  # 50 words = 100
    
    return (
        diversity_score * diversity_weight +
        complexity_score * complexity_weight +
        volume_score * volume_weight
    )


def calculate_fluency_score(
    filler_ratio: float,
    repetition_ratio: float,
    false_start_count: int,
    total_words: int
) -> float:
    """
    Calculate a fluency score.
    
    Lower fillers and repetitions = higher score
    
    Args:
        filler_ratio: Ratio of filler words (0-1)
        repetition_ratio: Ratio of repetitions (0-1)
        false_start_count: Number of false starts
        total_words: Total word count
        
    Returns:
        Score between 0 and 100
    """
    # Start with 100 and subtract penalties
    score = 100.0
    
    # Filler penalty: -20 per 1%
    filler_penalty = filler_ratio * 2000  # 5% = -100
    
    # Repetition penalty: -15 per 1%
    repetition_penalty = repetition_ratio * 1500
    
    # False start penalty: -5 per occurrence
    false_start_penalty = false_start_count * 5
    
    # Bonus for longer fluent speech
    if total_words > 100 and (filler_ratio + repetition_ratio) < 0.05:
        score += 10  # Bonus for sustained fluency
    
    return max(0, score - filler_penalty - repetition_penalty - false_start_penalty)


def calculate_overall_score(
    speech_rate_score: float,
    pause_score: float,
    vocabulary_score: float,
    fluency_score: float,
    weights: Optional[Tuple[float, float, float, float]] = None
) -> float:
    """
    Calculate overall speech quality score.
    
    Args:
        speech_rate_score: Score for speech rate (0-100)
        pause_score: Score for pauses (0-100)
        vocabulary_score: Score for vocabulary (0-100)
        fluency_score: Score for fluency (0-100)
        weights: Optional custom weights (speech_rate, pause, vocabulary, fluency)
        
    Returns:
        Overall score between 0 and 100
    """
    if weights is None:
        # Default weights
        weights = (0.25, 0.20, 0.25, 0.30)  # Fluency slightly more important
    
    w_rate, w_pause, w_vocab, w_fluency = weights
    
    return (
        speech_rate_score * w_rate +
        pause_score * w_pause +
        vocabulary_score * w_vocab +
        fluency_score * w_fluency
    )
