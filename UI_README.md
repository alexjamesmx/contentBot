# ContentBot Pro UI

Modern React-based web interface for ContentBot - The automated viral Shorts generator.

## 🎨 Features

- **Modern Dark UI**: Professional, easy-on-the-eyes interface
- **Real-time Video Generation**: Step-by-step visual feedback
- **Template Editor**: Customize story prompts and hooks for each genre
- **Media Manager**: Drag-and-drop background video uploads
- **Subtitle Configurator**: Visual subtitle customization with live preview
- **Analytics Dashboard**: Track your video production
- **Settings Panel**: Easy API key management

## 🚀 Quick Start

### 1. Start the Backend (Flask API)

```bash
# From project root
python app.py
```

Backend will run at: `http://localhost:5000`

### 2. Start the Frontend (React UI)

```bash
# In a new terminal
cd contentbot-ui
npm run dev
```

Frontend will run at: `http://localhost:5173`

### 3. Open Your Browser

Navigate to: `http://localhost:5173`

---

## 📁 UI Structure

```
contentbot-ui/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx         # Overview & recent videos
│   │   ├── Generator.jsx         # Main video generation interface
│   │   ├── Templates.jsx         # Story template editor
│   │   ├── MediaManager.jsx      # Background video management
│   │   ├── SubtitleConfig.jsx    # Subtitle customization
│   │   ├── SettingsPage.jsx      # API keys & configuration
│   │   └── Analytics.jsx         # Production analytics
│   ├── App.jsx                   # Main app with routing
│   └── index.css                 # TailwindCSS styles
├── tailwind.config.js
├── vite.config.js
└── package.json
```

---

## 🎯 Usage Guide

### Dashboard
- View recent videos
- Quick stats overview
- Jump to generator

### Generator (Main Feature)
1. **Select Genre**: comedy, terror, AITA, etc.
2. **Choose Background**: Random or specific video
3. **Configure Settings**:
   - Words per subtitle (1-4, recommend 2)
   - Use ElevenLabs TTS (premium quality)
   - Custom story (optional)
4. **Click "Generate Video"**
5. **Watch Progress**: Story → Audio → Subtitles → Video
6. **Download Result**: Video saved to `output/pending_review/`

### Templates
- Edit story prompts for each genre
- Customize hook patterns
- Modify system prompts for AI generation
- Save changes (persists to `story_templates.py`)

### Media Manager
- Upload background videos (drag & drop)
- View all backgrounds with file sizes
- Delete unused backgrounds
- Supports MP4, MOV files

### Subtitle Config
- **Live Preview**: See changes in real-time
- **Font Size**: 40-120px (default: 80px)
- **Colors**: Font & stroke colors (default: yellow text, black stroke)
- **Stroke Width**: 0-8px outline
- **Words Per Chunk**: 1-5 words (2-3 = most viral)
- **Position**: Top, center, or bottom
- **Font Family**: Impact, Arial Bold, Bebas Neue, etc.

### Settings
- **API Keys**:
  - Groq API (required) - AI story generation
  - ElevenLabs API (optional) - Premium TTS
  - Reddit API (optional) - Story scraping
- **Status Indicators**: Green = configured, Red = missing
- **Video Config**: Read-only (optimized for Shorts)
- **Asset Status**: Count of backgrounds and fonts

### Analytics
- Total videos generated
- Weekly production stats
- Genre distribution
- Recent activity timeline
- File size analytics

---

## 🔧 Customization (White Label)

### Change Branding

Edit `contentbot-ui/src/App.jsx`:

```jsx
// Change app name & logo
<h1 className="text-xl font-bold">YourBrandName</h1>
<p className="text-xs text-gray-400">Pro Edition</p>
```

### Change Colors

Edit `contentbot-ui/tailwind.config.js`:

```js
colors: {
  primary: {
    // Change to your brand color
    500: '#YOUR_COLOR',
    600: '#YOUR_COLOR_DARKER',
    ...
  }
}
```

### Change Footer

Edit `contentbot-ui/src/App.jsx`:

```jsx
<div className="p-4 border-t border-dark-border text-xs text-gray-500">
  <p>Version 1.0.0</p>
  <p className="mt-1">© 2025 YourCompany</p>
</div>
```

---

## 🛠️ Development

### Install Dependencies

```bash
cd contentbot-ui
npm install
```

### Run Development Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

Production files will be in `contentbot-ui/dist/`

### Preview Production Build

```bash
npm run preview
```

---

## 📦 Tech Stack

**Frontend:**
- React 18
- Vite (build tool)
- TailwindCSS (styling)
- React Router (navigation)
- Axios (API calls)
- Lucide React (icons)

**Backend:**
- Flask (Python web framework)
- Flask-CORS (API access)
- Existing ContentBot modules

---

## 🔌 API Endpoints

The UI connects to these Flask backend endpoints:

### Config
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration

### Templates
- `GET /api/templates` - Get all story templates
- `GET /api/templates/<genre>` - Get specific template
- `PUT /api/templates/<genre>` - Update template

### Generation
- `POST /api/generate/story` - Generate story
- `POST /api/generate/audio` - Generate TTS audio
- `POST /api/generate/subtitles` - Generate subtitles
- `POST /api/generate/video` - Create final video

### Files
- `GET /api/files/backgrounds` - List background videos
- `POST /api/files/backgrounds` - Upload background
- `DELETE /api/files/backgrounds/<filename>` - Delete background
- `GET /api/files/videos` - List generated videos
- `GET /api/files/video/<filename>` - Serve video file

### Health
- `GET /api/health` - Health check

---

## 🚨 Troubleshooting

### "Network Error" in UI
- Make sure Flask backend is running (`python app.py`)
- Check if backend is on `http://localhost:5000`
- CORS should be enabled (flask-cors installed)

### UI Not Loading
- Check if React dev server is running (`npm run dev`)
- Clear browser cache
- Check console for errors (F12)

### API Keys Not Saving
- Make sure `.env` file exists in project root
- Check file permissions
- Restart Flask backend after changing `.env`

### Videos Not Generating
- Check Flask terminal for error logs
- Verify API keys are configured
- Ensure background videos exist in `assets/backgrounds/`

---

## 📈 Future Enhancements

### Planned Features:
- [ ] Batch video generation
- [ ] Scheduling & auto-posting to platforms
- [ ] User authentication & multi-user support
- [ ] Payment integration (Stripe)
- [ ] License key system
- [ ] Video preview player in browser
- [ ] Direct platform upload (TikTok/Instagram/YouTube)
- [ ] Template marketplace
- [ ] AI voice cloning
- [ ] Advanced analytics with platform metrics

---

## 💰 Selling This Software

### White Label Checklist:
1. ✅ Change branding (app name, logo, colors)
2. ✅ Replace API keys section with your own affiliate links
3. ✅ Add your support/documentation links
4. ✅ Build production version (`npm run build`)
5. ✅ Package with Python backend
6. ✅ Add license key validation (optional)
7. ✅ Create installation wizard/script
8. ✅ Write user documentation

### Pricing Suggestions:
- **One-time license**: $99-299
- **Monthly subscription**: $29-79/month
- **Lifetime deal**: $499-999
- **Agency license**: $1999+

### Where to Sell:
- Gumroad
- LemonSqueezy
- AppSumo
- Your own website
- Discord communities
- Reddit (r/sidehustle, r/passive_income)

---

## 📧 Support

For issues or questions:
1. Check Flask terminal logs
2. Check browser console (F12)
3. Review `SESSION_CONTEXT.md` for architecture details
4. Check GitHub issues (if open source)

---

**Built with ❤️ by ContentBot Team**

Ready to automate your way to viral success! 🚀
