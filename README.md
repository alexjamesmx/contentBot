# ContentBot - Viral Shorts Automation

Fully automated Reddit story scraper + AI video generator for TikTok, Instagram Reels, and YouTube Shorts.

**Features:** Reddit scraping with **authentic screenshots**, ElevenLabs TTS, viral subtitles, duplicate detection, multi-genre support.

## 🚀 Quick Start

### 1. Setup API Keys

Edit `.env` file:

```bash
# Required for AI story generation
GROQ_API_KEY=your_groq_key_here

# Optional: Premium TTS (recommended)
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Optional: Reddit scraping
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
```

**Get API Keys:**
- Groq (free): https://console.groq.com/
- ElevenLabs ($5/mo recommended): https://elevenlabs.io/
- Reddit (free): See `CLAUDE.md`

**For Reddit Screenshots:**
```bash
pip install playwright
python -m playwright install chromium
```
See `SCREENSHOT_SETUP.md` for details.

**File Caching (Save Tokens):**
```bash
# Reuse existing audio/video files (saves time & API credits)
REUSE_EXISTING_FILES=true    # Default: true
```

Set to `false` for production (always generate fresh content).

### 2. Add Background Videos

Download 3-5 videos (Minecraft parkour, Subway Surfers, etc.) and save to `assets/backgrounds/`

**Quick sources:**
- Pexels: https://www.pexels.com/videos/ (search "minecraft parkour")
- YouTube: Search "minecraft parkour no copyright" and download
- Record your own gameplay

### 3. Create Your First Video

```bash
# AI-generated story
python create_video.py comedy

# Reddit story (requires Reddit API setup)
python create_video.py aita --reddit
```

Check `output/pending_review/` for your video!

---

## 📁 Project Structure

```
contentBot/
├── create_video.py              # ⭐ Main entry point
├── create_video_interactive.py  # Interactive mode
├── requirements.txt             # Dependencies
├── .env                        # API keys (DO NOT COMMIT)
├── README.md                   # This file
├── SESSION_CONTEXT.md          # Full project context
├── REDDIT_SETUP_GUIDE.md       # Reddit API setup
│
├── src/                        # Source code
│   ├── generation/             # Video generation
│   │   ├── story_generator.py
│   │   ├── tts_generator.py
│   │   ├── tts_elevenlabs.py
│   │   ├── subtitle_generator.py
│   │   └── video_composer.py
│   ├── scrapers/               # Reddit scraping
│   │   └── reddit_scraper.py
│   ├── utils/                  # Utilities
│   │   ├── config.py
│   │   └── duplicate_detector.py
│   └── publishing/             # Platform upload (Phase 2)
│
├── scripts/                    # Setup utilities
│   ├── download_fonts.py
│   ├── download_assets.py
│   └── download_music.py
│
├── tests/                      # Test files
│   └── test_story.py
│
├── assets/                     # Media assets
│   ├── backgrounds/            # Background videos
│   ├── fonts/                  # Subtitle fonts
│   └── music/                  # Background music
│
└── output/                     # Generated videos
    ├── pending_review/         # Videos to review
    └── published/              # Published videos
```

---

## 🎬 Usage Examples

### AI-Generated Stories
```bash
python create_video.py comedy
python create_video.py terror
python create_video.py aita
```

### Reddit Stories (Auto-scraped)
```bash
# Fetch from r/AmItheAsshole
python create_video.py aita --reddit

# Fetch from specific subreddit
python create_video.py --reddit --subreddit tifu
python create_video.py --reddit --subreddit confession
```

### Advanced Options
```bash
# Custom story
python create_video.py --custom "Your story text here..."

# Different TTS accent (gTTS)
python create_video.py comedy --accent uk

# No subtitles
python create_video.py comedy --no-subs

# Custom background
python create_video.py --background assets/backgrounds/minecraft.mp4
```

**Available genres:** `comedy`, `terror`, `aita`, `genz_chaos`, `relationship_drama`

---

## ✅ Features

**Content Sources:**
- ✅ AI story generation (Groq API)
- ✅ Reddit story scraping (PRAW)
- ✅ Custom story input
- ✅ Duplicate detection

**Audio:**
- ✅ ElevenLabs TTS (premium, 6 viral voices)
- ✅ Google TTS (free fallback)
- ✅ Multi-accent support

**Video:**
- ✅ Viral subtitle system (2-word chunks, yellow text)
- ✅ Auto background video selection
- ✅ 9:16 vertical format (TikTok/Reels/Shorts)
- ✅ Genre-optimized fonts

**Automation:**
- ✅ End-to-end pipeline (story → video)
- ✅ Viral score ranking for Reddit posts
- ✅ Automatic file overwriting
- ✅ Quality validation

---

## 🎯 Recommended Setup

### Essential (Required):
1. ✅ Groq API key (free) - AI story generation
2. ✅ Background videos (3-5 files in `assets/backgrounds/`)

### Recommended (Better Quality):
3. ⭐ ElevenLabs API ($5/mo) - Premium TTS voices
   - 30x better quality than free TTS
   - Viral "narrator voice" trend
   - Genre-specific voices (Mark, Snap, Peter, etc.)

### Optional (More Content):
4. 🔄 Reddit API (free) - Auto-scrape viral stories
   - Setup guide: `REDDIT_SETUP_GUIDE.md`
   - Auto-duplicate detection
   - Viral score ranking

---

## 💡 Viral Optimization Tips

**Content:**
- Use Reddit stories for proven viral potential
- `comedy` and `aita` have highest engagement
- Stories auto-optimized for 45-90s duration

**Quality:**
- Use ElevenLabs TTS for +30% retention
- Yellow subtitles (2-word chunks) = more viral
- Genre-specific fonts auto-selected

**Workflow:**
- Reddit mode prevents duplicate posts automatically
- Files auto-overwrite (no cleanup needed)
- Videos saved to `output/pending_review/` for review

---

## 🔧 Troubleshooting

**"GROQ_API_KEY not found"**
- Check `.env` file exists (not `.env.example`)
- Verify API key is set: `GROQ_API_KEY=gsk_...`

**"No backgrounds found"**
- Download 3-5 background clips
- Save to `assets/backgrounds/`
- Name them `minecraft_1.mp4`, `subway_surfers_1.mp4`, etc.

---

## 📚 Documentation

- **Main guide**: `README.md` (this file)
- **Full context**: `SESSION_CONTEXT.md` (project architecture, goals)
- **Reddit setup**: `REDDIT_SETUP_GUIDE.md` (if using Reddit mode)

## 🎯 Phase 2 Roadmap

- [ ] Batch generation (10+ videos at once)
- [ ] Background music mixing (FFmpeg audio layer)
- [ ] Multi-TTS engine wrapper (OpenAI, TikTok TTS, AWS Polly)
- [ ] Rich CLI interface (colored output, progress bars)
- [ ] Auto-upload to platforms
- [ ] Analytics dashboard

## 📊 Tech Stack

- **AI**: Groq API (Llama 3.3 70B)
- **Reddit**: PRAW (Reddit API wrapper)
- **TTS**: ElevenLabs + Google TTS
- **Video**: MoviePy + FFmpeg
- **Language**: Python 3.13
