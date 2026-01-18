"""Multi-part story series manager with context preservation."""
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from src.generation.story_generator import StoryGenerator
from src.utils.config import PROJECT_ROOT


class StoryContextManager:
    """Manages multi-part story series with context preservation."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize the context manager.

        Args:
            storage_dir: Directory to store series data (defaults to cache/story_series/)
        """
        self.storage_dir = storage_dir or (PROJECT_ROOT / "cache" / "story_series")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.story_generator = StoryGenerator()

    def create_series(
        self,
        genre: str,
        total_parts: int,
        theme: str,
        base_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new story series.

        Args:
            genre: Story genre (comedy, terror, aita, genz_chaos, relationship_drama)
            total_parts: Total number of parts in the series
            theme: Overall theme/topic for the series
            base_prompt: Optional custom base prompt

        Returns:
            dict with story_id and series_metadata
        """
        if total_parts < 1:
            raise ValueError("Series must have at least 1 part")
        if total_parts > 10:
            raise ValueError("Series cannot exceed 10 parts")

        story_id = str(uuid.uuid4())

        series_data = {
            "story_id": story_id,
            "title": self._generate_timestamp_title(genre),
            "genre": genre,
            "total_parts": total_parts,
            "current_part": 0,
            "theme": theme,
            "base_prompt": base_prompt,
            "parts": [],
            "context": {
                "characters": [],
                "plot_points": [],
                "tone": self._get_tone_for_genre(genre),
                "location": ""
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "auto_title": False
        }

        self._save_series(story_id, series_data)

        return {
            "story_id": story_id,
            "series_metadata": {
                "genre": genre,
                "total_parts": total_parts,
                "theme": theme,
                "created_at": series_data["created_at"]
            }
        }

    def generate_next_part(
        self,
        story_id: str,
        target_duration: int = 75
    ) -> Dict[str, Any]:
        """Generate the next part in a series.

        Args:
            story_id: UUID of the story series
            target_duration: Target duration in seconds (default: 75)

        Returns:
            dict with story_text, part_metadata, duration
        """
        series_data = self._load_series(story_id)

        if not series_data:
            raise ValueError(f"Story series not found: {story_id}")

        current_part = series_data["current_part"]
        total_parts = series_data["total_parts"]

        if current_part >= total_parts:
            raise ValueError(f"Series complete: {current_part}/{total_parts} parts already generated")

        next_part_num = current_part + 1

        # Build contextual prompt
        contextual_prompt = self._build_contextual_prompt(
            series_data=series_data,
            part_number=next_part_num,
            target_duration=target_duration
        )

        # Generate story using existing StoryGenerator
        story_result = self.story_generator.generate_story(
            genre=series_data["genre"],
            custom_prompt=contextual_prompt,
            target_duration=target_duration
        )

        # Extract context from generated story
        self._extract_and_update_context(series_data, story_result["story"], next_part_num)

        # Add part to series
        part_data = {
            "part": next_part_num,
            "story_text": story_result["story"],
            "duration": story_result["estimated_duration"],
            "word_count": story_result["word_count"],
            "timestamp": datetime.now().isoformat(),
            "audio_path": None,
            "video_path": None,
            "metadata": {}
        }

        series_data["parts"].append(part_data)
        series_data["current_part"] = next_part_num
        series_data["updated_at"] = datetime.now().isoformat()

        self._save_series(story_id, series_data)

        return {
            "story_text": story_result["story"],
            "part_metadata": {
                "part": next_part_num,
                "total_parts": total_parts,
                "word_count": story_result["word_count"],
                "hook": story_result["hook"]
            },
            "duration": story_result["estimated_duration"]
        }

    def get_series(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get series information.

        Args:
            story_id: UUID of the story series

        Returns:
            dict with story_id, parts, current_part, metadata or None if not found
        """
        series_data = self._load_series(story_id)

        if not series_data:
            return None

        return {
            "story_id": series_data["story_id"],
            "parts": series_data["parts"],
            "current_part": series_data["current_part"],
            "metadata": {
                "genre": series_data["genre"],
                "total_parts": series_data["total_parts"],
                "theme": series_data["theme"],
                "context": series_data["context"],
                "created_at": series_data["created_at"],
                "updated_at": series_data["updated_at"]
            }
        }

    def list_all_series(self) -> List[Dict[str, Any]]:
        """List all story series.

        Returns:
            list of dicts with story_id, title, parts_count, genre
        """
        all_series = []

        for series_file in self.storage_dir.glob("*.json"):
            try:
                with open(series_file, 'r', encoding='utf-8') as f:
                    series_data = json.load(f)

                all_series.append({
                    "story_id": series_data["story_id"],
                    "title": series_data.get("title", self._generate_title(series_data)),
                    "parts_count": series_data["current_part"],
                    "total_parts": series_data["total_parts"],
                    "genre": series_data["genre"],
                    "theme": series_data["theme"],
                    "created_at": series_data["created_at"],
                    "updated_at": series_data["updated_at"],
                    "current_part": series_data["current_part"],
                    "parts": series_data.get("parts", [])
                })
            except Exception as e:
                print(f"Error loading series {series_file}: {e}")
                continue

        # Sort by updated_at (most recent first)
        all_series.sort(key=lambda x: x["updated_at"], reverse=True)

        return all_series

    def link_assets_to_part(
        self,
        series_id: str,
        part_number: int,
        audio_path: Optional[str] = None,
        video_path: Optional[str] = None
    ) -> None:
        """Link audio/video files to a specific part.

        Args:
            series_id: UUID of the series
            part_number: Part number to link assets to
            audio_path: Path to audio file (relative to output dir)
            video_path: Path to video file (relative to output dir)
        """
        series_data = self._load_series(series_id)

        if not series_data:
            raise ValueError(f"Story series not found: {series_id}")

        for part in series_data["parts"]:
            if part["part"] == part_number:
                if audio_path:
                    part["audio_path"] = audio_path
                if video_path:
                    part["video_path"] = video_path
                series_data["updated_at"] = datetime.now().isoformat()
                self._save_series(series_id, series_data)
                return

        raise ValueError(f"Part {part_number} not found in series {series_id}")

    def update_series_total_parts(self, series_id: str, new_total: int) -> None:
        """Update the total_parts count for a series.

        Args:
            series_id: UUID of the series
            new_total: New total parts count
        """
        series_data = self._load_series(series_id)

        if not series_data:
            raise ValueError(f"Story series not found: {series_id}")

        if new_total < series_data["current_part"]:
            raise ValueError(f"Cannot set total_parts ({new_total}) less than current_part ({series_data['current_part']})")

        if new_total > 10:
            raise ValueError("Series cannot exceed 10 parts")

        series_data["total_parts"] = new_total
        series_data["updated_at"] = datetime.now().isoformat()
        self._save_series(series_id, series_data)

    def update_part_metadata(self, series_id: str, part_number: int, metadata_update: Dict[str, Any]) -> None:
        """Update metadata for a specific part in a series.

        Args:
            series_id: UUID of the series
            part_number: Part number to update (1-indexed)
            metadata_update: Dictionary of metadata fields to update
        """
        series_data = self._load_series(series_id)

        if not series_data:
            raise ValueError(f"Story series not found: {series_id}")

        # Find the part
        part_found = False
        for part in series_data["parts"]:
            if part["part"] == part_number:
                part["metadata"].update(metadata_update)
                part_found = True
                break

        if not part_found:
            raise ValueError(f"Part {part_number} not found in series {series_id}")

        series_data["updated_at"] = datetime.now().isoformat()
        self._save_series(series_id, series_data)

    def delete_series(self, story_id: str) -> None:
        """Delete a story series and all associated files.

        Args:
            story_id: UUID of the series to delete
        """
        series_data = self._load_series(story_id)

        if not series_data:
            raise ValueError(f"Story series not found: {story_id}")

        pending_dir = PROJECT_ROOT / "output" / "pending"

        for part in series_data.get("parts", []):
            if part.get("audio_path"):
                audio_file = pending_dir / part["audio_path"]
                if audio_file.exists():
                    try:
                        audio_file.unlink()
                        print(f"[DELETE] Removed audio: {part['audio_path']}")
                    except Exception as e:
                        print(f"[DELETE] Warning: Failed to delete audio {part['audio_path']}: {e}")

            if part.get("video_path"):
                video_file = pending_dir / part["video_path"]
                if video_file.exists():
                    try:
                        video_file.unlink()
                        print(f"[DELETE] Removed video: {part['video_path']}")
                    except Exception as e:
                        print(f"[DELETE] Warning: Failed to delete video {part['video_path']}: {e}")

                json_file = video_file.with_suffix('.json')
                if json_file.exists():
                    try:
                        json_file.unlink()
                        print(f"[DELETE] Removed metadata: {json_file.name}")
                    except Exception as e:
                        print(f"[DELETE] Warning: Failed to delete metadata {json_file.name}: {e}")

        series_file = self.storage_dir / f"{story_id}.json"
        if series_file.exists():
            try:
                series_file.unlink()
                print(f"[DELETE] Removed series file: {story_id}.json")
            except Exception as e:
                raise Exception(f"Failed to delete series file: {e}")

    def generate_ai_title(self, series_id: str) -> Optional[str]:
        """Generate AI title from first part content via Groq.

        Args:
            series_id: UUID of the series

        Returns:
            Generated title or None if fails
        """
        series_data = self._load_series(series_id)

        if not series_data or not series_data["parts"]:
            return None

        if series_data.get("auto_title", False):
            return series_data.get("title")

        first_part = series_data["parts"][0]["story_text"]

        try:
            from groq import Groq
            from src.utils.config import GROQ_API_KEY

            if not GROQ_API_KEY:
                return None

            client = Groq(api_key=GROQ_API_KEY)

            prompt = f"""Generate a catchy, 5-7 word title for this {series_data['genre']} story:

{first_part[:500]}

Requirements:
- 5-7 words maximum
- Engaging and clickable
- Genre-appropriate tone
- No quotes or special characters
- Title only, no explanation

Title:"""

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated to current model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=30
            )

            title = completion.choices[0].message.content.strip()
            title = title.replace('"', '').replace("'", '').strip()

            if len(title) > 70:
                title = title[:67] + "..."

            series_data["title"] = title
            series_data["auto_title"] = True
            series_data["updated_at"] = datetime.now().isoformat()
            self._save_series(series_id, series_data)

            return title

        except Exception as e:
            print(f"Error generating AI title: {e}")
            return None

    def _generate_timestamp_title(self, genre: str) -> str:
        """Generate timestamp-based title for instant creation.

        Args:
            genre: Story genre

        Returns:
            Timestamp-based title
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        genre_label = genre.replace('_', ' ').title()
        return f"{genre_label}-{timestamp}"

    def _build_contextual_prompt(
        self,
        series_data: Dict[str, Any],
        part_number: int,
        target_duration: int
    ) -> str:
        """Build a contextual prompt that references previous parts.

        Args:
            series_data: Complete series data
            part_number: The part number being generated
            target_duration: Target duration in seconds

        Returns:
            Contextual prompt string
        """
        genre = series_data["genre"]
        theme = series_data["theme"]
        total_parts = series_data["total_parts"]
        context = series_data["context"]
        parts = series_data["parts"]

        # Calculate word count target
        target_words = int(target_duration * 2.5)
        min_words = max(150, target_words - 20)
        max_words = min(220, target_words + 30)

        if part_number == 1:
            # First part - establish the series
            prompt = f"""Generate Part 1 of a {total_parts}-part {genre} story series.

SERIES THEME: {theme}

This is the FIRST part - establish the foundation:
- Introduce main characters/setting
- Set up the initial conflict or situation
- Create intrigue that makes viewers want Part 2
- END with a hook: "...but that was just the beginning" or "Little did I know..."

MONETIZATION REQUIREMENTS:
- Word count: {min_words}-{max_words} words ({target_duration} seconds)
- Speaking pace: ~2.5 words/second with natural pauses
- MINIMUM {min_words} words required for monetization

VIRAL RETENTION:
- Hook viewers in first 3 seconds
- Fast pacing, no fluff
- End with cliffhanger/tease for Part 2
- Make them comment "I NEED PART 2!"

Generate Part 1 (target {target_words} words):"""

        else:
            # Subsequent parts - reference previous events
            previous_summaries = []
            for part in parts:
                part_num = part["part"]
                # Extract first and last sentences for context
                story_lines = part["story_text"].split('. ')
                first_line = story_lines[0] if story_lines else ""
                last_line = story_lines[-1] if len(story_lines) > 1 else ""
                previous_summaries.append(f"Part {part_num}: Started with '{first_line[:60]}...', ended with '{last_line[:60]}...'")

            previous_context = "\n".join(previous_summaries)

            # Determine part positioning
            is_final = (part_number == total_parts)
            position_guidance = ""

            if is_final:
                position_guidance = f"""This is the FINAL part ({part_number}/{total_parts}):
- Resolve the main conflict
- Provide satisfying conclusion
- End with impact (viewers share/comment)
- Optional: tease future content if appropriate"""
            else:
                position_guidance = f"""This is Part {part_number} of {total_parts} (MIDDLE):
- Continue the story naturally from Part {part_number - 1}
- Escalate the conflict/situation
- Add new developments or twists
- END with hook for Part {part_number + 1}"""

            # Build context references
            character_list = ", ".join(context["characters"]) if context["characters"] else "the narrator"
            plot_points_text = "\n".join(f"- {point}" for point in context["plot_points"][-3:])  # Last 3 plot points

            prompt = f"""Generate Part {part_number} of a {total_parts}-part {genre} story series.

SERIES THEME: {theme}
CHARACTERS: {character_list}
TONE: {context["tone"]}

PREVIOUS EVENTS:
{previous_context}

KEY PLOT POINTS SO FAR:
{plot_points_text}

{position_guidance}

CONTINUITY REQUIREMENTS:
- Reference events from previous parts naturally
- Maintain consistent character voices/motivations
- Keep the same tone as established parts
- Use phrases like "After what happened..." or "Since then..."

MONETIZATION REQUIREMENTS:
- Word count: {min_words}-{max_words} words ({target_duration} seconds)
- MINIMUM {min_words} words required for monetization

VIRAL RETENTION:
- Quick recap in first sentence (for new viewers)
- Fast pacing, maintain momentum
- {"Satisfying resolution" if is_final else "Cliffhanger ending"}

Generate Part {part_number} (target {target_words} words):"""

        return prompt

    def _extract_and_update_context(
        self,
        series_data: Dict[str, Any],
        story_text: str,
        part_number: int
    ) -> None:
        """Extract context from generated story and update series context.

        Args:
            series_data: Series data to update (modified in place)
            story_text: Generated story text
            part_number: Part number being added
        """
        context = series_data["context"]

        # Extract potential character names (capitalized words that appear multiple times)
        words = story_text.split()
        capitalized = [w.strip('.,!?"()') for w in words if w and w[0].isupper() and len(w) > 2]

        # Add new characters (simple heuristic: capitalized words appearing 2+ times)
        from collections import Counter
        word_counts = Counter(capitalized)
        for word, count in word_counts.items():
            if count >= 2 and word not in context["characters"] and word not in ["I", "The", "A", "An"]:
                context["characters"].append(word)

        # Extract plot points (sentences with emotional words or actions)
        sentences = [s.strip() for s in story_text.split('.') if s.strip()]
        emotional_keywords = ['shocked', 'realized', 'discovered', 'found', 'happened', 'told', 'said', 'decided', 'went', 'saw']

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in emotional_keywords):
                # Add as plot point (truncate if too long)
                plot_point = sentence[:80] + "..." if len(sentence) > 80 else sentence
                if plot_point not in context["plot_points"]:
                    context["plot_points"].append(plot_point)

        # Keep only last 5 plot points to avoid bloat
        context["plot_points"] = context["plot_points"][-5:]

        # Extract location mentions (simple heuristic)
        location_keywords = ['house', 'apartment', 'school', 'office', 'store', 'restaurant', 'park', 'car', 'room']
        for keyword in location_keywords:
            if keyword in story_text.lower() and not context["location"]:
                context["location"] = keyword

    def _get_tone_for_genre(self, genre: str) -> str:
        """Get default tone for genre.

        Args:
            genre: Story genre

        Returns:
            Tone description
        """
        tone_map = {
            "comedy": "humorous and lighthearted",
            "terror": "suspenseful and ominous",
            "aita": "conversational and seeking judgment",
            "genz_chaos": "chaotic and unhinged",
            "relationship_drama": "emotional and dramatic"
        }
        return tone_map.get(genre, "engaging")

    def _generate_title(self, series_data: Dict[str, Any]) -> str:
        """Generate a title for the series.

        Args:
            series_data: Series data

        Returns:
            Generated title
        """
        theme = series_data["theme"]
        genre = series_data["genre"]
        # Truncate theme if too long
        theme_short = theme[:40] + "..." if len(theme) > 40 else theme
        return f"{genre.title()}: {theme_short}"

    def _save_series(self, story_id: str, series_data: Dict[str, Any]) -> None:
        """Save series data to disk.

        Args:
            story_id: UUID of the series
            series_data: Complete series data
        """
        filepath = self.storage_dir / f"{story_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(series_data, f, indent=2, ensure_ascii=False)

    def _load_series(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Load series data from disk.

        Args:
            story_id: UUID of the series

        Returns:
            Series data or None if not found
        """
        filepath = self.storage_dir / f"{story_id}.json"

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading series {story_id}: {e}")
            return None


# CLI testing
if __name__ == "__main__":
    import sys

    print("Multi-Part Story Context Manager\n")

    manager = StoryContextManager()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python story_context_manager.py create <genre> <parts> <theme>")
        print("  python story_context_manager.py next <story_id>")
        print("  python story_context_manager.py list")
        print("  python story_context_manager.py get <story_id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 5:
            print("Error: create requires <genre> <parts> <theme>")
            sys.exit(1)

        genre = sys.argv[2]
        total_parts = int(sys.argv[3])
        theme = " ".join(sys.argv[4:])

        result = manager.create_series(genre, total_parts, theme)
        print(f"\nSeries created!")
        print(f"Story ID: {result['story_id']}")
        print(f"Genre: {genre}")
        print(f"Total parts: {total_parts}")
        print(f"Theme: {theme}")

    elif command == "next":
        if len(sys.argv) < 3:
            print("Error: next requires <story_id>")
            sys.exit(1)

        story_id = sys.argv[2]

        print(f"\nGenerating next part for series: {story_id}")
        result = manager.generate_next_part(story_id)
        print(f"\nPart {result['part_metadata']['part']}/{result['part_metadata']['total_parts']} generated!")
        print(f"Duration: {result['duration']}s")
        print(f"Word count: {result['part_metadata']['word_count']}")
        print("\nStory:")
        print("="*60)
        print(result['story_text'])
        print("="*60)

    elif command == "list":
        series_list = manager.list_all_series()
        print(f"\nFound {len(series_list)} series:\n")
        for series in series_list:
            print(f"ID: {series['story_id']}")
            print(f"  Title: {series['title']}")
            print(f"  Progress: {series['parts_count']}/{series['total_parts']} parts")
            print(f"  Genre: {series['genre']}")
            print()

    elif command == "get":
        if len(sys.argv) < 3:
            print("Error: get requires <story_id>")
            sys.exit(1)

        story_id = sys.argv[2]
        series = manager.get_series(story_id)

        if not series:
            print(f"Series not found: {story_id}")
            sys.exit(1)

        print(f"\nSeries: {story_id}")
        print(f"Progress: {series['current_part']}/{series['metadata']['total_parts']} parts")
        print(f"Genre: {series['metadata']['genre']}")
        print(f"Theme: {series['metadata']['theme']}")
        print(f"\nParts:")
        for part in series['parts']:
            print(f"  Part {part['part']}: {part['word_count']} words, {part['duration']}s")
