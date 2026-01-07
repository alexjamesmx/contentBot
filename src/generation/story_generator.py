"""AI story generation using Groq API."""
import random
from typing import Optional
from groq import Groq

from src.utils.config import GROQ_API_KEY, STORY_TEMPERATURE, STORY_MAX_TOKENS
from src.generation.story_templates import get_template, list_genres


class StoryGenerator:
    """Generate viral stories using AI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the story generator.

        Args:
            api_key: Groq API key (defaults to config)
        """
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it in .env file.")

        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and high quality (updated model)

    def generate_story(
        self,
        genre: str = "comedy",
        custom_prompt: Optional[str] = None,
        temperature: float = STORY_TEMPERATURE,
        max_tokens: int = STORY_MAX_TOKENS,
        target_duration: int = 60
    ) -> dict:
        """Generate a viral story.

        Args:
            genre: Story genre (comedy, terror, aita, genz_chaos, relationship_drama)
            custom_prompt: Optional custom prompt (overrides template)
            temperature: Creativity level (0.0-2.0, higher = more creative)
            max_tokens: Maximum story length
            target_duration: Target duration in seconds (default: 60)

        Returns:
            dict with 'story', 'hook', 'genre', 'template_used'
        """
        # Get template
        template = get_template(genre)

        # Build prompt
        if custom_prompt:
            user_prompt = custom_prompt
        else:
            # Pick random hook and structure
            hook = random.choice(template["hook_patterns"])
            structure = random.choice(template["structure_prompts"])

            # Calculate target word count (average 2.5 words per second)
            target_words = int(target_duration * 2.5)
            min_words = int(target_words * 0.8)
            max_words = int(target_words * 1.2)

            user_prompt = f"""Generate a viral {template['name']} story.

Hook to use: "{hook}"

Story structure: {structure}

STRICT REQUIREMENTS:
- Start with the hook EXACTLY as written
- Target {target_duration} seconds when read aloud ({min_words}-{max_words} words)
- MUST have complete beginning, middle, and END with twist/punchline
- Every sentence must advance the story - no filler
- End with IMPACT - satisfying conclusion
- Write in first person, conversational, fast-paced
- COUNT YOUR WORDS - aim for EXACTLY {target_words} words

IMPORTANT: Write the FULL {target_words}-word story. Don't stop early!

Generate the story now:"""

        # Generate with Groq
        # Calculate dynamic max_tokens based on target duration (give AI enough room)
        if not custom_prompt:
            dynamic_max_tokens = max(max_tokens, int(target_words * 2))
        else:
            dynamic_max_tokens = max_tokens

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": template["system_prompt"]},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=dynamic_max_tokens,
                top_p=0.95,
                stream=False
            )

            story_text = response.choices[0].message.content.strip()

            # Extract hook (first line/sentence)
            hook_used = story_text.split('\n')[0].split('.')[0]

            return {
                "story": story_text,
                "hook": hook_used,
                "genre": genre,
                "template_used": template["name"],
                "word_count": len(story_text.split()),
                "estimated_duration": self._estimate_duration(story_text)
            }

        except Exception as e:
            raise Exception(f"Story generation failed: {str(e)}")


    def _estimate_duration(self, text: str) -> float:
        """Estimate audio duration in seconds.

        Average speaking rate: ~150 words per minute = 2.5 words/second
        """
        word_count = len(text.split())
        return round(word_count / 2.5, 1)

    def validate_story(self, story: dict) -> tuple[bool, list[str]]:
        """Validate story meets viral criteria.

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Check duration (target 30-60s max)
        duration = story["estimated_duration"]
        if duration < 20:
            issues.append(f"Too short: {duration}s (min 20s)")
        elif duration > 65:
            issues.append(f"Too long: {duration}s (max 60s) - will be cut off")

        # Check word count (strict for viral retention)
        word_count = story["word_count"]
        if word_count < 50:
            issues.append(f"Too few words: {word_count} (min 50)")
        elif word_count > 160:
            issues.append(f"Too many words: {word_count} (max 150 for viral)")

        # Check hook exists
        if not story.get("hook"):
            issues.append("Missing hook")

        return (len(issues) == 0, issues)


# CLI testing
if __name__ == "__main__":
    import sys

    print("🤖 ContentBot Story Generator\n")

    # Check API key
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY not set!")
        print("1. Copy .env.example to .env")
        print("2. Get free API key from: https://console.groq.com/")
        print("3. Add it to .env file")
        sys.exit(1)

    # Initialize generator
    generator = StoryGenerator()

    # Show available genres
    print("Available genres:", ", ".join(list_genres()))
    print()

    # Generate test story
    genre = sys.argv[1] if len(sys.argv) > 1 else "comedy"

    print(f"Generating {genre} story...\n")
    story = generator.generate_story(genre=genre)

    # Validate
    is_valid, issues = generator.validate_story(story)

    # Display
    print("="*60)
    print(f"GENRE: {story['genre']} ({story['template_used']})")
    print(f"DURATION: ~{story['estimated_duration']}s")
    print(f"WORDS: {story['word_count']}")
    print(f"VALID: {'✅ YES' if is_valid else '❌ NO - ' + ', '.join(issues)}")
    print("="*60)
    print()
    print(story['story'])
    print()
    print("="*60)
