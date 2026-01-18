# Integration Tests - Quick Start

## What's Tested

Complete end-to-end video generation pipeline with all genres, effects, and error cases.

## Quick Start

### 1. Prerequisites
```bash
# Install pytest
pip install pytest pytest-timeout

# API keys in .env
GROQ_API_KEY=your_key
ELEVENLABS_API_KEY=optional
```

### 2. Add Background Videos
```bash
# Copy at least one video to assets/backgrounds/
# Videos should be 1080x1920 or will auto-crop
cp /path/to/gameplay.mp4 assets/backgrounds/
```

### 3. Run Tests

**Quick test** (2-3 minutes):
```bash
pytest test_full_pipeline.py -v
```

**Include slow tests** (30+ minutes):
```bash
pytest test_full_pipeline.py -m slow -v
```

**Test one genre**:
```bash
pytest test_full_pipeline.py::TestAllGenres::test_genre_produces_valid_video -v
```

## Test Files

- `test_full_pipeline.py` - All integration tests (1200+ lines)
- `conftest.py` - Shared fixtures and configuration
- `pytest.ini` - Pytest configuration with markers

## What Gets Tested

### Complete Pipeline (60+ seconds each)
- Story generation (Groq AI)
- TTS audio creation
- Subtitle generation (4-word chunks)
- Video composition (1080x1920, 30fps)
- All effects applied

### All Genres
- comedy
- terror
- aita
- genz_chaos
- relationship_drama

### Effects
- Zoom effects
- Subtitle style overrides
- Background changes
- Multiple effects combined

### Error Handling
- Missing background fallback
- Invalid effect timelines
- Empty text handling
- API failures

### Performance
- End-to-end execution time
- Subtitle timing accuracy

## Test Output

Success looks like:
```
test_full_pipeline.py::TestAllGenres::test_genre_produces_valid_video[comedy] PASSED
[TEST] Testing comedy genre...
[comedy] Duration: 59.2s - PASS
```

## Common Issues

| Issue | Solution |
|-------|----------|
| GROQ_API_KEY missing | Add to .env |
| No backgrounds | Copy video to assets/backgrounds/ |
| Timeout (300s) | Slow test, try -m "not slow" |
| Memory error | System under heavy load, retry |

## For Developers

See `../TESTING.md` for:
- Full documentation
- Detailed test descriptions
- Performance benchmarks
- CI/CD integration
- Adding new tests

## Performance (Reference)

- Story gen: 3-5s
- TTS: 4-8s
- Subtitles: <1s
- Video composition: 20-40s
- Total: 30-60s

---

**Next Step**: See `../TESTING.md` for complete documentation
