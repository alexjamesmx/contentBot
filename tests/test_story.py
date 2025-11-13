"""Quick test script for story generation."""
import sys
from src.generation.story_generator import StoryGenerator
from src.generation.story_templates import list_genres
from src.utils.config import GROQ_API_KEY


def main():
    print("🤖 ContentBot Story Generator Test\n")
    print("=" * 60)

    # Check API key
    if not GROQ_API_KEY:
        print("❌ ERROR: GROQ_API_KEY not set!")
        print("\n📝 Setup Instructions:")
        print("1. Go to https://console.groq.com/")
        print("2. Sign up and create a FREE API key")
        print("3. Open .env file in this directory")
        print("4. Replace 'your_groq_api_key_here' with your actual key")
        print("5. Run this script again\n")
        sys.exit(1)

    print(f"✅ API Key found: {GROQ_API_KEY[:20]}...")
    print(f"✅ Available genres: {', '.join(list_genres())}\n")
    print("=" * 60)

    # Get genre from command line or default to comedy
    genre = sys.argv[1] if len(sys.argv) > 1 else "comedy"

    if genre not in list_genres():
        print(f"❌ Invalid genre: {genre}")
        print(f"Choose from: {', '.join(list_genres())}")
        sys.exit(1)

    print(f"\n🎬 Generating {genre.upper()} story...\n")

    # Generate story
    try:
        generator = StoryGenerator()
        story = generator.generate_story(genre=genre)

        # Validate
        is_valid, issues = generator.validate_story(story)

        # Display results
        print("=" * 60)
        print(f"📊 STORY METRICS")
        print("=" * 60)
        print(f"Genre: {story['genre']} ({story['template_used']})")
        print(f"Duration: ~{story['estimated_duration']}s")
        print(f"Word Count: {story['word_count']}")
        print(f"Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
        if not is_valid:
            print(f"Issues: {', '.join(issues)}")
        print("=" * 60)
        print()
        print("📝 GENERATED STORY:")
        print()
        print(story['story'])
        print()
        print("=" * 60)
        print()
        print("✅ Story generation successful!")
        print("🎯 Next: Build TTS + video pipeline")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check your API key is valid")
        print("- Verify internet connection")
        print("- Try again in a few seconds")
        sys.exit(1)


if __name__ == "__main__":
    main()
