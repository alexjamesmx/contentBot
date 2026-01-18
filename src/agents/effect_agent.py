"""AI Effect Agent - Generates effect timelines from natural language prompts."""

import json
from typing import List, Dict, Any, Optional, Tuple
from groq import Groq


class EffectAgent:
    """AI agent that generates effect timelines from natural language prompts.

    This agent analyzes story content and user requests to automatically
    generate JSON effect timelines that can be applied to videos.

    Example:
        User: "Add zoom effects on emphasis words"
        Agent: Generates zoom_effect entries for SHOCKED, INSANE, etc.
    """

    def __init__(self, groq_client: Optional[Groq] = None, api_key: Optional[str] = None):
        """Initialize effect agent.

        Args:
            groq_client: Optional Groq client instance
            api_key: Optional Groq API key (if client not provided)
        """
        if groq_client:
            self.client = groq_client
        elif api_key:
            self.client = Groq(api_key=api_key)
        else:
            raise ValueError("Either groq_client or api_key must be provided")

        self.model = "llama-3.3-70b-versatile"

    def generate_timeline_from_prompt(
        self,
        prompt: str,
        story_text: str,
        audio_duration: float,
        subtitles: Optional[List[Tuple[float, float, str]]] = None
    ) -> List[Dict[str, Any]]:
        """Generate effect timeline from natural language prompt.

        Args:
            prompt: User's natural language request (e.g., "Add zoom at emotional peaks")
            story_text: Full story text for context
            audio_duration: Total audio duration in seconds
            subtitles: Optional subtitle timing info

        Returns:
            List of effect dictionaries ready for EffectEngine

        Example:
            >>> agent = EffectAgent(api_key="...")
            >>> timeline = agent.generate_timeline_from_prompt(
            ...     "Add dramatic zoom when shocked",
            ...     story_text="I was SHOCKED when...",
            ...     audio_duration=65.0
            ... )
            >>> print(timeline)
            [{"type": "zoom_effect", "trigger": {...}, "parameters": {...}}]
        """
        # Build comprehensive system prompt with effect documentation
        system_prompt = self._build_system_prompt(story_text, audio_duration, subtitles)

        # Call Groq API for effect generation
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for structured output
                max_tokens=2000,
                response_format={"type": "json_object"}  # Force JSON response
            )

            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)

            # Extract effects array
            effects = result.get('effects', [])

            print(f"[EFFECT AGENT] Generated {len(effects)} effects from prompt: '{prompt}'")
            return effects

        except Exception as e:
            print(f"[EFFECT AGENT ERROR] {e}")
            return []

    def _build_system_prompt(
        self,
        story_text: str,
        audio_duration: float,
        subtitles: Optional[List[Tuple[float, float, str]]]
    ) -> str:
        """Build comprehensive system prompt for effect generation.

        Args:
            story_text: Story text for context
            audio_duration: Video duration
            subtitles: Subtitle timing info

        Returns:
            System prompt string
        """
        # Analyze story for emphasis words
        emphasis_words = self._extract_emphasis_words(story_text)
        emphasis_str = ", ".join(emphasis_words) if emphasis_words else "None detected"

        # Estimate climax timing (usually around 60-70% through story)
        climax_time = audio_duration * 0.65

        system_prompt = f"""You are an expert video effect designer for viral TikTok/YouTube Shorts content.

Your task is to generate a JSON effect timeline based on user requests. Analyze the story content and create effects that enhance engagement and retention.

**STORY CONTEXT:**
Duration: {audio_duration:.1f} seconds
Text length: {len(story_text)} characters
Detected emphasis words: {emphasis_str}
Estimated climax timing: {climax_time:.1f}s

Story excerpt:
{story_text[:500]}...

**AVAILABLE EFFECT TYPES:**

1. **zoom_effect** - Zoom video at specific moments
   - Triggers: word_match (regex pattern), time (exact second)
   - Parameters:
     * scale: 1.0-1.3 (1.15 recommended for subtle zoom)
     * duration_ms: 200-500 (300 is smooth)
     * easing: "ease_in_out" (smooth), "linear" (constant)
   - Best for: Emphasis words, shocking moments, climax

2. **subtitle_style_override** - Change subtitle appearance
   - Triggers: time_range (start_time, end_time)
   - Parameters:
     * color: hex code (e.g., "#FF0000" for red)
     * size: 60-100 (90 for emphasis)
     * animation: "pulse", "fade", null
   - Best for: Climax, emotional peaks, important dialogue

3. **background_change** - Switch background video
   - Triggers: time (exact second)
   - Parameters:
     * new_source: filename (e.g., "minecraft_parkour.mp4")
     * transition: "cut", "crossfade", "fade"
     * transition_duration: 0.5-2.0 seconds
   - Best for: Scene changes, mood shifts

**EFFECT DESIGN GUIDELINES:**

1. **Subtlety First**: Don't overwhelm viewers
   - Max 5-8 zoom effects per video
   - Use subtle scales (1.1-1.15)
   - Space effects at least 3-5s apart

2. **Strategic Timing**:
   - Hook (0-3s): Grab attention immediately
   - Retention boost (15s mark): Keep viewers past algorithm threshold
   - Climax (60-70% through): Peak emotional impact
   - Ending (last 10s): Satisfying conclusion

3. **Match Emotion to Effect**:
   - Shocking moments: Quick zoom (200ms)
   - Dramatic reveals: Subtitle color change to red
   - Mood shifts: Background change with crossfade

4. **Viral Optimization**:
   - Emphasize emotional words: SHOCKED, INSANE, NEVER, ALWAYS, WORST, BEST
   - Create pattern interrupts every 10-15 seconds
   - Enhance climax with multiple effects (zoom + subtitle style)

**OUTPUT FORMAT:**

Return ONLY valid JSON with this structure:
{{
  "effects": [
    {{
      "id": "descriptive_name",
      "type": "effect_type",
      "trigger": {{"type": "trigger_type", ...}},
      "parameters": {{...}}
    }}
  ]
}}

**EXAMPLES:**

User: "Add zoom on emphasis words"
Output:
{{
  "effects": [
    {{
      "id": "zoom_emphasis",
      "type": "zoom_effect",
      "trigger": {{"type": "word_match", "pattern": "SHOCKED|INSANE|NEVER|ALWAYS"}},
      "parameters": {{"scale": 1.15, "duration_ms": 300, "easing": "ease_in_out"}}
    }}
  ]
}}

User: "Make climax dramatic with red subtitles"
Output:
{{
  "effects": [
    {{
      "id": "climax_red_subtitles",
      "type": "subtitle_style_override",
      "trigger": {{"type": "time_range", "start_time": 40.0, "end_time": 50.0}},
      "parameters": {{"color": "#FF0000", "size": 90}}
    }},
    {{
      "id": "climax_zoom",
      "type": "zoom_effect",
      "trigger": {{"type": "time", "time": 45.0}},
      "parameters": {{"scale": 1.2, "duration_ms": 400}}
    }}
  ]
}}

Remember:
- Analyze the story carefully
- Choose appropriate effect timing
- Keep it subtle and professional
- Output ONLY valid JSON"""

        return system_prompt

    def _extract_emphasis_words(self, story_text: str) -> List[str]:
        """Extract emphasis words (CAPS) from story text.

        Args:
            story_text: Story text to analyze

        Returns:
            List of emphasized words found
        """
        import re

        # Find words in all caps (at least 3 letters)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', story_text)

        # Remove duplicates and limit
        unique_words = list(set(caps_words))[:10]

        return unique_words
