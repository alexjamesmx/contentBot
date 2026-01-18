# ContentBot Integration Test Suite

Comprehensive test suite for the ContentBot video generation pipeline.

## Overview

The integration test suite validates the complete end-to-end video generation pipeline:

```
Story Generation → TTS Audio → Subtitles → Effects → Final Video
```

## Test Coverage

### Complete Pipeline Tests
- **test_comedy_story_full_pipeline_60_seconds** - Full pipeline validation (Story → TTS → Subtitles → Video)
  - Validates story generation (150-220 words)
  - Verifies TTS audio (55-65s duration)
  - Checks subtitle generation (4-word chunks)
  - Confirms video output (1080x1920, 30fps)

### Genre Tests
Tests all 5 ContentBot genres produce valid videos:
- **comedy** - Gen-Z Chaos Comedy
- **terror** - Creepy Horror Stories
- **aita** - Am I The Asshole Stories
- **genz_chaos** - Gen-Z Chaos Stories
- **relationship_drama** - Relationship Drama Stories

Each genre test:
1. Generates a story with AI (Groq)
2. Creates TTS audio
3. Generates 4-word subtitles
4. Composes final video
5. Validates specifications

### Effects Integration Tests
- **test_video_with_zoom_effects** - Zoom effects on video background
- **test_video_with_subtitle_style_override** - Dynamic subtitle styling
- **test_video_with_all_effects_combined** - Multiple effects in one video

### Error Handling Tests
- **test_missing_background_video_uses_fallback** - Graceful fallback when background missing
- **test_invalid_effect_timeline_handled_gracefully** - Invalid effects don't crash
- **test_tts_generator_handles_empty_text** - Edge case handling
- **test_tts_api_failure_handling** - API failure recovery

### Performance Tests
- **test_complete_pipeline_execution_time** - Measures end-to-end performance
  - Target: <120s for full pipeline (testing)
  - Production target: <60s

### Subtitle Validation Tests
- **test_four_word_chunk_sizing** - Verifies 4-word chunks (viral optimized)
- **test_subtitle_timing_matches_audio_duration** - Timing accuracy

## Running Tests

### Prerequisites

1. **API Keys** (in `.env`):
   ```env
   GROQ_API_KEY=your_groq_key
   ELEVENLABS_API_KEY=your_elevenlabs_key (optional)
   ```

2. **Background Videos** (in `assets/backgrounds/`):
   - Required: At least one MP4 video (1080x1920 or auto-crops)
   - Recommended: Multiple videos for variety

3. **Fonts** (in `assets/fonts/`):
   - Montserrat-Black.ttf (recommended)
   - Or Windows system fonts (fallback)

4. **Dependencies**:
   ```bash
   pip install pytest pytest-timeout moviepy
   ```

### Basic Commands

**Run all fast tests** (excludes slow tests):
```bash
pytest tests/integration/test_full_pipeline.py -v
```

**Run only slow integration tests** (30-60s each):
```bash
pytest tests/integration/test_full_pipeline.py -m slow -v
```

**Run specific test class**:
```bash
pytest tests/integration/test_full_pipeline.py::TestCompleteVideoGenerationPipeline -v
```

**Run specific test**:
```bash
pytest tests/integration/test_full_pipeline.py::TestAllGenres::test_genre_produces_valid_video -v
```

**Run with performance timing**:
```bash
pytest tests/integration/test_full_pipeline.py -v --durations=10
```

**Run with detailed output**:
```bash
pytest tests/integration/test_full_pipeline.py -v -s
```

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.slow` - Slow tests (30-60s each, skipped by default)
- `@pytest.mark.integration` - Integration tests (full pipeline)
- `@pytest.mark.unit` - Unit tests (individual components)

**Usage**:
```bash
pytest -m integration           # Only integration tests
pytest -m "not slow"            # All except slow tests
pytest -m "slow and integration" # Slow integration tests only
```

## Test Structure

### Fixtures

- **test_story_gen** - Story generator (session-scoped)
- **tts_generator** - Text-to-speech generator
- **subtitle_generator** - Subtitle generator (4-word chunks)
- **video_composer** - Video composition engine
- **mock_background_video** - Creates/finds test background video
- **temp_video_dir** - Temporary directory for test outputs
- **cleanup_test_videos** - Auto-cleanup after tests

### Helper Functions

- **verify_video_file(path, min_duration, max_duration)**
  - Validates video exists and meets specifications
  - Returns metadata dict with duration, resolution, fps, file size

## Expected Output

### Test Success Output

```
test_full_pipeline.py::TestCompleteVideoGenerationPipeline::test_comedy_story_full_pipeline_60_seconds PASSED

[TEST] Starting full pipeline test for comedy story (60s)...
[STAGE 1] Generating story...
[VALIDATE] Story valid: True, Issues: []
[STAGE 2] Generating TTS audio...
[TTS] Generated audio: 59.2s
[STAGE 3] Generating subtitles...
[SUBTITLES] Generated 15 subtitle chunks (4-word chunks)
[STAGE 4] Composing final video...
[VERIFY] Checking video output...
[SUCCESS] Video created successfully!
  Duration: 59.2s (expected 55-65s)
  Resolution: 1080x1920 (expected 1080x1920)
  FPS: 30 (expected 30)
  File size: 45.3MB
```

## Common Issues

### 1. "GROQ_API_KEY not set"
**Solution**: Add API key to `.env`:
```env
GROQ_API_KEY=your_key_here
```

### 2. "No background videos found"
**Solution**: Add video to `assets/backgrounds/`:
```bash
# Download free gameplay video or record your own
cp /path/to/video.mp4 assets/backgrounds/
```

### 3. "Font not found" (uses fallback)
**Solution**: Optional, system fonts work fine. To use Montserrat:
```bash
python scripts/download_fonts.py
```

### 4. Test timeout (300s exceeded)
**Solution**: Slow test taking too long
- Check CPU/disk is not under heavy load
- Reduce concurrent tests
- Increase timeout in `pytest.ini`

### 5. Memory error during video composition
**Solution**: MoviePy clips not being closed properly
- Tests include proper cleanup via fixtures
- If issue persists, reduce video resolution in config

## Performance Benchmarks

On development machine (reference):

| Component | Time | Target |
|-----------|------|--------|
| Story generation | 3-5s | <5s |
| TTS generation | 4-8s | <8s (or cached) |
| Subtitle generation | <1s | <1s |
| Video composition | 20-40s | <30s |
| **Total Pipeline** | 30-60s | <60s |

**Note**: First run slower (background download, font loading). Subsequent runs use cache.

## Debugging Tests

### Enable verbose logging:
```bash
pytest tests/integration/test_full_pipeline.py -v -s
```

### Run single test with print statements visible:
```bash
pytest tests/integration/test_full_pipeline.py::TestCompleteVideoGenerationPipeline::test_comedy_story_full_pipeline_60_seconds -v -s
```

### Check generated videos:
```
output/pending_review/test_*.mp4
```

## CI/CD Integration

For automated testing, create `.github/workflows/tests.yml`:

```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt pytest pytest-timeout
      - run: pytest tests/integration/test_full_pipeline.py -m "not slow"
```

## Adding New Tests

### Template for new test:

```python
@pytest.mark.slow
@pytest.mark.integration
def test_new_feature(test_story_gen, tts_generator, subtitle_generator,
                     video_composer, mock_background_video, temp_video_dir):
    """Test description of what's being validated."""
    print("\n[TEST] Testing new feature...")

    # Arrange - set up test data
    story = test_story_gen.generate_story(genre="comedy", target_duration=60)

    # Act - execute the code being tested
    audio_path = Path(temp_video_dir) / "test_audio.mp3"
    audio = tts_generator.generate_audio(story["story"], output_path=str(audio_path))

    # Assert - verify results
    assert os.path.exists(audio), "Audio should be created"
    assert tts_generator.get_audio_duration(audio) > 0, "Audio should have duration"

    print(f"[SUCCESS] Feature works correctly")
```

## Best Practices

1. **Use fixtures** for common setup (story gen, TTS, composer)
2. **Mark slow tests** with `@pytest.mark.slow`
3. **Clean up temp files** via fixtures (auto-cleanup)
4. **Verify output format** with `verify_video_file()`
5. **Mock external APIs** for unit tests, use real for integration
6. **Add descriptive print statements** for debugging
7. **Test error cases** explicitly (invalid input, missing files)

## Test Maintenance

### Update tests when:
- Pipeline stages change
- New genres added
- Effect types modified
- API behavior changes

### Regular checks:
- Run full test suite weekly
- Monitor performance benchmarks
- Update expected output specs if needed
- Keep fixture data current

## Contact & Issues

For test failures or questions:
1. Check TESTING.md (this file)
2. Review test output carefully
3. Check .env configuration
4. Verify assets/backgrounds/ has videos
5. Check API keys are valid

---

**Last Updated**: January 2026
**Test Count**: 20+ integration tests
**Coverage**: Complete pipeline + all genres + effects + error handling
