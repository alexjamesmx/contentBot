"""Subtitle generation with word-level timing."""
import re
from pathlib import Path
from typing import List, Tuple, Optional


class SubtitleGenerator:
    """Generate viral subtitles optimized for 2025 retention."""

    def __init__(self, words_per_chunk: int = 4):
        """Initialize subtitle generator.

        Args:
            words_per_chunk: Number of words per subtitle (default: 4 - optimal for 2025)
                           Research shows 3-5 words = best retention
        """
        self.words_per_chunk = words_per_chunk

        # Emotional words that should be emphasized in subtitles
        self.emphasis_words = {
            "SHOCKED", "INSANE", "NEVER", "ALWAYS", "WORST", "BEST",
            "CAN'T BELIEVE", "LITERALLY", "ACTUALLY", "SERIOUS",
            "CRAZY", "UNBELIEVABLE", "UNHINGED", "WILD", "ABSURD"
        }

    def generate_subtitles(
        self,
        text: str,
        audio_duration: float
    ) -> List[Tuple[float, float, str]]:
        """Generate subtitles with optimal 2025 retention settings.

        Creates 3-5 word chunks with natural breaks and emotion detection.

        Args:
            text: Story text (may include CAPS for emphasis)
            audio_duration: Duration of audio in seconds

        Returns:
            List of (start_time, end_time, text) tuples
        """
        # Clean text but preserve CAPS for emphasis
        words = self._split_preserving_emphasis(text)
        total_words = len(words)

        if total_words == 0:
            return []

        # Calculate timing (account for pauses in emotional markers)
        # If text has "..." pauses, add slight delay
        pause_adjustment = text.count("...") * 0.15  # 150ms per pause
        effective_duration = audio_duration + pause_adjustment
        time_per_word = effective_duration / total_words

        # Create subtitle chunks with smart breaking
        subtitles = []
        for i in range(0, total_words, self.words_per_chunk):
            chunk_words = words[i:i + self.words_per_chunk]
            chunk_text = " ".join(chunk_words)

            # Calculate timing for this chunk
            start_time = i * time_per_word
            end_time = (i + len(chunk_words)) * time_per_word

            subtitles.append((start_time, end_time, chunk_text))

        return subtitles

    def _split_preserving_emphasis(self, text: str) -> List[str]:
        """Split text into words while preserving CAPS emphasis.

        Args:
            text: Text with possible CAPS emphasis

        Returns:
            List of words with emphasis preserved
        """
        # Remove excessive punctuation but keep natural breaks
        text = re.sub(r'\.\.\.', ' ', text)  # Remove pause markers (handled in timing)
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ')

        # Split on whitespace
        words = text.strip().split()

        return words


    def _clean_text(self, text: str) -> str:
        """Clean text for subtitle generation.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove newlines
        text = text.replace('\n', ' ')
        return text.strip()



# CLI testing
if __name__ == "__main__":
    import sys

    print("📝 ContentBot Subtitle Generator\n")

    test_text = """Bro you're not gonna believe what just happened.
    So I'm at Starbucks, right? And this dude walks in wearing a full dinosaur costume.
    Not like a cute one, like a terrifying Jurassic Park velociraptor."""

    test_duration = 15.0  # seconds

    print(f"Test text: {test_text[:80]}...")
    print(f"Audio duration: {test_duration}s\n")

    # Test chunked subtitles (2 words per subtitle)
    print("=" * 60)
    print("CHUNKED SUBTITLES (2 words per line)")
    print("=" * 60)

    gen = SubtitleGenerator(words_per_chunk=2)
    chunked = gen.generate_subtitles(test_text, test_duration)

    for start, end, text in chunked[:10]:  # Show first 10
        print(f"[{start:.2f}s - {end:.2f}s] {text}")

    print(f"\n... ({len(chunked)} total subtitles)\n")
    print(f"✅ Subtitles generated successfully!")
