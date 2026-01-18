# Development Rules for Claude

## Code Modification Rules

**Before editing ANY file:**
1. Read the entire file first (understand context)
2. Identify root cause, not symptoms
3. Ensure change aligns with studio vision
4. Test immediately after (`python -m py_compile <file>.py`)

**When adding features:**
1. Start with backend API endpoint (if needed)
2. Implement frontend UI component
3. Connect with existing pipeline
4. Test end-to-end workflow
5. Update CLAUDE.md if architecture changes

**Performance targets:**
- Story generation: <5s
- TTS generation: <8s (or instant if cached)
- Video render: <30s for 60s video
- Total pipeline: <45s end-to-end

## Testing Requirements

**MANDATORY after ANY code change:**
```bash
# 1. Syntax check
python -m py_compile <modified_file>.py

# 2. Run the actual functionality
# For generation: test full pipeline via UI
# For API: test endpoint with curl/Postman

# 3. Verify output quality
# For videos: check subtitles visible, audio synced
```

## What NOT to Do
- ❌ Create documentation files (update CLAUDE.md or README.md only)
- ❌ Add features not requested by user
- ❌ Implement "TODO" placeholders (finish it or skip it)
- ❌ Break existing video generation pipeline
- ❌ Add unnecessary abstractions/helpers for one-time use
- ❌ Use emojis in code (only in docs if requested)
- ❌ Create empty directories without functional content
- ❌ Add non-functional UI mockups without backend integration
