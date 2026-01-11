"""ElevenLabs TTS integration for premium voiceovers with smart caching."""
from typing import Optional
from pathlib import Path
import os
import hashlib
import json

# v1.x SDK
try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except Exception as e:
    ELEVENLABS_AVAILABLE = False
    ELEVENLABS_IMPORT_ERROR = e

from src.utils.config import OUTPUT_DIR, REUSE_EXISTING_FILES, PROJECT_ROOT


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

        # Cache directory for ElevenLabs audio
        self.cache_dir = PROJECT_ROOT / "cache" / "elevenlabs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_index = self.cache_dir / "index.json"
        self._load_cache_index()

    def _load_cache_index(self):
        """Load cache index from disk"""
        if self.cache_index.exists():
            with open(self.cache_index, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def _save_cache_index(self):
        """Save cache index to disk"""
        with open(self.cache_index, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)

    def _get_cache_key(self, text: str, voice: str, settings: dict) -> str:
        """Generate cache key from text + voice + settings"""
        cache_data = {
            'text': text,
            'voice': voice,
            'settings': settings
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _get_cached_audio(self, cache_key: str) -> Optional[str]:
        """Get cached audio path if exists"""
        if cache_key in self.cache:
            cached_path = Path(self.cache[cache_key]['path'])
            if cached_path.exists():
                print(f"[CACHE HIT] Reusing cached ElevenLabs audio (saved API credits!)")
                print(f"[CACHE] File: {cached_path.name}")
                return str(cached_path)
            else:
                # Remove stale cache entry
                del self.cache[cache_key]
                self._save_cache_index()
        return None

    def _cache_audio(self, cache_key: str, audio_path: str, text: str, voice: str):
        """Save audio to cache"""
        import time
        self.cache[cache_key] = {
            'path': audio_path,
            'voice': voice,
            'text_preview': text[:100],
            'created_at': time.time()
        }
        self._save_cache_index()
        print(f"[CACHE] Saved to cache for future reuse")

    def generate_audio(
        self,
        text: str,
        voice: str = "mark",
        output_path: Optional[str] = None,
        stability: float = 0.45,
        similarity_boost: float = 0.75,
        style: float = 0.3,
        model_id: str = "eleven_turbo_v2_5",
        output_format: str = "mp3_44100_128",
        optimize_streaming_latency: str = "0",
        add_emotion: bool = True
    ) -> str:
        """Generate audio using ElevenLabs with optimal settings for viral storytelling.

        Args:
            text: Story text to convert
            voice: Voice ID (mark, snap, peter, viraj, rachel, adam)
            output_path: Optional output path (uses cache by default)
            stability: 0.45 optimal for stories (prevents monotony)
            similarity_boost: 0.75 recommended
            style: 0.3 for emotional stories, 0.0 for flat narration
            model_id: eleven_turbo_v2_5 best for storytelling with emotion
            output_format: Audio quality
            optimize_streaming_latency: Streaming optimization
            add_emotion: Automatically add pauses and emphasis (recommended)

        Returns:
            Path to generated audio file
        """
        # Add emotional markers for more natural delivery (2025 best practice)
        if add_emotion:
            from src.generation.story_generator import StoryGenerator
            original_text = text
            text = StoryGenerator.add_emotional_markers(text)
            if text != original_text:
                print("[EMOTION] Added natural pauses and emphasis for TTS")
        if voice not in self.VIRAL_VOICES:
            print(f"[WARNING] Unknown voice '{voice}', using 'mark'")
            voice = "mark"

        voice_id = self.VIRAL_VOICES[voice]["voice_id"]
        print(f"[ELEVENLABS] Using voice: {self.VIRAL_VOICES[voice]['name']}")
        print(f"[INFO] {self.VIRAL_VOICES[voice]['description']}")

        # Generate cache key from content
        settings = {
            'stability': stability,
            'similarity_boost': similarity_boost,
            'style': style,
            'model_id': model_id
        }
        cache_key = self._get_cache_key(text, voice, settings)

        # Check cache first (saves API credits!)
        cached_path = self._get_cached_audio(cache_key)
        if cached_path:
            return cached_path

        # Set output path (use cache directory)
        if output_path is None:
            output_path = self.cache_dir / f"{cache_key}.mp3"
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing file if regenerating
        if output_path.exists():
            output_path.unlink()

        print(f"[ELEVENLABS] Generating new audio (will be cached)...")

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

        # Cache this audio for future reuse
        self._cache_audio(cache_key, str(output_path), text, voice)

        return str(output_path)



# CLI testing
if __name__ == "__main__":
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("[ERROR] ELEVENLABS_API_KEY not set")
        raise SystemExit(1)

    print("\n=== ElevenLabs TTS Test ===\n")
    print("Available voices:")
    for key, voice in ElevenLabsTTS.VIRAL_VOICES.items():
        print(f"  {voice['name']} ({key}) - {voice['description']}")

    tts = ElevenLabsTTS(api_key)
    text = ("Bro, you're not gonna believe what just happened. "
            "This is the most unhinged story of 2025.")
    print("\n[TEST] Generating sample with Mark voice...")
    out = tts.generate_audio(text, voice="mark")
    print(f"[SAVED] {out}\n[INFO] Play the file to hear the voice!")