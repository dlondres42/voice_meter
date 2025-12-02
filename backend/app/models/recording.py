from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import Base


class Recording(Base):
    """Database model for speech recordings - focused on Presentation mode"""
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Recording metadata
    category = Column(String(50), nullable=False, default="presentation")
    duration_seconds = Column(Float, nullable=False)
    
    # Text comparison fields
    expected_text = Column(Text, nullable=True)  # User's intended speech text
    transcribed_text = Column(Text, nullable=True)  # Whisper transcription result
    
    # Comparison metrics
    similarity_ratio = Column(Float, nullable=True)  # 0-1 ratio
    pronunciation_score = Column(Integer, nullable=True)  # 0-100 score
    word_accuracy = Column(Float, nullable=True)  # 0-1 ratio
    levenshtein_distance = Column(Integer, nullable=True)
    expected_word_count = Column(Integer, nullable=True)
    transcribed_word_count = Column(Integer, nullable=True)
    
    # Difference details (JSON)
    missing_words_json = Column(Text, nullable=True)  # JSON array
    extra_words_json = Column(Text, nullable=True)  # JSON array
    mispronounced_words_json = Column(Text, nullable=True)  # JSON array
    
    # Primary metrics (Articulation Rate) - kept for backward compatibility
    words_per_minute = Column(Float, nullable=False)
    speech_rate = Column(Float, nullable=False)
    articulation_rate = Column(Float, nullable=False)
    ideal_min_ppm = Column(Integer, nullable=False, default=140)
    ideal_max_ppm = Column(Integer, nullable=False, default=160)
    is_within_range = Column(Boolean, nullable=False)
    
    # Advanced metrics
    active_speech_time = Column(Float, nullable=False)
    silence_ratio = Column(Float, nullable=False)
    pause_count = Column(Integer, nullable=False)
    avg_pause_duration = Column(Float, nullable=False)
    pacing_consistency = Column(Float, nullable=False)
    local_variation_detected = Column(Boolean, nullable=False)
    intelligibility_score = Column(Float, nullable=False)
    
    # Overall score
    overall_score = Column(Integer, nullable=False)  # 0-100
    
    # Feedback and confidence
    feedback = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Volume metrics (for screen 7 chart)
    volume_min_db = Column(Float)
    volume_max_db = Column(Float)
    volume_avg_db = Column(Float)
    volume_data_json = Column(Text)  # JSON array of volume over time
    
    # Additional analysis
    recommendations = Column(Text)  # JSON array of recommendations
    patterns_identified = Column(Text)  # JSON array of patterns
    
    # Advanced speech analysis (based on research paper)
    # Language detection
    detected_language = Column(String(10), nullable=True)  # 'pt-BR', 'en-US'
    language_confidence = Column(Float, nullable=True)
    
    # Speech Rate Metrics
    speaking_rate_spm = Column(Float, nullable=True)  # Syllables per minute (with pauses)
    articulation_rate_spm = Column(Float, nullable=True)  # Syllables per minute (without pauses)
    speech_duration_seconds = Column(Float, nullable=True)  # Duration without pauses
    pause_duration_total = Column(Float, nullable=True)  # Total pause time
    speech_rate_classification = Column(String(20), nullable=True)  # slow/medium/fast
    
    # Pause Metrics
    total_pauses = Column(Integer, nullable=True)
    total_pause_duration = Column(Float, nullable=True)
    average_pause_duration = Column(Float, nullable=True)
    longest_pause = Column(Float, nullable=True)
    pauses_per_minute = Column(Float, nullable=True)
    pause_ratio = Column(Float, nullable=True)
    
    # Vocabulary Metrics
    total_words = Column(Integer, nullable=True)
    unique_words = Column(Integer, nullable=True)
    vocabulary_richness = Column(Float, nullable=True)  # Type-Token Ratio
    average_word_length = Column(Float, nullable=True)
    complex_words_count = Column(Integer, nullable=True)
    complex_words_ratio = Column(Float, nullable=True)
    filler_words_count = Column(Integer, nullable=True)
    filler_words_ratio = Column(Float, nullable=True)
    lexical_density = Column(Float, nullable=True)
    
    # Fluency Metrics
    fluency_score = Column(Float, nullable=True)  # 0-100
    hesitation_rate = Column(Float, nullable=True)
    repetition_count = Column(Integer, nullable=True)
    self_corrections_count = Column(Integer, nullable=True)
    incomplete_sentences = Column(Integer, nullable=True)
    
    # Advanced analysis JSON (full analysis)
    advanced_analysis_json = Column(Text, nullable=True)
    
    # User notes
    title = Column(String(200))  # User-provided title
    notes = Column(Text)  # User notes


class UserStatistics(Base):
    """Aggregated user statistics (single row per user, updated periodically)"""
    __tablename__ = "user_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Overall stats
    total_recordings = Column(Integer, default=0)
    total_duration_seconds = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    member_since = Column(DateTime(timezone=True), server_default=func.now())
    
    # Progress tracking
    score_trend = Column(Float, default=0.0)  # +/- points this month
    recordings_this_week = Column(Integer, default=0)
    recordings_this_month = Column(Integer, default=0)
    
    # Best metrics
    best_score = Column(Integer, default=0)
    best_score_date = Column(DateTime(timezone=True))
    
    # Evolution data (for screen 9 chart)
    evolution_data_json = Column(Text)  # JSON array of scores over last 30 days
