"""
Advanced Speech Analysis Service
Based on research from "User speech rates and preferences for system speech rates"
(Dowding et al., International Journal of Human-Computer Studies, 2024)

This service provides comprehensive speech metrics including:
- Speech Rate (SR) and Articulation Rate (AR)
- Pause analysis
- Vocabulary complexity
- Fluency metrics
- Speaking style classification
- Multi-language support (Portuguese and English)
"""
import re
import math
import logging
from typing import Dict, List, Optional, Tuple
from collections import Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# =============================================================================
# PORTUGUESE LANGUAGE CONFIGURATION
# =============================================================================
PORTUGUESE_VOWELS = set('aeiouáéíóúàèìòùâêîôûãõäëïöü')
PORTUGUESE_DIGRAPHS = ['lh', 'nh', 'ch', 'rr', 'ss', 'qu', 'gu']

# Common filler words in Portuguese (hesitation markers)
PORTUGUESE_FILLERS = {
    'é', 'hum', 'uhm', 'ah', 'eh', 'ahn', 'então', 'tipo', 
    'né', 'sabe', 'entende', 'assim', 'bom', 'bem', 'olha',
    'veja', 'pois', 'enfim', 'basicamente', 'literalmente'
}

# Portuguese function words for lexical density
PORTUGUESE_FUNCTION_WORDS = {
    'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
    'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos',
    'por', 'para', 'com', 'sem', 'sob', 'sobre',
    'e', 'ou', 'mas', 'porém', 'contudo', 'todavia',
    'que', 'qual', 'quais', 'quem', 'onde', 'quando', 'como',
    'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
    'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes',
    'meu', 'minha', 'teu', 'tua', 'seu', 'sua', 'nosso', 'nossa',
    'este', 'esta', 'esse', 'essa', 'aquele', 'aquela',
    'isto', 'isso', 'aquilo', 'ser', 'estar', 'ter', 'haver',
    'é', 'são', 'foi', 'foram', 'será', 'seria'
}

# Portuguese complex word suffixes
PORTUGUESE_COMPLEX_SUFFIXES = [
    'mente', 'ção', 'ções', 'dade', 'ismo', 'ista', 
    'ível', 'ável', 'ência', 'ância', 'mento', 'tivo'
]

# =============================================================================
# ENGLISH LANGUAGE CONFIGURATION
# =============================================================================
ENGLISH_VOWELS = set('aeiouy')

# Common filler words in English (hesitation markers)
ENGLISH_FILLERS = {
    'um', 'uh', 'uhm', 'er', 'ah', 'like', 'you know', 'basically',
    'literally', 'actually', 'honestly', 'right', 'okay', 'so',
    'well', 'i mean', 'kind of', 'sort of', 'anyway', 'whatever'
}

# English function words for lexical density
ENGLISH_FUNCTION_WORDS = {
    'the', 'a', 'an', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'mine', 'yours', 'hers', 'ours', 'theirs',
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
    'and', 'or', 'but', 'if', 'because', 'as', 'until', 'while',
    'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
    'who', 'whom', 'which', 'what', 'where', 'when', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'just', 'also', 'now', 'here', 'there', 'then'
}

# English complex word suffixes
ENGLISH_COMPLEX_SUFFIXES = [
    'tion', 'sion', 'ness', 'ment', 'able', 'ible', 'ful', 'less',
    'ous', 'ive', 'ity', 'ism', 'ist', 'ology', 'ical', 'ally'
]

# =============================================================================
# LANGUAGE DETECTION WORDS
# =============================================================================
# High-frequency unique words for each language
PORTUGUESE_MARKERS = {
    'que', 'não', 'uma', 'para', 'com', 'está', 'isso', 'mais',
    'como', 'mas', 'por', 'muito', 'também', 'foi', 'são', 'tem',
    'seu', 'sua', 'ele', 'ela', 'você', 'nós', 'eles', 'nosso',
    'esse', 'essa', 'aqui', 'onde', 'quando', 'porque', 'então',
    'até', 'depois', 'agora', 'sempre', 'ainda', 'apenas', 'sobre',
    'já', 'fazer', 'pode', 'deve', 'vai', 'vou', 'estou', 'tinha',
    'seria', 'podemos', 'temos', 'precisamos', 'conseguimos'
}

ENGLISH_MARKERS = {
    'the', 'and', 'that', 'have', 'for', 'not', 'with', 'you',
    'this', 'but', 'his', 'from', 'they', 'were', 'been', 'have',
    'their', 'would', 'there', 'what', 'about', 'which', 'when',
    'make', 'can', 'will', 'more', 'these', 'want', 'way', 'could',
    'people', 'than', 'first', 'been', 'who', 'its', 'now', 'find',
    'because', 'should', 'think', 'know', 'going', 'need', 'really'
}

COMPLEX_WORD_MIN_LENGTH = 10


@dataclass
class SpeechRateMetrics:
    """Metrics related to speech rate based on the paper"""
    speaking_rate_spm: float  # Syllables per minute (with pauses)
    articulation_rate_spm: float  # Syllables per minute (without pauses)
    words_per_minute: float
    total_duration_seconds: float
    speech_duration_seconds: float  # Duration without pauses
    pause_duration_seconds: float
    classification: str  # 'slow', 'medium', 'fast'


@dataclass
class PauseMetrics:
    """Metrics related to pauses in speech"""
    total_pauses: int
    total_pause_duration: float
    average_pause_duration: float
    longest_pause: float
    pauses_per_minute: float
    pause_ratio: float  # Ratio of pause time to total time


@dataclass
class VocabularyMetrics:
    """Metrics related to vocabulary complexity"""
    total_words: int
    unique_words: int
    vocabulary_richness: float  # Type-Token Ratio (TTR)
    average_word_length: float
    complex_words_count: int
    complex_words_ratio: float
    filler_words_count: int
    filler_words_ratio: float
    lexical_density: float  # Content words / Total words


@dataclass
class FluencyMetrics:
    """Metrics related to speech fluency"""
    fluency_score: float  # 0-100
    hesitation_rate: float  # Hesitations per minute
    repetition_count: int
    self_corrections_count: int
    incomplete_sentences: int


@dataclass
class LanguageDetection:
    """Language detection result"""
    detected_language: str  # 'pt-BR', 'en-US', 'unknown'
    confidence: float  # 0-1
    portuguese_score: float
    english_score: float


@dataclass 
class ComprehensiveSpeechAnalysis:
    """Complete speech analysis results"""
    language: LanguageDetection
    speech_rate: SpeechRateMetrics
    pauses: PauseMetrics
    vocabulary: VocabularyMetrics
    fluency: FluencyMetrics
    overall_score: float
    feedback: List[str]
    recommendations: List[str]


class SpeechAnalysisService:
    """
    Advanced speech analysis service implementing metrics from speech research.
    Supports both Portuguese (pt-BR) and English (en-US) with automatic detection.
    
    Reference values from the paper (English speakers):
    - Mean Speaking Rate: ~199 syll/min (spontaneous), ~237 syll/min (read)
    - Mean Articulation Rate: ~246 syll/min (spontaneous), ~288 syll/min (read)
    - Fast speakers: > 263 syll/min AR
    - Slow speakers: < 228 syll/min AR
    
    For Portuguese, rates are typically slightly lower.
    """
    
    # Reference values (can vary by language)
    SPEECH_RATE_THRESHOLDS = {
        'pt-BR': {'slow': 180, 'fast': 250},
        'en-US': {'slow': 200, 'fast': 280}
    }
    
    # Ideal speaking rates for presentations (words per minute)
    IDEAL_SPEAKING_RATE = {
        'pt-BR': {'min': 140, 'max': 170},
        'en-US': {'min': 150, 'max': 180}
    }
    
    # Pause thresholds (in seconds)
    MIN_PAUSE_DURATION = 0.25  # 250ms as per paper
    LONG_PAUSE_THRESHOLD = 2.0
    
    def __init__(self):
        logger.info("✅ Speech Analysis Service initialized (PT-BR & EN-US)")
    
    def detect_language(self, text: str) -> LanguageDetection:
        """
        Detect whether the text is in Portuguese or English.
        Uses word frequency analysis with language-specific markers.
        
        Args:
            text: The transcribed text to analyze
            
        Returns:
            LanguageDetection with detected language and confidence
        """
        words = self._extract_words(text)
        words_set = set(words)
        total_words = len(words)
        
        if total_words == 0:
            return LanguageDetection(
                detected_language='unknown',
                confidence=0.0,
                portuguese_score=0.0,
                english_score=0.0
            )
        
        # Count matches for each language
        pt_matches = len(words_set.intersection(PORTUGUESE_MARKERS))
        en_matches = len(words_set.intersection(ENGLISH_MARKERS))
        
        # Also check for Portuguese-specific characters
        pt_chars = len(re.findall(r'[áéíóúàâêôãõç]', text.lower()))
        pt_char_bonus = min(pt_chars / max(len(text), 1) * 100, 5)  # Up to 5 bonus points
        
        # Calculate scores (normalized)
        pt_score = (pt_matches / len(PORTUGUESE_MARKERS)) * 100 + pt_char_bonus
        en_score = (en_matches / len(ENGLISH_MARKERS)) * 100
        
        # Determine language
        if pt_score > en_score and pt_score > 5:
            detected = 'pt-BR'
            confidence = min(pt_score / (pt_score + en_score + 0.1), 0.99)
        elif en_score > pt_score and en_score > 5:
            detected = 'en-US'
            confidence = min(en_score / (pt_score + en_score + 0.1), 0.99)
        else:
            # Default to Portuguese if uncertain
            detected = 'pt-BR'
            confidence = 0.5
        
        logger.info(f"🌍 Language detected: {detected} (confidence: {confidence:.2f})")
        logger.info(f"   PT score: {pt_score:.1f}, EN score: {en_score:.1f}")
        
        return LanguageDetection(
            detected_language=detected,
            confidence=round(confidence, 2),
            portuguese_score=round(pt_score, 2),
            english_score=round(en_score, 2)
        )
    
    def count_syllables(self, word: str, language: str = 'pt-BR') -> int:
        """
        Count syllables in a word based on language.
        
        Args:
            word: The word to count syllables for
            language: 'pt-BR' or 'en-US'
            
        Returns:
            Number of syllables
        """
        word = word.lower().strip()
        if not word:
            return 0
        
        # Remove punctuation
        word = re.sub(r'[^\w]', '', word)
        if not word:
            return 0
        
        if language == 'en-US':
            return self._count_syllables_english(word)
        else:
            return self._count_syllables_portuguese(word)
    
    def _count_syllables_portuguese(self, word: str) -> int:
        """Count syllables in a Portuguese word."""
        syllables = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in PORTUGUESE_VOWELS
            if is_vowel and not prev_is_vowel:
                syllables += 1
            prev_is_vowel = is_vowel
        
        return max(1, syllables)
    
    def _count_syllables_english(self, word: str) -> int:
        """
        Count syllables in an English word.
        Uses vowel counting with English-specific rules.
        """
        word = word.lower()
        syllables = 0
        prev_is_vowel = False
        
        for i, char in enumerate(word):
            is_vowel = char in ENGLISH_VOWELS
            
            # 'e' at end of word is usually silent
            if char == 'e' and i == len(word) - 1 and syllables > 0:
                continue
            
            if is_vowel and not prev_is_vowel:
                syllables += 1
            
            prev_is_vowel = is_vowel
        
        # Handle special cases
        # Words ending in 'le' preceded by consonant
        if word.endswith('le') and len(word) > 2 and word[-3] not in ENGLISH_VOWELS:
            syllables += 1
        
        return max(1, syllables)
    
    def count_syllables_text(self, text: str, language: str = 'pt-BR') -> int:
        """Count total syllables in a text."""
        words = self._extract_words(text)
        return sum(self.count_syllables(word, language) for word in words)
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text, removing punctuation."""
        text = text.lower()
        # Support both Portuguese and English characters
        words = re.findall(r'\b[a-záéíóúàèìòùâêîôûãõäëïöüç]+\b', text)
        return words
    
    def analyze_speech_rate(
        self, 
        text: str, 
        total_duration: float,
        language: str = 'pt-BR',
        segments: Optional[List[Dict]] = None
    ) -> SpeechRateMetrics:
        """
        Analyze speech rate metrics.
        
        Args:
            text: Transcribed text
            total_duration: Total audio duration in seconds
            language: 'pt-BR' or 'en-US'
            segments: Optional list of segments with timing info
            
        Returns:
            SpeechRateMetrics with detailed rate analysis
        """
        words = self._extract_words(text)
        total_syllables = self.count_syllables_text(text, language)
        total_words = len(words)
        
        if total_duration <= 0:
            total_duration = 1.0  # Avoid division by zero
        
        # Calculate pause duration from segments if available
        pause_duration = 0.0
        if segments and len(segments) > 1:
            for i in range(1, len(segments)):
                gap = segments[i].get('start', 0) - segments[i-1].get('end', 0)
                if gap >= self.MIN_PAUSE_DURATION:
                    pause_duration += gap
        
        speech_duration = max(0.1, total_duration - pause_duration)
        
        # Calculate rates (per minute)
        speaking_rate_spm = (total_syllables / total_duration) * 60
        articulation_rate_spm = (total_syllables / speech_duration) * 60
        words_per_minute = (total_words / total_duration) * 60
        
        # Get thresholds for the detected language
        thresholds = self.SPEECH_RATE_THRESHOLDS.get(language, self.SPEECH_RATE_THRESHOLDS['pt-BR'])
        
        # Classify speaker pace
        if articulation_rate_spm < thresholds['slow']:
            classification = 'slow'
        elif articulation_rate_spm > thresholds['fast']:
            classification = 'fast'
        else:
            classification = 'medium'
        
        return SpeechRateMetrics(
            speaking_rate_spm=round(speaking_rate_spm, 1),
            articulation_rate_spm=round(articulation_rate_spm, 1),
            words_per_minute=round(words_per_minute, 1),
            total_duration_seconds=round(total_duration, 2),
            speech_duration_seconds=round(speech_duration, 2),
            pause_duration_seconds=round(pause_duration, 2),
            classification=classification
        )
    
    def analyze_pauses(
        self,
        total_duration: float,
        segments: Optional[List[Dict]] = None
    ) -> PauseMetrics:
        """
        Analyze pause patterns in speech.
        
        Pauses are important indicators of:
        - Hesitation and uncertainty
        - Natural breathing patterns
        - Emphasis and dramatic effect
        """
        pauses = []
        
        if segments and len(segments) > 1:
            for i in range(1, len(segments)):
                gap = segments[i].get('start', 0) - segments[i-1].get('end', 0)
                if gap >= self.MIN_PAUSE_DURATION:
                    pauses.append(gap)
        
        total_pauses = len(pauses)
        total_pause_duration = sum(pauses)
        
        if total_pauses > 0:
            average_pause = total_pause_duration / total_pauses
            longest_pause = max(pauses)
        else:
            average_pause = 0.0
            longest_pause = 0.0
        
        if total_duration > 0:
            pauses_per_minute = (total_pauses / total_duration) * 60
            pause_ratio = total_pause_duration / total_duration
        else:
            pauses_per_minute = 0.0
            pause_ratio = 0.0
        
        return PauseMetrics(
            total_pauses=total_pauses,
            total_pause_duration=round(total_pause_duration, 2),
            average_pause_duration=round(average_pause, 2),
            longest_pause=round(longest_pause, 2),
            pauses_per_minute=round(pauses_per_minute, 1),
            pause_ratio=round(pause_ratio, 3)
        )
    
    def analyze_vocabulary(self, text: str, language: str = 'pt-BR') -> VocabularyMetrics:
        """
        Analyze vocabulary complexity and richness.
        
        Args:
            text: The transcribed text
            language: 'pt-BR' or 'en-US'
        
        Metrics include:
        - Type-Token Ratio (vocabulary richness)
        - Complex word usage
        - Filler word frequency
        - Lexical density
        """
        words = self._extract_words(text)
        total_words = len(words)
        
        if total_words == 0:
            return VocabularyMetrics(
                total_words=0,
                unique_words=0,
                vocabulary_richness=0.0,
                average_word_length=0.0,
                complex_words_count=0,
                complex_words_ratio=0.0,
                filler_words_count=0,
                filler_words_ratio=0.0,
                lexical_density=0.0
            )
        
        # Unique words (Type-Token Ratio)
        unique_words = len(set(words))
        vocabulary_richness = unique_words / total_words
        
        # Average word length
        total_length = sum(len(word) for word in words)
        average_word_length = total_length / total_words
        
        # Get language-specific settings
        if language == 'en-US':
            filler_words = ENGLISH_FILLERS
            function_words = ENGLISH_FUNCTION_WORDS
            complex_suffixes = ENGLISH_COMPLEX_SUFFIXES
        else:
            filler_words = PORTUGUESE_FILLERS
            function_words = PORTUGUESE_FUNCTION_WORDS
            complex_suffixes = PORTUGUESE_COMPLEX_SUFFIXES
        
        # Complex words (long words or with complex suffixes)
        complex_words = []
        for word in words:
            is_complex = (
                len(word) >= COMPLEX_WORD_MIN_LENGTH or
                any(word.endswith(suffix) for suffix in complex_suffixes)
            )
            if is_complex:
                complex_words.append(word)
        
        complex_words_count = len(complex_words)
        complex_words_ratio = complex_words_count / total_words
        
        # Filler words
        filler_count = sum(1 for word in words if word in filler_words)
        filler_ratio = filler_count / total_words
        
        # Lexical density (content words vs function words)
        content_words = sum(1 for word in words if word not in function_words)
        lexical_density = content_words / total_words
        
        return VocabularyMetrics(
            total_words=total_words,
            unique_words=unique_words,
            vocabulary_richness=round(vocabulary_richness, 3),
            average_word_length=round(average_word_length, 2),
            complex_words_count=complex_words_count,
            complex_words_ratio=round(complex_words_ratio, 3),
            filler_words_count=filler_count,
            filler_words_ratio=round(filler_ratio, 3),
            lexical_density=round(lexical_density, 3)
        )
    
    def analyze_fluency(
        self,
        text: str,
        total_duration: float,
        segments: Optional[List[Dict]] = None
    ) -> FluencyMetrics:
        """
        Analyze speech fluency.
        
        Fluency indicators:
        - Hesitation rate (long pauses)
        - Word repetitions
        - Self-corrections
        - Incomplete sentences
        """
        words = self._extract_words(text)
        
        # Count repetitions (consecutive identical words)
        repetitions = 0
        for i in range(1, len(words)):
            if words[i] == words[i-1]:
                repetitions += 1
        
        # Count self-corrections (words followed by similar words)
        self_corrections = 0
        for i in range(1, len(words)):
            if words[i] != words[i-1]:
                # Check if words are similar (possible correction)
                from difflib import SequenceMatcher
                ratio = SequenceMatcher(None, words[i-1], words[i]).ratio()
                if 0.5 < ratio < 0.9:  # Similar but not identical
                    self_corrections += 1
        
        # Count incomplete sentences (very rough estimate)
        sentences = re.split(r'[.!?]', text)
        incomplete = sum(1 for s in sentences if len(s.strip().split()) < 3 and len(s.strip()) > 0)
        
        # Count hesitations (long pauses)
        hesitations = 0
        if segments and len(segments) > 1:
            for i in range(1, len(segments)):
                gap = segments[i].get('start', 0) - segments[i-1].get('end', 0)
                if gap >= self.LONG_PAUSE_THRESHOLD:
                    hesitations += 1
        
        # Calculate hesitation rate
        if total_duration > 0:
            hesitation_rate = (hesitations / total_duration) * 60
        else:
            hesitation_rate = 0.0
        
        # Calculate fluency score (0-100)
        # Penalize: repetitions, self-corrections, hesitations, incomplete sentences
        base_score = 100
        penalty = 0
        
        if len(words) > 0:
            penalty += (repetitions / len(words)) * 20
            penalty += (self_corrections / len(words)) * 15
            penalty += hesitation_rate * 5
            penalty += incomplete * 3
        
        fluency_score = max(0, min(100, base_score - penalty))
        
        return FluencyMetrics(
            fluency_score=round(fluency_score, 1),
            hesitation_rate=round(hesitation_rate, 2),
            repetition_count=repetitions,
            self_corrections_count=self_corrections,
            incomplete_sentences=incomplete
        )
    
    def generate_feedback(
        self,
        language_detection: LanguageDetection,
        speech_rate: SpeechRateMetrics,
        pauses: PauseMetrics,
        vocabulary: VocabularyMetrics,
        fluency: FluencyMetrics
    ) -> Tuple[List[str], List[str]]:
        """Generate human-readable feedback and recommendations in the detected language."""
        feedback = []
        recommendations = []
        
        lang = language_detection.detected_language
        ideal_rate = self.IDEAL_SPEAKING_RATE.get(lang, self.IDEAL_SPEAKING_RATE['pt-BR'])
        
        # Language-specific messages
        if lang == 'en-US':
            # English feedback
            feedback.append(f"🌍 Language detected: English (confidence: {language_detection.confidence:.0%})")
            
            # Speech rate feedback
            if speech_rate.classification == 'fast':
                feedback.append("🏃 You are speaking relatively fast.")
                recommendations.append("Try to slow down a bit for better comprehension.")
            elif speech_rate.classification == 'slow':
                feedback.append("🐢 Your speaking pace is slow.")
                recommendations.append("Consider speeding up slightly to maintain engagement.")
            else:
                feedback.append("✅ Your speaking pace is appropriate.")
            
            # Words per minute feedback
            wpm = speech_rate.words_per_minute
            if wpm < ideal_rate['min']:
                feedback.append(f"📊 Rate: {wpm:.0f} words/min (below ideal: {ideal_rate['min']}-{ideal_rate['max']}).")
            elif wpm > ideal_rate['max']:
                feedback.append(f"📊 Rate: {wpm:.0f} words/min (above ideal: {ideal_rate['min']}-{ideal_rate['max']}).")
            else:
                feedback.append(f"📊 Rate: {wpm:.0f} words/min (within ideal range!).")
            
            # Pause feedback
            if pauses.pause_ratio > 0.3:
                feedback.append("⏸️ Many pauses detected.")
                recommendations.append("Try to reduce pauses for better fluency.")
            elif pauses.pause_ratio < 0.1 and speech_rate.total_duration_seconds > 10:
                feedback.append("⚡ Few pauses - you're speaking non-stop.")
                recommendations.append("Strategic pauses help comprehension.")
            
            if pauses.longest_pause > 3.0:
                feedback.append(f"⚠️ Long pause detected: {pauses.longest_pause:.1f}s")
            
            # Vocabulary feedback
            if vocabulary.vocabulary_richness < 0.4:
                feedback.append("📝 Repetitive vocabulary detected.")
                recommendations.append("Try using synonyms to enrich your speech.")
            elif vocabulary.vocabulary_richness > 0.7:
                feedback.append("📚 Excellent vocabulary variety!")
            
            if vocabulary.filler_words_ratio > 0.1:
                feedback.append(f"💬 High use of filler words ({vocabulary.filler_words_count} detected).")
                recommendations.append("Reduce use of 'like', 'um', 'you know', etc.")
            
            if vocabulary.complex_words_ratio > 0.15:
                feedback.append("🎓 Good use of complex/technical vocabulary.")
            
            # Fluency feedback
            if fluency.fluency_score >= 80:
                feedback.append("🌟 Excellent fluency!")
            elif fluency.fluency_score >= 60:
                feedback.append("👍 Good overall fluency.")
            else:
                feedback.append("📈 There's room to improve fluency.")
            
            if fluency.repetition_count > 3:
                feedback.append(f"🔄 {fluency.repetition_count} word repetitions detected.")
                recommendations.append("Avoid repeating words consecutively.")
            
            if fluency.self_corrections_count > 2:
                feedback.append(f"✏️ {fluency.self_corrections_count} self-corrections detected.")
                recommendations.append("Practice more to reduce self-corrections.")
        
        else:
            # Portuguese feedback (default)
            feedback.append(f"🌍 Idioma detectado: Português (confiança: {language_detection.confidence:.0%})")
            
            # Speech rate feedback
            if speech_rate.classification == 'fast':
                feedback.append("🏃 Você está falando relativamente rápido.")
                recommendations.append("Tente desacelerar um pouco para melhor compreensão.")
            elif speech_rate.classification == 'slow':
                feedback.append("🐢 Seu ritmo de fala está lento.")
                recommendations.append("Considere acelerar levemente para manter o engajamento.")
            else:
                feedback.append("✅ Seu ritmo de fala está adequado.")
            
            # Words per minute feedback
            wpm = speech_rate.words_per_minute
            if wpm < ideal_rate['min']:
                feedback.append(f"📊 Taxa: {wpm:.0f} palavras/min (abaixo do ideal: {ideal_rate['min']}-{ideal_rate['max']}).")
            elif wpm > ideal_rate['max']:
                feedback.append(f"📊 Taxa: {wpm:.0f} palavras/min (acima do ideal: {ideal_rate['min']}-{ideal_rate['max']}).")
            else:
                feedback.append(f"📊 Taxa: {wpm:.0f} palavras/min (dentro do ideal!).")
            
            # Pause feedback
            if pauses.pause_ratio > 0.3:
                feedback.append("⏸️ Muitas pausas detectadas.")
                recommendations.append("Tente reduzir as pausas para maior fluidez.")
            elif pauses.pause_ratio < 0.1 and speech_rate.total_duration_seconds > 10:
                feedback.append("⚡ Poucas pausas - você está falando sem parar.")
                recommendations.append("Pausas estratégicas ajudam na compreensão.")
            
            if pauses.longest_pause > 3.0:
                feedback.append(f"⚠️ Pausa longa detectada: {pauses.longest_pause:.1f}s")
            
            # Vocabulary feedback
            if vocabulary.vocabulary_richness < 0.4:
                feedback.append("📝 Vocabulário repetitivo detectado.")
                recommendations.append("Tente usar sinônimos para enriquecer o texto.")
            elif vocabulary.vocabulary_richness > 0.7:
                feedback.append("📚 Excelente variedade de vocabulário!")
            
            if vocabulary.filler_words_ratio > 0.1:
                feedback.append(f"💬 Alto uso de palavras de preenchimento ({vocabulary.filler_words_count} detectadas).")
                recommendations.append("Reduza o uso de 'tipo', 'então', 'né', etc.")
            
            if vocabulary.complex_words_ratio > 0.15:
                feedback.append("🎓 Bom uso de vocabulário complexo/técnico.")
            
            # Fluency feedback
            if fluency.fluency_score >= 80:
                feedback.append("🌟 Excelente fluência!")
            elif fluency.fluency_score >= 60:
                feedback.append("👍 Boa fluência geral.")
            else:
                feedback.append("📈 Há espaço para melhorar a fluência.")
            
            if fluency.repetition_count > 3:
                feedback.append(f"🔄 {fluency.repetition_count} repetições de palavras detectadas.")
                recommendations.append("Evite repetir palavras consecutivamente.")
            
            if fluency.self_corrections_count > 2:
                feedback.append(f"✏️ {fluency.self_corrections_count} autocorreções detectadas.")
                recommendations.append("Pratique mais para reduzir autocorreções.")
        
        return feedback, recommendations
    
    def analyze_comprehensive(
        self,
        text: str,
        total_duration: float,
        segments: Optional[List[Dict]] = None,
        language_hint: Optional[str] = None
    ) -> ComprehensiveSpeechAnalysis:
        """
        Perform comprehensive speech analysis with automatic language detection.
        
        Args:
            text: Transcribed text
            total_duration: Total audio duration in seconds
            segments: Optional list of segments with timing info
            language_hint: Optional language hint ('pt', 'en', 'pt-BR', 'en-US')
            
        Returns:
            ComprehensiveSpeechAnalysis with all metrics
        """
        logger.info("🔍 Performing comprehensive speech analysis...")
        
        # Detect language (or use hint if provided)
        if language_hint:
            # Normalize hint
            if language_hint.lower() in ['pt', 'pt-br', 'portuguese']:
                detected_lang = LanguageDetection('pt-BR', 1.0, 100.0, 0.0)
            elif language_hint.lower() in ['en', 'en-us', 'english']:
                detected_lang = LanguageDetection('en-US', 1.0, 0.0, 100.0)
            else:
                detected_lang = self.detect_language(text)
        else:
            detected_lang = self.detect_language(text)
        
        language = detected_lang.detected_language
        logger.info(f"🌍 Using language: {language}")
        
        # Analyze all components with detected language
        speech_rate = self.analyze_speech_rate(text, total_duration, language, segments)
        pauses = self.analyze_pauses(total_duration, segments)
        vocabulary = self.analyze_vocabulary(text, language)
        fluency = self.analyze_fluency(text, total_duration, segments)
        
        # Generate feedback in the detected language
        feedback, recommendations = self.generate_feedback(
            detected_lang, speech_rate, pauses, vocabulary, fluency
        )
        
        # Calculate overall score (weighted average)
        overall_score = (
            self._score_speech_rate(speech_rate, language) * 0.25 +
            self._score_pauses(pauses) * 0.15 +
            self._score_vocabulary(vocabulary) * 0.25 +
            fluency.fluency_score * 0.35
        )
        
        logger.info(f"✅ Analysis complete. Language: {language}, Overall score: {overall_score:.1f}")
        
        return ComprehensiveSpeechAnalysis(
            language=detected_lang,
            speech_rate=speech_rate,
            pauses=pauses,
            vocabulary=vocabulary,
            fluency=fluency,
            overall_score=round(overall_score, 1),
            feedback=feedback,
            recommendations=recommendations
        )
    
    def _score_speech_rate(self, sr: SpeechRateMetrics, language: str = 'pt-BR') -> float:
        """Convert speech rate to a 0-100 score."""
        wpm = sr.words_per_minute
        ideal = self.IDEAL_SPEAKING_RATE.get(language, self.IDEAL_SPEAKING_RATE['pt-BR'])
        
        # Ideal range based on language
        if ideal['min'] <= wpm <= ideal['max']:
            return 100.0
        
        # Calculate distance from ideal range
        if wpm < ideal['min']:
            distance = ideal['min'] - wpm
        else:
            distance = wpm - ideal['max']
        
        # Penalize 2 points per wpm outside ideal
        return max(0, 100 - distance * 2)
    
    def _score_pauses(self, p: PauseMetrics) -> float:
        """Convert pause metrics to a 0-100 score."""
        # Ideal pause ratio: 0.1-0.25
        if 0.1 <= p.pause_ratio <= 0.25:
            base_score = 100.0
        elif p.pause_ratio < 0.1:
            base_score = 80.0  # Too few pauses
        else:
            # Too many pauses
            base_score = max(0, 100 - (p.pause_ratio - 0.25) * 200)
        
        # Penalize very long pauses
        if p.longest_pause > 3.0:
            base_score -= 10
        
        return max(0, base_score)
    
    def _score_vocabulary(self, v: VocabularyMetrics) -> float:
        """Convert vocabulary metrics to a 0-100 score."""
        score = 50.0  # Base score
        
        # Reward vocabulary richness (TTR)
        score += v.vocabulary_richness * 30
        
        # Reward complex words (up to a point)
        score += min(v.complex_words_ratio * 50, 15)
        
        # Penalize filler words
        score -= v.filler_words_ratio * 50
        
        return max(0, min(100, score))
    
    def to_dict(self, analysis: ComprehensiveSpeechAnalysis) -> Dict:
        """Convert analysis to dictionary for JSON serialization."""
        return {
            "language": {
                "detected_language": analysis.language.detected_language,
                "confidence": analysis.language.confidence,
                "portuguese_score": analysis.language.portuguese_score,
                "english_score": analysis.language.english_score
            },
            "speech_rate": {
                "speaking_rate_spm": analysis.speech_rate.speaking_rate_spm,
                "articulation_rate_spm": analysis.speech_rate.articulation_rate_spm,
                "words_per_minute": analysis.speech_rate.words_per_minute,
                "total_duration_seconds": analysis.speech_rate.total_duration_seconds,
                "speech_duration_seconds": analysis.speech_rate.speech_duration_seconds,
                "pause_duration_seconds": analysis.speech_rate.pause_duration_seconds,
                "classification": analysis.speech_rate.classification
            },
            "pauses": {
                "total_pauses": analysis.pauses.total_pauses,
                "total_pause_duration": analysis.pauses.total_pause_duration,
                "average_pause_duration": analysis.pauses.average_pause_duration,
                "longest_pause": analysis.pauses.longest_pause,
                "pauses_per_minute": analysis.pauses.pauses_per_minute,
                "pause_ratio": analysis.pauses.pause_ratio
            },
            "vocabulary": {
                "total_words": analysis.vocabulary.total_words,
                "unique_words": analysis.vocabulary.unique_words,
                "vocabulary_richness": analysis.vocabulary.vocabulary_richness,
                "average_word_length": analysis.vocabulary.average_word_length,
                "complex_words_count": analysis.vocabulary.complex_words_count,
                "complex_words_ratio": analysis.vocabulary.complex_words_ratio,
                "filler_words_count": analysis.vocabulary.filler_words_count,
                "filler_words_ratio": analysis.vocabulary.filler_words_ratio,
                "lexical_density": analysis.vocabulary.lexical_density
            },
            "fluency": {
                "fluency_score": analysis.fluency.fluency_score,
                "hesitation_rate": analysis.fluency.hesitation_rate,
                "repetition_count": analysis.fluency.repetition_count,
                "self_corrections_count": analysis.fluency.self_corrections_count,
                "incomplete_sentences": analysis.fluency.incomplete_sentences
            },
            "overall_score": analysis.overall_score,
            "feedback": analysis.feedback,
            "recommendations": analysis.recommendations
        }


# Global instance
_speech_analysis_service: Optional[SpeechAnalysisService] = None

def get_speech_analysis_service() -> SpeechAnalysisService:
    """Get or create the speech analysis service singleton."""
    global _speech_analysis_service
    if _speech_analysis_service is None:
        _speech_analysis_service = SpeechAnalysisService()
    return _speech_analysis_service
