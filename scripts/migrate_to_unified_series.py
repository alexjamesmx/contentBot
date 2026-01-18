"""Migrate existing single stories to unified series format."""
import json
from pathlib import Path
from datetime import datetime
import uuid
import sys

PROJECT_ROOT = Path(__file__).parent.parent
OLD_STORIES_DIR = PROJECT_ROOT / "output" / "stories"
NEW_SERIES_DIR = PROJECT_ROOT / "cache" / "story_series"


def migrate_single_story_to_series(story_path: Path):
    """Convert old single story JSON to series format."""
    with open(story_path, 'r', encoding='utf-8') as f:
        old_story = json.load(f)

    series_id = str(uuid.uuid4())

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    genre = old_story.get('genre', 'comedy')
    genre_label = genre.replace('_', ' ').title()

    new_series = {
        "series_id": series_id,
        "title": old_story.get('title', f"{genre_label}-{timestamp}"),
        "genre": genre,
        "total_parts": 1,
        "current_part": 1,
        "theme": old_story.get('title', 'Migrated story'),
        "base_prompt": None,
        "parts": [{
            "part": 1,
            "story_text": old_story.get('story', ''),
            "duration": old_story.get('estimated_duration', 60),
            "word_count": old_story.get('word_count', 0),
            "timestamp": old_story.get('created_at', datetime.now().isoformat()),
            "audio_path": None,
            "video_path": None,
            "metadata": {}
        }],
        "context": {
            "characters": [],
            "plot_points": [],
            "tone": "migrated",
            "location": ""
        },
        "created_at": old_story.get('created_at', datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
        "auto_title": True
    }

    output_path = NEW_SERIES_DIR / f"{series_id}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_series, f, indent=2, ensure_ascii=False)

    return series_id


def main():
    print("=" * 60)
    print("ContentBot: Unified Series Migration Tool")
    print("=" * 60)
    print()

    if not OLD_STORIES_DIR.exists():
        print(f"✓ No old stories directory found at: {OLD_STORIES_DIR}")
        print("  Nothing to migrate.")
        return

    NEW_SERIES_DIR.mkdir(parents=True, exist_ok=True)

    story_files = list(OLD_STORIES_DIR.glob("*.json"))

    if not story_files:
        print(f"✓ Old stories directory is empty: {OLD_STORIES_DIR}")
        print("  Nothing to migrate.")
        return

    print(f"Found {len(story_files)} stories to migrate")
    print(f"Source: {OLD_STORIES_DIR}")
    print(f"Destination: {NEW_SERIES_DIR}")
    print()

    response = input("Proceed with migration? (y/n): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return

    print()
    print("Migrating stories...")
    print("-" * 60)

    migrated = 0
    failed = []

    for story_file in story_files:
        try:
            series_id = migrate_single_story_to_series(story_file)
            print(f"✓ {story_file.name} → {series_id}")
            migrated += 1
        except Exception as e:
            print(f"✗ {story_file.name}: {e}")
            failed.append(story_file.name)

    print("-" * 60)
    print()
    print(f"Migration complete: {migrated} stories converted to series")

    if failed:
        print(f"Failed: {len(failed)} stories")
        for name in failed:
            print(f"  - {name}")
    print()
    print("Next steps:")
    print(f"  1. Verify migrated data in: {NEW_SERIES_DIR}")
    print(f"  2. Backup old stories: {OLD_STORIES_DIR}")
    print(f"  3. (Optional) Delete old directory when ready")


if __name__ == "__main__":
    main()
