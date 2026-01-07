# ContentBot - AI Viral Video Generator

Turn stories into viral short-form videos with AI voiceovers and subtitles.

## Quick Start

### Prerequisites
```bash
python --version
node --version
```

### Setup

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure API keys**
Edit `.env`:
```
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key  # Premium
```

3. **Add background videos**
Place MP4 videos in `assets/backgrounds/`

### Start Application

**Terminal 1 - Backend:**
```bash
python app.py
```
Runs at: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd contentbot-ui
npm install
npm run dev
```
Runs at: http://localhost:5173

### CLI Mode
```bash
python create_video.py comedy
python create_video.py --custom "Your story here"
```

## Features
- ✅ AI story generation (Groq)
- ✅ Premium TTS with caching (ElevenLabs)
- ✅ Viral subtitle formatting
- ✅ 9:16 vertical video output
- ✅ Story library (save & edit)
- ✅ Web interface

## Documentation
- **Full details**: See [PROJECT.md](PROJECT.md)
- **API keys**: [Groq](https://console.groq.com/) | [ElevenLabs](https://elevenlabs.io/)

## Tech Stack
Python • Flask • React • MoviePy • ElevenLabs • Groq
