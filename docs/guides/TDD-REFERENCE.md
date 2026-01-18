# TDD Reference Card

## The Core Cycle

```
RED (Write failing test)
    ↓
GREEN (Write minimal code)
    ↓
REFACTOR (Clean up)
    ↓
Repeat
```

## Essential Commands

| Task | Command |
|------|---------|
| Run all tests | `pytest tests/ -v` |
| Run unit tests only | `pytest tests/unit/ -v` |
| Run specific file | `pytest tests/unit/test_file.py -v` |
| Run specific test | `pytest tests/unit/test_file.py::test_name -v` |
| Show coverage | `pytest tests/unit/ --cov=src --cov-report=term-missing` |
| HTML coverage report | `pytest tests/unit/ --cov=src --cov-report=html` |
| Run with print output | `pytest -v -s` |
| Verbose errors | `pytest -vvs --tb=long` |

## AAA Pattern Template

```python
def test_feature_behavior():
    """One sentence: what is being tested"""
    
    # ARRANGE - Set up test data
    input_data = {...}
    expected_result = {...}
    
    # ACT - Execute code under test
    actual_result = function_to_test(input_data)
    
    # ASSERT - Verify results
    assert actual_result == expected_result
```

## Fixture Template

```python
# In tests/conftest.py

@pytest.fixture
def reusable_data():
    """Description of fixture"""
    return create_test_data()

# Usage in tests:
def test_something(reusable_data):
    result = process(reusable_data)
    assert result is correct
```

## Mocking Template

```python
from unittest.mock import patch, MagicMock

def test_api_call():
    with patch('module.external_api') as mock_api:
        # Set return value
        mock_api.return_value = {'key': 'value'}
        
        # Test code that calls API
        result = code_using_api()
        
        # Verify mock was called correctly
        mock_api.assert_called_once()
        mock_api.assert_called_with('expected', 'args')
```

## Parametrized Test Template

```python
@pytest.mark.parametrize("input,expected", [
    ("case1", "result1"),
    ("case2", "result2"),
    ("case3", "result3"),
])
def test_multiple_cases(input, expected):
    assert function(input) == expected
```

## Test Organization

```
tests/
├── unit/                    # Fast, no external APIs
│   ├── test_story_generator.py
│   ├── test_subtitle_generator.py
│   └── test_video_effects.py
│
├── integration/             # Slower, uses real APIs/DB
│   ├── test_pipeline.py
│   ├── test_api_endpoints.py
│   └── test_full_video_generation.py
│
└── conftest.py             # Shared fixtures
```

## Test Naming Rules

| Type | Pattern | Example |
|------|---------|---------|
| Unit test | `test_<function>_<condition>_<expected>` | `test_story_generator_creates_150_to_220_word_story()` |
| Parametrized | `test_<feature>_with_<case>` | `test_subtitle_sync_with_fast_audio()` |
| Edge case | `test_<feature>_handles_<error>_gracefully()` | `test_api_handles_missing_param_gracefully()` |

## Coverage Goals

- **Target**: 85%+ for `src/`
- **Acceptable**: 75-85% (complex features often lower)
- **Never**: <70% (too many edge cases untested)

Check with: `pytest tests/unit/ --cov=src --cov-report=term-missing`

## Common Assertions

```python
# Equality
assert value == expected
assert value != unexpected

# Type checking
assert isinstance(obj, ClassName)
assert type(value) == dict

# Membership
assert item in list
assert key in dict

# Truthiness
assert condition  # True
assert not condition  # False

# Exceptions
with pytest.raises(ValueError):
    function_that_raises()

# Strings
assert "substring" in result
assert result.startswith("prefix")
assert result.endswith("suffix")

# Collections
assert len(items) == 5
assert [] == []
assert set([1,2,3]) == {1,2,3}
```

## Pre-Commit Checklist

Before creating a commit:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage >= 85%: `pytest tests/unit/ --cov=src`
- [ ] No syntax errors: `python -m py_compile src/generation/*.py`
- [ ] No unused imports: `grep "^import\|^from" <file> | verify used`
- [ ] Descriptive test names
- [ ] AAA pattern followed
- [ ] Fixtures used for reusable data
- [ ] Mocks used for external APIs
- [ ] Resources cleaned up (files, DB connections)

## Debugging Failed Tests

```bash
# 1. Show more detail
pytest test_file.py::test_function -vv

# 2. Show print statements
pytest test_file.py::test_function -s

# 3. Stop at first failure
pytest test_file.py -x

# 4. Show last N failures
pytest test_file.py --lf  # last failed
pytest test_file.py --ff  # failed first

# 5. Drop into debugger on failure
pytest test_file.py --pdb

# 6. Full traceback
pytest test_file.py --tb=long
```

## Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: run for each test
def fresh_data():
    return create_data()

@pytest.fixture(scope="module")  # Run once per test file
def expensive_resource():
    return expensive_setup()

@pytest.fixture(scope="session")  # Run once per test session
def database():
    return setup_db_once()
```

## Skipping Tests

```python
# Skip unconditionally
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

# Skip conditionally
@pytest.mark.skipif(
    not API_KEY,
    reason="API_KEY not set in environment"
)
def test_api_integration():
    pass

# Skip in code
def test_something():
    if condition:
        pytest.skip("Reason why skipping")
    # Test code...
```

## Useful pytest.ini Settings

See: `pytest.ini` in project root

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short
```

---

**Full Guide**: See `docs/guides/tdd-workflow.md`
**Quick Start**: See `docs/guides/QUICKSTART-TDD.md`

Last updated: January 11, 2026
