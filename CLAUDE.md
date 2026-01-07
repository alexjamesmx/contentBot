# ContentBot - Viral Reddit Story Video Generator

**Mission**: Build a profitable automated system generating viral TikTok/YouTube Shorts content using Reddit stories + gameplay backgrounds (Subway Surfer/Minecraft parkour style).

**Status**: MVP - Basic pipeline works, fixing video generation bugs

---

## Market Research

### The Opportunity

**Proven Business Model**:
- Reddit story videos get **millions of views** on TikTok/YT Shorts
- Faceless channels earning **$1,000+/month** with automation
- Low competition in 2025, high demand for "brainrot" content

**Why This Works**:
1. **Dual-stimulus content** - Engaging visuals (parkour) + dramatic stories = hooks attention
2. **Endless content supply** - Reddit generates thousands of viral stories daily
3. **TikTok Creator Rewards** - $0.50-$5 per 1000 views (vs old $0.02-$0.04)
4. **YouTube Shorts Fund** - Additional monetization layer
5. **Proven retention** - Subway Surfer/Minecraft keeps viewers watching

### Monetization Paths

**Primary**:
- TikTok Creator Rewards Program (10K followers, 100K views/30d, 1min+ videos)
- YouTube Partner Program (Shorts Fund)

**Secondary**:
- Sponsorships ($200+ per shoutout)
- Affiliate marketing in comments
- Selling shoutouts/logo placements

**Key Requirement**: Must be **original content** - can't just scrape Reddit screenshots. Need AI-generated stories or heavy transformative editing.

### Competition Analysis

**Existing GitHub Solutions**:
- [FullyAutomatedRedditVideoMakerBot](https://github.com/raga70/FullyAutomatedRedditVideoMakerBot) - Auto-posts to TikTok/IG/YT
- [RedditVideoMakerBot](https://github.com/elebumm/RedditVideoMakerBot) - 6K+ stars, most popular
- [RedditReels](https://github.com/vvinniev34/RedditReels) - Full automation with uploaders

**Our Advantage**:
- AI-generated stories (not scraped) = fully original content
- Premium ElevenLabs voices = better retention
- Smart caching = 90% cost reduction
- Modern tech stack (MoviePy 2.x, Groq AI)

### Content Strategy

**Best Subreddits** (for inspiration, not scraping):
- r/AmItheAsshole - Controversial dilemmas
- r/ProRevenge - Justice stories
- r/TIFU - Embarrassing moments
- r/relationship_advice - Drama

**Viral Font Research**:
- **#1: Montserrat Bold** (used in 60% of viral videos)
- Font size: 36-40px
- Position: Bottom third (280px from bottom)
- Style: Yellow text + black stroke = max visibility
- Background: 60% opacity black for readability

**Optimal Video Format**:
- Length: 1-3 minutes (TikTok Creativity Program requirement)
- Resolution: 1080x1920 (9:16 vertical)
- FPS: 30 (smooth on mobile)
- Hook: First 3 seconds critical
- Retention: Background gameplay essential

---

## Current System Architecture

```
Story Generation (Groq AI - llama-3.3-70b)
    ↓
Audio Generation (ElevenLabs Premium TTS w/ caching)
    ↓
Subtitle Sync (2-word chunks, viral style)
    ↓
Video Composition (MoviePy 2.x)
    ↓
Output: 1080x1920 MP4 ready for upload
```

### Tech Stack

**Backend**:
- Python 3.11+
- Flask API
- Groq AI (story generation)
- ElevenLabs API (premium voice)
- MoviePy 2.x (video rendering)

**Frontend**:
- React + Vite
- TailwindCSS
- Axios for API calls

**Storage**:
- Local file system
- Smart caching (audio + metadata)

### File Structure

```
contentBot/
├── app.py                      # Flask API server
├── src/
│   ├── generation/
│   │   ├── story_generator.py     # AI story generation
│   │   ├── story_templates.py     # Genre templates (comedy, terror, AITA, etc)
│   │   ├── tts_elevenlabs.py      # Premium TTS with caching
│   │   ├── tts_generator.py       # Free gTTS fallback
│   │   ├── subtitle_generator.py  # 2-word viral subtitles
│   │   └── video_composer.py      # Final render
│   └── utils/
│       ├── config.py               # Environment config
│       └── metadata.py             # Video metadata + hashtags
├── assets/
│   ├── backgrounds/               # Gameplay videos (Subway Surfer, Minecraft)
│   └── fonts/                     # Montserrat-Bold.ttf (viral font)
├── output/
│   ├── pending_review/            # Generated videos
│   └── stories/                   # Story library (JSON)
└── cache/
    └── elevenlabs/                # Cached audio (saves $$)
```

---

## Known Issues & Fixes Needed

### CRITICAL - Video Generation Failing

**Symptoms**:
- Subtitles cut off at bottom of screen
- Video render crashes/hangs

**Root Cause Analysis**:
- ✅ FIXED: Subtitle positioning at 65% height caused cutoff
- ✅ FIXED: Font size too large (80px → 72px)
- ✅ FIXED: Margins too small (140px → 200px)
- NEW: Position now calculated from bottom: `height - txt_height - 280px`

**Testing Required**:
- [ ] Generate 30s test video
- [ ] Verify subtitles visible on mobile preview
- [ ] Check Montserrat-Bold font loads correctly
- [ ] Confirm ElevenLabs audio syncs with video

### Subtitle Optimization

**Current Settings** (video_composer.py:268-286):
```python
font_size=72          # Optimal for mobile
stroke_width=4        # Thick black outline
size=(width-200, None) # Safe margins
y_position = height - txt_height - 280  # Bottom third positioning
```

**Research-Based Best Practices**:
- Yellow text (current) = proven viral color
- Montserrat Bold (current) = #1 font for 2025
- 2-word chunks (current) = optimal retention
- Position: Bottom third, never center (blocks face/action)

---

## Development Roadmap

### Phase 1: MVP Working (Current)
- [x] AI story generation (Groq)
- [x] Premium TTS (ElevenLabs + caching)
- [x] Subtitle generation (2-word chunks)
- [x] Video composition pipeline
- [x] Web UI for generation
- [x] Story library
- [ ] **Fix video generation bugs** ← YOU ARE HERE
- [ ] End-to-end test: Story → Video → Upload

### Phase 2: Viral Optimization
- [ ] Add Montserrat-Bold font auto-download
- [ ] Implement word-by-word subtitle highlighting (trending in 2025)
- [ ] Add background music layer (copyright-free)
- [ ] Batch generation (10 videos at once)
- [ ] A/B test different fonts/colors
- [ ] Auto-thumbnail generation

### Phase 3: Full Automation
- [ ] Auto-upload to TikTok (pyppeteer/selenium)
- [ ] Auto-upload to YouTube Shorts (YouTube Data API)
- [ ] Auto-schedule posts (best times: 7-9pm, 12-2pm, 6-8am EST)
- [ ] Performance analytics dashboard
- [ ] Auto-hashtag optimization based on trends

### Phase 4: Scale & Monetization
- [ ] Multi-account management
- [ ] Hook testing (A/B test 5 hooks per story)
- [ ] Voice cloning (custom brand voice)
- [ ] Thumbnail A/B testing
- [ ] Sponsorship CRM
- [ ] Revenue tracking dashboard

---

## Critical Guidelines for Claude

### Code Style
- **Zero unnecessary comments** - Code should be self-documenting
- **Minimal tokens** - Every line must add value
- **Production-ready** - No TODOs, no placeholders
- **Error handling** - Fail fast with clear messages

### When Editing Code
1. **Read the entire file first** - Understand context
2. **Fix root cause, not symptoms** - Don't patch
3. **Test immediately** - Run `python -m py_compile` after edits
4. **Verify imports** - Check all dependencies load
5. **No breaking changes** - API must stay compatible

### Video Generation Rules
- **Subtitles MUST be readable on mobile** - Test on 5.5" screen mentally
- **Font MUST exist** - Fallback to Impact.ttf (Windows) if Montserrat missing
- **Positioning from bottom** - Never use percentage heights
- **Audio MUST sync** - 2-word chunks = duration / word_count
- **Background MUST loop** - Handle videos shorter than audio

### Performance Targets
- Story generation: <5s
- TTS generation: <8s (or instant if cached)
- Video render: <30s for 60s video
- Total pipeline: <45s end-to-end

### Business Priorities
1. **Functionality first** - Must generate working videos
2. **Quality second** - Videos must look professional
3. **Speed third** - Optimize after it works
4. **Features last** - No new features until core works

---

## Quick Commands

### Start Backend
```bash
python app.py
# Backend: http://localhost:5000
```

### Start Frontend
```bash
cd contentbot-ui && npm run dev
# Frontend: http://localhost:5173
```

### Test Video Generation (CLI)
```bash
python -c "
from src.generation.story_generator import StoryGenerator
from src.generation.tts_elevenlabs import ElevenLabsTTS
from src.generation.subtitle_generator import SubtitleGenerator
from src.generation.video_composer import VideoComposer
from src.utils.config import ELEVENLABS_API_KEY

# Generate story
gen = StoryGenerator()
story = gen.generate_story(genre='comedy')
print(f'Story: {story[\"story\"][:100]}...')

# Generate audio
tts = ElevenLabsTTS(ELEVENLABS_API_KEY)
audio_path = tts.generate_audio(story['story'], voice='mark')
print(f'Audio: {audio_path}')

# Generate subtitles
from moviepy import AudioFileClip
audio = AudioFileClip(audio_path)
duration = audio.duration
audio.close()

sub_gen = SubtitleGenerator(words_per_chunk=2)
subs = sub_gen.generate_subtitles(story['story'], duration)
print(f'Subtitles: {len(subs)} chunks')

# Create video
composer = VideoComposer()
video_path = composer.create_video(
    audio_path=audio_path,
    subtitles=subs,
    genre='comedy'
)
print(f'Video: {video_path}')
"
```

### Check Subtitle Font
```bash
python -c "from pathlib import Path; print('Montserrat:', (Path('assets/fonts/Montserrat-Black.ttf').exists()))"
```

---

## Monetization Checklist

### TikTok Creator Rewards Requirements
- [ ] 10,000 followers
- [ ] 100,000 views in last 30 days
- [ ] Videos 1+ minutes long
- [ ] Original content (AI-generated = original ✓)
- [ ] Account in US/UK/Germany/Japan/Korea/France/Brazil
- [ ] 18+ years old

### Content Strategy
- [ ] Post 2x daily (3+ hours apart)
- [ ] Best times: 7-9pm, 12-2pm, 6-8am EST
- [ ] Use trending sounds (add background music layer)
- [ ] Optimize hashtags: #fyp #redditstories #storytime
- [ ] Reply to comments (engagement = algorithm boost)
- [ ] Cross-post to YouTube Shorts + Instagram Reels

### Revenue Optimization
- [ ] Add email to bio for sponsors
- [ ] Track RPM (should be $0.50-$5 per 1000 views)
- [ ] Test different genres (AITA > Comedy for engagement)
- [ ] A/B test hooks (first 3 seconds critical)
- [ ] Batch content (film 30 videos, post over 15 days)

---

## Research Sources

**Monetization**:
- [TikTok Creator Rewards Program Requirements](https://www.tiktok.com/creator-academy/en/article/creator-rewards-program)
- [TikTok Creativity Program Payout 2025](https://www.shortsgenerator.ai/blog/tiktok-creativity-program-beta-payout/)
- [How to Make Money with Reddit Story Videos](https://dicloak.com/blog-detail/how-to-make-money-with-reddit-story-tiktok-videos-tiktok-creativity-program)

**Viral Fonts & Styling**:
- [Best Fonts for TikTok Subtitles 2025](https://sendshort.ai/guides/tiktok-font/)
- [Montserrat: The Most Popular Subtitle Font](https://www.submagic.co/blog/best-font-for-subtitle)
- [Caption Style Guide for Viral Videos](https://www.capcut.com/resource/caption-style/)

**Automation**:
- [FullyAutomatedRedditVideoMakerBot](https://github.com/raga70/FullyAutomatedRedditVideoMakerBot)
- [RedditVideoMakerBot (6K+ stars)](https://github.com/elebumm/RedditVideoMakerBot)
- [Thread-2-Tok: Reddit to TikTok Automation](https://github.com/3milyfz/thread-2-tok)

**Business Models**:
- [AI Reddit Story Video Generator](https://www.revid.ai/tools/ai-reddit-story-video-generator) - Pricing: $19-60/month
- [Short AI Pricing](https://www.short.ai/minecraft-parkour-video) - $19/month for 40 videos

---

## Next Actions

1. **Test video generation** - Run CLI command above, verify output
2. **Fix any render errors** - Check MoviePy logs, font loading
3. **Verify subtitle positioning** - Open video, check bottom text visible
4. **Download Montserrat-Bold** - If missing, auto-download or use Impact fallback
5. **End-to-end test** - Generate 5 videos, check quality on mobile
6. **Deploy to production** - Once stable, set up auto-upload pipeline

**Current Blocker**: Video generation failing - subtitles fixed, need full test.

**Partner Mode**: I'm your technical co-founder. My job: ship working code fast, zero fluff. Your job: define what "working" means. Let's print money. 💰

---

## Testing Requirement

**MANDATORY**: After implementing or modifying ANY code:
1. Run syntax check: `python -m py_compile <file>.py`
2. Test the actual functionality (run the code)
3. Verify output meets expectations
4. For video generation: ensure video plays and subtitles are visible

**DO NOT** submit code without testing it first.
