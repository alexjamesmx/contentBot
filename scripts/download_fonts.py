"""Download viral fonts for subtitle generation."""
import requests
from pathlib import Path

FONTS_DIR = Path("assets/fonts")
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Google Fonts direct download URLs
FONTS = {
    "Montserrat-Black.ttf": "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Black.ttf",
    "Poppins-Black.ttf": "https://github.com/itfoundry/Poppins/raw/master/products/Poppins-Black.ttf",
    "BebasNeue-Regular.ttf": "https://github.com/dharmatype/Bebas-Neue/raw/master/fonts/BebasNeue-Regular.ttf",
    "Anton-Regular.ttf": "https://github.com/googlefonts/AntonFont/raw/main/fonts/ttf/Anton-Regular.ttf",
    "Inter-Bold.ttf": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.ttf",
}

def download_fonts():
    """Download all viral fonts."""
    print("Downloading viral fonts for ContentBot...\n")

    for filename, url in FONTS.items():
        filepath = FONTS_DIR / filename

        if filepath.exists():
            print(f"[OK] {filename} already exists")
            continue

        try:
            print(f"[DOWNLOAD] {filename}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"[OK] {filename} downloaded ({len(response.content)} bytes)")

        except Exception as e:
            print(f"[ERROR] Failed to download {filename}: {e}")

    print("\n[COMPLETE] Font download complete!")
    print(f"[SAVED] Fonts saved to: {FONTS_DIR.absolute()}")

if __name__ == "__main__":
    download_fonts()
