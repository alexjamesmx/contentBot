# Quick Start: TDD at ContentBot

## One-Minute Overview

**TDD = Write tests BEFORE code**

1. Write test that FAILS (RED)
2. Write minimal code to make it pass (GREEN)
3. Clean up code (REFACTOR)

## Most Used Commands

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Run specific test
pytest tests/unit/test_story_generator.py::test_function_name -v

# Run tests matching pattern
pytest -k "subtitle" -v
```

## Test File Template

```python
import pytest
from src.module import MyClass

def test_feature_does_something_when_condition():
    """Clear description of what is being tested"""
    # ARRANGE
    input_data = {'key': 'value'}

    # ACT
    result = MyClass.method(input_data)

    # ASSERT
    assert result == expected_value
```

## Common Patterns

### Fixture (Reusable Setup)
```python
@pytest.fixture
def sample_story():
    return "This is a test story with enough words..."

def test_something(sample_story):
    # sample_story is automatically provided
    assert len(sample_story) > 10
```

### Mock (Avoid External APIs)
```python
from unittest.mock import patch

def test_calls_api():
    with patch('groq.Groq') as mock_groq:
        mock_groq.return_value.create.return_value = {'result': 'mocked'}
        # Test code that uses Groq
```

### Parametrized (Test Multiple Cases)
```python
@pytest.mark.parametrize("genre,expected", [
    ("comedy", "joke_template"),
    ("terror", "horror_template"),
])
def test_genre_templates(genre, expected):
    assert get_template(genre) == expected
```

## Pre-Commit Checklist

Before pushing code:
```bash
# 1. Run all tests
pytest tests/ -v

# 2. Check coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# 3. Syntax check
python -m py_compile src/generation/*.py
```

## When Tests Fail

```bash
# See what went wrong (verbose + show print statements)
pytest tests/unit/test_file.py::test_function -vvs

# Show last 100 lines of output
pytest tests/unit/ -v --tb=long
```

## Coverage Report

```bash
# Generate HTML report
pytest tests/unit/ --cov=src --cov-report=html

# Open it
open htmlcov/index.html  # macOS
start htmlcov\index.html  # Windows
```

## Read Full Guide

See: `docs/guides/tdd-workflow.md`

---

**Goal**: 85%+ coverage for src/
**Rule**: Every feature needs tests BEFORE code
**Benefit**: Catch regressions immediately
