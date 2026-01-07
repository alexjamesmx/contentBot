"""Text-to-Speech generation for stories."""
import os
from pathlib import Path
from typing import Optional
from gtts import gTTS

from src.utils.config import OUTPUT_DIR, REUSE_EXISTING_FILES


class TTSGenerator:
    """Generate voiceovers from text using gTTS."""

    def __init__(self, lang: str = "en", tld: str = "com"):
        """Initialize TTS generator.

        Args:
            lang: Language code (default: en)
            tld: Top-level domain for accent (com=US, co.uk=British, com.au=Australian)
        """
        self.lang = lang
        self.tld = tld

    def generate_audio(
        self,
        text: str,
        output_path: Optional[str] = None,
        slow: bool = False
    ) -> str:
        """Generate audio from text.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (auto-generated if None)
            slow: Speak slowly (default: False for normal speed)

        Returns:
            Path to generated audio file
        """
        if not text:
            raise ValueError("Text cannot be empty")

        # Generate output path if not provided
        if output_path is None:
            output_path = OUTPUT_DIR / "temp_audio.mp3"
        else:
            output_path = Path(output_path)

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if we should reuse existing file (save time & API calls)
        if output_path.exists() and REUSE_EXISTING_FILES:
            print(f"[CACHE] Reusing existing audio: {output_path.name}")
            return str(output_path)

        # Remove existing file if regenerating
        if output_path.exists():
            output_path.unlink()

        try:
            # Generate TTS
            tts = gTTS(
                text=text,
                lang=self.lang,
                tld=self.tld,
                slow=slow
            )

            # Save to file
            tts.save(str(output_path))

            return str(output_path)

        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")

    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        from moviepy import AudioFileClip

        try:
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            return duration
        except Exception as e:
            raise Exception(f"Failed to get audio duration: {str(e)}")


# CLI testing
if __name__ == "__main__":
    import sys

    print("🎙️  ContentBot TTS Generator\n")

    test_text = "Bro you're not gonna believe what just happened. So I'm at Starbucks, right? And this dude walks in wearing a full dinosaur costume. Not like a cute one, like a terrifying Jurassic Park velociraptor. He orders a grande caramel macchiato, completely straight-faced, and the barista doesn't even blink. I'm losing it."

    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])

    print(f"Text: {test_text[:100]}...\n")
    print("Generating audio...\n")

    try:
        tts = TTSGenerator()
        audio_path = tts.generate_audio(test_text)
        duration = tts.get_audio_duration(audio_path)

        print(f"✅ Audio generated!")
        print(f"📁 Saved to: {audio_path}")
        print(f"⏱️  Duration: {duration:.1f}s")
        print(f"\n🎧 Play it to test: {audio_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
