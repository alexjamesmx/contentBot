# 📸 Reddit Screenshot Setup Guide

## Overview

ContentBot can now generate **authentic Reddit post screenshots** just like RedditVideoMakerBot! This creates more engaging videos by showing the actual Reddit UI instead of just text overlays.

## Quick Setup

### 1. Install Playwright

```bash
pip install playwright
```

### 2. Install Browser

Playwright needs to download Chromium (takes ~2 minutes):

```bash
python -m playwright install chromium
```

That's it! You're ready to generate screenshot videos.

---

## Usage

### Generate Reddit video WITH screenshots (default):

```bash
python create_video.py aita --reddit
```

This will:
1. Fetch a viral post from r/AmItheAsshole
2. **Capture a screenshot** of the actual Reddit post
3. Generate voiceover of the story
4. Overlay the screenshot on background video
5. **Output the Reddit thread URL** prominently

### Generate Reddit video WITHOUT screenshots (text subtitles):

```bash
python create_video.py aita --reddit --no-screenshots
```

---

## Screenshot Options

### Position Control

Control where the screenshot appears on the video:

```bash
# Screenshot at top (default: center)
python create_video.py --reddit --screenshot-position top

# Screenshot at center (most common)
python create_video.py --reddit --screenshot-position center

# Screenshot at bottom
python create_video.py --reddit --screenshot-position bottom
```

### Comment Display Modes (NEW!)

Choose how comment screenshots are displayed:

```bash
# Sequential: Show one screenshot at a time (default)
python create_video.py --reddit --comment-display sequential

# Overlay: Stack all screenshots with staggered fade-in
python create_video.py --reddit --comment-display overlay

# Slide: Horizontal slide transitions between screenshots
python create_video.py --reddit --comment-display slide
```

### Theme Control

The screenshot generator supports three themes:

- **dark** (default): Dark mode Reddit
- **light**: Light mode Reddit
- **transparent** (NEW!): Transparent background for better video integration

Edit `create_video.py` to change theme:

```python
screenshot_gen = RedditScreenshotGenerator(theme="transparent")
```

---

## NEW Features

### 🎬 Screenshot Animations

All screenshots now automatically include smooth animations:

- **Fade In**: Gradual opacity increase
- **Slide Up**: Smooth entrance from bottom
- **Zoom In**: Scale from 80% to 100%

Screenshots alternate between animation types for variety and engagement!

### ♻️ Screenshot Caching

Screenshots are automatically cached to speed up batch generation:

- First generation captures and saves screenshots
- Subsequent runs reuse cached screenshots
- Saves time and API calls
- Stored in `output/pending_review/screenshots/[post_id]/`

To disable caching, edit the screenshot generator call in `create_video.py`:

```python
screenshots = screenshot_gen.capture_post_screenshot(
    ...,
    use_cache=False  # Force fresh screenshot
)
```

### 🔄 Retry Logic

Automatic retry with exponential backoff for reliability:

- 3 retry attempts on failure
- 2-second initial delay, doubling each retry
- Handles network issues and slow page loads automatically

### 💬 Comment Screenshot Integration

Comments are now automatically captured and integrated into videos:

- Top 3 comments captured by default
- Displayed using selected display mode (sequential/overlay/slide)
- Each screenshot includes smooth animations
- Increases engagement and watch time

### 🎨 Custom Styling Options (Advanced)

Programmatically customize screenshot appearance:

```python
screenshots = screenshot_gen.capture_post_screenshot(
    post_url=url,
    font_scale=1.2,  # 20% larger fonts
    highlight_color="#ffff00",  # Yellow highlights on important text
    custom_css="""
        /* Your custom CSS here */
        .custom-class { color: red; }
    """
)
```

**Available options:**
- `font_scale`: Multiply font sizes (e.g., 1.2 = 20% larger)
- `highlight_color`: Highlight color for headings and bold text
- `custom_css`: Inject any custom CSS

---

## How It Works

1. **Browser Automation**: Playwright launches a headless Chromium browser
2. **Navigate to Reddit**: Opens the exact Reddit post URL
3. **Handle Popups**: Automatically closes NSFW warnings and "Use App" prompts
4. **Capture Screenshot**: Takes a high-quality PNG of the post content
5. **Save Screenshot**: Stored in `output/pending_review/screenshots/`
6. **Overlay on Video**: The screenshot is scaled and positioned on the background video

---

## Benefits vs Text Subtitles

**✅ Authenticity**: Shows real Reddit UI (more trustworthy)
**✅ Visual Appeal**: Colored upvote buttons, awards, profile pics
**✅ Professionalism**: Looks like major viral content channels
**✅ Engagement**: Viewers recognize the Reddit format instantly

**When to use text subtitles instead:**
- Faster rendering (no screenshot generation time)
- Custom stories (not from Reddit)
- AI-generated stories
- When Playwright isn't installed

---

## Troubleshooting

### "Playwright not found"
```bash
pip install playwright
python -m playwright install chromium
```

### "Timeout loading Reddit post"
- Reddit might be slow or down
- Try again in a few minutes
- Use `--no-screenshots` as fallback

### "Screenshot generation failed"
The script will automatically fall back to text subtitles if screenshot generation fails.

### Browser not found
```bash
# Reinstall browsers
python -m playwright install chromium
```

---

## Reddit Thread URL Output

When generating Reddit videos, the thread URL is now displayed **prominently**:

```
🔗 ==========================================================
   REDDIT THREAD: https://www.reddit.com/r/AmItheAsshole/...
   ==========================================================
📸 Screenshot: output/pending_review/screenshots/xyz/post.png
```

You can:
- **Copy the URL** to credit the source in video descriptions
- **Visit the thread** to read comments for follow-up videos
- **Track engagement** to see if your video drives traffic

---

## Example Output

```bash
$ python create_video.py aita --reddit

🤖 CONTENTBOT - VIRAL VIDEO GENERATOR
============================================================

🔍 Fetching story from Reddit...
[REDDIT] Fetching posts from r/AmItheAsshole...
[REDDIT] Found 45 quality posts from 50 fetched
✅ Found post: AITA for refusing to pay for my daughter's wedding...
   Upvotes: 3500 | Comments: 892
   Viral Score: 2847

🔗 ==========================================================
   REDDIT THREAD: https://www.reddit.com/r/AmItheAsshole/...
   ==========================================================

✅ Story ready: 145 words (~58s)

📸 Generating Reddit screenshot...
🌐 Loading Reddit post...
📷 Capturing post screenshot...
✅ Post screenshot saved: post.png
💬 Capturing up to 3 comment screenshots...
✅ Comment 1 screenshot saved
✅ Comment 2 screenshot saved
✅ Comment 3 screenshot saved
✅ Captured 3 comment screenshots
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
📁 Video: output/pending_review/aita_short.mp4
⏱️  Duration: 58.2s
🎭 Genre: aita
📊 Word count: 145
🔖 Source: reddit

🔗 ==========================================================
   REDDIT THREAD: https://www.reddit.com/r/AmItheAsshole/...
   ==========================================================
📸 Screenshot: output/pending_review/screenshots/xyz/post.png
============================================================
```

---

## Advanced: Customize Comment Capture

Comments are captured by default (top 3). To customize, edit `create_video.py`:

```python
screenshots = screenshot_gen.capture_post_screenshot(
    post_url=story['source_url'],
    output_dir=str(PENDING_DIR / "screenshots"),
    post_id=story['reddit_id'],
    capture_comments=True,  # Already enabled by default
    max_comments=5  # Capture top 5 instead of 3
)
```

To disable comment capture:

```python
screenshots = screenshot_gen.capture_post_screenshot(
    ...,
    capture_comments=False  # Only capture main post
)
```

Comment screenshots are saved as:
- `comment_1.png`
- `comment_2.png`
- etc.

And automatically integrated into the video based on `--comment-display` mode!

---

## Credits

Screenshot implementation inspired by [RedditVideoMakerBot](https://github.com/elebumm/RedditVideoMakerBot) ✨
