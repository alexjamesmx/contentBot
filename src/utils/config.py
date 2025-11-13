"""Configuration management for ContentBot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
FONTS_DIR = ASSETS_DIR / "fonts"
OUTPUT_DIR = PROJECT_ROOT / "output"
PENDING_DIR = OUTPUT_DIR / "pending_review"
PUBLISHED_DIR = OUTPUT_DIR / "published"

# Ensure directories exist
for directory in [BACKGROUNDS_DIR, FONTS_DIR, PENDING_DIR, PUBLISHED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Reddit API
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ContentBot/1.0")

# Video Settings
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", 1080))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", 1920))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", 30))
VIDEO_MIN_DURATION = int(os.getenv("VIDEO_MIN_DURATION", 45))
VIDEO_MAX_DURATION = int(os.getenv("VIDEO_MAX_DURATION", 90))

# Story Generation Settings
STORY_TEMPERATURE = float(os.getenv("STORY_TEMPERATURE", 0.9))
STORY_MAX_TOKENS = int(os.getenv("STORY_MAX_TOKENS", 500))
DEFAULT_GENRE = os.getenv("DEFAULT_GENRE", "comedy")

# File Caching (Save tokens & time)
REUSE_EXISTING_FILES = os.getenv("REUSE_EXISTING_FILES", "true").lower() == "true"

# Validation
def validate_config():
    """Validate critical configuration."""
    errors = []

    if not GROQ_API_KEY and not OPENAI_API_KEY:
        errors.append("Missing AI API key: Set GROQ_API_KEY or OPENAI_API_KEY in .env")

    if not BACKGROUNDS_DIR.exists():
        errors.append(f"Backgrounds directory not found: {BACKGROUNDS_DIR}")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

    return True

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ Configuration valid!")
    except ValueError as e:
        print(f"❌ {e}")
