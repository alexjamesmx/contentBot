"""Video metadata and publishing info generator."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class VideoMetadata:
    """Generate and manage video metadata for publishing."""

    # Viral hashtags based on research
    REDDIT_STORY_HASHTAGS = [
        "#redditstories", "#reddit", "#aita", "#storytime", "#redditreadings",
        "#askreddit", "#amitheasshole", "#redditstory", "#storytimewithme",
        "#redditconfessions", "#truestory", "#redditdrama", "#viralstories"
    ]

    GENERAL_VIRAL_HASHTAGS = [
        "#fyp", "#foryou", "#foryoupage", "#viral", "#trending", "#fy"
    ]

    GENRE_HASHTAGS = {
        "comedy": ["#funny", "#comedy", "#funnyvideos", "#lol", "#humor"],
        "terror": ["#scary", "#creepy", "#horror", "#scarystories", "#creepypasta"],
        "aita": ["#aita", "#relationship", "#drama", "#advice", "#relationshipadvice"],
        "genz_chaos": ["#genz", "#unhinged", "#chaotic", "#relatable", "#memes"],
        "relationship_drama": ["#relationship", "#dating", "#love", "#breakup", "#toxic"]
    }

    def __init__(self):
        """Initialize metadata generator."""
        pass

    def generate_hashtags(self, genre: str, include_general: bool = True) -> List[str]:
        """Generate optimized hashtag list for the video.

        Args:
            genre: Video genre
            include_general: Include general viral hashtags

        Returns:
            List of hashtags (5-10 optimized for virality)
        """
        hashtags = []

        # Add genre-specific hashtags (3-5)
        genre_tags = self.GENRE_HASHTAGS.get(genre, self.GENRE_HASHTAGS["comedy"])
        hashtags.extend(genre_tags[:3])

        # Add general viral hashtags (2-3)
        if include_general:
            hashtags.extend(self.GENERAL_VIRAL_HASHTAGS[:3])

        # Add Reddit story tags if applicable (2-3)
        if genre in ["aita", "relationship_drama"]:
            hashtags.extend(self.REDDIT_STORY_HASHTAGS[:3])

        # Limit to 10 hashtags max (best practice)
        return hashtags[:10]

    def generate_caption(self, story: str, genre: str, max_length: int = 150) -> str:
        """Generate viral caption for the video.

        Args:
            story: Story text
            genre: Video genre
            max_length: Max caption length

        Returns:
            Optimized caption
        """
        # Extract hook (first sentence)
        hook = story.split('.')[0].split('!')[0].split('?')[0]

        # Truncate if too long
        if len(hook) > max_length:
            hook = hook[:max_length-3] + "..."

        # Add genre-specific call to action
        cta = {
            "comedy": "💀 Tag someone who needs to see this",
            "terror": "😱 Would you survive this?",
            "aita": "🤔 Drop your verdict in comments",
            "genz_chaos": "💀 The chaos is unmatched",
            "relationship_drama": "🚩 Red flag or nah?"
        }

        caption = f"{hook}\n\n{cta.get(genre, '💀 What do you think?')}"
        return caption

    def create_metadata_json(
        self,
        video_path: str,
        story: dict,
        audio_path: str,
        subtitle_path: str,
        genre: str
    ) -> Dict:
        """Create complete metadata JSON for the video.

        Args:
            video_path: Path to video file
            story: Story dict from generator
            audio_path: Path to audio file
            subtitle_path: Path to subtitle file
            genre: Video genre

        Returns:
            Complete metadata dict
        """
        hashtags = self.generate_hashtags(genre)
        caption = self.generate_caption(story['story'], genre)

        metadata = {
            "video": {
                "path": video_path,
                "duration": story.get('estimated_duration', 0),
                "format": "vertical_9:16",
                "resolution": "1080x1920",
                "created_at": datetime.now().isoformat()
            },
            "content": {
                "genre": genre,
                "story": story['story'],
                "word_count": story.get('word_count', len(story['story'].split())),
                "hook": story.get('hook', ''),
                "template": story.get('template_used', '')
            },
            "assets": {
                "audio": audio_path,
                "subtitles": subtitle_path
            },
            "publishing": {
                "platforms": ["tiktok", "instagram", "youtube_shorts"],
                "caption": caption,
                "hashtags": hashtags,
                "hashtags_string": " ".join(hashtags),
                "best_post_times": ["7-9pm EST", "12-2pm EST", "6-8am EST"],
                "suggested_music": self._get_music_suggestions(genre)
            },
            "optimization": {
                "font_used": "BebasNeue" if genre in ["comedy", "genz_chaos"] else "Anton",
                "text_color": "yellow",
                "subtitle_chunks": "2_words",
                "viral_score": self._calculate_viral_score(story)
            }
        }

        return metadata


    def _get_music_suggestions(self, genre: str) -> List[str]:
        """Get trending music suggestions by genre.

        Args:
            genre: Video genre

        Returns:
            List of music styles/trends
        """
        music_map = {
            "comedy": ["Upbeat pop", "Meme sounds", "Trending viral audio"],
            "terror": ["Ambient horror", "Creepy piano", "Tension builds"],
            "aita": ["Dramatic piano", "Tense strings", "Suspenseful ambient"],
            "genz_chaos": ["Hyperpop", "Sped up songs", "Chaotic edits"],
            "relationship_drama": ["Sad piano", "Emotional indie", "Breakup songs"]
        }
        return music_map.get(genre, music_map["comedy"])

    def _calculate_viral_score(self, story: dict) -> int:
        """Calculate viral potential score (0-100).

        Args:
            story: Story dict

        Returns:
            Viral score
        """
        score = 50  # Base score

        # Duration bonus (30-60s is optimal)
        duration = story.get('estimated_duration', 45)
        if 30 <= duration <= 60:
            score += 20
        elif duration < 30:
            score -= 10
        elif duration > 80:
            score -= 20

        # Word count bonus (100-150 optimal)
        word_count = story.get('word_count', 100)
        if 100 <= word_count <= 150:
            score += 15
        elif word_count < 80:
            score -= 10

        # Hook bonus
        if story.get('hook'):
            score += 15

        return max(0, min(100, score))


# CLI testing
if __name__ == "__main__":
    meta = VideoMetadata()

    # Test story
    test_story = {
        "story": "Bro you're not gonna believe this. I went to Starbucks and...",
        "genre": "comedy",
        "word_count": 120,
        "estimated_duration": 48.0,
        "hook": "Bro you're not gonna believe this",
        "template_used": "Gen-Z Comedy"
    }

    # Generate metadata
    metadata = meta.create_metadata_json(
        video_path="output/comedy_short.mp4",
        story=test_story,
        audio_path="output/audio.mp3",
        subtitle_path="output/subtitles.srt",
        genre="comedy"
    )

    # Display
    print(json.dumps(metadata, indent=2))
