# ContentBot - AI Viral Video Generator

## Mission
Turn text stories into viral short-form videos (TikTok/Reels/Shorts) with AI-powered voiceovers and subtitles.

## Core Workflow
```
Story (AI/Custom) → Audio (ElevenLabs/gTTS) → Subtitles → Video (9:16) → Gallery
```

## Tech Stack
- **Backend**: Python/Flask
- **Frontend**: React/Vite/TailwindCSS
- **AI**: Groq (stories), ElevenLabs (voice)
- **Video**: MoviePy/FFmpeg

## Quick Start

### 1. Backend
```bash
python app.py
# Runs on http://localhost:5000
```

### 2. Frontend
```bash
cd contentbot-ui
npm install
npm run dev
# Runs on http://localhost:5173
```

### 3. Cleanup (Optional)
```bash
python cleanup_junk.py
# Removes temp files, NUL files, etc.
```

## Project Structure
```
contentBot/
├── app.py                    # Flask API
├── create_video.py           # CLI generator
├── src/generation/           # Core engine
│   ├── story_generator.py    # AI stories (Groq)
│   ├── tts_elevenlabs.py     # Voice (cached)
│   ├── subtitle_generator.py # Viral subtitles
│   └── video_composer.py     # Final render
├── contentbot-ui/            # React web app
└── output/
    ├── pending_review/       # Videos
    └── stories/              # Story library
```

## Key Features

### ElevenLabs Caching (Saves $$)
- Automatic content-based caching
- Reuse audio for identical text
- **Result**: 90% cost reduction

### Story Library
- Save stories as editable JSON
- API: `GET/POST/PUT/DELETE /api/stories`
- Location: `output/stories/`

### Video Generation
- Genres: comedy, terror, aita, genz_chaos
- Format: 1080x1920 (9:16 vertical)
- Subtitles: 2-word chunks (viral style)

## Environment Variables

**Required:**
```
GROQ_API_KEY=your_key
```

**Recommended:**
```
ELEVENLABS_API_KEY=your_key
```

## API Endpoints

### Generation
```
POST /api/generate/story      # AI story
POST /api/generate/audio      # TTS (cached)
POST /api/generate/subtitles  # Sync subtitles
POST /api/generate/video      # Render final
```

### Story Library
```
GET    /api/stories           # List all
POST   /api/stories           # Save new
PUT    /api/stories/<id>      # Edit
DELETE /api/stories/<id>      # Delete
```

### Files
```
GET  /api/files/videos        # Generated videos
GET  /api/files/backgrounds   # Background clips
POST /api/upload/video        # Upload source
```

## Current Status - MVP COMPLETE ✅

✅ **Working:**
- AI story generation (Groq AI)
- TTS with smart caching (ElevenLabs + free fallback)
- Subtitle generation (2-word viral chunks)
- Video composition (MoviePy 2.x)
- **NEW: Step-by-step UI with edit-before-execute**
- **NEW: Story editing before audio generation**
- **NEW: Voice selection (Mark, Emily, Josh, Bella)**
- **NEW: Subtitle editing before video creation**
- **NEW: Video length control (15-180s)**
- **NEW: Random background cutting for varied footage**
- Story library backend
- Web UI (Dashboard, Generator, Settings)

🚧 **TODO (Future):**
- Story Library UI page
- Background music layer
- Auto-upload to TikTok/YouTube
- Batch generation (10 videos at once)
- Analytics dashboard

## Focus Areas

### 1. Content Generation
- Fast AI story generation (Groq)
- High-quality voice (ElevenLabs)
- Viral subtitle formatting
- Optimized rendering

### 2. Customer Experience
- Simple web interface
- Real-time progress
- Video preview
- Easy story editing
- Gallery management

## Performance
- **Video generation**: ~20 seconds
- **With cache**: ~10 seconds
- **Cost**: 90% cheaper with caching

## Development Priorities
1. **Speed**: Fast generation pipeline
2. **Quality**: Premium voice + viral formatting
3. **UX**: Simple, beautiful web interface
4. **Cost**: Smart caching to save API credits

## Next Steps
1. Build Story Library UI
2. Add Video Upload UI
3. Implement video trimming
4. Add batch generation
