# Backend Architecture

## 📁 Project Structure

```
backend/app/
├── __init__.py           # Package initialization with version
├── common/               # Shared utilities
│   ├── __init__.py
│   ├── constants.py      # Application constants
│   └── exceptions.py     # Custom exceptions
├── dto/                  # Data Transfer Objects
│   ├── __init__.py
│   └── analysis.py       # Analysis result dataclasses
├── enums/                # Enumerations
│   ├── __init__.py
│   ├── language.py       # Language enums
│   └── analysis.py       # Analysis enums
├── interfaces/           # Abstract interfaces
│   ├── __init__.py
│   └── services.py       # Service protocols
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── text.py           # Text processing utilities
│   ├── audio.py          # Audio processing utilities
│   └── metrics.py        # Metrics calculations
├── api/                  # API layer
│   ├── __init__.py
│   ├── api.py            # Main router
│   └── endpoints/        # Endpoint handlers
├── core/                 # Core configuration
│   ├── __init__.py
│   └── config.py         # Settings
├── db/                   # Database layer
│   ├── __init__.py
│   ├── base.py           # Base model
│   └── init_db.py        # DB initialization
├── models/               # ORM models
│   ├── __init__.py
│   ├── recording.py      # Recording model
│   └── speech.py         # Speech model
├── schemas/              # Pydantic schemas
│   ├── __init__.py
│   └── speech.py         # Speech schemas
└── services/             # Business logic
    ├── __init__.py
    ├── speech_analysis_service.py     # Original service
    ├── speech_analysis_service_v2.py  # Refactored service
    └── transcription_service.py       # Transcription service
```

## 🎯 Design Patterns Used

### 1. **Singleton Pattern**
Used for service instances to ensure single initialization:
```python
_speech_analysis_service: Optional[SpeechAnalysisService] = None

def get_speech_analysis_service() -> SpeechAnalysisService:
    global _speech_analysis_service
    if _speech_analysis_service is None:
        _speech_analysis_service = SpeechAnalysisService()
    return _speech_analysis_service
```

### 2. **Protocol Pattern (Structural Subtyping)**
Interfaces defined using `Protocol` for duck typing support:
```python
@runtime_checkable
class TranscriptionServiceInterface(Protocol):
    async def transcribe_audio(self, audio_path: str, ...) -> Dict[str, Any]: ...
```

### 3. **Data Transfer Object (DTO) Pattern**
Dataclasses for structured data transfer:
```python
@dataclass
class SpeechRateMetrics:
    words_per_minute: float
    syllables_per_second: float
    # ... other fields
```

### 4. **Strategy Pattern**
Language-specific configurations allow different strategies per language:
```python
FILLER_WORDS = {
    "pt-BR": {"tipo", "assim", "né", ...},
    "en-US": {"like", "um", "you know", ...},
}
```

### 5. **Factory Pattern**
Service creation through factory functions:
```python
def get_speech_analysis_service() -> SpeechAnalysisService:
    # Creates or returns existing instance
```

## 📦 Module Descriptions

### `common/`
**Purpose:** Shared resources used across the application.

- **constants.py**: Static configuration values
  - Language codes and defaults
  - Speech rate thresholds (WPM)
  - Pause duration thresholds
  - Filler words by language
  - Stopwords by language
  - Feedback messages (bilingual)

- **exceptions.py**: Custom exception hierarchy
  - `VoiceMeterException`: Base exception
  - `AudioProcessingError`: Audio issues
  - `TranscriptionError`: Whisper API errors
  - `LanguageDetectionError`: Detection failures
  - `ValidationError`: Input validation
  - `AnalysisError`: Analysis failures

### `dto/`
**Purpose:** Immutable data structures for transferring analysis results.

- **analysis.py**: Analysis result dataclasses
  - `SpeechRateMetrics`: WPM, syllables/sec, classification
  - `PauseMetrics`: Pause counts and durations
  - `VocabularyMetrics`: TTR, complexity, diversity
  - `FluencyMetrics`: Fillers, repetitions, corrections
  - `LanguageDetectionResult`: Detected language + confidence
  - `AdvancedAnalysisResult`: Complete analysis aggregate
  - `FeedbackItem`: Individual feedback message

### `enums/`
**Purpose:** Type-safe enumerations for categorization.

- **language.py**: Language definitions
  - `LanguageCode`: ISO codes (pt-BR, en-US)
  - `Language`: Display names

- **analysis.py**: Analysis categories
  - `SpeechRateClassification`: too_slow → too_fast
  - `FeedbackSeverity`: info → critical
  - `VocabularyLevel`: basic → expert
  - `PauseType`: micro → extended

### `interfaces/`
**Purpose:** Abstract contracts for dependency injection.

- **services.py**: Service protocols
  - `TranscriptionServiceInterface`
  - `TextComparisonServiceInterface`
  - `AnalysisServiceInterface`
  - `BaseService`: Abstract base with lifecycle
  - `BaseAnalyzer`: Abstract analyzer base

### `utils/`
**Purpose:** Stateless utility functions.

- **text.py**: Text processing
  - `normalize_text()`: Unicode normalization
  - `tokenize()`: Word tokenization
  - `count_syllables()`: Syllable counting (PT/EN)
  - `remove_punctuation()`: Clean text

- **audio.py**: Audio utilities
  - `validate_audio_format()`: Format validation
  - `get_mime_type()`: MIME type detection

- **metrics.py**: Metric calculations
  - `calculate_wpm()`: Words per minute
  - `calculate_ttr()`: Type-Token Ratio
  - `calculate_similarity()`: Text similarity
  - `calculate_*_score()`: Quality scores

## 🔄 Adding New Features

### Adding a New Language
1. Add to `enums/language.py`:
   ```python
   class LanguageCode(str, Enum):
       SPANISH = "es-ES"  # Add new language
   ```

2. Add constants in `common/constants.py`:
   ```python
   FILLER_WORDS["es-ES"] = {"pues", "bueno", ...}
   STOPWORDS["es-ES"] = {"el", "la", ...}
   FEEDBACK_MESSAGES["es-ES"] = {...}
   ```

3. Add syllable counting in `utils/text.py`:
   ```python
   def _count_syllables_spanish(word: str) -> int:
       ...
   ```

### Adding a New Metric
1. Create DTO in `dto/analysis.py`:
   ```python
   @dataclass
   class EmotionMetrics:
       sentiment: str
       confidence: float
   ```

2. Add calculation in `utils/metrics.py`

3. Integrate in service:
   ```python
   def analyze_emotion(self, text: str) -> EmotionMetrics:
       ...
   ```

### Adding a New Exception
1. Add to `common/exceptions.py`:
   ```python
   class RateLimitError(ExternalServiceError):
       def __init__(self, retry_after: int):
           super().__init__(
               "Rate limit exceeded",
               details={"retry_after": retry_after}
           )
   ```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific module tests
pytest tests/test_speech_analyzer.py
```

## 📝 Code Style

- Follow PEP 8
- Use type hints everywhere
- Document with docstrings (Google style)
- Maximum line length: 100 characters
- Sort imports with isort

## 🚀 Future Improvements

- [ ] Add Redis caching for repeated analyses
- [ ] Implement async analysis pipeline
- [ ] Add WebSocket for real-time analysis
- [ ] Add more languages (Spanish, French)
- [ ] Add emotion detection
- [ ] Add voice quality metrics
