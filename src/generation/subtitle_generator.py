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
        audio_duration: float,
        output_path: Optional[str] = None
    ) -> List[Tuple[float, float, str]]:
        """Generate subtitles with timing.

        Args:
            text: Story text
            audio_duration: Duration of audio in seconds
            output_path: Optional path to save SRT file

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

        # Save to SRT file if path provided
        if output_path:
            self._save_srt(subtitles, output_path)

        return subtitles

    def generate_word_level_subtitles(
        self,
        text: str,
        audio_duration: float
    ) -> List[Tuple[float, float, str]]:
        """Generate word-by-word subtitles (for highlighting effect).

        Args:
            text: Story text
            audio_duration: Duration of audio in seconds

        Returns:
            List of (start_time, end_time, word) tuples
        """
        words = self._clean_text(text).split()
        total_words = len(words)

        if total_words == 0:
            return []

        time_per_word = audio_duration / total_words

        subtitles = []
        for i, word in enumerate(words):
            start_time = i * time_per_word
            end_time = (i + 1) * time_per_word
            subtitles.append((start_time, end_time, word))

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

    def _save_srt(self, subtitles: List[Tuple[float, float, str]], output_path: str):
        """Save subtitles in SRT format.

        Args:
            subtitles: List of (start, end, text) tuples
            output_path: Path to save SRT file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing file if it exists (explicit overwrite)
        if output_path.exists():
            output_path.unlink()

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, (start, end, text) in enumerate(subtitles, 1):
                # SRT format:
                # 1
                # 00:00:00,000 --> 00:00:02,000
                # Subtitle text
                f.write(f"{i}\n")
                f.write(f"{self._format_timestamp(start)} --> {self._format_timestamp(end)}\n")
                f.write(f"{text}\n\n")

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


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

    # Test chunked subtitles (3 words per subtitle)
    print("=" * 60)
    print("CHUNKED SUBTITLES (3 words per line)")
    print("=" * 60)

    gen = SubtitleGenerator(words_per_chunk=3)
    chunked = gen.generate_subtitles(test_text, test_duration)

    for start, end, text in chunked[:5]:  # Show first 5
        print(f"[{start:.2f}s - {end:.2f}s] {text}")

    print(f"\n... ({len(chunked)} total subtitles)\n")

    # Test word-level subtitles
    print("=" * 60)
    print("WORD-LEVEL SUBTITLES (for highlighting)")
    print("=" * 60)

    word_level = gen.generate_word_level_subtitles(test_text, test_duration)

    for start, end, word in word_level[:10]:  # Show first 10 words
        print(f"[{start:.2f}s - {end:.2f}s] {word}")

    print(f"\n... ({len(word_level)} total words)\n")

    # Save SRT
    srt_path = "output/test_subtitles.srt"
    gen.generate_subtitles(test_text, test_duration, output_path=srt_path)
    print(f"✅ SRT file saved to: {srt_path}")
