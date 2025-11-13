"""Interactive video creation with step-by-step human verification."""
import sys
import json
from pathlib import Path

from src.generation.story_generator import StoryGenerator
from src.generation.tts_generator import TTSGenerator
from src.generation.tts_elevenlabs import ElevenLabsTTS
from src.generation.subtitle_generator import SubtitleGenerator
from src.generation.video_composer import VideoComposer
from src.generation.story_templates import list_genres
from src.utils.config import GROQ_API_KEY, ELEVENLABS_API_KEY, BACKGROUNDS_DIR, PENDING_DIR
from src.utils.metadata import VideoMetadata


def ask_yes_no(question: str, default: bool = True) -> bool:
    """Ask user yes/no question.

    Args:
        question: Question to ask
        default: Default answer

    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes']


def save_intermediate_files(story: dict, audio_path: str, subtitles: list, output_dir: Path):
    """Save story, audio, and subtitles for editing.

    Args:
        story: Story dict
        audio_path: Path to audio file
        subtitles: List of subtitle tuples
        output_dir: Output directory

    Returns:
        Dict of saved file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save story as text
    story_file = output_dir / "story.txt"
    with open(story_file, 'w', encoding='utf-8') as f:
        f.write(story['story'])

    # Save story metadata as JSON
    story_json = output_dir / "story.json"
    with open(story_json, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2)

    # Save subtitles as SRT
    srt_file = output_dir / "subtitles.srt"
    sub_gen = SubtitleGenerator()
    sub_gen._save_srt(subtitles, str(srt_file))

    print(f"\n[SAVED] Intermediate files:")
    print(f"  Story text: {story_file}")
    print(f"  Story JSON: {story_json}")
    print(f"  Audio: {audio_path}")
    print(f"  Subtitles: {srt_file}")
    print()

    return {
        "story_text": str(story_file),
        "story_json": str(story_json),
        "audio": audio_path,
        "subtitles": str(srt_file)
    }


def create_viral_video_interactive(genre: str = "comedy"):
    """Create video with step-by-step human verification.

    Args:
        genre: Video genre

    Returns:
        dict with video info
    """
    print("=" * 60)
    print("INTERACTIVE VIRAL VIDEO CREATOR")
    print("=" * 60)
    print()
    print("[INFO] You'll review each step before proceeding")
    print()

    # Step 1: Generate Story
    print("=" * 60)
    print("STEP 1: STORY GENERATION")
    print("=" * 60)
    print()

    story_gen = StoryGenerator()
    story = story_gen.generate_story(genre=genre)

    # Validate
    is_valid, issues = story_gen.validate_story(story)

    # Display story
    print(f"[GENRE] {story['genre'].upper()}")
    print(f"[LENGTH] {story['word_count']} words (~{story['estimated_duration']:.0f}s)")
    if not is_valid:
        print(f"[WARNING] {', '.join(issues)}")
    print()
    print("-" * 60)
    print(story['story'])
    print("-" * 60)
    print()

    if not ask_yes_no("Accept this story?", default=True):
        print("[CANCELLED] Story rejected. Regenerating...")
        # Regenerate (simplified - could loop)
        story = story_gen.generate_story(genre=genre)
        print()
        print("-" * 60)
        print(story['story'])
        print("-" * 60)
        print()

    # Step 2: Generate Voiceover
    print()
    print("=" * 60)
    print("STEP 2: VOICEOVER GENERATION")
    print("=" * 60)
    print()

    # Use ElevenLabs if API key is set, otherwise use gTTS
    if ELEVENLABS_API_KEY:
        print("[INFO] Using ElevenLabs TTS (premium quality)")
        tts = ElevenLabsTTS(ELEVENLABS_API_KEY)
        # Get appropriate voice for genre
        voice = tts.get_voice_for_genre(genre)
        audio_path = PENDING_DIR / f"temp_audio_{genre}.mp3"
        audio_path = tts.generate_audio(story['story'], voice=voice, output_path=str(audio_path))
        # Use TTSGenerator for duration calculation
        temp_tts = TTSGenerator()
        audio_duration = temp_tts.get_audio_duration(audio_path)
    else:
        print("[INFO] Using gTTS (free)")
        tts = TTSGenerator()
        audio_path = PENDING_DIR / f"temp_audio_{genre}.mp3"
        audio_path = tts.generate_audio(story['story'], output_path=str(audio_path))
        audio_duration = tts.get_audio_duration(audio_path)

    print(f"[GENERATED] {audio_duration:.1f}s voiceover")
    print(f"[SAVED] {audio_path}")
    print()

    if not ask_yes_no("Listen to audio and continue?", default=True):
        print("[INFO] You can replace the audio file manually if needed")
        input("Press Enter when ready to continue...")

    # Step 3: Generate Subtitles
    print()
    print("=" * 60)
    print("STEP 3: SUBTITLE GENERATION")
    print("=" * 60)
    print()

    sub_gen = SubtitleGenerator(words_per_chunk=2)
    subtitles = sub_gen.generate_subtitles(story['story'], audio_duration)

    print(f"[GENERATED] {len(subtitles)} subtitle chunks")
    print(f"[PREVIEW] First 5 chunks:")
    for i, (start, end, text) in enumerate(subtitles[:5], 1):
        print(f"  {i}. [{start:.1f}s-{end:.1f}s] {text}")
    print()

    # Save intermediate files
    intermediate_files = save_intermediate_files(
        story, str(audio_path), subtitles, PENDING_DIR / f"{genre}_intermediate"
    )

    if not ask_yes_no("Proceed with video creation?", default=True):
        print()
        print("[PAUSED] You can now:")
        print(f"  - Edit story: {intermediate_files['story_text']}")
        print(f"  - Replace audio: {intermediate_files['audio']}")
        print(f"  - Edit subtitles: {intermediate_files['subtitles']}")
        print()
        if not ask_yes_no("Resume after edits?", default=False):
            print("[CANCELLED] Exiting. Files saved for manual processing.")
            return None

    # Step 4: Create Video
    print()
    print("=" * 60)
    print("STEP 4: VIDEO CREATION")
    print("=" * 60)
    print()

    composer = VideoComposer()
    output_path = PENDING_DIR / f"{genre}_short.mp4"

    print("[INFO] Creating video with:")
    print(f"  - Viral {genre} font")
    print(f"  - Yellow subtitles (2-word chunks)")
    print(f"  - {audio_duration:.1f}s duration")
    print()

    video_path = composer.create_video(
        audio_path=str(audio_path),
        subtitles=subtitles,
        output_path=str(output_path),
        story_metadata=story,
        genre=story['genre']
    )

    # Step 5: Generate Publishing Metadata
    print()
    print("=" * 60)
    print("STEP 5: PUBLISHING METADATA")
    print("=" * 60)
    print()

    meta_gen = VideoMetadata()
    metadata = meta_gen.create_metadata_json(
        video_path=video_path,
        story=story,
        audio_path=str(audio_path),
        subtitle_path=intermediate_files['subtitles'],
        genre=genre
    )

    # Save metadata
    metadata_path = Path(video_path).with_suffix('.json')
    meta_gen.save_metadata(metadata, str(metadata_path))

    # Display
    print("[CAPTION]")
    print(metadata['publishing']['caption'])
    print()
    print("[HASHTAGS]")
    print(metadata['publishing']['hashtags_string'])
    print()
    print("[MUSIC SUGGESTIONS]")
    for music in metadata['publishing']['suggested_music']:
        print(f"  - {music}")
    print()
    print(f"[VIRAL SCORE] {metadata['optimization']['viral_score']}/100")
    print()

    # Final review
    print()
    print("=" * 60)
    print("VIDEO CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"[VIDEO] {video_path}")
    print(f"[METADATA] {metadata_path}")
    print(f"[DURATION] {audio_duration:.1f}s")
    print("=" * 60)
    print()

    print("[NEXT STEPS]")
    print("1. Review video quality")
    print("2. Add background music manually (see suggestions above)")
    print("3. Use caption + hashtags for posting")
    print("4. Post at optimal times: 7-9pm EST, 12-2pm EST, or 6-8am EST")
    print()

    if ask_yes_no("Open output folder?", default=True):
        import os
        os.startfile(PENDING_DIR)

    return {
        "video_path": video_path,
        "metadata_path": metadata_path,
        "intermediate_files": intermediate_files,
        "metadata": metadata
    }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive video creator with human verification"
    )

    parser.add_argument(
        'genre',
        nargs='?',
        default='comedy',
        choices=list_genres(),
        help='Video genre (default: comedy)'
    )

    args = parser.parse_args()

    # Check prerequisites
    if not GROQ_API_KEY:
        print("[ERROR] GROQ_API_KEY not set in .env file")
        sys.exit(1)

    backgrounds = list(BACKGROUNDS_DIR.glob("*.mp4"))
    if not backgrounds:
        print("[ERROR] No background videos found!")
        print(f"Add MP4 videos to: {BACKGROUNDS_DIR}")
        sys.exit(1)

    # Create video interactively
    try:
        result = create_viral_video_interactive(genre=args.genre)

        if result:
            print()
            print("[SUCCESS] Video ready for review and posting!")

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
