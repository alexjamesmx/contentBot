# Integration Test Checklist

Quick reference for setting up and running integration tests.

## Pre-Test Setup

- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install pytest pytest-timeout moviepy numpy pillow groq elevenlabs`
- [ ] `.env` file exists with API keys
  - [ ] `GROQ_API_KEY` set
  - [ ] `ELEVENLABS_API_KEY` set (optional)
- [ ] Background video in `assets/backgrounds/`
  - [ ] At least one MP4 file
  - [ ] Format: 1080x1920 or will auto-crop
  - [ ] Duration: 10+ seconds recommended

## Test Verification

### Quick Tests (2-3 minutes)
```bash
cd C:\Users\sgale\Documents\contentBot
pytest tests/integration/test_full_pipeline.py -v
```

Expected: 6+ tests passing

- [ ] Tests collected successfully
- [ ] No "GROQ_API_KEY missing" errors
- [ ] No "No background videos found" errors
- [ ] All fast tests pass (6 tests)

### Full Test Suite (30+ minutes)
```bash
pytest tests/integration/test_full_pipeline.py -m slow -v
```

Expected: 10+ tests passing (includes slow tests)

- [ ] All genre tests pass (comedy, terror, aita, genz_chaos, relationship_drama)
- [ ] All effect tests pass
- [ ] Error handling tests pass
- [ ] Performance test completes

### Specific Test - Full Pipeline
```bash
pytest tests/integration/test_full_pipeline.py::TestCompleteVideoGenerationPipeline::test_comedy_story_full_pipeline_60_seconds -v -s
```

This is the core validation test. Expected: PASSED

- [ ] Story generation works
- [ ] Story is valid (150-220 words)
- [ ] TTS audio created (55-65s)
- [ ] Subtitles generated (4-word chunks)
- [ ] Video composed (1080x1920, 30fps)
- [ ] Video duration is 55-65s

### All Genres Test
```bash
pytest tests/integration/test_full_pipeline.py::TestAllGenres -v
```

Expected: 5 tests passing (one per genre)

- [ ] comedy PASSED
- [ ] terror PASSED
- [ ] aita PASSED
- [ ] genz_chaos PASSED
- [ ] relationship_drama PASSED

### Effects Tests
```bash
pytest tests/integration/test_full_pipeline.py::TestEffectsIntegration -v
```

Expected: 3 tests passing

- [ ] test_video_with_zoom_effects PASSED
- [ ] test_video_with_subtitle_style_override PASSED
- [ ] test_video_with_all_effects_combined PASSED

### Error Handling Tests
```bash
pytest tests/integration/test_full_pipeline.py::TestErrorHandling -v
```

Expected: 4 tests passing

- [ ] test_missing_background_video_uses_fallback PASSED
- [ ] test_invalid_effect_timeline_handled_gracefully PASSED
- [ ] test_tts_generator_handles_empty_text PASSED
- [ ] test_tts_api_failure_handling PASSED

### Performance Test
```bash
pytest tests/integration/test_full_pipeline.py::TestPipelinePerformance -v -s
```

Expected: 1 test passing, timing output visible

- [ ] test_complete_pipeline_execution_time PASSED
- [ ] Total time < 120s
- [ ] Performance breakdown printed

### Subtitle Tests
```bash
pytest tests/integration/test_full_pipeline.py::TestSubtitleGeneration -v
```

Expected: 2 tests passing

- [ ] test_four_word_chunk_sizing PASSED
- [ ] test_subtitle_timing_matches_audio_duration PASSED

## Post-Test Validation

### Verify Video Output
```bash
# Check generated test videos
ls output/pending_review/test_*.mp4
```

- [ ] Test videos created
- [ ] File sizes reasonable (>1MB each)
- [ ] Files deletable (cleanup works)

### Check Logs
Look for errors in output:

- [ ] No "API rate limit" errors
- [ ] No "Background not found" errors (fallback should work)
- [ ] No "FFmpeg" errors
- [ ] No "CUDA" or GPU errors (CPU-only is fine)

## Troubleshooting Checklist

### Tests won't run
- [ ] pytest installed: `pip install pytest`
- [ ] Test file exists: `tests/integration/test_full_pipeline.py`
- [ ] Current directory correct: `C:\Users\sgale\Documents\contentBot`

### GROQ_API_KEY missing error
- [ ] `.env` file exists in project root
- [ ] `.env` contains: `GROQ_API_KEY=your_key`
- [ ] Key is valid (test with `python -c "from groq import Groq; Groq(api_key='KEY')"``)

### No background videos found
- [ ] `assets/backgrounds/` directory exists
- [ ] At least one `.mp4` file in directory
- [ ] File has size > 0: `ls -lh assets/backgrounds/`

### Tests timeout (>300s)
- [ ] Computer not under heavy load
- [ ] Network connection stable (API calls timeout)
- [ ] Increase timeout in `pytest.ini` if needed
- [ ] Run with `-m "not slow"` to skip slow tests

### Memory errors
- [ ] Available RAM > 4GB
- [ ] Close other applications
- [ ] Try running single test: `pytest tests/integration/test_full_pipeline.py::TestErrorHandling::test_tts_generator_handles_empty_text`

### Video composition fails
- [ ] FFmpeg installed and in PATH
- [ ] MoviePy installed: `pip install moviepy`
- [ ] Check disk space: `df -h`

## Success Criteria

A successful test run should:

1. **All tests pass** (green checkmarks)
2. **No errors or exceptions** in output
3. **Test videos generated** in `output/pending_review/`
4. **Performance within target**:
   - Story generation: <5s
   - TTS generation: <8s
   - Total pipeline: <60s (testing) or <120s (slow)
5. **Cleanup successful** (test files removed after tests)

## Common Successful Output

```
tests/integration/test_full_pipeline.py::TestErrorHandling::test_missing_background_video_uses_fallback PASSED
tests/integration/test_full_pipeline.py::TestErrorHandling::test_invalid_effect_timeline_handled_gracefully PASSED
tests/integration/test_full_pipeline.py::TestErrorHandling::test_tts_generator_handles_empty_text PASSED
tests/integration/test_full_pipeline.py::TestSubtitleGeneration::test_four_word_chunk_sizing PASSED
tests/integration/test_full_pipeline.py::TestSubtitleGeneration::test_subtitle_timing_matches_audio_duration PASSED

========================= 5 passed, 10 deselected in 15.23s =========================
```

## Performance Expectations

### Time per Stage (Reference)
- Story generation: 3-5 seconds
- TTS generation: 4-8 seconds
- Subtitle generation: <1 second
- Video composition: 20-40 seconds
- **Total: 30-60 seconds**

### Factors Affecting Performance
- First run slower (downloads, caching)
- Network latency (Groq API calls)
- CPU/GPU availability
- Disk speed
- Video rendering complexity

### Optimization Tips
- Use `-m "not slow"` for quick validation
- Run tests individually for faster feedback
- Cache downloaded models/fonts
- Increase system resources if possible

## Test Runner Script

Convenient way to run tests:

```bash
# All fast tests
python tests/run_integration_tests.py

# Include slow tests
python tests/run_integration_tests.py --slow

# Test specific genre
python tests/run_integration_tests.py --genre comedy

# With timing information
python tests/run_integration_tests.py --durations 10

# Help
python tests/run_integration_tests.py --help
```

## Documentation Reference

- **tests/TESTING.md** - Complete documentation
- **tests/integration/README.md** - Quick start guide
- **INTEGRATION_TEST_SUMMARY.md** - Full overview
- **tests/run_integration_tests.py** - Test runner script

## Environment Variables

Required in `.env`:
```env
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (falls back to gTTS)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Optional defaults
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_FPS=30
```

## Final Validation

Before considering tests "complete", verify:

- [ ] All test classes documented
- [ ] All test methods run
- [ ] All genres validated
- [ ] All effects tested
- [ ] Error cases handled
- [ ] Performance within target
- [ ] No flaky/intermittent failures
- [ ] Cleanup successful

## Running by Day/Week

### Daily Quick Check (5 minutes)
```bash
pytest tests/integration/test_full_pipeline.py::TestErrorHandling -v
```

### Weekly Full Suite (1 hour)
```bash
pytest tests/integration/test_full_pipeline.py -m slow -v --durations=10
```

### Before Deployment
```bash
pytest tests/integration/test_full_pipeline.py -v
python tests/run_integration_tests.py --slow
```

---

**Last Updated**: January 2026
**Status**: Production Ready
