# ContentBot - AI Content Creation Studio

**Automated viral video generation for TikTok/YouTube Shorts**

Generate professional-quality videos in under 60 seconds - from AI story to final MP4.

---

## 🚀 Quick Start

```bash
# Backend
python app.py
# Runs on http://localhost:5000

# Frontend (new terminal)
cd contentbot-ui && npm run dev
# Runs on http://localhost:5173
```

**Environment Setup** - Create `.env`:
```
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

---

## 💡 What This Does

**Input**: Click "Generate Story" → Choose genre
**Output**: Full video (story + voice + subtitles + background)

**Pipeline**:
1. AI generates human-like story (150-220 words)
2. ElevenLabs creates emotional voiceover
3. System generates viral subtitles (4-word chunks, yellow text)
4. MoviePy composes final video (1080x1920, 60-90s)

---

## 🎯 Key Features

**✅ Core Complete**:
- 5 genres (comedy, terror, AITA, gen-z, relationship)
- Premium TTS with emotion + smart caching
- Viral subtitle system (Montserrat Bold, optimal positioning)
- Batch mode (generate 5-20 videos sequentially)
- Analytics dashboard with monetization projections
- **NEW: Functional Subtitle Editor** (customize fonts, colors, timing)

**🚧 In Progress**:
- Background music layer
- Hook A/B testing
- Auto-upload to TikTok/YouTube

---

## 📊 Monetization Ready

**TikTok Creator Rewards 2025**:
- ✅ 60-90s duration (system default: 75s)
- ✅ Original AI content (passes platform checks)
- ✅ Human-like quality (anti-AI detection prompts)

**Revenue Potential**: $450-$1,800/month at 600K-1.2M views

---

## 🛠️ Tech Stack

**Backend**: Python 3.11 | Flask | Groq AI | ElevenLabs | MoviePy 2.x
**Frontend**: React + Vite | TailwindCSS
**AI Models**: llama-3.3-70b (stories) | eleven_turbo_v2_5 (voice)

---

## 📚 Documentation

- **README.md** (this file): Quick start, overview
- **CLAUDE.md**: Development rules, studio vision, AI instructions
- **PROJECT.md**: API reference, troubleshooting

---

## 🎬 Viral Optimizations (2025 Research)

**Stories**:
- Conversational style with filler words ("like", "literally")
- 150-220 words for 60-90s duration
- CAPS for emphasis, "..." for pauses

**Subtitles**:
- 4-word chunks (proven retention sweet spot)
- Montserrat Bold font (60% of viral videos)
- Yellow text + black stroke (max visibility)
- Bottom positioning (420px margin)

**Voice**:
- ElevenLabs turbo_v2_5 model
- Stability: 0.45, Style: 0.3 (natural emotion)
- Auto-added pauses and emphasis

---

## 🚦 Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   cd contentbot-ui && npm install
   ```

2. **Set up API keys** (`.env` file)

3. **Start both servers** (backend + frontend)

4. **Generate first video**:
   - Open http://localhost:5173
   - Click "Generator"
   - Select genre, adjust settings
   - Click through pipeline steps
   - Download final MP4

---

## 💰 Path to $1K+/Month

**Month 1-2**: Generate 60+ videos, post 2x daily
**Month 3**: Build to 10K followers + 100K views/30 days
**Month 4+**: Apply for Creator Rewards, earn $600-$1,800/month

**Success Formula**: Consistency > Perfection

---

## 🎓 For Developers

**Purpose-Driven Development**: Every feature must help creators make better content, enable automation, or improve monetization.

**Before adding features**: Read CLAUDE.md for development philosophy and integration requirements.

**Testing**: Always run `python -m py_compile` after changes. Test full pipeline via UI.

---

**Built for creators who want to scale faceless content production 🚀**

Last updated: January 10, 2026
