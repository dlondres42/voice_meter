"""
Transcription and text comparison service using OpenAI Whisper API
"""
import tempfile
import os
import logging
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional
import Levenshtein
from openai import OpenAI

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for transcribing audio and comparing with expected text"""
    
    def __init__(self):
        """
        Initialize the transcription service with OpenAI API
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        logger.info("✅ OpenAI Whisper API client initialized")
    
    def transcribe_audio(self, audio_data: bytes, language: str = "pt") -> Dict:
        """
        Transcribe audio data to text using OpenAI Whisper API
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (default: Portuguese)
            
        Returns:
            Dict with transcription results
        """
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            logger.info(f"🎤 Transcribing audio via OpenAI Whisper API...")
            
            # Open the audio file and send to OpenAI
            with open(temp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            
            transcribed_text = transcript.text.strip()
            logger.info(f"✅ Transcription complete: {transcribed_text[:100]}...")
            
            # Extract segments if available
            segments = []
            if hasattr(transcript, 'segments') and transcript.segments:
                for segment in transcript.segments:
                    segments.append({
                        "text": segment.get("text", "").strip(),
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0)
                    })
            
            duration = transcript.duration if hasattr(transcript, 'duration') else 0
            
            return {
                "text": transcribed_text,
                "language": language,
                "segments": segments,
                "duration": duration
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison
        - Convert to lowercase
        - Remove punctuation
        - Normalize whitespace
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def compare_texts(self, expected_text: str, transcribed_text: str) -> Dict:
        """
        Compare expected text with transcribed text
        
        Args:
            expected_text: The text the user intended to say
            transcribed_text: The text transcribed from audio
            
        Returns:
            Dict with comparison metrics and details
        """
        # Normalize both texts
        expected_normalized = self.normalize_text(expected_text)
        transcribed_normalized = self.normalize_text(transcribed_text)
        
        # Split into words
        expected_words = expected_normalized.split()
        transcribed_words = transcribed_normalized.split()
        
        # Calculate similarity ratio (0-1)
        sequence_matcher = SequenceMatcher(None, expected_normalized, transcribed_normalized)
        similarity_ratio = sequence_matcher.ratio()
        
        # Calculate Levenshtein distance
        levenshtein_distance = Levenshtein.distance(expected_normalized, transcribed_normalized)
        
        # Calculate word-level accuracy
        word_accuracy = self._calculate_word_accuracy(expected_words, transcribed_words)
        
        # Find differences
        differences = self._find_differences(expected_words, transcribed_words)
        
        # Calculate pronunciation score (0-100)
        pronunciation_score = int(similarity_ratio * 100)
        
        # Generate feedback
        feedback = self._generate_feedback(
            pronunciation_score,
            differences,
            len(expected_words),
            len(transcribed_words)
        )
        
        return {
            "expected_text": expected_text,
            "transcribed_text": transcribed_text,
            "expected_normalized": expected_normalized,
            "transcribed_normalized": transcribed_normalized,
            "similarity_ratio": round(similarity_ratio, 4),
            "pronunciation_score": pronunciation_score,
            "levenshtein_distance": levenshtein_distance,
            "word_accuracy": round(word_accuracy, 4),
            "expected_word_count": len(expected_words),
            "transcribed_word_count": len(transcribed_words),
            "missing_words": differences["missing"],
            "extra_words": differences["extra"],
            "mispronounced_words": differences["mispronounced"],
            "feedback": feedback
        }
    
    def _calculate_word_accuracy(self, expected: List[str], transcribed: List[str]) -> float:
        """Calculate word-level accuracy"""
        if not expected:
            return 1.0 if not transcribed else 0.0
        
        matcher = SequenceMatcher(None, expected, transcribed)
        matching_blocks = matcher.get_matching_blocks()
        
        matched_words = sum(block.size for block in matching_blocks)
        return matched_words / len(expected)
    
    def _find_differences(self, expected: List[str], transcribed: List[str]) -> Dict:
        """Find missing, extra, and mispronounced words"""
        differences = {
            "missing": [],
            "extra": [],
            "mispronounced": []
        }
        
        matcher = SequenceMatcher(None, expected, transcribed)
        opcodes = matcher.get_opcodes()
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'delete':
                # Words in expected but not in transcribed
                differences["missing"].extend(expected[i1:i2])
            elif tag == 'insert':
                # Words in transcribed but not in expected
                differences["extra"].extend(transcribed[j1:j2])
            elif tag == 'replace':
                # Potentially mispronounced words
                expected_chunk = expected[i1:i2]
                transcribed_chunk = transcribed[j1:j2]
                
                for exp_word in expected_chunk:
                    # Find closest match in transcribed chunk
                    best_match = None
                    best_ratio = 0
                    for trans_word in transcribed_chunk:
                        ratio = SequenceMatcher(None, exp_word, trans_word).ratio()
                        if ratio > best_ratio:
                            best_ratio = ratio
                            best_match = trans_word
                    
                    if best_match and best_ratio > 0.5:
                        differences["mispronounced"].append({
                            "expected": exp_word,
                            "heard": best_match,
                            "similarity": round(best_ratio, 2)
                        })
                    else:
                        differences["missing"].append(exp_word)
        
        return differences
    
    def _generate_feedback(
        self, 
        score: int, 
        differences: Dict, 
        expected_count: int,
        transcribed_count: int
    ) -> str:
        """Generate human-readable feedback"""
        feedback_parts = []
        
        # Overall score feedback
        if score >= 90:
            feedback_parts.append("🎉 Excelente! Sua pronúncia está muito próxima do texto esperado.")
        elif score >= 75:
            feedback_parts.append("👍 Bom trabalho! Sua pronúncia está bem próxima do texto esperado.")
        elif score >= 50:
            feedback_parts.append("📈 Razoável. Há espaço para melhorias na pronúncia.")
        else:
            feedback_parts.append("💪 Continue praticando! A pronúncia precisa de mais atenção.")
        
        # Missing words feedback
        if differences["missing"]:
            missing_count = len(differences["missing"])
            if missing_count <= 3:
                feedback_parts.append(f"⚠️ Palavras não detectadas: {', '.join(differences['missing'][:5])}")
            else:
                feedback_parts.append(f"⚠️ {missing_count} palavras não foram detectadas.")
        
        # Mispronounced words feedback
        if differences["mispronounced"]:
            mispronounced = differences["mispronounced"][:3]  # Show top 3
            for item in mispronounced:
                feedback_parts.append(
                    f"🔄 '{item['expected']}' soou como '{item['heard']}'"
                )
        
        # Extra words feedback
        if differences["extra"]:
            extra_count = len(differences["extra"])
            if extra_count <= 3:
                feedback_parts.append(f"➕ Palavras extras detectadas: {', '.join(differences['extra'][:5])}")
            else:
                feedback_parts.append(f"➕ {extra_count} palavras extras foram detectadas.")
        
        # Word count comparison
        diff = transcribed_count - expected_count
        if abs(diff) > 2:
            if diff > 0:
                feedback_parts.append(f"📊 Você disse {diff} palavras a mais do que o esperado.")
            else:
                feedback_parts.append(f"📊 Você disse {abs(diff)} palavras a menos do que o esperado.")
        
        return " ".join(feedback_parts)


# Global instance (will be initialized on first use)
_transcription_service: Optional[TranscriptionService] = None

def get_transcription_service() -> TranscriptionService:
    """Get or create the transcription service singleton"""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
