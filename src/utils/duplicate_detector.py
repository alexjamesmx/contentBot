"""Duplicate detection to prevent recreating the same videos."""
import json
from pathlib import Path
from typing import Set, Optional
from datetime import datetime

from src.utils.config import OUTPUT_DIR


class DuplicateDetector:
    """Track used Reddit posts to avoid duplicates."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize duplicate detector.

        Args:
            db_path: Path to JSON database file
        """
        if db_path is None:
            db_path = OUTPUT_DIR / "used_posts.json"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing database
        self.used_posts = self._load_database()

    def _load_database(self) -> dict:
        """Load database from file.

        Returns:
            Dictionary of used posts
        """
        if not self.db_path.exists():
            return {"reddit": {}, "custom": []}

        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Failed to load duplicate database: {e}")
            return {"reddit": {}, "custom": []}

    def _save_database(self):
        """Save database to file."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.used_posts, f, indent=2, default=str)
        except Exception as e:
            print(f"[ERROR] Failed to save duplicate database: {e}")

    def is_duplicate(self, reddit_id: str, subreddit: str = None) -> bool:
        """Check if Reddit post has been used.

        Args:
            reddit_id: Reddit post ID
            subreddit: Subreddit name (optional)

        Returns:
            True if duplicate
        """
        return reddit_id in self.used_posts.get("reddit", {})

    def mark_as_used(
        self,
        reddit_id: str,
        subreddit: str,
        title: str,
        video_path: str = None
    ):
        """Mark Reddit post as used.

        Args:
            reddit_id: Reddit post ID
            subreddit: Subreddit name
            title: Post title
            video_path: Path to generated video
        """
        if "reddit" not in self.used_posts:
            self.used_posts["reddit"] = {}

        self.used_posts["reddit"][reddit_id] = {
            "subreddit": subreddit,
            "title": title,
            "video_path": video_path,
            "created_at": datetime.now().isoformat(),
        }

        self._save_database()
        print(f"[DUPLICATE] Marked r/{subreddit}/{reddit_id} as used")

    def get_unused_posts(self, posts: list) -> list:
        """Filter out duplicate posts.

        Args:
            posts: List of post dictionaries with 'id' field

        Returns:
            List of unused posts
        """
        unused = [
            post for post in posts
            if not self.is_duplicate(post.get("id", ""))
        ]

        filtered_count = len(posts) - len(unused)
        if filtered_count > 0:
            print(f"[DUPLICATE] Filtered out {filtered_count} duplicate posts")

        return unused

    def get_stats(self) -> dict:
        """Get usage statistics.

        Returns:
            Statistics dictionary
        """
        reddit_count = len(self.used_posts.get("reddit", {}))

        # Get subreddit breakdown
        subreddit_counts = {}
        for post_id, data in self.used_posts.get("reddit", {}).items():
            sub = data.get("subreddit", "unknown")
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1

        return {
            "total_reddit_posts": reddit_count,
            "by_subreddit": subreddit_counts,
            "database_path": str(self.db_path),
        }

    def clear_database(self):
        """Clear all tracked posts (use with caution)."""
        self.used_posts = {"reddit": {}, "custom": []}
        self._save_database()
        print("[DUPLICATE] Database cleared")


# CLI testing
if __name__ == "__main__":
    print("🔍 ContentBot Duplicate Detector\n")

    detector = DuplicateDetector()

    # Show stats
    stats = detector.get_stats()
    print("=" * 60)
    print("CURRENT STATS")
    print("=" * 60)
    print(f"Total Reddit posts used: {stats['total_reddit_posts']}")
    print(f"Database: {stats['database_path']}")

    if stats['by_subreddit']:
        print("\nBy Subreddit:")
        for sub, count in stats['by_subreddit'].items():
            print(f"  r/{sub}: {count} posts")
    else:
        print("\n(No posts tracked yet)")

    print("\n" + "=" * 60)
    print("TEST: Mark sample post as used")
    print("=" * 60)

    detector.mark_as_used(
        reddit_id="test123",
        subreddit="AmItheAsshole",
        title="AITA for testing duplicate detection?",
        video_path="output/test_video.mp4"
    )

    print(f"\nIs 'test123' duplicate? {detector.is_duplicate('test123')}")
    print(f"Is 'test456' duplicate? {detector.is_duplicate('test456')}")

    # Show updated stats
    stats = detector.get_stats()
    print(f"\nTotal posts now: {stats['total_reddit_posts']}")

    print("\n✅ Duplicate detector test complete!")
