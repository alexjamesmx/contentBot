# Code Examples Included in TDD Documentation

Complete reference of all code examples in the TDD workflow documentation.

## Red-Green-Refactor Cycle Examples

All three practical examples follow this cycle:

1. **RED** - Write test that fails
2. **GREEN** - Write minimal code to pass
3. **REFACTOR** - Clean up while keeping tests green

---

## Example 1: Adding Story Genre (horror_comedy)

### RED Phase: Write Failing Test

```python
# tests/unit/test_story_generator.py

def test_story_generator_supports_horror_comedy_genre():
    gen = StoryGenerator()
    story = gen.generate_story(genre='horror_comedy')

    assert story['genre'] == 'horror_comedy'
    assert 150 <= story['word_count'] <= 220

def test_story_generator_horror_comedy_template_exists():
    from src.generation.story_templates import list_genres
    assert 'horror_comedy' in list_genres()
```

### GREEN Phase: Minimal Implementation

```python
# src/generation/story_templates.py

GENRE_TEMPLATES = {
    'horror_comedy': {
        'name': 'Horror Comedy',
        'hook_patterns': [
            'So like, I thought my apartment was haunted but...',
        ],
        'structure_prompts': [
            'Setup scary, end with comedic twist',
        ],
        'tone': 'Conversational tension with comedy',
    }
}

def list_genres():
    return list(GENRE_TEMPLATES.keys())
```

### Run Tests

```bash
pytest tests/unit/test_story_generator.py::test_story_generator_supports_horror_comedy_genre -v
# PASSED
```

---

## Example 2: Adding Video Effect (pulse_zoom)

### RED Phase: Write Tests

```python
# tests/unit/test_video_effects.py

def test_pulse_zoom_creates_keyframes():
    effect = PulseZoomEffect(start_time=5.0, end_time=10.0, intensity=0.15)
    timeline = effect.generate_keyframes()

    assert len(timeline) > 0
    assert timeline[0][0] >= 5.0
    assert all(0.85 <= scale <= 1.15 for time, scale in timeline)


def test_pulse_zoom_respects_intensity():
    subtle = PulseZoomEffect(0, 5, intensity=0.05)
    dramatic = PulseZoomEffect(0, 5, intensity=0.25)

    subtle_max = max(s for t, s in subtle.generate_keyframes())
    dramatic_max = max(s for t, s in dramatic.generate_keyframes())

    assert subtle_max < dramatic_max
```

### GREEN Phase: Implementation

```python
# src/generation/video_effects.py

import math

class PulseZoomEffect:
    def __init__(self, start_time, end_time, intensity=0.15):
        self.start_time = start_time
        self.end_time = end_time
        self.intensity = max(0.01, min(0.5, intensity))

    def generate_keyframes(self):
        duration = self.end_time - self.start_time
        keyframes = []

        for i in range(11):
            t = i / 10
            time = self.start_time + t * duration
            pulse = math.sin(t * math.pi)
            zoom = 1.0 + (pulse * self.intensity)
            keyframes.append((time, zoom))

        return keyframes
```

---

## Example 3: Adding API Endpoint

### RED Phase: Write Integration Tests

```python
# tests/integration/test_batch_generation_api.py

import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_batch_generate_accepts_request(client):
    payload = {'count': 3, 'genre': 'comedy', 'target_duration': 75}
    response = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'job_id' in data
    assert data['status'] == 'queued'


def test_batch_generate_validates_count(client):
    payload = {'count': 50, 'genre': 'comedy'}
    response = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400


def test_batch_generate_validates_genre(client):
    payload = {'count': 3, 'genre': 'invalid_genre'}
    response = client.post(
        '/api/stories/batch-generate',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400
```

### GREEN Phase: Implementation

```python
# app.py

from flask import Blueprint, request, jsonify
import uuid

stories_bp = Blueprint('stories', __name__, url_prefix='/api/stories')
VALID_GENRES = ['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama']

@stories_bp.route('/batch-generate', methods=['POST'])
def batch_generate():
    try:
        data = request.get_json()
        count = data.get('count', 1)

        if not isinstance(count, int) or count < 1 or count > 20:
            return jsonify({'error': 'count must be 1-20'}), 400

        genre = data.get('genre', 'comedy')
        if genre not in VALID_GENRES:
            return jsonify({'error': 'invalid genre'}), 400

        target_duration = data.get('target_duration', 75)
        if not (60 <= target_duration <= 90):
            return jsonify({'error': 'target_duration must be 60-90'}), 400

        job_id = str(uuid.uuid4())

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

---

## Core Testing Patterns

### AAA Pattern

```python
def test_feature():
    """Clear description"""
    # ARRANGE - Set up
    input_data = {'key': 'value'}
    expected = calculate_expected()

    # ACT - Execute
    result = function_under_test(input_data)

    # ASSERT - Verify
    assert result == expected
```

### Fixtures

```python
# tests/conftest.py

@pytest.fixture
def sample_story():
    return "Story text here..."

@pytest.fixture
def story_generator():
    return StoryGenerator()

# Usage:
def test_something(sample_story, story_generator):
    result = story_generator.process(sample_story)
    assert result is not None
```

### Mocking

```python
from unittest.mock import patch

def test_api_call():
    with patch('groq.Groq') as mock_groq:
        mock_groq.return_value.create.return_value = {'result': 'mocked'}

        result = call_api()

        mock_groq.assert_called_once()
        assert result['result'] == 'mocked'
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("comedy", "joke_template"),
    ("terror", "horror_template"),
])
def test_templates(input, expected):
    assert get_template(input) == expected
```

---

## Common Assertions

```python
# Equality
assert value == expected

# Type
assert isinstance(obj, MyClass)

# Membership
assert item in list

# Exceptions
with pytest.raises(ValueError):
    bad_function()

# Strings
assert "text" in result
assert result.startswith("prefix")

# Collections
assert len(items) == 5
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# HTML report
pytest tests/unit/ --cov=src --cov-report=html

# Specific file
pytest tests/unit/test_file.py -v

# Specific test
pytest tests/unit/test_file.py::test_name -v
```

---

## Pre-Commit Checklist

```bash
# 1. Tests pass
pytest tests/ -v

# 2. Coverage OK
pytest tests/unit/ --cov=src --cov-report=term-missing

# 3. Syntax valid
python -m py_compile src/generation/*.py

# 4. Commit
git add . && git commit -m "feat: description"
```

---

**For full context and explanations**, see:
- `tdd-workflow.md` - Complete TDD guide
- `TDD-REFERENCE.md` - Command reference
- `QUICKSTART-TDD.md` - One-page guide

All examples follow ContentBot TDD standards.

Last Updated: January 11, 2026
