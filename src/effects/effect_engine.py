"""Effect Timeline Engine - Applies effects from JSON timelines to video clips."""

import re
from typing import List, Dict, Tuple, Any, Optional
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
import numpy as np


class EffectEngine:
    """Applies effects from timeline JSON to video clips.

    Supports effect types:
    - zoom_effect: Zoom video at specific times/words
    - subtitle_style_override: Change subtitle appearance during time range
    - background_change: Switch background video mid-generation
    """

    def __init__(self, timeline: List[Dict[str, Any]]):
        """Initialize effect engine.

        Args:
            timeline: List of effect dictionaries from JSON config
        """
        self.timeline = timeline

    def apply_effects(
        self,
        video_clip: VideoFileClip,
        subtitles: List[Tuple[float, float, str]],
        story_text: str,
        subtitle_clips: Optional[List] = None
    ) -> Tuple[VideoFileClip, List[Tuple[float, float, str]], List]:
        """Apply all effects from timeline.

        Args:
            video_clip: Base video clip
            subtitles: List of (start, end, text) tuples
            story_text: Full story text for word matching
            subtitle_clips: Optional list of subtitle clip objects

        Returns:
            Tuple of (modified_video_clip, modified_subtitles, modified_subtitle_clips)
        """
        if not self.timeline:
            return video_clip, subtitles, subtitle_clips or []

        modified_video = video_clip
        modified_subtitles = subtitles
        modified_subtitle_clips = subtitle_clips or []

        print(f"[EFFECTS] Applying {len(self.timeline)} effects from timeline...")

        for i, effect in enumerate(self.timeline):
            effect_type = effect.get('type')
            effect_id = effect.get('id', f'effect_{i}')

            try:
                if effect_type == 'zoom_effect':
                    modified_video = self._apply_zoom(
                        modified_video, effect, story_text, subtitles
                    )
                    print(f"[EFFECT] Applied {effect_id}: zoom_effect")

                elif effect_type == 'subtitle_style_override':
                    modified_subtitle_clips = self._apply_subtitle_override(
                        modified_subtitle_clips, effect, subtitles
                    )
                    print(f"[EFFECT] Applied {effect_id}: subtitle_style_override")

                elif effect_type == 'background_change':
                    modified_video = self._apply_background_change(
                        modified_video, effect
                    )
                    print(f"[EFFECT] Applied {effect_id}: background_change")

                else:
                    print(f"[WARN] Unknown effect type: {effect_type}")

            except Exception as e:
                print(f"[ERROR] Failed to apply {effect_id}: {e}")
                continue

        return modified_video, modified_subtitles, modified_subtitle_clips

    def _apply_zoom(
        self,
        clip: VideoFileClip,
        effect: Dict,
        story_text: str,
        subtitles: List[Tuple[float, float, str]]
    ) -> VideoFileClip:
        """Apply zoom effect based on trigger.

        Args:
            clip: Video clip to zoom
            effect: Effect configuration
            story_text: Full story text
            subtitles: Subtitle timing info

        Returns:
            Modified video clip with zoom effects
        """
        trigger = effect.get('trigger', {})
        params = effect.get('parameters', {})

        scale = params.get('scale', 1.15)
        duration_ms = params.get('duration_ms', 300)
        duration_sec = duration_ms / 1000.0

        zoom_times = self._find_trigger_times(trigger, story_text, subtitles)

        if not zoom_times:
            print(f"[ZOOM] No trigger matches found")
            return clip

        print(f"[ZOOM] Found {len(zoom_times)} zoom triggers")

        # Apply zoom at each time
        # For simplicity, we'll use resize effect at specific times
        # More advanced implementation would use fl_time for smooth zoom

        def zoom_effect_func(get_frame, t):
            """Apply zoom at specific timestamps."""
            frame = get_frame(t)

            # Check if we're in a zoom window
            for zoom_time in zoom_times:
                if zoom_time <= t < zoom_time + duration_sec:
                    # Calculate zoom progress (0 to 1 to 0 for smooth in-out)
                    progress = (t - zoom_time) / duration_sec
                    current_scale = 1.0 + (scale - 1.0) * (1 - abs(2 * progress - 1))

                    # Resize frame
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h / current_scale), int(w / current_scale)

                    # Crop to center
                    y1 = (h - new_h) // 2
                    x1 = (w - new_w) // 2
                    cropped = frame[y1:y1+new_h, x1:x1+new_w]

                    # Resize back to original size
                    from PIL import Image
                    # MoviePy uses BGR (OpenCV), PIL expects RGB - convert!
                    cropped_rgb = cropped[:, :, ::-1]  # BGR → RGB
                    pil_img = Image.fromarray(cropped_rgb)
                    resized = pil_img.resize((w, h), Image.Resampling.LANCZOS)
                    # Convert back to BGR for MoviePy
                    resized_bgr = np.array(resized)[:, :, ::-1]  # RGB → BGR
                    return resized_bgr

            return frame

        # Apply the zoom effect using MoviePy 2.x transform()
        try:
            zoomed_clip = clip.transform(zoom_effect_func)
            return zoomed_clip
        except Exception as e:
            print(f"[ZOOM ERROR] {e}")
            return clip

    def _apply_subtitle_override(
        self,
        subtitle_clips: List,
        effect: Dict,
        subtitles: List[Tuple[float, float, str]]
    ) -> List:
        """Apply subtitle style override during time range.

        Args:
            subtitle_clips: List of subtitle clip objects (ImageClip with timing)
            effect: Effect configuration
            subtitles: Subtitle timing info

        Returns:
            Modified subtitle clips with new styling applied
        """
        trigger = effect.get('trigger', {})
        params = effect.get('parameters', {})

        if trigger.get('type') != 'time_range':
            print(f"[SUBTITLE] Subtitle override only supports time_range trigger")
            return subtitle_clips

        start_time = trigger.get('start_time', 0)
        end_time = trigger.get('end_time', 0)

        new_color = params.get('color')
        new_size = params.get('size')

        print(f"[SUBTITLE] Overriding style from {start_time}s to {end_time}s")
        if new_color:
            print(f"  Color: {new_color}")
        if new_size:
            print(f"  Size: {new_size}")

        # Find subtitle clips that overlap with the time range
        modified_clips = []

        for i, clip in enumerate(subtitle_clips):
            # Extract timing info from clip
            clip_start = clip.start if hasattr(clip, 'start') else 0
            clip_end = clip_start + (clip.duration if hasattr(clip, 'duration') else 0)

            # Check if this subtitle overlaps with override time range
            overlaps = not (clip_end <= start_time or clip_start >= end_time)

            if overlaps:
                # Find corresponding subtitle text
                matching_subtitle = None
                for sub_start, sub_end, sub_text in subtitles:
                    if abs(sub_start - clip_start) < 0.1:  # Match within 100ms
                        matching_subtitle = (sub_start, sub_end, sub_text)
                        break

                if matching_subtitle:
                    # Recreate clip with new style
                    print(f"  Recreating subtitle {i+1} with new style: '{matching_subtitle[2][:30]}'")
                    new_clip = self._recreate_subtitle_clip(
                        matching_subtitle,
                        font_size=new_size if new_size else 72,
                        text_color=new_color if new_color else 'yellow',
                        stroke_width=4
                    )
                    modified_clips.append(new_clip)
                else:
                    # Keep original if we can't find matching subtitle
                    modified_clips.append(clip)
            else:
                # Outside override range, keep original
                modified_clips.append(clip)

        return modified_clips

    def _recreate_subtitle_clip(
        self,
        subtitle: Tuple[float, float, str],
        font_size: int = 72,
        text_color: str = 'yellow',
        stroke_width: int = 4,
        video_width: int = 1080,
        video_height: int = 1920
    ):
        """Recreate a single subtitle clip with new styling.

        Args:
            subtitle: (start, end, text) tuple
            font_size: Font size in pixels
            text_color: Text color name or hex
            stroke_width: Stroke width in pixels
            video_width: Video width for positioning
            video_height: Video height for positioning

        Returns:
            New ImageClip with updated styling
        """
        from PIL import Image, ImageDraw, ImageFont
        from pathlib import Path
        import numpy as np

        start, end, text = subtitle

        # Get font path (use Montserrat as default)
        fonts_dir = Path(__file__).parent.parent.parent / 'assets' / 'fonts'
        font_path = fonts_dir / 'Montserrat-Black.ttf'
        if not font_path.exists():
            # Fallback to Windows system font
            font_path = r"C:\Windows\Fonts\impact.ttf"

        # Font setup
        pil_font = ImageFont.truetype(str(font_path), size=font_size)

        # Measure text with stroke padding
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text.upper(), font=pil_font, stroke_width=stroke_width)
        text_width = bbox[2] - bbox[0] + stroke_width * 2
        text_height = bbox[3] - bbox[1] + stroke_width * 2

        # Create image with padding
        img_width = min(text_width + 20, video_width - 100)
        img_height = text_height + 20

        # Render text
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Center text in image
        x = (img_width - text_width) // 2 + stroke_width
        y = (img_height - text_height) // 2 + stroke_width

        # Parse color (handle named colors and hex)
        color_map = {
            'yellow': (255, 255, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
        }

        if text_color.lower() in color_map:
            text_col = color_map[text_color.lower()]
        elif text_color.startswith('#'):
            # Parse hex color
            hex_color = text_color.lstrip('#')
            text_col = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            text_col = (255, 255, 0)  # Default to yellow

        # Draw text with stroke
        draw.text((x, y), text.upper(), font=pil_font, fill=text_col,
                 stroke_width=stroke_width, stroke_fill=(0, 0, 0))

        # Convert to MoviePy clip
        txt_clip = ImageClip(np.array(img))

        # Position (same logic as original)
        text_height = txt_clip.h if txt_clip.h else 100
        safe_bottom_margin = 420
        y_position = video_height - safe_bottom_margin - text_height - 50

        txt_clip = txt_clip.with_position(('center', y_position))
        txt_clip = txt_clip.with_start(start)
        txt_clip = txt_clip.with_duration(end - start)

        return txt_clip

    def _apply_background_change(
        self,
        clip: VideoFileClip,
        effect: Dict
    ) -> VideoFileClip:
        """Switch background video at specific time.

        Args:
            clip: Current video clip
            effect: Effect configuration

        Returns:
            Modified video with background change
        """
        trigger = effect.get('trigger', {})
        params = effect.get('parameters', {})

        if trigger.get('type') != 'time':
            print(f"[BACKGROUND] Background change only supports time trigger")
            return clip

        switch_time = trigger.get('time', 0)
        new_source = params.get('new_source')
        transition_type = params.get('transition', 'cut')
        transition_duration = params.get('transition_duration', 1.0)

        if not new_source:
            print(f"[BACKGROUND] No new_source specified")
            return clip

        print(f"[BACKGROUND] Switching to {new_source} at {switch_time}s with '{transition_type}' transition")

        try:
            from pathlib import Path

            # Validate switch time
            if switch_time <= 0 or switch_time >= clip.duration:
                print(f"[BACKGROUND ERROR] Switch time {switch_time}s out of range (0 to {clip.duration}s)")
                return clip

            # Load new background video
            new_source_path = Path(new_source)
            if not new_source_path.exists():
                # Try relative to assets/backgrounds/
                from pathlib import Path
                assets_path = Path(__file__).parent.parent.parent / 'assets' / 'backgrounds' / new_source
                if assets_path.exists():
                    new_source_path = assets_path
                else:
                    print(f"[BACKGROUND ERROR] Video not found: {new_source}")
                    return clip

            print(f"[BACKGROUND] Loading new background from: {new_source_path.name}")
            new_bg = VideoFileClip(str(new_source_path))

            # Split original clip
            clip_part1 = clip.subclipped(0, switch_time)
            remaining_duration = clip.duration - switch_time

            # Prepare new background (crop/resize to match original)
            target_w, target_h = clip.w, clip.h
            target_aspect = target_w / target_h
            new_aspect = new_bg.w / new_bg.h

            # Crop new background to match aspect ratio
            if abs(new_aspect - target_aspect) > 0.01:
                if new_aspect > target_aspect:
                    # Too wide, crop width
                    new_width = int(new_bg.h * target_aspect)
                    x_center = new_bg.w / 2
                    x1 = int(x_center - new_width / 2)
                    new_bg = new_bg.cropped(x1=x1, width=new_width)
                else:
                    # Too tall, crop height
                    new_height = int(new_bg.w / target_aspect)
                    y_center = new_bg.h / 2
                    y1 = int(y_center - new_height / 2)
                    new_bg = new_bg.cropped(y1=y1, height=new_height)

            # Resize to match original
            new_bg = new_bg.resized((target_w, target_h))

            # Loop or trim new background to match remaining duration
            if new_bg.duration < remaining_duration:
                # Loop if too short
                num_loops = int(remaining_duration / new_bg.duration) + 1
                new_bg = concatenate_videoclips([new_bg] * num_loops)

            # Trim to exact duration
            clip_part2 = new_bg.subclipped(0, remaining_duration)

            # Apply transition
            if transition_type == 'cut':
                # Simple concatenation
                final_clip = concatenate_videoclips([clip_part1, clip_part2])

            elif transition_type == 'fade':
                # Crossfade transition
                fade_duration = min(transition_duration, switch_time, remaining_duration)

                # Fade out first clip
                clip_part1 = clip_part1.fadein(0).fadeout(fade_duration)

                # Fade in second clip
                clip_part2 = clip_part2.fadein(fade_duration).fadeout(0)

                # Overlap the fades
                clip_part2 = clip_part2.with_start(switch_time - fade_duration)

                # Use CompositeVideoClip to blend during overlap
                final_clip = CompositeVideoClip([clip_part1, clip_part2])
                final_clip = final_clip.with_duration(clip.duration)

            else:
                print(f"[BACKGROUND WARN] Unknown transition type '{transition_type}', using cut")
                final_clip = concatenate_videoclips([clip_part1, clip_part2])

            print(f"[BACKGROUND] Successfully switched background at {switch_time}s")
            return final_clip

        except Exception as e:
            print(f"[BACKGROUND ERROR] Failed to switch background: {e}")
            import traceback
            traceback.print_exc()
            return clip

    def _find_trigger_times(
        self,
        trigger: Dict,
        story_text: str,
        subtitles: List[Tuple[float, float, str]]
    ) -> List[float]:
        """Find timestamps where trigger condition is met.

        Args:
            trigger: Trigger configuration
            story_text: Full story text
            subtitles: Subtitle timing info

        Returns:
            List of timestamps in seconds
        """
        trigger_type = trigger.get('type')
        times = []

        if trigger_type == 'word_match':
            pattern = trigger.get('pattern', '')

            # Find all matching words in subtitles
            for start, end, text in subtitles:
                if re.search(pattern, text, re.IGNORECASE):
                    times.append(start)

        elif trigger_type == 'time':
            times.append(trigger.get('time', 0))

        elif trigger_type == 'time_range':
            # For ranges, return start time
            times.append(trigger.get('start_time', 0))

        return times
