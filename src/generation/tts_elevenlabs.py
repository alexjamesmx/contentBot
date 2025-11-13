"""ElevenLabs TTS integration for premium voiceovers."""
from typing import Optional
from pathlib import Path
import os

# v1.x SDK
try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except Exception as e:
    ELEVENLABS_AVAILABLE = False
    ELEVENLABS_IMPORT_ERROR = e

from src.utils.config import OUTPUT_DIR, REUSE_EXISTING_FILES


class ElevenLabsTTS:
    """Premium TTS using ElevenLabs (requires API key)."""

    VIRAL_VOICES = {
        "mark":   {"voice_id": "XrExE9yKIg1WjnnlVkGX", "name": "Mark",
                   "description": "Best for storytelling, casual TikToks (friendly narrator)",
                   "best_for": ["comedy", "aita", "relationship_drama"]},
        "snap":   {"voice_id": "gWaDC0oXAheKoZfljzuI", "name": "Snap",
                   "description": "Playful, upbeat, Gen-Z friendly (memes, commentary)",
                   "best_for": ["comedy", "genz_chaos"]},
        "peter":  {"voice_id": "N2lVS1w4EtoT3dr4eOWO", "name": "Peter",
                   "description": "Bold narrator voice (trending narrator format)",
                   "best_for": ["terror", "aita"]},
        "viraj":  {"voice_id": "bajNon13EdhNMndG3z05", "name": "Viraj",
                   "description": "Warm, passionate, expressive (Indian accent)",
                   "best_for": ["relationship_drama", "aita"]},
        "rachel": {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel",
                   "description": "Clear, calm narrator (professional storytelling)",
                   "best_for": ["terror", "aita"]},
        "adam":   {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam",
                   "description": "Deep, authoritative (serious content)",
                   "best_for": ["terror", "aita"]},
    }

    def __init__(self, api_key: str):
        if not ELEVENLABS_AVAILABLE:
            raise ImportError(
                f"ElevenLabs SDK not available or incompatible. "
                f"Original error: {repr(ELEVENLABS_IMPORT_ERROR)}"
            )
        self.api_key = api_key
        os.environ["ELEVENLABS_API_KEY"] = api_key
        self.client = ElevenLabs(api_key=api_key)

    def generate_audio(
        self,
        text: str,
        voice: str = "mark",
        output_path: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        optimize_streaming_latency: str = "0",
    ) -> str:
        """Generate audio using ElevenLabs v1.x streaming API."""
        if voice not in self.VIRAL_VOICES:
            print(f"[WARNING] Unknown voice '{voice}', using 'mark'")
            voice = "mark"

        voice_id = self.VIRAL_VOICES[voice]["voice_id"]
        print(f"[ELEVENLABS] Using voice: {self.VIRAL_VOICES[voice]['name']}")
        print(f"[INFO] {self.VIRAL_VOICES[voice]['description']}")

        if output_path is None:
            output_path = OUTPUT_DIR / f"elevenlabs_{voice}.mp3"
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if we should reuse existing file (save ElevenLabs credits!)
        if output_path.exists() and REUSE_EXISTING_FILES:
            print(f"[CACHE] Reusing existing ElevenLabs audio: {output_path.name}")
            return str(output_path)

        # Remove existing file if regenerating
        if output_path.exists():
            output_path.unlink()

        # Convert (streaming chunks)
        try:
            stream = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id=model_id,
                text=text,
                output_format=output_format,               # e.g., "mp3_44100_128"
                optimize_streaming_latency=optimize_streaming_latency,
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    use_speaker_boost=True,
                ),
            )
        except Exception as e:
            if "voice" in str(e).lower():
                print("[WARN] Voice ID not available on this account. Falling back to 'rachel'.")
                voice_id = self.VIRAL_VOICES["rachel"]["voice_id"]
                stream = self.client.text_to_speech.convert(
                    voice_id=voice_id,
                    model_id=model_id,
                    text=text,
                    output_format=output_format,
                    optimize_streaming_latency=optimize_streaming_latency,
                    voice_settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost,
                        style=style,
                        use_speaker_boost=True,
                    ),
                )
            else:
                raise

        # Write streamed chunks
        with open(output_path, "wb") as f:
            for chunk in stream:
                if chunk:
                    f.write(chunk)

        return str(output_path)

    def get_voice_for_genre(self, genre: str) -> str:
        for key, data in self.VIRAL_VOICES.items():
            if genre in data["best_for"]:
                return key
        return "mark"

    @staticmethod
    def list_voices():
        print("\n" + "=" * 60)
        print("ELEVENLABS VIRAL VOICES (2025)")
        print("=" * 60)
        for key, voice in ElevenLabsTTS.VIRAL_VOICES.items():
            print(f"\n{voice['name']} ({key})")
            print(f"  Description: {voice['description']}")
            print(f"  Best for: {', '.join(voice['best_for'])}")
        print("\n" + "=" * 60)


# CLI testing
if __name__ == "__main__":
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("[ERROR] ELEVENLABS_API_KEY not set")
        raise SystemExit(1)

    ElevenLabsTTS.list_voices()

    tts = ElevenLabsTTS(api_key)
    text = ("Bro, you're not gonna believe what just happened. "
            "This is the most unhinged story of 2025.")
    print("\n[TEST] Generating sample with Mark voice...")
    out = tts.generate_audio(text, voice="mark")
    print(f"[SAVED] {out}\n[INFO] Play the file to hear the voice!")