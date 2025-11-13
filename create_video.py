"""Main pipeline: Story → Audio → Video"""
import sys
import argparse
from pathlib import Path

from src.generation.story_generator import StoryGenerator
from src.generation.tts_generator import TTSGenerator
from src.generation.tts_elevenlabs import ElevenLabsTTS
from src.generation.subtitle_generator import SubtitleGenerator
from src.generation.video_composer import VideoComposer
from src.generation.story_templates import list_genres
from src.scrapers.reddit_scraper import RedditScraper
from src.scrapers.reddit_screenshot_generator import RedditScreenshotGenerator
from src.utils.duplicate_detector import DuplicateDetector
from src.utils.config import (
    GROQ_API_KEY,
    ELEVENLABS_API_KEY,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    BACKGROUNDS_DIR,
    PENDING_DIR
)


def create_viral_video(
    genre: str = "comedy",
    custom_story: str = None,
    reddit_mode: bool = False,
    reddit_subreddit: str = None,
    accent: str = "us",
    background_video: str = None,
    skip_subtitles: bool = False,
    output_dir: str = None,
    use_screenshots: bool = True,
    screenshot_position: str = "center",
    comment_display_mode: str = "sequential"
) -> dict:
    """Create a complete viral video from start to finish.

    Args:
        genre: Story genre (comedy, terror, aita, genz_chaos, relationship_drama)
        custom_story: Use custom story text instead of generating
        reddit_mode: Fetch story from Reddit instead of AI generation
        reddit_subreddit: Specific subreddit to fetch from (default: based on genre)
        accent: TTS accent (us, uk, aus, india, canada)
        background_video: Specific background video path (random if None)
        skip_subtitles: Don't add subtitles
        output_dir: Output directory (pending_review if None)
        use_screenshots: Generate and use Reddit screenshots (only for reddit_mode)
        screenshot_position: Screenshot position (top, center, bottom)
        comment_display_mode: How to display comments (sequential, overlay, slide)

    Returns:
        dict with video_path, story, audio_path, etc.
    """
    print("=" * 60)
    print("🤖 CONTENTBOT - VIRAL VIDEO GENERATOR")
    print("=" * 60)
    print()

    # Step 1: Generate, scrape, or use custom story
    if custom_story:
        print("📝 Using custom story...")
        story = {
            "story": custom_story,
            "genre": genre,
            "word_count": len(custom_story.split()),
            "estimated_duration": len(custom_story.split()) / 2.5,
            "source": "custom"
        }
    elif reddit_mode:
        print("🔍 Fetching story from Reddit...")

        # Check if Reddit API is configured
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            print("❌ ERROR: Reddit API not configured!")
            print("See REDDIT_SETUP_GUIDE.md for setup instructions")
            raise ValueError("Reddit API credentials required for --reddit mode")

        # Initialize scraper and duplicate detector
        scraper = RedditScraper()
        detector = DuplicateDetector()

        # Map genre to subreddit if not specified
        genre_to_subreddit = {
            "aita": "AmItheAsshole",
            "relationship_drama": "relationship_advice",
            "comedy": "tifu",
            "genz_chaos": "confession",
            "terror": "LetsNotMeet",
        }

        subreddit = reddit_subreddit or genre_to_subreddit.get(genre, "AmItheAsshole")

        # Fetch posts
        posts = scraper.fetch_posts(
            subreddit=subreddit,
            limit=50,
            min_upvotes=200,
            min_words=75,
            max_words=250,
        )

        # Filter out duplicates
        posts = detector.get_unused_posts(posts)

        if not posts:
            print("❌ No unused posts found. Try a different subreddit or clear duplicate database.")
            raise ValueError("No unused Reddit posts available")

        # Get best post
        best_post = posts[0]
        print(f"✅ Found post: {best_post['title'][:60]}...")
        print(f"   Upvotes: {best_post['upvotes']} | Comments: {best_post['num_comments']}")
        print(f"   Viral Score: {best_post['viral_score']:.0f}")
        print()
        print("🔗 " + "=" * 58)
        print(f"   REDDIT THREAD: {best_post['url']}")
        print("   " + "=" * 58)
        print()

        # Format for video
        story = RedditScraper.format_for_video(best_post)

        # Mark as used
        detector.mark_as_used(
            reddit_id=best_post['id'],
            subreddit=best_post['subreddit'],
            title=best_post['title']
        )

    else:
        print(f"🎭 Generating {genre.upper()} story with AI...")
        story_gen = StoryGenerator()
        story = story_gen.generate_story(genre=genre)

        # Validate
        is_valid, issues = story_gen.validate_story(story)
        if not is_valid:
            print(f"⚠️  Story validation warnings: {', '.join(issues)}")

        story["source"] = "ai"

    print(f"✅ Story ready: {story['word_count']} words (~{story['estimated_duration']:.0f}s)")
    print()
    print("📖 STORY PREVIEW:")
    print("-" * 60)
    print(story['story'][:200] + "..." if len(story['story']) > 200 else story['story'])
    print("-" * 60)
    print()

    # Step 1.5: Generate Reddit screenshot if in Reddit mode
    screenshot_path = None
    comment_screenshots = []
    if reddit_mode and use_screenshots:
        print("📸 Generating Reddit screenshot...")
        try:
            screenshot_gen = RedditScreenshotGenerator(theme="dark")
            screenshots = screenshot_gen.capture_post_screenshot(
                post_url=story['source_url'],
                output_dir=str(PENDING_DIR / "screenshots"),
                post_id=story['reddit_id'],
                capture_comments=True,  # Capture comments for engagement
                max_comments=3  # Top 3 comments
            )
            screenshot_path = screenshots['post']
            comment_screenshots = screenshots.get('comments', [])
            print(f"✅ Screenshot saved: {Path(screenshot_path).name}")
            if comment_screenshots:
                print(f"✅ Captured {len(comment_screenshots)} comment screenshot(s)")
        except Exception as e:
            print(f"⚠️  Screenshot generation failed: {e}")
            print("   Falling back to text subtitles...")
            use_screenshots = False
        print()

    # Step 2: Generate voiceover
    print("🎙️  Generating voiceover...")

    # Use ElevenLabs if API key is set, otherwise use gTTS
    if ELEVENLABS_API_KEY:
        print("🎤 Using ElevenLabs TTS (premium quality)")
        tts = ElevenLabsTTS(ELEVENLABS_API_KEY)
        # Get appropriate voice for genre
        voice = tts.get_voice_for_genre(genre)
        audio_path = PENDING_DIR / f"temp_audio_{genre}.mp3"
        audio_path = tts.generate_audio(story['story'], voice=voice, output_path=str(audio_path))
        # Use TTSGenerator for duration calculation
        temp_tts = TTSGenerator()
        audio_duration = temp_tts.get_audio_duration(audio_path)
    else:
        print("🎤 Using gTTS (free)")
        tts = TTSGenerator()
        audio_path = PENDING_DIR / f"temp_audio_{genre}.mp3"
        audio_path = tts.generate_audio(story['story'], output_path=str(audio_path))
        audio_duration = tts.get_audio_duration(audio_path)

    print(f"✅ Voiceover generated: {audio_duration:.1f}s")
    print()

    # Step 3: Generate subtitles (2 words = faster, more viral pacing)
    subtitles = None
    if not skip_subtitles:
        print("📝 Generating subtitles...")
        sub_gen = SubtitleGenerator(words_per_chunk=2)  # Faster pacing for retention
        subtitles = sub_gen.generate_subtitles(story['story'], audio_duration)
        print(f"✅ Generated {len(subtitles)} subtitle chunks")
        print()

    # Step 4: Compose video
    print("🎬 Composing final video...")
    composer = VideoComposer()

    output_path = output_dir or PENDING_DIR
    output_path = Path(output_path) / f"{genre}_short.mp4"

    # Use screenshot if available (Reddit mode), otherwise use subtitles
    video_path = composer.create_video(
        audio_path=audio_path,
        background_video=background_video,
        subtitles=subtitles if not screenshot_path else None,  # Don't add text if using screenshots
        output_path=str(output_path),
        story_metadata=story,
        genre=story['genre'],  # Pass genre for viral font selection
        screenshot_path=screenshot_path,
        screenshot_position=screenshot_position,
        comment_screenshots=comment_screenshots if comment_screenshots else None,
        comment_display_mode=comment_display_mode
    )

    print()
    print("=" * 60)
    print("🎉 VIDEO CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📁 Video: {video_path}")
    print(f"⏱️  Duration: {audio_duration:.1f}s")
    print(f"🎭 Genre: {story['genre']}")
    print(f"📊 Word count: {story['word_count']}")
    print(f"🔖 Source: {story.get('source', 'unknown')}")
    if story.get('source') == 'reddit':
        print()
        print("🔗 " + "=" * 58)
        print(f"   REDDIT THREAD: {story.get('source_url', 'N/A')}")
        print("   " + "=" * 58)
        if screenshot_path:
            print(f"📸 Screenshot: {screenshot_path}")
    print("=" * 60)
    print()

    return {
        "video_path": video_path,
        "audio_path": audio_path,
        "story": story,
        "duration": audio_duration,
        "subtitle_count": len(subtitles) if subtitles else 0
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create viral short-form videos automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python create_video.py comedy                       # Generate AI comedy video
  python create_video.py aita --reddit                # Get story from r/AmItheAsshole (with screenshot)
  python create_video.py --reddit --subreddit tifu    # Get from r/tifu
  python create_video.py terror --accent uk           # British horror story
  python create_video.py --reddit --no-screenshots    # Reddit with text subtitles
  python create_video.py --reddit --screenshot-position top  # Screenshot at top
  python create_video.py genz_chaos --no-subs         # No subtitles
  python create_video.py --custom "Your story..."     # Use custom story

Available genres: {', '.join(list_genres())}
        """
    )

    parser.add_argument(
        'genre',
        nargs='?',
        default='comedy',
        choices=list_genres(),
        help='Video genre (default: comedy)'
    )

    parser.add_argument(
        '--custom',
        type=str,
        help='Use custom story text instead of generating'
    )

    parser.add_argument(
        '--reddit',
        action='store_true',
        help='Fetch story from Reddit instead of AI generation'
    )

    parser.add_argument(
        '--subreddit',
        type=str,
        help='Specific subreddit to fetch from (e.g., "tifu", "confession")'
    )

    parser.add_argument(
        '--accent',
        default='us',
        choices=['us', 'uk', 'aus', 'india', 'canada'],
        help='TTS voice accent (default: us)'
    )

    parser.add_argument(
        '--background',
        type=str,
        help='Specific background video file'
    )

    parser.add_argument(
        '--no-subs',
        action='store_true',
        help='Skip subtitle generation'
    )

    parser.add_argument(
        '--no-screenshots',
        action='store_true',
        help='Disable Reddit screenshot generation (use text subtitles instead)'
    )

    parser.add_argument(
        '--screenshot-position',
        default='center',
        choices=['top', 'center', 'bottom'],
        help='Screenshot vertical position (default: center)'
    )

    parser.add_argument(
        '--comment-display',
        default='sequential',
        choices=['sequential', 'overlay', 'slide'],
        help='Comment screenshot display mode (default: sequential)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output directory (default: output/pending_review)'
    )

    args = parser.parse_args()

    # Check prerequisites
    if not GROQ_API_KEY:
        print("❌ ERROR: GROQ_API_KEY not set in .env file")
        print("Get your free key at: https://console.groq.com/")
        sys.exit(1)

    backgrounds = list(BACKGROUNDS_DIR.glob("*.mp4"))
    if not backgrounds and not args.background:
        print("❌ ERROR: No background videos found!")
        print(f"Add MP4 videos to: {BACKGROUNDS_DIR}")
        print("\nDownload copyright-free gameplay videos:")
        print("- Minecraft parkour")
        print("- Subway Surfers")
        print("- GTA gameplay")
        sys.exit(1)

    # Create video
    try:
        result = create_viral_video(
            genre=args.genre,
            custom_story=args.custom,
            reddit_mode=args.reddit,
            reddit_subreddit=args.subreddit,
            accent=args.accent,
            background_video=args.background,
            skip_subtitles=args.no_subs,
            output_dir=args.output,
            use_screenshots=not args.no_screenshots,
            screenshot_position=args.screenshot_position,
            comment_display_mode=args.comment_display
        )

        print("✅ Ready for review and posting!")
        print(f"🎬 Open: {result['video_path']}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
