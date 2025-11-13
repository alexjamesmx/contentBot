# 🧪 Screenshot Features Testing Guide

## Prerequisites Check

Before testing, verify you have everything installed:

### 1. Check Playwright Installation

```bash
# Check if Playwright is installed
python -c "import playwright; print('✅ Playwright installed')"

# If not installed:
pip install playwright
python -m playwright install chromium
```

### 2. Verify API Keys

```bash
# Check if all APIs are configured
python -c "from src.utils.config import REDDIT_CLIENT_ID, ELEVENLABS_API_KEY; print('✅ APIs configured' if REDDIT_CLIENT_ID and ELEVENLABS_API_KEY else '❌ Missing API keys')"
```

### 3. Check Background Videos

```bash
# Windows
dir assets\backgrounds\*.mp4

# Linux/Mac
ls -lh assets/backgrounds/*.mp4
```

---

## 🎯 Test Suite

### Test 1: Basic Screenshot Capture (Standalone)

**Purpose:** Verify screenshot generator works independently

```bash
# Test the screenshot generator directly
python -m src.scrapers.reddit_screenshot_generator
```

**Expected Output:**
```
📸 Reddit Screenshot Generator Test

📸 Capturing screenshot of: https://www.reddit.com/r/AmItheAsshole/...
🌐 Loading Reddit post...
📷 Capturing post screenshot...
✅ Post screenshot saved: post.png
💬 Capturing up to 3 comment screenshots...
✅ Comment 1 screenshot saved
✅ Comment 2 screenshot saved
✅ Comment 3 screenshot saved
✅ Captured 3 comment screenshots

============================================================
✅ SCREENSHOT TEST COMPLETE
============================================================
📁 Post screenshot: output/screenshots/test/test_post/post.png
📁 Comment screenshots: 3
   1. comment_1.png
   2. comment_2.png
   3. comment_3.png
============================================================
```

**Verification:**
- Check `output/screenshots/test/test_post/` folder
- Verify PNG files exist
- Open images and confirm they show Reddit content

---

### Test 2: Basic Reddit Video with Screenshots

**Purpose:** Test full pipeline with default settings

```bash
python create_video.py aita --reddit
```

**Expected Features:**
- ✅ Post screenshot captured
- ✅ 3 comment screenshots captured
- ✅ Sequential display mode
- ✅ Fade-in, slide-up, zoom-in animations
- ✅ Screenshots cached for next run

**Expected Output:**
```
🤖 CONTENTBOT - VIRAL VIDEO GENERATOR
============================================================

🔍 Fetching story from Reddit...
✅ Found post: AITA for refusing to pay...
   Upvotes: 3500 | Comments: 892

📸 Generating Reddit screenshot...
🌐 Loading Reddit post...
📷 Capturing post screenshot...
✅ Post screenshot saved: post.png
💬 Capturing up to 3 comment screenshots...
✅ Captured 3 comment screenshot(s)

🎙️  Generating voiceover...
✅ Voiceover generated: 58.2s

🎬 Composing final video...
📸 Adding Reddit screenshot overlay...
💬 Adding 3 comment screenshot(s)...
🎬 Rendering video to: aita_short.mp4

============================================================
🎉 VIDEO CREATED SUCCESSFULLY!
============================================================
```

**Verification:**
- Video file created: `output/pending_review/aita_short.mp4`
- Screenshots folder: `output/pending_review/screenshots/[post_id]/`
- Open video and verify:
  - Post appears first
  - Comments appear sequentially
  - Smooth animations between screenshots
  - Each screenshot visible for ~15-20 seconds

---

### Test 3: Caching System

**Purpose:** Verify screenshots are reused on second run

```bash
# First run (captures screenshots)
python create_video.py aita --reddit

# Second run (should use cache)
python create_video.py aita --reddit
```

**Expected Output on Second Run:**
```
📸 Generating Reddit screenshot...
♻️  Using cached screenshot: post.png
♻️  Found 3 cached comment(s)
```

**Verification:**
- Second run is significantly faster (~5-10x)
- No "🌐 Loading Reddit post..." message
- Screenshots not re-downloaded

**Measure Speed:**
```bash
# Windows
powershell "Measure-Command {python create_video.py aita --reddit}"

# Linux/Mac
time python create_video.py aita --reddit
```

---

### Test 4: Comment Display Modes

**Purpose:** Test all three display modes

#### 4a. Sequential Mode (Default)
```bash
python create_video.py aita --reddit --comment-display sequential
```

**Verify:** Screenshots appear one at a time

#### 4b. Overlay Mode
```bash
python create_video.py aita --reddit --comment-display overlay
```

**Verify:** All screenshots stacked vertically, visible simultaneously

#### 4c. Slide Mode
```bash
python create_video.py aita --reddit --comment-display slide
```

**Verify:** Screenshots slide in from right with smooth transitions

**Visual Check:**
- Open each video in a player
- Watch the first 30 seconds
- Confirm different transition styles

---

### Test 5: Screenshot Positioning

**Purpose:** Test positioning options

```bash
# Top position
python create_video.py aita --reddit --screenshot-position top

# Center position (default)
python create_video.py aita --reddit --screenshot-position center

# Bottom position
python create_video.py aita --reddit --screenshot-position bottom
```

**Verification:**
- Screenshots appear at correct vertical position
- No cutoff or overlap with video edges

---

### Test 6: Animations

**Purpose:** Verify all animation types work

**Already tested in Test 2**, but to isolate:

```bash
python create_video.py aita --reddit --comment-display sequential
```

**Watch for:**
- **Screenshot 1 (Post):** Fade-in animation
- **Screenshot 2 (Comment 1):** Slide-up animation
- **Screenshot 3 (Comment 2):** Zoom-in animation
- **Screenshot 4 (Comment 3):** Fade-in again (cycles)

**Frame-by-frame check:**
- Use VLC media player
- Press 'E' to step frame-by-frame
- Verify smooth transitions (0.4-0.5 second duration)

---

### Test 7: Transparent Theme

**Purpose:** Test transparent background mode

**Edit `create_video.py` line 156:**
```python
screenshot_gen = RedditScreenshotGenerator(theme="transparent")
```

**Run:**
```bash
python create_video.py aita --reddit
```

**Verification:**
- Screenshots should have transparent backgrounds
- Background video visible through screenshot
- Text has shadow for readability

**Compare:**
- Generate one video with `theme="dark"`
- Generate one with `theme="transparent"`
- Visually compare the appearance

---

### Test 8: Error Handling & Retry

**Purpose:** Test retry logic handles failures

**Simulate failure (temporarily break Reddit URL):**

Edit `create_video.py` line 158 temporarily:
```python
# Add typo to URL to trigger retry
post_url = story['source_url'] + "INVALID"
```

**Run:**
```bash
python create_video.py aita --reddit
```

**Expected Output:**
```
📸 Capturing screenshot of: https://www.reddit.com/...INVALID
⚠️  Attempt 1 failed: ...
   Retrying in 2.0s...
⚠️  Attempt 2 failed: ...
   Retrying in 4.0s...
⚠️  Attempt 3 failed: ...
❌ Failed after 3 attempts: ...
⚠️  Screenshot generation failed: ...
   Falling back to text subtitles...
```

**Verification:**
- 3 retry attempts occur
- Delays increase exponentially
- Graceful fallback to text subtitles
- Video still generates successfully

**IMPORTANT:** Revert the change after testing!

---

### Test 9: Custom Styling (Advanced)

**Purpose:** Test font scaling and highlighting

**Edit `create_video.py` line 156-164:**
```python
screenshot_gen = RedditScreenshotGenerator(theme="dark")
screenshots = screenshot_gen.capture_post_screenshot(
    post_url=story['source_url'],
    output_dir=str(PENDING_DIR / "screenshots"),
    post_id=story['reddit_id'],
    capture_comments=True,
    max_comments=3,
    font_scale=1.3,  # 30% larger fonts
    highlight_color="#ffff00"  # Yellow highlights
)
```

**Run:**
```bash
python create_video.py aita --reddit
```

**Verification:**
- Open screenshot files
- Text should be 30% larger than normal
- Bold text and headings should have yellow background

---

### Test 10: Different Subreddits

**Purpose:** Test across different Reddit communities

```bash
# r/tifu
python create_video.py comedy --reddit --subreddit tifu

# r/relationship_advice
python create_video.py relationship_drama --reddit --subreddit relationship_advice

# r/confession
python create_video.py genz_chaos --reddit --subreddit confession
```

**Verification:**
- All subreddits work correctly
- Different post formats handled properly
- Screenshots capture various UI styles

---

## 🔍 Visual Inspection Checklist

For each generated video, check:

### Screenshot Quality
- [ ] Screenshots are clear and readable
- [ ] No cutoff text or edges
- [ ] Proper scaling (not pixelated)
- [ ] Colors look correct
- [ ] Reddit UI elements visible

### Animations
- [ ] Smooth transitions (no jerky movement)
- [ ] Appropriate duration (0.4-0.5s)
- [ ] Different animations for variety
- [ ] No visual glitches

### Layout
- [ ] Screenshots positioned correctly
- [ ] No overlap with video edges
- [ ] Consistent sizing across screenshots
- [ ] Readable on mobile preview (9:16 format)

### Timing
- [ ] Screenshots appear at right times
- [ ] Duration matches audio/story
- [ ] No gaps or black frames
- [ ] Smooth overall flow

---

## 📊 Performance Benchmarks

Expected timings:

| Operation | First Run | Cached Run | Speedup |
|-----------|-----------|------------|---------|
| Screenshot capture | 8-12s | 0.5-1s | 10-15x |
| Full video generation | 60-90s | 55-70s | 1.2x |
| Total pipeline | 90-120s | 60-80s | 1.5x |

**Run benchmarks:**

```bash
# Windows PowerShell
Measure-Command {python create_video.py aita --reddit}

# Linux/Mac
time python create_video.py aita --reddit
```

---

## 🐛 Common Issues & Solutions

### Issue: "Playwright not found"
```bash
pip install playwright
python -m playwright install chromium
```

### Issue: Screenshots are blank/black
- **Cause:** Page not fully loaded
- **Solution:** Increase timeout in code:
  ```python
  screenshots = screenshot_gen.capture_post_screenshot(..., timeout=60000)
  ```

### Issue: "Unable to find element"
- **Cause:** Reddit changed their HTML structure
- **Solution:** Check Reddit selector in `reddit_screenshot_generator.py` line 213

### Issue: Animations not visible
- **Cause:** Video player doesn't show subtle effects
- **Solution:** Try different player (VLC, MPV) or slow down playback

### Issue: Cache not working
- **Cause:** Post ID mismatch
- **Solution:** Check post ID in filenames match
  ```bash
  dir output\pending_review\screenshots
  ```

---

## ✅ Success Criteria

All tests pass if:

1. ✅ Standalone screenshot test generates 1 post + 3 comments
2. ✅ Full video pipeline completes without errors
3. ✅ Cached run is 5-10x faster
4. ✅ All 3 display modes produce different videos
5. ✅ All 3 positions work correctly
6. ✅ Animations are visible and smooth
7. ✅ Retry logic handles failures gracefully
8. ✅ Custom styling (fonts, highlights) applies correctly
9. ✅ Multiple subreddits work
10. ✅ Generated videos are watchable and engaging

---

## 📝 Test Report Template

```
# Screenshot Features Test Report

**Date:** 2025-11-10
**Tester:** [Your Name]
**Environment:** Windows/Linux/Mac

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| 1. Basic Screenshot | ✅/❌ | |
| 2. Full Pipeline | ✅/❌ | |
| 3. Caching | ✅/❌ | |
| 4. Display Modes | ✅/❌ | |
| 5. Positioning | ✅/❌ | |
| 6. Animations | ✅/❌ | |
| 7. Transparent Theme | ✅/❌ | |
| 8. Error Handling | ✅/❌ | |
| 9. Custom Styling | ✅/❌ | |
| 10. Subreddits | ✅/❌ | |

## Performance

- First run: ___ seconds
- Cached run: ___ seconds
- Speedup: ___x

## Issues Found

1. [Issue description]
2. [Issue description]

## Recommendations

[Any suggestions for improvements]
```

---

## 🚀 Quick Start Testing

**Minimal test (5 minutes):**
```bash
# 1. Test standalone screenshot
python -m src.scrapers.reddit_screenshot_generator

# 2. Test full pipeline
python create_video.py aita --reddit

# 3. Test caching
python create_video.py aita --reddit
```

**Full test suite (30 minutes):**
Run all 10 tests above

**Production verification (2 hours):**
- Run full test suite
- Generate 5-10 videos with different settings
- Visual inspection of all outputs
- Performance benchmarking
- Documentation review

---

**Good luck with testing! 🎉**
