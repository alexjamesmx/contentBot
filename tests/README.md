# Tests

Test scripts for ContentBot development.

## Available Tests

### `test_story.py`
Test the story generator without creating videos.

```bash
python tests/test_story.py comedy
python tests/test_story.py aita
```

**What it does:**
- Generates a story using the AI
- Validates story metrics
- Shows preview without creating video

**Useful for:**
- Testing your Groq API key
- Previewing story quality
- Debugging story generation issues

---

## Running Tests

All test files can be run directly:

```bash
python tests/test_story.py [genre]
```

Available genres: `comedy`, `terror`, `aita`, `genz_chaos`, `relationship_drama`
