"""Download viral fonts and assets for video creation."""
import os
import requests
from pathlib import Path
import zipfile
import io

# Asset directories
FONTS_DIR = Path("assets/fonts")
SOUNDS_DIR = Path("assets/sounds")

FONTS_DIR.mkdir(parents=True, exist_ok=True)
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, save_path: Path) -> bool:
    """Download file from URL."""
    try:
        print(f"[>] Downloading {save_path.name}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] Downloaded {save_path.name}")
        return True
    except Exception as e:
        print(f"[X] Failed to download {save_path.name}: {e}")
        return False


def download_google_font(font_name: str, weight: str = "700") -> bool:
    """Download font from Google Fonts API."""
    try:
        # Google Fonts API
        api_url = f"https://fonts.google.com/download?family={font_name.replace(' ', '+')}"

        print(f"⬇️  Downloading {font_name}...")
        response = requests.get(api_url, timeout=30)

        if response.status_code == 200:
            # Extract zip
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # Find TTF files
                for file_name in zip_ref.namelist():
                    if file_name.endswith('.ttf'):
                        # Extract to fonts directory
                        zip_ref.extract(file_name, FONTS_DIR)
                        extracted_path = FONTS_DIR / file_name
                        # Rename to simpler name
                        simple_name = f"{font_name.replace(' ', '')}-Bold.ttf"
                        final_path = FONTS_DIR / simple_name
                        if extracted_path.exists():
                            os.rename(extracted_path, final_path)
                        print(f"✅ Installed {simple_name}")
                        return True
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def download_viral_fonts():
    """Download most viral TikTok/Reels fonts."""
    print("=" * 60)
    print("DOWNLOADING VIRAL FONTS")
    print("=" * 60)
    print()

    # Direct download links for popular fonts
    fonts = {
        # Bebas Neue - SUPER viral on TikTok
        "BebasNeue-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",

        # Anton - Bold and impactful
        "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",

        # Montserrat Bold - Clean and modern
        "Montserrat-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf",
        "Montserrat-Black.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Black.ttf",

        # Oswald - Condensed and punchy
        "Oswald-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Bold.ttf",

        # Roboto - Universal favorite
        "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf",
        "Roboto-Black.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Black.ttf",

        # Poppins - Trendy and readable
        "Poppins-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
        "Poppins-Black.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Black.ttf",

        # Inter - Modern and clean
        "Inter-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-Bold.ttf",
    }

    downloaded = 0
    for font_file, url in fonts.items():
        save_path = FONTS_DIR / font_file
        if save_path.exists():
            print(f"⏭️  {font_file} already exists")
            downloaded += 1
        else:
            if download_file(url, save_path):
                downloaded += 1

    print()
    print(f"✅ {downloaded}/{len(fonts)} fonts ready!")
    print(f"📁 Saved to: {FONTS_DIR}")
    print()


def create_viral_font_config():
    """Create config for viral font rotation."""
    config = """# Viral Font Configuration

# Most viral fonts for TikTok/Reels (in order of virality)

VIRAL_FONTS = [
    "BebasNeue-Regular.ttf",      # #1 Most viral - condensed, bold
    "Anton-Regular.ttf",           # #2 Super impactful
    "Montserrat-Black.ttf",        # #3 Clean and modern
    "Poppins-Black.ttf",           # #4 Trendy, readable
    "Oswald-Bold.ttf",             # #5 Condensed, punchy
    "Roboto-Black.ttf",            # #6 Universal favorite
    "Inter-Bold.ttf",              # #7 Modern alternative
]

# Font styles by genre
GENRE_FONTS = {
    "comedy": ["BebasNeue-Regular.ttf", "Anton-Regular.ttf"],
    "terror": ["Anton-Regular.ttf", "Oswald-Bold.ttf"],
    "aita": ["Montserrat-Black.ttf", "Poppins-Black.ttf"],
    "genz_chaos": ["BebasNeue-Regular.ttf", "Poppins-Black.ttf"],
    "relationship_drama": ["Poppins-Black.ttf", "Montserrat-Black.ttf"],
}
"""

    config_path = FONTS_DIR / "FONT_CONFIG.txt"
    with open(config_path, 'w') as f:
        f.write(config)

    print(f"✅ Font config created: {config_path}")


def show_font_preview():
    """Show which fonts are installed."""
    print()
    print("=" * 60)
    print("📚 INSTALLED FONTS")
    print("=" * 60)

    fonts = list(FONTS_DIR.glob("*.ttf"))
    if fonts:
        for i, font in enumerate(fonts, 1):
            print(f"{i}. {font.name}")
    else:
        print("No fonts installed yet!")

    print()


def main():
    """Download all viral assets."""
    print()
    print("=" * 60)
    print("🚀 VIRAL ASSETS DOWNLOADER")
    print("=" * 60)
    print()

    # Download fonts
    download_viral_fonts()

    # Create config
    create_viral_font_config()

    # Show preview
    show_font_preview()

    print("=" * 60)
    print("✅ ALL ASSETS DOWNLOADED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Fonts saved to: assets/fonts/")
    print("2. Run video creation with new fonts!")
    print("3. The most viral font (Bebas Neue) will be used by default")
    print()


if __name__ == "__main__":
    main()
