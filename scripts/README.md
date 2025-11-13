# Setup Scripts

One-time setup utilities for ContentBot.

## Available Scripts

### `download_fonts.py`
Downloads viral fonts for subtitle generation.

```bash
python scripts/download_fonts.py
```

Downloads to: `assets/fonts/`

---

### `download_assets.py`
Downloads sample background videos and fonts.

```bash
python scripts/download_assets.py
```

Downloads to: `assets/backgrounds/` and `assets/fonts/`

---

### `download_music.py`
Downloads copyright-free background music.

```bash
python scripts/download_music.py
```

Downloads to: `assets/music/`

**Note:** Background music is not yet integrated into the video pipeline.

---

## When to Use

Run these scripts **once** during initial setup if you need:
- Fonts (if missing)
- Sample backgrounds (if you don't have your own)
- Music (for future use)

Most users won't need these - just add your own backgrounds manually to `assets/backgrounds/`.
