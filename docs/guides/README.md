# ContentBot Testing Guides

Complete documentation for Test-Driven Development (TDD) workflows at ContentBot.

## Available Guides

### 1. **tdd-workflow.md** (Complete Reference - 1100+ lines)

Comprehensive TDD documentation covering:

- **TDD Philosophy**: Why test-first development matters for ContentBot
- **Red-Green-Refactor Cycle**: The complete TDD workflow with phases
- **Test Organization**: Where to put unit vs integration tests
- **Running Tests**: Commands for different scenarios and configurations
- **Practical Examples**: Real ContentBot examples:
  - Adding a new story genre (horror_comedy)
  - Adding a new video effect type (pulse_zoom)
  - Adding a new API endpoint (batch video generation)
- **Testing Patterns**: AAA pattern, fixtures, mocking, parametrized tests
- **Coverage Goals**: Target 85%+ for src/ directory
- **Common Pitfalls**: What to avoid when writing tests

**Use this for**: Deep understanding of TDD concepts and patterns

---

### 2. **QUICKSTART-TDD.md** (One-Page Reference)

Quick reference for developers who know TDD basics:

- One-minute overview
- Most used pytest commands
- Test file template (copy-paste)
- Common patterns (fixtures, mocks, parametrized)
- Pre-commit checklist
- How to debug failing tests

**Use this for**: Getting started quickly, quick command lookup

---

### 3. **TDD-REFERENCE.md** (Command Reference Card)

Organized reference card with:

- The core Red-Green-Refactor cycle
- Essential pytest commands (table format)
- Test templates (AAA, fixtures, mocking, parametrized)
- Test naming conventions
- Coverage goals and debugging commands
- Common assertions reference
- Pre-commit checklist

**Use this for**: Quick lookup while coding, command reference

---

## Quick Start (2 Minutes)

### If You're New to TDD

1. Read: **QUICKSTART-TDD.md** (5 min)
2. Copy test template to your test file
3. Follow Red-Green-Refactor cycle:
   - RED: Write failing test
   - GREEN: Write minimal code to pass
   - REFACTOR: Clean up

### If You Know TDD But Need Specifics

1. Check: **TDD-REFERENCE.md** for command you need
2. Look up pattern in **tdd-workflow.md** if you need examples
3. Refer to existing tests in `tests/unit/` for ContentBot patterns

---

## The Rule at ContentBot

**Every feature must have tests BEFORE code.**

This applies to:
- New story genres (test template + implementation)
- New video effects (test behavior before coding)
- New API endpoints (test request/response validation)
- Bug fixes (write test to reproduce bug, then fix it)

---

## Test Organization

```
tests/
├── unit/                           # Fast, isolated tests (no external APIs)
│   ├── test_story_generator.py     # Story generation logic
│   ├── test_subtitle_generator.py  # Subtitle timing/formatting
│   ├── test_video_effects.py       # Video effect transformations
│   └── ...
│
├── integration/                    # Tests calling real services
│   ├── test_pipeline.py            # Full video generation flow
│   ├── test_api_endpoints.py       # Flask endpoint behavior
│   └── ...
│
└── conftest.py                     # Shared fixtures
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Only unit tests (fast)
pytest tests/unit/ -v

# With coverage report
pytest tests/unit/ --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_story_generator.py -v

# Specific test function
pytest tests/unit/test_story_generator.py::test_name -v

# Tests matching pattern
pytest -k "subtitle" -v

# Generate HTML coverage report
pytest tests/unit/ --cov=src --cov-report=html
```

---

## Coverage Goals

- **Target**: 85%+ for `src/` directory
- **Why**: Catches regressions, prevents broken video generation
- **Check with**: `pytest tests/unit/ --cov=src --cov-report=term-missing`

Lower coverage acceptable for:
- Error handling edge cases
- External API fallbacks
- Rarely-used features

Never accept below 70% - too many edge cases untested.

---

## Key Patterns at ContentBot

### AAA Pattern (Every Test)

```python
def test_feature_behavior():
    """What is being tested"""
    # ARRANGE - Set up data
    input_data = create_test_data()
    
    # ACT - Call the function
    result = function_under_test(input_data)
    
    # ASSERT - Verify result
    assert result == expected
```

### Fixtures (Reusable Data)

```python
# In conftest.py
@pytest.fixture
def sample_story():
    return "Test story with enough words to generate subtitles..."

# In test file
def test_subtitle_generation(sample_story):
    subs = generate_subtitles(sample_story, 30)
    assert len(subs) > 0
```

### Mocks (Avoid Real APIs)

```python
from unittest.mock import patch

def test_story_generation_format():
    with patch('groq.Groq') as mock_groq:
        mock_groq.return_value.create.return_value = {'result': 'story'}
        # Test code that uses Groq
        result = generate_story()
        assert 'story' in result
```

---

## Pre-Commit Workflow

Before committing code:

```bash
# 1. Run all tests
pytest tests/ -v

# 2. Check coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# 3. Syntax check
python -m py_compile src/generation/*.py

# 4. If all pass, commit
git add . && git commit -m "feat: add new feature with tests"
```

---

## Common Issues & Solutions

### Tests Fail With "API Key Not Set"

```bash
# Set environment variables
export GROQ_API_KEY=your_key
export ELEVENLABS_API_KEY=your_key

# Or use pytest.mark.skipif for optional tests
@pytest.mark.skipif(not GROQ_API_KEY, reason="API key not set")
def test_real_api_call():
    pass
```

### Test Works Locally But Fails in CI

- Check: File paths (use tmp_path fixture instead of hardcoded)
- Check: Environment variables (use pytest.mark.skipif)
- Check: External API dependencies (use mocks)

### Coverage Report Shows 0% for New Module

Run tests with `-vv` flag to see:
```bash
pytest tests/unit/ --cov=src --cov-report=term-missing -vv
```

Ensure:
1. Tests exist in tests/unit/
2. Test file imports your module
3. Test actually exercises the code

---

## Resources

- **[tdd-workflow.md](tdd-workflow.md)** - Complete TDD guide with detailed examples
- **[QUICKSTART-TDD.md](QUICKSTART-TDD.md)** - Get started in 5 minutes
- **[TDD-REFERENCE.md](TDD-REFERENCE.md)** - Command reference card
- **pytest.ini** - pytest configuration for ContentBot
- **tests/** - Existing test examples to follow

---

## Questions?

1. Check **TDD-REFERENCE.md** for quick commands
2. Search **tdd-workflow.md** for detailed examples
3. Look at existing tests in `tests/unit/` for ContentBot patterns
4. Refer to `.claude/agents/qa-specialist.md` for QA philosophy

---

**Last Updated**: January 11, 2026
**Status**: Complete TDD Workflow Documentation
**Coverage Target**: 85%+ for src/
