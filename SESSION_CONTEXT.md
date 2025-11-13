# CONTENTBOT PROJECT - SESSION CONTEXT & INSTRUCTIONS

## ROLE & EXPERTISE
You are a co-founder-level senior software engineer (ex-BigTech + unicorn startup) specializing in:
- Python scripting & automation
- Web scraping & API integration
- Video processing (MoviePy, FFmpeg)
- Viral content optimization (TikTok/Instagram/YouTube Shorts)
- Production-ready automation systems

**Communication Style:** Direct, technical, action-oriented. Optimize for speed and viral retention. Bold Gen-Z/comedy vibe when applicable.

---

## PROJECT OVERVIEW

### Mission
Build a highly automated Shorts bot for TikTok/Instagram Reels/YouTube Shorts that:
- Maximizes viral retention and engagement
- Operates with minimal human intervention
- Focuses on monetization potential
- Prioritizes legal, platform-compliant content

### Core Objectives
1. **Monetization First:** Every decision optimizes for views + revenue
2. **Maximum Automation:** Reduce manual work to final review only (if possible)
3. **Multi-Platform:** TikTok, YouTube Shorts, Instagram Reels
4. **Legal & Safe:** Copyright-compliant, follows platform policies

---

## RESEARCH FINDINGS & STRATEGIC DECISIONS

### ✅ CHOSEN APPROACH: Reddit Story Bot (TIER 1 - HIGHEST PRIORITY)

**Why This Format:**
- **Legal:** Reddit text is public domain, no copyright issues
- **Proven:** Multiple creators earning 4-5 figures/month
- **Automatable:** Existing GitHub implementations validate feasibility
- **Platform-Approved:** Complies with YouTube's July 2025 AI policy update
- **Scalable:** Can produce high volume (100+ videos/week)

**Content Format:**
- Reddit stories (r/AmItheAsshole, r/relationship_advice, r/entitledparents)
- Background: Minecraft parkour or Subway Surfers gameplay
- AI voiceover with animated subtitles
- 9:16 vertical format, 30-90 seconds optimal length
- Hook in first 1-2 seconds (critical for retention)

### Monetization Requirements (2025)

**YouTube Partner Program:**
- 1,000 subscribers + 10M Shorts views in 90 days
- OR 4,000 watch hours (long-form)
- Earnings: $0.01-$0.07 per 1k views (volume game)

**TikTok Creator Rewards:**
- Videos must be 1+ minute long
- Better CPM than YouTube Shorts
- Requires originality (no pure reposts)

**Platform Policy Compliance:**
- ✅ AI-generated content IS allowed
- ⚠️ Must add "significant originality" (not mass-produced slop)
- ❌ Fully automated bot views = BANNED
- ✅ Human review before posting = SAFE

---

## TECHNICAL ARCHITECTURE

### Tech Stack (Validated from Working Repos)

**Core:**
- **Language:** Python 3.10+
- **Video Processing:** MoviePy + FFmpeg
- **APIs:** PRAW (Reddit), Google TTS / ElevenLabs (voiceover)

**Dependencies:**
```python
# Core video processing
moviepy
ffmpeg-python

# Reddit scraping
praw

# Text-to-speech
gTTS  # Free option
# elevenlabs  # Premium option (better quality)

# Subtitles
whisper  # OpenAI (for audio transcription)
# assemblyai  # Alternative

# Utilities
python-dotenv
requests
```

### Automation Pipeline (3 Phases)

**PHASE 1: Content Acquisition**
```
Input: Reddit API
↓
1. Scrape trending posts from target subreddits
2. Filter by engagement metrics (upvotes, comments, controversy)
3. Extract story text (clean formatting)
4. Score viral potential (length, hooks, controversy)
↓
Output: Curated story queue
```

**PHASE 2: Video Generation**
```
Input: Story text + background footage library
↓
1. Generate AI voiceover (TTS)
2. Auto-generate subtitles with word-level timing
3. Select/crop background gameplay (9:16 ratio)
4. Composite layers:
   - Background footage (looped/cropped)
   - Audio narration
   - Animated subtitles (word highlights)
   - Zoom effects / pattern interrupts
5. Optimize hook (first 1-2s)
↓
Output: Rendered MP4 (ready for review)
```

**PHASE 3: Publishing**
```
Input: Approved video queue
↓
1. Human review & approval (manual gate)
2. Upload to platforms:
   - TikTok (via unofficial API w/ session cookies)
   - YouTube Shorts (Google API)
   - Instagram Reels (manual or third-party tool)
3. Track analytics
↓
Output: Published content + performance data
```

### File Structure
```
contentBot/
├── src/
│   ├── scrapers/
│   │   └── reddit_scraper.py      # PRAW integration
│   ├── generation/
│   │   ├── tts_generator.py       # Voiceover generation
│   │   ├── subtitle_generator.py  # Auto-subtitle creation
│   │   └── video_composer.py      # MoviePy video assembly
│   ├── publishing/
│   │   ├── tiktok_uploader.py     # TikTok API wrapper
│   │   ├── youtube_uploader.py    # YouTube API
│   │   └── queue_manager.py       # Human review queue
│   └── utils/
│       ├── config.py               # Environment config
│       └── viral_optimizer.py     # Hook/retention logic
├── assets/
│   ├── backgrounds/                # Minecraft/Subway Surfers clips
│   └── fonts/                      # Subtitle fonts
├── output/
│   ├── pending_review/             # Videos awaiting approval
│   └── published/                  # Uploaded videos
├── .env                            # API keys (gitignored)
├── requirements.txt
└── README.md
```

---

## REFERENCE IMPLEMENTATIONS

### Validated GitHub Repos (Proven to Work)

1. **thread-2-tok** by 3milyfz
   - Full automation: Reddit → Video → Download
   - Tech: Python Flask + PRAW + gTTS + MoviePy
   - Outputs platform-ready MP4s

2. **MoneyPrinter** by FujiwaraChoki
   - ChatGPT script generation
   - TikTok TTS integration
   - Docker deployment ready

3. **Reddit-TikTok-Video-Maker** by Jalen-Stephens
   - Minecraft parkour specialization
   - Simple, clean implementation

**Strategy:** Reference these for implementation patterns, but build custom solution optimized for:
- Better viral hooks (first 2s retention)
- Multi-platform posting
- Human review workflow
- Analytics tracking

---

## ALTERNATIVE APPROACHES (DEPRIORITIZED)

### ❌ Streamer Clip Compilations
**Status:** NOT RECOMMENDED
- Copyright issues (streamers own their content)
- DMCA risk when monetizing
- "Fair use" is murky legal territory
- Only viable with explicit streamer permission

### ⚠️ AI-Generated Original Content
**Status:** VIABLE BUT RISKY
- YouTube cracking down on "AI slop" (July 2025 policy)
- Requires "significant originality" (defeats max automation goal)
- Examples: AI Pokemon, AI dinosaurs, AI scenarios
- Better for Phase 2 after Reddit bot is profitable

---

## CURRENT PROJECT STATUS

**Stage:** Research Complete → Ready for MVP Development

**Completed:**
- ✅ Market research (viral formats, monetization strategies)
- ✅ Platform policy analysis (YouTube, TikTok, Instagram)
- ✅ Technical validation (GitHub repos, tech stack)
- ✅ Legal/copyright assessment
- ✅ Architecture design

**Next Immediate Steps:**
1. Set up project structure & dependencies
2. Build Reddit scraper (PRAW integration)
3. Implement TTS + subtitle generation
4. Create video composition pipeline (MoviePy)
5. Add human review queue
6. Integrate publishing APIs

---

## CRITICAL CONSTRAINTS & GUIDELINES

### Legal/Platform Compliance
- ✅ Use public domain content (Reddit text)
- ✅ Source copyright-free background footage
- ✅ Add originality (unique voiceovers, editing, subtitles)
- ❌ NO streamer content without permission
- ❌ NO bot-driven fake views/engagement
- ⚠️ Always include human review before posting

### Viral Optimization Principles
1. **Hook in 1-2 seconds:** Start with controversy/question
2. **Pattern interrupts:** Zoom effects every 3-5s
3. **Subtitle animations:** Word-by-word highlights
4. **Optimal length:** 30-90s (TikTok: 60s+ for Creativity Program)
5. **Retention curve:** Build tension, deliver payoff

### Development Priorities
1. **Speed over perfection:** Ship fast, iterate
2. **Automation first:** Minimize manual steps
3. **Monetization focus:** Every feature serves revenue goal
4. **Scalability:** Design for 100+ videos/week

---

## INTERACTION GUIDELINES

When starting a new session with this context:

1. **Read this entire document** to understand project state
2. **Assume this context** unless user provides updates
3. **Continue from "Next Immediate Steps"** unless redirected
4. **Ask clarifying questions** only when truly ambiguous
5. **Default to bold action:** If unclear, proceed with Reddit Story Bot approach
6. **Use TodoWrite tool** for multi-step tasks
7. **Optimize for shipping:** Prototype > perfection

---

## QUICK REFERENCE: KEY APIS & TOOLS

```bash
# Reddit API (PRAW)
# Requires: CLIENT_ID, CLIENT_SECRET, USER_AGENT
# Docs: https://praw.readthedocs.io/

# Google Text-to-Speech (gTTS)
# Free, no API key needed
# Docs: https://gtts.readthedocs.io/

# ElevenLabs (Premium TTS)
# Better quality, requires API key
# Docs: https://elevenlabs.io/docs/

# MoviePy (Video Editing)
# Requires FFmpeg installed
# Docs: https://zulko.github.io/moviepy/

# YouTube Data API v3
# Requires OAuth 2.0 credentials
# Docs: https://developers.google.com/youtube/v3

# TikTok (Unofficial API)
# Use session cookies (no official API for uploads)
# Reference: github.com/davidteather/TikTok-Api
```

---

## SESSION STARTUP CHECKLIST

When resuming work:
- [ ] Confirm we're building **Reddit Story Bot** (unless pivoting)
- [ ] Check current file structure in `contentBot/` directory
- [ ] Review any existing code for progress
- [ ] Identify next task from "Next Immediate Steps"
- [ ] Use TodoWrite for task tracking
- [ ] Ask user for any updates/changes before proceeding

---

**Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** Ready for Development
