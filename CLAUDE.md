# Who are we 
I'm a startup founder product engineer building a complete AI-powered content creation studio at scale. We care about automation, speed, and real-world results.

# ContentBot - AI Content Creation Studio

**Mission**: Build a complete, professional AI-powered video creation studio for generating viral TikTok/YouTube Shorts automatically.

**Product Vision**: Enable creators to produce high-quality, monetizable video content at scale - from idea to final video in under 60 seconds.

**Status**: ✅ Core Pipeline Complete | 🚧 Building Full Studio Features (Jan 2026)

---

## 🎯 Core Principle: Purpose-Driven Development

### CRITICAL RULES FOR AI (Claude)

When making ANY code change, modification, or addition:

1. **Every change must serve the complete studio vision**
   - Does this help creators make better content?
   - Does this enable automation/scale?
   - Does this improve monetization potential?
   - If NO to all three → don't implement it

2. **Zero waste policy**
   - No unnecessary comments (code should be self-documenting)
   - No placeholder TODOs (implement or don't)
   - No "nice to have" features (only essential)
   - Minimal token usage in all files

3. **Production-first mindset**
   - Every feature must work end-to-end
   - Test immediately after implementation
   - No breaking changes to existing pipeline
   - Fail fast with clear error messages

4. **Studio integration requirement**
   - New features must integrate with existing UI/API
   - Must follow current design patterns
   - Must use existing infrastructure (Flask, React, MoviePy)
   - No isolated features that don't connect

### Development Philosophy

**We are building a startup product for real users (creators making money).**

This means:
- **Functionality > Features** - Working basic feature beats broken advanced feature
- **Speed > Perfection** - Ship fast, iterate based on user feedback
- **Integration > Innovation** - Connect existing tools well rather than invent new ones
- **Monetization > Metrics** - Track what makes users money, not vanity metrics

---

## 🏗️ System Architecture

### Current Pipeline (MVP - Complete)

```
1. Story Generation → Groq AI (llama-3.3-70b, human-like prompts)
2. Audio Generation → ElevenLabs TTS (premium voices, smart caching)
3. Subtitle Sync → 4-word chunks, viral positioning
4. Video Composition → MoviePy 2.x (1080x1920, 30fps)
5. Output → MP4 ready for TikTok/YouTube Shorts
```

### Tech Stack

**Backend**: Python 3.11+ | Flask API | Groq AI | ElevenLabs | MoviePy 2.x
**Frontend**: React + Vite | TailwindCSS | Axios
**Storage**: Local filesystem | Smart caching (audio + metadata)

### File Structure (Essential Paths)

```
app.py                               # Flask API server
src/generation/
  ├── story_generator.py            # AI story generation (5 genres)
  ├── story_templates.py            # Genre-specific prompts
  ├── tts_elevenlabs.py             # Premium TTS with caching
  ├── subtitle_generator.py         # 4-word viral subtitles
  └── video_composer.py             # Final render pipeline
contentbot-ui/src/pages/            # React UI components
assets/backgrounds/                  # Gameplay videos
output/pending_review/              # Generated videos
cache/elevenlabs/                   # Cached audio (cost savings)
```

---

## 💰 Monetization Strategy (TikTok Creator Rewards 2025)

### Requirements Checklist
- ✅ **60+ second videos** (system defaults to 75s)
- ✅ **Original content** (AI-generated = original)
- ✅ **Human-like quality** (anti-AI detection prompts)
- ⏳ **10,000 followers** (requires posting consistency)
- ⏳ **100K views/30 days** (requires 2x daily posts)

### Revenue Potential
- **Conservative**: $450/month (600K views at $0.75 RPM)
- **Moderate**: $1,200/month (1.2M views at $1.00 RPM)
- **High-retention**: $1,800/month (1.2M views at $1.50 RPM + bonus)

### Content Strategy
- Post 2x daily, 3+ hours apart
- Best times: 7-9pm, 12-2pm, 6-8am EST
- Cross-post: TikTok + YouTube Shorts + Instagram Reels
- Engage with comments (algorithm boost)

---

## 🎬 Studio Features (Current + Roadmap)

### ✅ Phase 1: Core Pipeline (COMPLETE)
- [x] AI story generation (5 genres: comedy, terror, AITA, gen-z, relationship)
- [x] Premium TTS with emotion (ElevenLabs optimized)
- [x] Viral subtitle system (4-word chunks, yellow text, Montserrat Bold)
- [x] Video composition (background + audio + subtitles)
- [x] Web UI (step-by-step workflow)
- [x] Story library (save/reuse stories)
- [x] Analytics dashboard (monetization projections)

### 🚧 Phase 2: Studio Automation (IN PROGRESS)
- [x] Batch mode (generate 5-20 videos sequentially)
- [ ] **Subtitle Editor** (live preview, custom styling per video)
- [ ] Background music layer (copyright-free tracks)
- [ ] Hook A/B testing (5 variations per story)
- [ ] Auto-upload integration (TikTok/YouTube APIs)

### 📋 Phase 3: Scale & Optimization (PLANNED)
- [ ] Multi-account management
- [ ] Advanced analytics (retention heatmaps, best hooks)
- [ ] Template marketplace (import/export genre prompts)
- [ ] Voice cloning (custom brand voice)
- [ ] Performance tracking (link TikTok/YouTube metrics)

---

## 🎨 Viral Optimization (2025 Research-Backed)

### Story Generation
- **Target**: 150-220 words (60-90s duration at 2.5 words/sec)
- **Style**: Conversational, filler words ("like", "literally"), sentence fragments
- **Emotion**: CAPS for emphasis, "..." for pauses
- **Hook**: First sentence must grab attention (question, bold statement)
- **Anti-AI**: Avoid "delve", "utilize", "moreover" (AI tells)

### Voice Generation (ElevenLabs Settings)
```python
stability = 0.45           # Natural variation (not robotic)
similarity_boost = 0.75    # Match target speaker
style = 0.3                # Emotional delivery
model = "eleven_turbo_v2_5"  # Best for storytelling
use_speaker_boost = True   # Enhanced emotion
```

### Subtitle System
- **Words per chunk**: 4 (proven retention sweet spot)
- **Font**: Montserrat Bold (60% of viral videos use this)
- **Color**: Yellow (#FFFF00) + Black stroke (#000000, 3px)
- **Position**: Bottom third (420px margin from bottom)
- **Emphasis**: Preserve CAPS for emotional words

### Video Format
- **Resolution**: 1080x1920 (9:16 vertical)
- **FPS**: 30 (mobile-optimized)
- **Duration**: 60-90s (monetization + retention sweet spot)
- **Background**: Subway Surfer/Minecraft parkour (dual-stimulus)

---

## 🛠️ Development Guidelines for Claude

### Code Modification Rules

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
5. Update this file (CLAUDE.md) if architecture changes

**Performance targets:**
- Story generation: <5s
- TTS generation: <8s (or instant if cached)
- Video render: <30s for 60s video
- Total pipeline: <45s end-to-end

### Testing Requirements

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

### What NOT to Do
- ❌ Create documentation files (update CLAUDE.md or README.md only)
- ❌ Add features not requested by user
- ❌ Implement "TODO" placeholders (finish it or skip it)
- ❌ Break existing video generation pipeline
- ❌ Add unnecessary abstractions/helpers for one-time use
- ❌ Use emojis in code (only in docs if requested)

---

## 📚 Documentation Structure

**CLAUDE.md** (this file): AI instructions, studio vision, development rules
**README.md**: User-facing quick start, setup instructions, key features
**PROJECT.md**: Technical reference (API endpoints, troubleshooting)

All other docs are synthesized into these three files.

---

## 🚀 Quick Start Commands

```bash
# Start Backend
python app.py  # http://localhost:5000

# Start Frontend
cd contentbot-ui && npm run dev  # http://localhost:5173

# Quick Test (verify optimizations)
python -c "from src.generation.subtitle_generator import SubtitleGenerator; sg = SubtitleGenerator(); print(f'Words per chunk: {sg.words_per_chunk}')"
# Expected: words_per_chunk=4
```

---

## 🎯 Current Development Focus

### Immediate Priority: Functional Subtitle Editor

**Goal**: Enable users to customize subtitle styling and preview in real-time

**Requirements**:
1. Backend endpoint: `POST /api/subtitles/config` (save subtitle settings)
2. Backend endpoint: `GET /api/subtitles/config` (load saved settings)
3. Frontend: Make SubtitleConfig.jsx functional (currently just UI mockup)
4. Integration: Apply custom settings in video_composer.py
5. Persistence: Store config in JSON file (assets/subtitle_config.json)

**Implementation Notes**:
- Use existing video_composer.py subtitle rendering logic
- Allow per-video override or global default
- Preview must update in real-time (no backend calls for preview)
- Save should persist to filesystem (simple JSON storage)

### Next Priority: Background Music Layer

**Goal**: Add optional background music to videos (copyright-free)

**Requirements**:
1. Music library (assets/music/)
2. Backend endpoint: `POST /api/music/upload`
3. Generator UI: "Add Background Music" toggle
4. Video composer: Mix audio (story voice + music at 20% volume)

---

## 🔧 Known Issues & Fixes

### ✅ Completed Optimizations
- Story generation: Human-like authenticity (anti-AI detection)
- Duration targeting: 60-90s (monetization requirement)
- Subtitle optimization: 4-word chunks (retention)
- Voice emotion: Natural pauses and emphasis
- UI defaults: 75s duration, 4 words, ElevenLabs on

### 🐛 Current Bugs
- None reported (system stable)

### 💡 Future Enhancements
- Parallel batch processing (currently sequential)
- Resume failed batches
- Auto-upload to TikTok/YouTube
- Email notifications when batch completes

---

## 📊 Success Metrics

**Product success = User monetization success**

Track:
- Videos generated per day (goal: 10+)
- Monetizable videos % (60s+, should be 100%)
- Average video quality (manual review)
- Time from idea to final video (goal: <60s)

Don't track (vanity metrics):
- Code coverage
- Number of features
- Lines of code

---

## 💼 Business Context

**Target User**: Faceless content creators (TikTok/YouTube Shorts)
**User Goal**: Build audience, reach Creator Rewards, earn $1K+/month
**Our Goal**: Enable users to produce 60+ videos/month at professional quality

**Revenue Model** (future):
- Freemium: 10 videos/month free
- Pro: $19/month for unlimited + premium voices
- Agency: $99/month for multi-account + white-label

**Competitive Advantage**:
- AI-generated stories (100% original, not scraped)
- Smart caching (90% cost reduction vs competitors)
- Modern tech (MoviePy 2.x, Groq AI, ElevenLabs)
- Research-backed viral optimizations (2025 data)

---

## 📖 Key Research Sources

**Monetization**:
- TikTok Creator Rewards Program official docs
- TikTok Creativity Program Beta Payout 2025
- Reddit story channel revenue reports

**Viral Content**:
- Best Fonts for TikTok Subtitles 2025 (Montserrat dominance)
- Caption Style Guide for Viral Videos
- Subtitle retention studies (3-5 words optimal)

**Automation**:
- FullyAutomatedRedditVideoMakerBot (GitHub)
- RedditVideoMakerBot (6K+ stars, most popular)
- AI voice emotion optimization (ElevenLabs docs)

---

## 🎓 Studio Philosophy Summary

**We are building professional creator tools, not toys.**

Every feature must:
1. ✅ Help creators make better content
2. ✅ Enable automation/scale
3. ✅ Improve monetization potential

If a feature doesn't clearly serve one of these, don't build it.

**Development mantra**: Ship working features fast → Get user feedback → Iterate

---

**Last Updated**: January 10, 2026
**System Version**: 2.0 - Full Studio Evolution
**Current Phase**: Expanding from MVP to complete creation studio
