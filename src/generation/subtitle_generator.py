"""Subtitle generation with word-level timing."""
import re
from pathlib import Path
from typing import List, Tuple, Optional


class SubtitleGenerator:
    """Generate word-level subtitles for viral videos."""

    def __init__(self, words_per_chunk: int = 2):
        """Initialize subtitle generator.

        Args:
            words_per_chunk: Number of words per subtitle chunk (default: 3 for readability)
        """
        self.words_per_chunk = words_per_chunk

    def generate_subtitles(
        self,
        text: str,
        audio_duration: float
    ) -> List[Tuple[float, float, str]]:
        """Generate subtitles with timing.

        Args:
            text: Story text
            audio_duration: Duration of audio in seconds

        Returns:
            List of (start_time, end_time, text) tuples
        """
        # Clean and split text into words
        words = self._clean_text(text).split()
        total_words = len(words)

        if total_words == 0:
            return []

        # Calculate timing
        time_per_word = audio_duration / total_words

        # Create subtitle chunks
        subtitles = []
        for i in range(0, total_words, self.words_per_chunk):
            chunk_words = words[i:i + self.words_per_chunk]
            chunk_text = " ".join(chunk_words)

            # Calculate timing for this chunk
            start_time = i * time_per_word
            end_time = (i + len(chunk_words)) * time_per_word

            subtitles.append((start_time, end_time, chunk_text))

        return subtitles


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
