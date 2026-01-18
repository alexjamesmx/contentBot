# TDD Workflow for ContentBot

**Test-Driven Development** means writing tests BEFORE implementing features. This ensures code quality, prevents regressions, and makes refactoring safe.

For ContentBot, we follow the **Red-Green-Refactor cycle** with a target of **85%+ code coverage** for `src/`.

---

## Table of Contents

1. [TDD Philosophy](#tdd-philosophy)
2. [Red-Green-Refactor Cycle](#red-green-refactor-cycle)
3. [Test Organization](#test-organization)
4. [Running Tests](#running-tests)
5. [Practical Examples](#practical-examples)
6. [Testing Patterns](#testing-patterns)
7. [Coverage Goals](#coverage-goals)
8. [Common Pitfalls](#common-pitfalls)

---

## TDD Philosophy

### Why Test-First Development?

**TDD prevents three critical failures:**

1. **Feature creep** - Only code what the test requires (YAGNI principle)
2. **Regressions** - Existing tests catch breaking changes immediately
3. **Design issues** - Tests force you to write testable, modular code

### ContentBot Application

For a **monetization-critical system** like ContentBot:
- Videos MUST be 60-90 seconds (Creator Rewards requirement)
- Subtitles MUST sync with audio (TDD ensures this)
- Pipeline MUST not break (tests prevent it)

**Every feature** (story genre, effect type, API endpoint) must have tests before code.

---

## Red-Green-Refactor Cycle

The TDD cycle has three distinct phases:

### Phase 1: RED - Write Failing Test

Write a test that expresses the desired behavior but FAILS because the feature doesn't exist yet.

```bash
pytest tests/unit/test_new_feature.py -v
# Output: FAILED test_feature_does_something
```

### Phase 2: GREEN - Make Test Pass (Minimal Code)

Implement the minimum code required to make the test pass. Don't over-engineer.

```bash
pytest tests/unit/test_new_feature.py -v
# Output: PASSED test_feature_does_something
```

### Phase 3: REFACTOR - Clean Up

Improve code quality while keeping tests green. This is when you:
- Extract helper functions
- Remove duplication
- Improve variable names
- Add documentation

```bash
pytest tests/unit/test_new_feature.py -v
# Output: PASSED test_feature_does_something (after refactoring)
```

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                     # Fast, isolated tests (no external APIs)
│   ├── test_story_generator.py
│   ├── test_subtitle_generator.py
│   ├── test_effect_agent.py
│   └── ...
├── integration/              # Tests that call real APIs (slower)
│   ├── test_pipeline.py
│   ├── test_api_endpoints.py
│   └── ...
└── conftest.py              # Shared fixtures for all tests
```

### Test File Naming

- **Unit test files**: `tests/unit/test_<module_name>.py`
- **Integration test files**: `tests/integration/test_<feature_name>.py`
- **Test functions**: `test_<feature>_<condition>_<expected_result>()`

Example:
```python
# tests/unit/test_subtitle_generator.py

def test_subtitle_generator_splits_text_into_four_word_chunks():
    """Subtitles should use 4-word chunks for viral retention."""
    # Test code here...

def test_subtitle_generator_applies_yellow_color_when_initialized():
    """Subtitles should default to yellow (#FFFF00) for visibility."""
    # Test code here...
```

---

## Running Tests

### Quick Reference Commands

```bash
# Run all tests (verbose output)
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_story_generator.py -v

# Run specific test function
pytest tests/unit/test_story_generator.py::test_story_generator_creates_150_to_220_word_story -v

# Run tests with coverage report
pytest tests/unit/ --cov=src --cov-report=html

# Run tests matching a pattern
pytest -k "subtitle" -v  # All tests with "subtitle" in name

# Run with extra detail (show print statements)
pytest tests/unit/ -v -s
```

### Understanding pytest Output

```bash
$ pytest tests/unit/test_story_generator.py -v

tests/unit/test_story_generator.py::test_story_generator_creates_150_to_220_word_story PASSED  [ 20%]
tests/unit/test_story_generator.py::test_story_generator_uses_groq_api_when_available PASSED   [ 40%]
tests/unit/test_story_generator.py::test_story_generator_falls_back_when_api_key_missing FAILED [ 60%]

FAILED tests/unit/test_story_generator.py::test_story_generator_falls_back_when_api_key_missing
AssertionError: assert False == True

= short test summary info =
FAILED tests/unit/test_story_generator.py::test_story_generator_falls_back_when_api_key_missing - AssertionError: assert False == True

= 2 passed, 1 failed in 0.45s =
```

---

## Practical Examples

### Example 1: Adding a New Story Genre

**Goal**: Add "horror_comedy" genre to story generator (combines horror + comedy elements)

#### Step 1: Write Test First (RED)

File: `tests/unit/test_story_generator.py`

```python
import pytest
from src.generation.story_generator import StoryGenerator
from src.utils.config import GROQ_API_KEY

@pytest.mark.skipif(not GROQ_API_KEY, reason="GROQ_API_KEY not set")
def test_story_generator_supports_horror_comedy_genre():
    """Story generator should support 'horror_comedy' as a valid genre."""
    # Arrange
    gen = StoryGenerator()

    # Act
    story = gen.generate_story(genre='horror_comedy')

    # Assert
    assert story is not None
    assert isinstance(story, dict)
    assert 'story' in story
    assert story['genre'] == 'horror_comedy'
    assert 150 <= story['word_count'] <= 220
    assert 'horror' in story['template_used'].lower() or 'comedy' in story['template_used'].lower()


def test_story_generator_horror_comedy_genre_template_is_available():
    """Template for horror_comedy genre should be registered."""
    # Arrange
    from src.generation.story_templates import list_genres

    # Act
    available_genres = list_genres()

    # Assert
    assert 'horror_comedy' in available_genres


def test_story_generator_horror_comedy_generates_150_to_220_words():
    """Horror-comedy stories must meet monetization word count (150-220 words)."""
    # Arrange
    gen = StoryGenerator()

    # Act - Generate multiple stories to test consistency
    for _ in range(3):
        story = gen.generate_story(genre='horror_comedy')

        # Assert
        assert 150 <= story['word_count'] <= 220, \
            f"Horror-comedy story should be 150-220 words, got {story['word_count']}"
```

#### Step 2: Run Test (Should FAIL)

```bash
$ pytest tests/unit/test_story_generator.py::test_story_generator_supports_horror_comedy_genre -v

FAILED tests/unit/test_story_generator.py::test_story_generator_supports_horror_comedy_genre
ValueError: genre 'horror_comedy' not in available genres
```

#### Step 3: Implement Feature (GREEN)

File: `src/generation/story_templates.py`

```python
# Add to GENRE_TEMPLATES dictionary
GENRE_TEMPLATES = {
    # ... existing genres ...

    'horror_comedy': {
        'name': 'Horror Comedy',
        'description': 'Scary situations with hilarious twists',
        'hook_patterns': [
            'So like, I thought my apartment was haunted but...',
            'This is gonna sound crazy but I swear...',
            'I went to this creepy place and THE SCARIEST THING HAPPENED...',
        ],
        'structure_prompts': [
            'Build tension with scary setup, then subvert with hilarious punchline',
            'Setup involves supernatural element, resolution is absurdly mundane',
            'Start horrifying, end with unexpected comedy',
        ],
        'tone': 'Conversational but tense, with comedic relief',
        'anti_ai_markers': ['literally', 'like', 'okay so', 'i swear', 'i lost it'],
    }
}

def list_genres():
    """Return list of available genres."""
    return list(GENRE_TEMPLATES.keys())
```

#### Step 4: Run Test (Should PASS)

```bash
$ pytest tests/unit/test_story_generator.py::test_story_generator_supports_horror_comedy_genre -v

tests/unit/test_story_generator.py::test_story_generator_supports_horror_comedy_genre PASSED  [ 100%]
tests/unit/test_story_generator.py::test_story_generator_horror_comedy_genre_template_is_available PASSED [ 100%]
tests/unit/test_story_generator.py::test_story_generator_horror_comedy_generates_150_to_220_words PASSED [ 100%]

= 3 passed in 0.72s =
```

#### Step 5: Refactor (If Needed)

Look for duplicated test code and extract fixtures:

```python
# tests/conftest.py (shared fixtures)
import pytest
from src.generation.story_generator import StoryGenerator

@pytest.fixture
def story_generator():
    """Return a story generator instance."""
    return StoryGenerator()

@pytest.fixture
def all_genres():
    """Return list of all available genres."""
    from src.generation.story_templates import list_genres
    return list_genres()
```

Now simplify tests:

```python
def test_story_generator_supports_horror_comedy_genre(story_generator):
    """Story generator should support 'horror_comedy' as a valid genre."""
    # Arrange (fixture provides story_generator)

    # Act
    story = story_generator.generate_story(genre='horror_comedy')

    # Assert
    assert story['genre'] == 'horror_comedy'
    assert 150 <= story['word_count'] <= 220
```

---

### Example 2: Adding a New Video Effect Type

**Goal**: Add "pulse_zoom" effect (subtle zoom in/out effect matching audio emphasis)

#### Step 1: Write Test First (RED)

File: `tests/unit/test_video_effects.py`

```python
import pytest
from src.generation.video_effects import PulseZoomEffect

def test_pulse_zoom_effect_creates_zoom_timeline():
    """Pulse zoom effect should generate MoviePy composition with zoom keyframes."""
    # Arrange
    effect = PulseZoomEffect(
        start_time=5.0,
        end_time=10.0,
        intensity=0.15  # 15% zoom
    )

    # Act
    timeline = effect.generate_keyframes()

    # Assert
    assert timeline is not None
    assert len(timeline) > 0
    # Each keyframe: (time, zoom_scale)
    assert timeline[0][0] >= 5.0  # First keyframe at or after start
    assert timeline[-1][0] <= 10.0  # Last keyframe at or before end
    assert all(0.85 <= scale <= 1.15 for time, scale in timeline)  # Scale within bounds


def test_pulse_zoom_effect_applies_to_video_clip():
    """Pulse zoom effect should apply zoom transformation to MoviePy VideoClip."""
    # Arrange
    from moviepy import VideoFileClip
    from pathlib import Path

    # Create minimal test video
    test_video_path = Path("tests/fixtures/test_1s_video.mp4")
    if not test_video_path.exists():
        pytest.skip("Test video fixture not available")

    clip = VideoFileClip(str(test_video_path))
    effect = PulseZoomEffect(start_time=0.0, end_time=1.0, intensity=0.1)

    # Act
    modified_clip = effect.apply(clip)

    # Assert
    assert modified_clip is not None
    assert modified_clip.duration == clip.duration
    assert modified_clip.size == clip.size


def test_pulse_zoom_effect_respects_intensity_parameter():
    """Effect intensity should control zoom magnitude (higher = more zoom)."""
    # Arrange
    effect_subtle = PulseZoomEffect(start_time=0, end_time=5, intensity=0.05)
    effect_dramatic = PulseZoomEffect(start_time=0, end_time=5, intensity=0.25)

    # Act
    subtle_timeline = effect_subtle.generate_keyframes()
    dramatic_timeline = effect_dramatic.generate_keyframes()

    # Assert
    subtle_max_zoom = max(scale for time, scale in subtle_timeline)
    dramatic_max_zoom = max(scale for time, scale in dramatic_timeline)

    assert subtle_max_zoom < dramatic_max_zoom
    assert subtle_max_zoom < 1.1  # < 10% zoom
    assert dramatic_max_zoom > 1.2  # > 20% zoom
```

#### Step 2: Run Tests (Should FAIL)

```bash
$ pytest tests/unit/test_video_effects.py -v

ModuleNotFoundError: No module named 'src.generation.video_effects'
```

#### Step 3: Implement Feature (GREEN)

File: `src/generation/video_effects.py`

```python
"""Video effects: zoom, filters, etc."""
from typing import List, Tuple


class PulseZoomEffect:
    """Pulse zoom effect - subtle zoom in/out on emphasis."""

    def __init__(self, start_time: float, end_time: float, intensity: float = 0.15):
        """Initialize pulse zoom effect.

        Args:
            start_time: When effect starts (seconds)
            end_time: When effect ends (seconds)
            intensity: Zoom magnitude (0.05 = 5%, 0.25 = 25%)
        """
        self.start_time = start_time
        self.end_time = end_time
        self.intensity = max(0.01, min(0.5, intensity))  # Clamp 1%-50%

    def generate_keyframes(self) -> List[Tuple[float, float]]:
        """Generate zoom keyframes.

        Returns:
            List of (time, zoom_scale) tuples
        """
        duration = self.end_time - self.start_time
        keyframes = []

        # Create smooth pulse: 1.0 -> 1.0+intensity -> 1.0
        steps = 10
        for i in range(steps + 1):
            t = i / steps  # 0 to 1
            time = self.start_time + t * duration

            # Sine wave for smooth pulse
            import math
            pulse = math.sin(t * math.pi)  # 0 to 1 to 0
            zoom_scale = 1.0 + (pulse * self.intensity)

            keyframes.append((time, zoom_scale))

        return keyframes

    def apply(self, clip):
        """Apply zoom effect to MoviePy VideoClip.

        Args:
            clip: MoviePy VideoClip

        Returns:
            Modified VideoClip with zoom effect
        """
        from moviepy import vfx

        # For now, return original (full implementation would use set_position + resize)
        # In production, use two-pass rendering:
        # Pass 1: Get all effects
        # Pass 2: Apply effects to final composition

        return clip.copy()
```

#### Step 4: Run Tests (Should PASS)

```bash
$ pytest tests/unit/test_video_effects.py -v

tests/unit/test_video_effects.py::test_pulse_zoom_effect_creates_zoom_timeline PASSED           [ 33%]
tests/unit/test_video_effects.py::test_pulse_zoom_effect_applies_to_video_clip SKIPPED          [ 66%]
tests/unit/test_video_effects.py::test_pulse_zoom_effect_respects_intensity_parameter PASSED   [ 100%]

= 2 passed, 1 skipped in 0.18s =
```

---

### Example 3: Adding a New API Endpoint

**Goal**: Add `POST /api/stories/batch-generate` endpoint for generating multiple stories

#### Step 1: Write Integration Test First (RED)

File: `tests/integration/test_batch_generation_api.py`

```python
import pytest
from app import app
import json


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_batch_generate_endpoint_accepts_post_request(client):
    """POST /api/stories/batch-generate should accept batch generation request."""
    # Arrange
    payload = {
        'count': 3,
        'genre': 'comedy',
        'target_duration': 75
    }

    # Act
    response = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'job_id' in data
    assert 'status' in data
    assert data['status'] == 'queued'


def test_batch_generate_endpoint_validates_count_parameter(client):
    """Endpoint should validate count is 1-20 (avoid excessive generation)."""
    # Arrange - invalid: count too high
    payload = {'count': 50, 'genre': 'comedy'}

    # Act
    response = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Assert
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'count' in data['error'].lower()


def test_batch_generate_endpoint_validates_genre_parameter(client):
    """Endpoint should validate genre is from allowed list."""
    # Arrange - invalid genre
    payload = {'count': 3, 'genre': 'invalid_genre'}

    # Act
    response = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Assert
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'genre' in data['error'].lower()


def test_batch_generate_endpoint_returns_job_id(client):
    """Endpoint should return unique job_id for tracking batch status."""
    # Arrange
    payload = {'count': 2, 'genre': 'comedy'}

    # Act
    response1 = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    response2 = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Assert
    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)
    assert data1['job_id'] != data2['job_id']
```

#### Step 2: Run Tests (Should FAIL)

```bash
$ pytest tests/integration/test_batch_generation_api.py -v

NOT FOUND: POST /api/stories/batch-generate
```

#### Step 3: Implement Endpoint (GREEN)

File: `app.py` or `src/api/routes.py`

```python
from flask import Blueprint, request, jsonify
from src.generation.story_generator import StoryGenerator
import uuid

stories_bp = Blueprint('stories', __name__, url_prefix='/api/stories')

VALID_GENRES = ['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama', 'horror_comedy']


@stories_bp.route('/batch-generate', methods=['POST'])
def batch_generate():
    """Generate multiple stories in batch mode.

    Request body:
    {
        "count": 3-20,
        "genre": "comedy",
        "target_duration": 60-90 (optional, default 75)
    }
    """
    try:
        data = request.get_json()

        # Validate count
        count = data.get('count', 1)
        if not isinstance(count, int) or count < 1 or count > 20:
            return jsonify({'error': 'count must be 1-20'}), 400

        # Validate genre
        genre = data.get('genre', 'comedy')
        if genre not in VALID_GENRES:
            return jsonify({
                'error': f'genre must be one of: {", ".join(VALID_GENRES)}'
            }), 400

        # Validate target_duration
        target_duration = data.get('target_duration', 75)
        if not isinstance(target_duration, (int, float)) or not (60 <= target_duration <= 90):
            return jsonify({
                'error': 'target_duration must be 60-90 seconds'
            }), 400

        # Create batch job
        job_id = str(uuid.uuid4())

        # TODO: Queue batch job (for async processing)
        # For now, return job details

        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'count': count,
            'genre': genre,
            'target_duration': target_duration
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### Step 4: Run Tests (Should PASS)

```bash
$ pytest tests/integration/test_batch_generation_api.py -v

tests/integration/test_batch_generation_api.py::test_batch_generate_endpoint_accepts_post_request PASSED        [ 20%]
tests/integration/test_batch_generation_api.py::test_batch_generate_endpoint_validates_count_parameter PASSED   [ 40%]
tests/integration/test_batch_generation_api.py::test_batch_generate_endpoint_validates_genre_parameter PASSED   [ 60%]
tests/integration/test_batch_generation_api.py::test_batch_generate_endpoint_returns_job_id PASSED             [ 80%]

= 4 passed in 0.21s =
```

---

## Testing Patterns

### AAA Pattern (Arrange-Act-Assert)

Every test should follow this structure:

```python
def test_feature_behavior():
    """Clear description of what is tested."""

    # ARRANGE: Set up test data
    input_data = {
        'story': 'This is a test story',
        'duration': 45.5
    }
    expected_chunks = 4

    # ACT: Execute the code under test
    subtitles = SubtitleGenerator().generate_subtitles(
        input_data['story'],
        input_data['duration']
    )

    # ASSERT: Verify the results
    assert len(subtitles) == expected_chunks
    assert all(chunk['word_count'] == 4 for chunk in subtitles)
```

### Fixture Pattern

Fixtures are reusable setup/teardown for tests:

```python
# tests/conftest.py

import pytest
from pathlib import Path
from src.generation.story_generator import StoryGenerator
from src.generation.subtitle_generator import SubtitleGenerator


@pytest.fixture
def story_generator():
    """Return a story generator instance."""
    return StoryGenerator()


@pytest.fixture
def sample_story():
    """Sample 75-word story for testing."""
    return """I was at Starbucks yesterday when this guy walks in wearing a full dinosaur
    costume. I'm talking T-Rex arms, tail, the whole thing. He orders a venti iced coffee
    in the deepest voice ever. The barista doesn't blink. Just asks for his name. He says
    "REGINALD THE TERRIBLE" and I literally lost it."""


@pytest.fixture
def sample_story_metadata():
    """Metadata for sample story."""
    return {
        'genre': 'comedy',
        'word_count': 75,
        'estimated_duration': 30.0
    }


@pytest.fixture
def temp_video_directory(tmp_path):
    """Create temporary directory for test videos."""
    video_dir = tmp_path / "videos"
    video_dir.mkdir()
    yield str(video_dir)
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def subtitle_generator():
    """Return subtitle generator with standard settings."""
    return SubtitleGenerator(
        words_per_chunk=4,
        color='yellow',
        font_size=60
    )
```

### Mocking Pattern

Use mocks to avoid external API calls in unit tests:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock


def test_story_generator_uses_groq_api():
    """Story generator should call Groq API with correct parameters."""

    # Arrange
    mock_groq_response = {
        'choices': [{'message': {'content': 'Generated story text here...'}}]
    }

    with patch('groq.Groq') as mock_groq:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_groq_response
        mock_groq.return_value = mock_client

        gen = StoryGenerator(api_key='test_key')

        # Act
        story = gen.generate_story(genre='comedy')

        # Assert
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'llama-3.3-70b-versatile'
        assert 'comedy' in str(call_args).lower()


def test_subtitle_generator_handles_missing_font_gracefully():
    """Subtitle generator should use fallback font if specified font missing."""

    # Arrange
    with patch('moviepy.TextClip') as mock_text_clip:
        mock_text_clip.side_effect = OSError("Font not found")

        # Act & Assert
        gen = SubtitleGenerator()
        # Should not raise, should use fallback
        subtitles = gen.generate_subtitles("Test story", 30.0)
        assert len(subtitles) > 0
```

### Parametrized Tests

Test multiple inputs with one test function:

```python
import pytest

@pytest.mark.parametrize("genre,expected_template", [
    ("comedy", "joke_template"),
    ("terror", "horror_template"),
    ("aita", "judgment_template"),
    ("genz_chaos", "chaos_template"),
    ("relationship_drama", "drama_template"),
])
def test_story_generator_uses_correct_template_for_genre(genre, expected_template):
    """Each genre should use its specific template."""
    gen = StoryGenerator()
    story = gen.generate_story(genre=genre)

    assert story['template_used'] == expected_template


@pytest.mark.parametrize("duration,expected_min_words,expected_max_words", [
    (60, 130, 180),
    (75, 160, 205),  # Standard: 150-220
    (90, 190, 235),
])
def test_story_generator_word_count_scales_with_duration(
    duration,
    expected_min_words,
    expected_max_words
):
    """Story word count should scale with target duration."""
    gen = StoryGenerator()
    story = gen.generate_story(target_duration=duration)

    assert expected_min_words <= story['word_count'] <= expected_max_words
```

---

## Coverage Goals

### Target: 85%+ for src/

We aim for **85% code coverage** for the `src/` directory (production code).

### Check Coverage

```bash
# Generate coverage report
pytest tests/unit/ --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
# or
start htmlcov\index.html  # Windows
# or
xdg-open htmlcov/index.html  # Linux
```

### Understanding Coverage

```
src/generation/story_generator.py     150 lines   92%  (8 lines uncovered)
src/generation/subtitle_generator.py  145 lines   88%  (17 lines uncovered)
src/generation/video_composer.py      328 lines   76%  (78 lines uncovered)
```

Lines uncovered typically:
- Error handling edge cases (good to skip)
- External API fallbacks
- Unused features

### Improve Coverage

1. **Identify uncovered lines**: `grep -n "# pragma: no cover" src/`
2. **Write tests for edge cases**: What if API fails? What if file missing?
3. **Use `pytest --cov` with `-v` flag** to see which tests cover which lines

```bash
pytest tests/unit/ --cov=src --cov-report=term-missing -v
```

---

## Common Pitfalls

### Pitfall 1: Tests That Are Too Brittle

**Bad - Tests break with minor refactors:**

```python
def test_story_generator_output_format():
    """Story generator output structure."""
    gen = StoryGenerator()
    story = gen.generate_story()

    # Too specific - breaks if dict order changes
    assert list(story.keys())[0] == 'story'
    assert story['story'].startswith('I was')
```

**Good - Tests focus on behavior, not implementation:**

```python
def test_story_generator_returns_complete_story_data():
    """Story generator returns all required fields."""
    gen = StoryGenerator()
    story = gen.generate_story()

    # Check required fields exist
    assert 'story' in story
    assert 'word_count' in story
    assert 'genre' in story
    assert 'estimated_duration' in story

    # Check types
    assert isinstance(story['story'], str)
    assert isinstance(story['word_count'], int)
```

### Pitfall 2: Skipped Tests Without Reason

**Bad - Missing context:**

```python
def test_video_rendering():
    pytest.skip()  # Why? What's needed?
    # Test code...
```

**Good - Clear skip condition:**

```python
@pytest.mark.skipif(
    not ELEVENLABS_API_KEY,
    reason="ELEVENLABS_API_KEY not set in environment"
)
def test_video_rendering_with_premium_voice():
    """Integration test requires ElevenLabs API key."""
    # Test code...
```

### Pitfall 3: Not Cleaning Up Resources

**Bad - File handles leak, can cause test failures:**

```python
def test_video_generation():
    clip = VideoFileClip("test.mp4")
    # Forgot to close!
    # Next test might fail due to file lock
```

**Good - Proper cleanup:**

```python
def test_video_generation():
    clip = VideoFileClip("test.mp4")
    try:
        # Test code...
        pass
    finally:
        clip.close()  # Always cleanup


# Better: Use context manager
def test_video_generation_with_context():
    with VideoFileClip("test.mp4") as clip:
        # Test code...
        pass
    # Auto cleanup
```

### Pitfall 4: Tests That Need External APIs

**Bad - Tests fail when API down:**

```python
def test_story_generation_calls_real_groq_api():
    """This will fail if Groq API is down."""
    gen = StoryGenerator()
    story = gen.generate_story()
    assert story is not None
```

**Good - Use mocks for unit tests:**

```python
def test_story_generator_formats_groq_request_correctly():
    """Unit test: verify request format, not API response."""
    with patch('groq.Groq.chat.completions.create') as mock_create:
        mock_create.return_value = {'choices': [{'message': {'content': 'test'}}]}

        gen = StoryGenerator()
        gen.generate_story(genre='comedy')

        # Verify request structure
        call_kwargs = mock_create.call_args[1]
        assert 'model' in call_kwargs
        assert 'messages' in call_kwargs
```

### Pitfall 5: Unclear Assertion Messages

**Bad - Hard to debug failures:**

```python
def test_subtitle_generation():
    subs = generate_subtitles("story", 30)
    assert len(subs) == 8
    assert subs[0]['color'] == 'yellow'
```

**Good - Descriptive assertions:**

```python
def test_subtitle_generation():
    subs = generate_subtitles("story", 30)

    assert len(subs) == 8, \
        f"Expected 8 subtitle chunks, got {len(subs)}"

    assert subs[0]['color'] == 'yellow', \
        f"First subtitle should be yellow, got {subs[0]['color']}"
```

---

## Pre-Commit Testing

### Run Before Each Commit

```bash
# Run full test suite
pytest tests/ -v

# Check coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Syntax check (Python compile)
python -m py_compile src/generation/*.py

# Type hints (if using mypy)
mypy src/ --ignore-missing-imports
```

### Git Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## TDD Checklist

Before marking a feature DONE:

- [ ] Tests written BEFORE implementation
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Coverage >= 85% for modified files (`--cov=src`)
- [ ] Integration test added (if API endpoint)
- [ ] Edge cases tested (missing params, invalid input)
- [ ] Fixtures used for reusable test data
- [ ] No `pytest.skip()` without reason
- [ ] Mocks used for external APIs
- [ ] Resource cleanup (file handles, DB connections)
- [ ] Test names describe behavior, not implementation
- [ ] AAA pattern followed in all tests
- [ ] No hardcoded file paths (use fixtures/tmp_path)
- [ ] Error messages clear and specific

---

## Key Takeaways

1. **Write tests FIRST** - RED phase forces you to think about requirements
2. **Keep tests simple** - One behavior per test
3. **Use fixtures** - Reduce duplication with `@pytest.fixture`
4. **Mock external APIs** - Unit tests should be fast and reliable
5. **Aim for 85%+ coverage** - Don't chase 100%, focus on critical paths
6. **Refactor safely** - Tests catch regressions immediately
7. **Automate verification** - Pre-commit hooks run tests before commit

**Remember**: TDD is not about writing tests, it's about **design**.

Tests guide you toward simpler, more modular, more testable code.

---

**Last Updated**: January 11, 2026
**Related Docs**: [.claude/agents/qa-specialist.md](../../.claude/agents/qa-specialist.md), [PROJECT.md](../PROJECT.md)
