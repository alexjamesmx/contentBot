"""Download popular copyright-free music for TikTok/Reels."""
import os
import requests
from pathlib import Path


MUSIC_DIR = Path("assets/music")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)


# Curated list of popular copyright-free music (YouTube Audio Library & Free Music Archive)
POPULAR_TRACKS = {
    # Upbeat/Comedy
    "happy_upbeat_1": {
        "name": "Happy Upbeat Pop",
        "url": "https://www.chosic.com/wp-content/uploads/2021/05/Creo_-_Sphere.mp3",
        "genre": "comedy",
        "bpm": 128,
        "mood": "energetic"
    },
    "funny_quirky_1": {
        "name": "Funny Quirky Beat",
        "url": "https://www.chosic.com/wp-content/uploads/2021/04/The-Epic-Hero.mp3",
        "genre": "comedy",
        "bpm": 120,
        "mood": "playful"
    },

    # Suspense/Terror
    "dark_ambient_1": {
        "name": "Dark Ambient Horror",
        "url": "https://www.chosic.com/wp-content/uploads/2021/03/The-Epic-Hero-2.mp3",
        "genre": "terror",
        "bpm": 80,
        "mood": "suspenseful"
    },
    "creepy_tension_1": {
        "name": "Creepy Tension Build",
        "url": "https://www.chosic.com/wp-content/uploads/2021/02/Cold-Nights.mp3",
        "genre": "terror",
        "bpm": 90,
        "mood": "eerie"
    },

    # Drama/AITA
    "dramatic_piano_1": {
        "name": "Dramatic Piano",
        "url": "https://www.chosic.com/wp-content/uploads/2020/12/Prelude-No.-1.mp3",
        "genre": "aita",
        "bpm": 72,
        "mood": "emotional"
    },

    # Gen-Z/Chaos
    "hyperpop_1": {
        "name": "Hyperpop Energy",
        "url": "https://www.chosic.com/wp-content/uploads/2021/06/Jaxius_-_Wish_You_Were_Here.mp3",
        "genre": "genz_chaos",
        "bpm": 140,
        "mood": "chaotic"
    },
}


# Alternative: Direct download links (backup)
BACKUP_SOURCES = [
    {
        "name": "YouTube Audio Library",
        "url": "https://www.youtube.com/audiolibrary",
        "note": "Manual download - filter by 'No attribution required'"
    },
    {
        "name": "Pixabay Music",
        "url": "https://pixabay.com/music/search/tiktok/",
        "note": "Free download - search 'tiktok' or 'comedy'"
    },
    {
        "name": "Chosic Free Music",
        "url": "https://www.chosic.com/free-music/for-tiktok/",
        "note": "Free TikTok background music"
    },
    {
        "name": "Free Music Archive",
        "url": "https://freemusicarchive.org/",
        "note": "Large library of CC music"
    }
]


def download_track(track_id: str, track_data: dict) -> bool:
    """Download a single music track.

    Args:
        track_id: Track identifier
        track_data: Track metadata

    Returns:
        True if successful
    """
    try:
        # Create filename
        filename = f"{track_id}.mp3"
        save_path = MUSIC_DIR / filename

        if save_path.exists():
            print(f"[EXISTS] {track_data['name']}")
            return True

        print(f"[DOWNLOADING] {track_data['name']}...")

        # Download
        response = requests.get(track_data['url'], stream=True, timeout=60)
        response.raise_for_status()

        # Save
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[SUCCESS] {track_data['name']} saved to {save_path}")
        return True

    except Exception as e:
        print(f"[FAILED] {track_data['name']}: {e}")
        return False


def download_all_music():
    """Download all curated music tracks."""
    print("=" * 60)
    print("COPYRIGHT-FREE MUSIC DOWNLOADER")
    print("=" * 60)
    print()

    successful = 0
    total = len(POPULAR_TRACKS)

    for track_id, track_data in POPULAR_TRACKS.items():
        if download_track(track_id, track_data):
            successful += 1

    print()
    print("=" * 60)
    print(f"[COMPLETE] {successful}/{total} tracks downloaded")
    print(f"[LOCATION] {MUSIC_DIR}")
    print("=" * 60)
    print()


def create_music_guide():
    """Create guide for downloaded music."""
    guide_path = MUSIC_DIR / "MUSIC_GUIDE.txt"

    with open(guide_path, 'w') as f:
        f.write("COPYRIGHT-FREE MUSIC GUIDE\n")
        f.write("=" * 60 + "\n\n")

        f.write("DOWNLOADED TRACKS:\n\n")
        for track_id, track_data in POPULAR_TRACKS.items():
            f.write(f"{track_id}.mp3\n")
            f.write(f"  Name: {track_data['name']}\n")
            f.write(f"  Genre: {track_data['genre']}\n")
            f.write(f"  BPM: {track_data['bpm']}\n")
            f.write(f"  Mood: {track_data['mood']}\n\n")

        f.write("\n" + "=" * 60 + "\n\n")
        f.write("USAGE BY GENRE:\n\n")

        genres = {}
        for track_id, track_data in POPULAR_TRACKS.items():
            genre = track_data['genre']
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(f"{track_id}.mp3 - {track_data['name']}")

        for genre, tracks in genres.items():
            f.write(f"{genre.upper()}:\n")
            for track in tracks:
                f.write(f"  - {track}\n")
            f.write("\n")

        f.write("=" * 60 + "\n\n")
        f.write("MANUAL DOWNLOAD SOURCES:\n\n")

        for source in BACKUP_SOURCES:
            f.write(f"{source['name']}\n")
            f.write(f"  URL: {source['url']}\n")
            f.write(f"  Note: {source['note']}\n\n")

        f.write("\n" + "=" * 60 + "\n\n")
        f.write("HOW TO ADD MUSIC TO VIDEOS:\n\n")
        f.write("1. Use video editing software (CapCut, DaVinci Resolve)\n")
        f.write("2. Import video + music file\n")
        f.write("3. Set music volume to -20dB (background level)\n")
        f.write("4. Ensure voiceover is louder than music\n")
        f.write("5. Export and upload\n\n")

        f.write("COPYRIGHT:\n")
        f.write("All tracks are copyright-free for commercial use.\n")
        f.write("Attribution may be required - check source links.\n")

    print(f"[CREATED] Music guide: {guide_path}")


def show_manual_sources():
    """Display manual download sources."""
    print()
    print("=" * 60)
    print("MANUAL DOWNLOAD SOURCES (BEST QUALITY)")
    print("=" * 60)
    print()
    print("[INFO] For trending/viral music, download manually:")
    print()

    for source in BACKUP_SOURCES:
        print(f"{source['name']}")
        print(f"  URL: {source['url']}")
        print(f"  {source['note']}")
        print()

    print("=" * 60)
    print()
    print("[TIP] Best practices:")
    print("  1. Search for 'tiktok' or your genre")
    print("  2. Filter by 'No attribution required' or 'CC0'")
    print("  3. Download MP3 format")
    print("  4. Save to assets/music/")
    print()


def main():
    """Main entry point."""
    print()
    print("COPYRIGHT-FREE MUSIC SETUP")
    print()
    print("This will download curated background music for your videos.")
    print()

    choice = input("Download curated tracks? [Y/n]: ").strip().lower()

    if choice in ['', 'y', 'yes']:
        download_all_music()
        create_music_guide()

    print()
    show_manual_sources()

    print()
    print("[DONE] Music setup complete!")
    print()
    print("Next steps:")
    print("1. Check assets/music/ for downloaded tracks")
    print("2. Read MUSIC_GUIDE.txt for usage info")
    print("3. Download trending music manually from sources above")
    print()


if __name__ == "__main__":
    main()
