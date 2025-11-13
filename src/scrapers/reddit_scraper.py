"""Reddit content scraper for viral story automation."""
import praw
from typing import List, Dict, Optional
from datetime import datetime
import re

from src.utils.config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
)


class RedditScraper:
    """Scrape and filter Reddit posts for video generation."""

    # Target subreddits optimized for viral content
    DEFAULT_SUBREDDITS = [
        "AmItheAsshole",
        "relationship_advice",
        "entitledparents",
        "maliciouscompliance",
        "pettyrevenge",
        "tifu",  # Today I F'd Up
        "confession",
    ]

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        user_agent: str = None
    ):
        """Initialize Reddit scraper.

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
        """
        self.client_id = client_id or REDDIT_CLIENT_ID
        self.client_secret = client_secret or REDDIT_CLIENT_SECRET
        self.user_agent = user_agent or REDDIT_USER_AGENT

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Reddit API credentials not found. "
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env\n"
                "Get credentials at: https://www.reddit.com/prefs/apps"
            )

        # Initialize PRAW (Reddit API wrapper)
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )

    def fetch_posts(
        self,
        subreddit: str = "AmItheAsshole",
        limit: int = 50,
        time_filter: str = "day",  # day, week, month, year, all
        sort_by: str = "hot",  # hot, new, top, rising
        min_upvotes: int = 100,
        min_comments: int = 10,
        include_nsfw: bool = False,
        min_words: int = 75,
        max_words: int = 300,
    ) -> List[Dict]:
        """Fetch and filter Reddit posts.

        Args:
            subreddit: Subreddit name (without r/)
            limit: Max posts to fetch
            time_filter: Time filter for 'top' sort
            sort_by: Sorting method
            min_upvotes: Minimum upvotes
            min_comments: Minimum comments
            include_nsfw: Include NSFW posts
            min_words: Minimum word count
            max_words: Maximum word count

        Returns:
            List of filtered post dictionaries
        """
        # Clean subreddit name
        subreddit = subreddit.replace("r/", "").strip()

        print(f"[REDDIT] Fetching posts from r/{subreddit}...")

        # Get subreddit
        sub = self.reddit.subreddit(subreddit)

        # Fetch posts based on sort method
        if sort_by == "hot":
            posts = sub.hot(limit=limit)
        elif sort_by == "new":
            posts = sub.new(limit=limit)
        elif sort_by == "top":
            posts = sub.top(time_filter=time_filter, limit=limit)
        elif sort_by == "rising":
            posts = sub.rising(limit=limit)
        else:
            posts = sub.hot(limit=limit)

        filtered_posts = []

        for post in posts:
            # Skip if NSFW and not allowed
            if post.over_18 and not include_nsfw:
                continue

            # Skip if stickied (pinned posts)
            if post.stickied:
                continue

            # Get post text
            text = self._extract_text(post)
            if not text:
                continue

            # Count words
            word_count = len(text.split())

            # Filter by word count
            if word_count < min_words or word_count > max_words:
                continue

            # Filter by engagement
            if post.score < min_upvotes or post.num_comments < min_comments:
                continue

            # Calculate viral score
            viral_score = self._calculate_viral_score(post, word_count)

            # Build post data
            post_data = {
                "id": post.id,
                "title": post.title,
                "text": text,
                "subreddit": subreddit,
                "author": str(post.author) if post.author else "[deleted]",
                "url": f"https://reddit.com{post.permalink}",
                "upvotes": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "nsfw": post.over_18,
                "created_utc": datetime.fromtimestamp(post.created_utc),
                "word_count": word_count,
                "viral_score": viral_score,
            }

            filtered_posts.append(post_data)

        # Sort by viral score
        filtered_posts.sort(key=lambda x: x["viral_score"], reverse=True)

        print(f"[REDDIT] Found {len(filtered_posts)} quality posts from {limit} fetched")

        return filtered_posts

    def fetch_from_multiple_subreddits(
        self,
        subreddits: List[str] = None,
        posts_per_sub: int = 20,
        **kwargs
    ) -> List[Dict]:
        """Fetch posts from multiple subreddits.

        Args:
            subreddits: List of subreddit names
            posts_per_sub: Posts to fetch per subreddit
            **kwargs: Additional filter arguments

        Returns:
            Combined list of posts sorted by viral score
        """
        if subreddits is None:
            subreddits = self.DEFAULT_SUBREDDITS

        all_posts = []

        for sub in subreddits:
            try:
                posts = self.fetch_posts(
                    subreddit=sub,
                    limit=posts_per_sub,
                    **kwargs
                )
                all_posts.extend(posts)
            except Exception as e:
                print(f"[WARNING] Failed to fetch from r/{sub}: {e}")
                continue

        # Sort all posts by viral score
        all_posts.sort(key=lambda x: x["viral_score"], reverse=True)

        return all_posts

    def get_best_post(
        self,
        subreddit: str = "AmItheAsshole",
        **kwargs
    ) -> Optional[Dict]:
        """Get single best post from subreddit.

        Args:
            subreddit: Subreddit name
            **kwargs: Filter arguments

        Returns:
            Best post or None
        """
        posts = self.fetch_posts(subreddit=subreddit, **kwargs)
        return posts[0] if posts else None

    def _extract_text(self, post) -> str:
        """Extract and clean text from Reddit post.

        Args:
            post: PRAW submission object

        Returns:
            Cleaned text
        """
        # Get post text (selftext)
        text = post.selftext.strip()

        # If no text, try title only (for text posts)
        if not text:
            text = post.title

        # Remove [removed] and [deleted]
        if text.lower() in ["[removed]", "[deleted]"]:
            return ""

        # Clean text
        text = self._clean_text(text)

        return text

    def _clean_text(self, text: str) -> str:
        """Clean and format text for TTS.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)

        # Remove Reddit markdown links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove special characters that break TTS
        text = re.sub(r'[\*_~`]', '', text)

        # Strip whitespace
        text = text.strip()

        return text

    def _calculate_viral_score(self, post, word_count: int) -> float:
        """Calculate viral potential score.

        Args:
            post: PRAW submission object
            word_count: Word count

        Returns:
            Viral score (higher = more viral potential)
        """
        # Base engagement score
        engagement_score = (post.score * 0.7) + (post.num_comments * 0.3)

        # Upvote ratio bonus (controversial posts are viral)
        ratio_bonus = 1.0
        if post.upvote_ratio < 0.7:  # Controversial
            ratio_bonus = 1.5

        # Word count bonus (optimal range 75-150)
        word_bonus = 1.0
        if 75 <= word_count <= 150:
            word_bonus = 1.3
        elif 150 < word_count <= 200:
            word_bonus = 1.1

        # Recency bonus (newer posts)
        age_hours = (datetime.now().timestamp() - post.created_utc) / 3600
        recency_bonus = 1.0
        if age_hours < 24:
            recency_bonus = 1.2

        # Calculate final score
        viral_score = engagement_score * ratio_bonus * word_bonus * recency_bonus

        return viral_score

    @staticmethod
    def format_for_video(post_data: Dict) -> Dict:
        """Format Reddit post for video generation.

        Args:
            post_data: Raw post data

        Returns:
            Formatted story dict
        """
        # Combine title and text
        full_text = f"{post_data['title']}\n\n{post_data['text']}"

        # Estimate duration (2.5 words per second)
        estimated_duration = post_data['word_count'] / 2.5

        return {
            "story": full_text,
            "genre": "aita",  # Default, can be customized
            "word_count": post_data['word_count'],
            "estimated_duration": estimated_duration,
            "source": "reddit",
            "source_url": post_data['url'],
            "subreddit": post_data['subreddit'],
            "reddit_id": post_data['id'],
        }


# CLI testing
if __name__ == "__main__":
    import sys

    print("🔍 ContentBot Reddit Scraper\n")

    try:
        scraper = RedditScraper()
        print("✅ Connected to Reddit API\n")

        # Test single subreddit
        print("=" * 60)
        print("TEST 1: Fetch from r/AmItheAsshole")
        print("=" * 60)

        posts = scraper.fetch_posts(
            subreddit="AmItheAsshole",
            limit=25,
            min_upvotes=500,
            min_words=75,
            max_words=200,
        )

        print(f"\n📊 Top 5 posts by viral score:\n")
        for i, post in enumerate(posts[:5], 1):
            print(f"{i}. [{post['upvotes']} ⬆️] {post['title'][:60]}...")
            print(f"   Words: {post['word_count']} | Comments: {post['num_comments']}")
            print(f"   Viral Score: {post['viral_score']:.0f}")
            print(f"   URL: {post['url']}\n")

        if posts:
            print("=" * 60)
            print("TEST 2: Format best post for video")
            print("=" * 60)
            best_post = posts[0]
            formatted = RedditScraper.format_for_video(best_post)
            print(f"\n📖 Story Preview:")
            print(f"{formatted['story'][:300]}...\n")
            print(f"⏱️  Estimated Duration: {formatted['estimated_duration']:.1f}s")
            print(f"📊 Word Count: {formatted['word_count']}")

        print("\n✅ Reddit scraper test complete!")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nTo fix this:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'Create App' or 'Create Another App'")
        print("3. Select 'script' type")
        print("4. Copy client_id and secret")
        print("5. Add to .env file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
