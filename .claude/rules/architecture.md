# System Architecture

## Current Pipeline (MVP - Complete)

```
1. Story Generation → Groq AI (llama-3.3-70b, human-like prompts)
2. Audio Generation → ElevenLabs TTS (premium voices, smart caching)
3. Subtitle Sync → 4-word chunks, viral positioning
4. Video Composition → MoviePy 2.x (1080x1920, 30fps)
5. Output → MP4 ready for TikTok/YouTube Shorts
```

## Tech Stack

**Backend**: Python 3.11+ | Flask API | Groq AI | ElevenLabs | MoviePy 2.x
**Frontend**: React + Vite | TailwindCSS | Axios
**Storage**: Local filesystem | Smart caching (audio + metadata)

## File Structure (Essential Paths)

```
app.py                               # Flask API server
src/generation/
  ├── story_generator.py            # AI story generation (5 genres)
  ├── story_templates.py            # Genre-specific prompts
  ├── tts_elevenlabs.py             # Premium TTS with caching
  ├── subtitle_generator.py         # 4-word viral subtitles
  └── video_composer.py             # Final render pipeline
src/effects/
  └── effect_engine.py              # Video effects system
src/agents/
  └── effect_agent.py               # AI effect generation
contentbot-ui/src/pages/            # React UI components
assets/backgrounds/                  # Gameplay videos
output/pending_review/              # Generated videos
cache/elevenlabs/                   # Cached audio (cost savings)
tests/unit/                         # Unit tests
tests/integration/                  # Integration tests
```

## Viral Optimization (2025 Research-Backed)

### Story Generation
- **Target**: 150-220 words (60-90s duration at 2.5 words/sec)
- **Style**: Conversational, filler words ("like", "literally")
- **Emotion**: CAPS for emphasis, "..." for pauses
- **Hook**: First sentence must grab attention
- **Anti-AI**: Avoid "delve", "utilize", "moreover"

### Voice Generation (ElevenLabs Settings)
```python
stability = 0.45           # Natural variation
similarity_boost = 0.75    # Match target speaker
style = 0.3                # Emotional delivery
model = "eleven_turbo_v2_5"
use_speaker_boost = True
```

### Subtitle System
- **Words per chunk**: 4 (proven retention)
- **Font**: Montserrat Bold
- **Color**: Yellow (#FFFF00) + Black stroke (3px)
- **Position**: Bottom third (420px margin)

### Video Format
- **Resolution**: 1080x1920 (9:16 vertical)
- **FPS**: 30 (mobile-optimized)
- **Duration**: 60-90s (monetization sweet spot)
- **Background**: Subway Surfer/Minecraft parkour
