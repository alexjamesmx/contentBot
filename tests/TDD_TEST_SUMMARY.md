# TDD Test Suite Summary - Multi-Part Story Feature (Week 3)

## Overview
This document summarizes the TDD (Test-Driven Development) test suite written for the Multi-Part Story Feature. All tests are currently in the RED phase - they fail because the implementation classes don't exist yet. The backend specialist will implement the code to make these tests pass (GREEN phase).

## Test Files Created

### 1. Unit Tests: `tests/unit/test_story_context_manager.py` (13 tests)
Tests for the `StoryContextManager` class - the core backend logic for managing multi-part story series.

#### Test Classes and Methods:

**TestStoryContextManagerSeries** (3 tests)
- `test_create_series_generates_valid_story_id()` - Verifies series creation returns UUID-format story_id
- `test_create_series_initializes_metadata_correctly()` - Confirms metadata fields (genre, total_parts, theme, current_part, created_at) are properly initialized
- `test_create_series_with_invalid_genre_raises_error()` - Validates that invalid genres raise ValueError

**TestStoryContextManagerParts** (3 tests)
- `test_add_part_appends_to_parts_list()` - Verifies new parts are added to parts list
- `test_add_part_updates_current_part_counter()` - Confirms current_part counter increments with each addition
- `test_add_part_exceeding_total_parts_raises_error()` - Validates that exceeding part limit raises ValueError

**TestStoryContextManagerContext** (2 tests)
- `test_get_context_returns_previous_parts_summary()` - Verifies context contains summary of all previous parts
- `test_generate_contextual_prompt_references_previous_events()` - Confirms generated prompt includes context from previous parts

**TestStoryContextManagerPersistence** (3 tests)
- `test_save_series_creates_json_file()` - Verifies series is saved to JSON file
- `test_load_series_reads_existing_json()` - Confirms series can be loaded from JSON
- `test_load_nonexistent_series_raises_error()` - Validates FileNotFoundError for missing series

**TestStoryContextManagerListing** (2 tests)
- `test_list_series_returns_all_story_ids()` - Verifies all series IDs are returned from cache
- `test_list_series_returns_empty_when_no_series()` - Confirms empty list when cache is empty

### 2. Integration Tests: `tests/integration/test_story_series_api.py` (12 tests)
Tests for the REST API endpoints - the interface between frontend and backend.

#### Test Classes and Methods:

**TestStorySeriesAPICreation** (3 tests)
- `test_create_series_endpoint_returns_story_id()` - POST /api/stories/series returns 201 with story_id
- `test_create_series_endpoint_validates_input()` - Confirms 400 response for invalid input
- `test_create_series_endpoint_rejects_invalid_genre()` - Verifies 400 response for invalid genre

**TestStorySeriesAPINextPart** (4 tests)
- `test_next_part_endpoint_generates_story()` - POST /api/stories/series/{id}/next-part generates next part
- `test_next_part_endpoint_preserves_context()` - Confirms context from previous parts is used
- `test_next_part_with_invalid_story_id_returns_404()` - Validates 404 for non-existent series
- `test_next_part_exceeding_total_parts_returns_400()` - Confirms 400 when exceeding part limit

**TestStorySeriesAPIRetrieval** (2 tests)
- `test_get_series_endpoint_returns_metadata()` - GET /api/stories/series/{id} returns full metadata
- `test_list_series_endpoint_returns_all()` - GET /api/stories/series returns all series

**TestStorySeriesAPIWorkflow** (1 test)
- `test_full_series_generation_workflow()` - Complete workflow: create → add parts → retrieve → verify

**TestStorySeriesAPIValidation** (2 tests)
- `test_create_series_with_missing_fields_returns_400()` - Validates all required fields checked
- `test_create_series_with_invalid_total_parts_returns_400()` - Validates total_parts constraints (1-100)

### 3. Fixtures Added to `tests/conftest.py` (3 fixtures)

Three new reusable fixtures were added to `tests/conftest.py`:

```python
@pytest.fixture
def sample_series_metadata():
    """Standard series metadata for multi-part story tests."""
    return {
        "genre": "terror",
        "total_parts": 3,
        "theme": "haunted investigation"
    }

@pytest.fixture
def sample_story_part():
    """Standard story part for multi-part story tests."""
    return {
        "story_text": "I entered the house and heard strange noises.",
        "duration": 75,
        "hook": "The door slammed shut behind me."
    }

@pytest.fixture
def temp_series_cache():
    """Temporary directory for story series cache with cleanup."""
    with tempfile.TemporaryDirectory(prefix="story_series_test_") as temp_dir:
        yield temp_dir
```

## Testing Standards Applied

### AAA Pattern (Arrange, Act, Assert)
All tests follow the AAA pattern for clarity and maintainability:
- Arrange: Set up test data and mocks
- Act: Execute the code under test
- Assert: Verify the result

### Descriptive Test Names
Each test name describes exactly what is being tested, following pattern: `test_[unit]_[behavior]_[when_condition]`

### Fixtures for Reusability
Common test data is stored in pytest fixtures to avoid duplication and ensure consistency across tests.

### Markers
All tests use pytest markers for organization:
- `@pytest.mark.unit` for unit tests
- `@pytest.mark.integration` for integration tests

## TDD Red Phase Status

**Total Tests Written: 25**
- Unit Tests: 13
- Integration Tests: 12

**All Tests Currently FAIL** (Expected for TDD Red Phase)

### Expected Failures:

**Unit Tests**: `AttributeError: 'StoryContextManager' object has no attribute 'method_name'`
- Tests import a stub `StoryContextManager` class with no methods
- All method calls fail until backend specialist implements them

**Integration Tests**: `405 Method Not Allowed` or `JSONDecodeError`
- Tests try to call API endpoints that don't exist yet
- Backend specialist will create Flask routes to handle these endpoints

## Implementation Requirements for Backend Specialist

### Required Classes & Methods

**`src/generation/story_context_manager.py`**
```python
class StoryContextManager:
    def __init__(self, cache_dir: str = None)
    def create_series(self, genre: str, total_parts: int, theme: str) -> dict
    def add_part(self, story_id: str, part_data: dict) -> dict
    def get_context(self, story_id: str) -> dict
    def generate_contextual_prompt(self, story_id: str, genre: str) -> str
    def save_series(self, story_id: str, cache_dir: str = None) -> None
    def load_series(self, story_id: str, cache_dir: str = None) -> dict
    def list_series(self, cache_dir: str = None) -> list
```

### Required API Endpoints

**In `app.py`**
```
POST   /api/stories/series              - Create new series
POST   /api/stories/series/{id}/next-part - Generate next part
GET    /api/stories/series              - List all series
GET    /api/stories/series/{id}        - Get series metadata
```

## Running the Tests

### Run All New Tests
```bash
pytest tests/unit/test_story_context_manager.py tests/integration/test_story_series_api.py -v
```

### Run Only Unit Tests
```bash
pytest tests/unit/test_story_context_manager.py -v
```

### Run Only Integration Tests
```bash
pytest tests/integration/test_story_series_api.py -v
```

### Run with Coverage
```bash
pytest tests/unit/test_story_context_manager.py --cov=src.generation.story_context_manager --cov-report=html
```

## Next Steps (GREEN Phase)

1. Backend specialist implements `StoryContextManager` class
2. Backend specialist implements API endpoints in `app.py`
3. All 25 tests should pass with proper implementation
4. Tests serve as specification for what the feature must do

## Test Quality Checklist

- [x] All tests follow AAA pattern
- [x] All tests have descriptive names
- [x] All tests use appropriate markers
- [x] All tests use pytest fixtures for reusable setup
- [x] All tests are isolated (no test order dependencies)
- [x] All tests validate both success and error cases
- [x] All tests have clear assertions with expected values
- [x] No hardcoded paths (using fixtures and tmp_path)
- [x] Tests compile without syntax errors
- [x] Fixtures properly cleaned up (tempfile context managers)

---

**Created**: January 11, 2026
**TDD Phase**: RED (All tests fail, awaiting implementation)
**Total Test Count**: 25 (13 unit + 12 integration)
**Files Created**: 2 test files + 1 updated conftest.py
**Files Modified**: tests/conftest.py
