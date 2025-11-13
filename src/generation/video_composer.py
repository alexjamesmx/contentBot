"""Video composition - combine background, audio, and subtitles."""
import random
from pathlib import Path
from typing import Optional, List, Tuple

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips
)
import numpy as np

from src.utils.config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    BACKGROUNDS_DIR,
    PENDING_DIR,
    FONTS_DIR,
    REUSE_EXISTING_FILES
)


class VideoComposer:
    """Compose final video from components."""

    def __init__(
        self,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        fps: int = VIDEO_FPS,
        use_yellow_text: bool = True,  # Yellow = more viral
        add_zoom_effects: bool = True   # Pattern interrupts
    ):
        """Initialize video composer.

        Args:
            width: Video width (default: 1080)
            height: Video height (default: 1920 for 9:16)
            fps: Frames per second (default: 30)
            use_yellow_text: Use yellow text (more viral than white)
            add_zoom_effects: Add zoom pattern interrupts every 3-5s
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.use_yellow_text = use_yellow_text
        self.add_zoom_effects = add_zoom_effects

    def create_video(
        self,
        audio_path: str,
        background_video: Optional[str] = None,
        subtitles: Optional[List[Tuple[float, float, str]]] = None,
        output_path: Optional[str] = None,
        story_metadata: Optional[dict] = None,
        genre: str = "comedy",
        screenshot_path: Optional[str] = None,
        screenshot_position: str = "center",
        comment_screenshots: Optional[List[str]] = None,
        comment_display_mode: str = "sequential"
    ) -> str:
        """Create final video with all components.

        Args:
            audio_path: Path to audio file
            background_video: Path to background video (random if None)
            subtitles: List of (start, end, text) tuples
            output_path: Output path (auto-generated if None)
            story_metadata: Optional story info for filename
            genre: Video genre for font/styling
            screenshot_path: Path to Reddit post screenshot (if using screenshots)
            screenshot_position: Screenshot position (top, center, bottom)
            comment_screenshots: List of comment screenshot paths
            comment_display_mode: How to display comments ("sequential", "overlay", "slide")

        Returns:
            Path to generated video
        """
        print("[VIDEO] Starting video composition...")

        # Load audio
        print("[AUDIO] Loading audio...")
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration

        # Get background video
        if background_video is None:
            background_video = self._get_random_background()

        print(f"[VIDEO] Loading background: {Path(background_video).name}")
        background = self._prepare_background(background_video, audio_duration)

        # Set audio to background
        video_with_audio = background.with_audio(audio)

        # Add screenshot overlay if provided (Reddit mode)
        if screenshot_path:
            print("[SCREENSHOT] Adding Reddit screenshot overlay...")

            # If we have comment screenshots, add them too
            if comment_screenshots:
                print(f"[COMMENTS] Adding {len(comment_screenshots)} comment screenshot(s)...")
                video_with_screenshot = self._add_screenshots_with_comments(
                    video_with_audio,
                    screenshot_path,
                    comment_screenshots,
                    position=screenshot_position,
                    display_mode=comment_display_mode
                )
            else:
                video_with_screenshot = self._add_screenshot_overlay(
                    video_with_audio,
                    screenshot_path,
                    position=screenshot_position
                )
            video_with_subtitles = video_with_screenshot
        # Otherwise add text subtitles
        elif subtitles:
            # Get font name for display
            font_path = self._get_viral_font(genre)
            font_name = Path(font_path).name if font_path else "system default"
            print(f"Adding {len(subtitles)} subtitles with {font_name}...")
            video_with_subtitles = self._add_subtitles(video_with_audio, subtitles, genre)
        else:
            video_with_subtitles = video_with_audio

        # Generate output path
        if output_path is None:
            genre = story_metadata.get('genre', 'video') if story_metadata else 'video'
            timestamp = Path(audio_path).stem
            output_path = PENDING_DIR / f"{genre}_{timestamp}.mp4"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if we should reuse existing video (save rendering time!)
        if output_path.exists() and REUSE_EXISTING_FILES:
            print(f"[CACHE] Reusing existing video: {output_path.name}")
            # Still need to close clips to free memory
            audio.close()
            background.close()
            return str(output_path)

        # Remove existing file if regenerating
        if output_path.exists():
            print(f"[OVERWRITE] Overwriting existing file: {output_path.name}")
            output_path.unlink()

        # Render video
        print(f"[RENDER] Rendering video to: {output_path.name}")
        print("[WAIT] This may take a minute...")

        video_with_subtitles.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger='bar'  # Progress bar (can be 'bar' or None for quiet)
        )

        # Cleanup
        audio.close()
        background.close()
        video_with_subtitles.close()

        print(f"[SUCCESS] Video created: {output_path}")
        return str(output_path)

    def _prepare_background(self, video_path: str, target_duration: float) -> VideoFileClip:
        """Prepare background video (crop, loop, trim).

        Args:
            video_path: Path to background video
            target_duration: Target duration in seconds

        Returns:
            Prepared video clip
        """
        clip = VideoFileClip(video_path)

        # Crop to 9:16 aspect ratio if needed
        clip_aspect = clip.w / clip.h
        target_aspect = self.width / self.height

        if abs(clip_aspect - target_aspect) > 0.01:
            # Need to crop
            if clip_aspect > target_aspect:
                # Video is too wide, crop width
                new_width = int(clip.h * target_aspect)
                x_center = clip.w / 2
                x1 = int(x_center - new_width / 2)
                clip = clip.cropped(x1=x1, width=new_width)
            else:
                # Video is too tall, crop height
                new_height = int(clip.w / target_aspect)
                y_center = clip.h / 2
                y1 = int(y_center - new_height / 2)
                clip = clip.cropped(y1=y1, height=new_height)

        # Resize to target dimensions
        clip = clip.resized((self.width, self.height))

        # Loop or trim to match audio duration
        if clip.duration < target_duration:
            # Loop the video
            num_loops = int(target_duration / clip.duration) + 1
            clip = concatenate_videoclips([clip] * num_loops)

        # Trim to exact duration
        clip = clip.subclipped(0, target_duration)

        return clip

    def _add_subtitles(
        self,
        video: VideoFileClip,
        subtitles: List[Tuple[float, float, str]],
        genre: str = "comedy"
    ) -> CompositeVideoClip:
        """Add subtitles with viral effects.

        Args:
            video: Video clip
            subtitles: List of (start, end, text) tuples
            genre: Video genre for font selection

        Returns:
            Video with animated subtitles
        """
        subtitle_clips = []

        # Get viral font for this genre
        font_path = self._get_viral_font(genre)

        # Yellow text = more viral
        text_color = 'yellow' if self.use_yellow_text else 'white'

        for i, (start, end, text) in enumerate(subtitles):
            # Create text clip with viral font
            txt_clip = TextClip(
                text=text.upper(),
                font=font_path,
                font_size=80,  # Slightly smaller to prevent cutoff
                color=text_color,
                stroke_color='black',
                stroke_width=5,  # Thick outline for mobile
                size=(self.width - 140, None),
                method='caption',
                text_align='center',
                horizontal_align='center'
            )

            # Position higher to prevent cutoff (65% instead of 72%)
            txt_clip = txt_clip.with_position(('center', self.height * 0.65))
            txt_clip = txt_clip.with_start(start)
            txt_clip = txt_clip.with_duration(end - start)

            # TODO: Add slide-in animations in Phase 2
            # MoviePy 2.x needs different approach for animations

            subtitle_clips.append(txt_clip)

        # Composite video with subtitles
        final_video = CompositeVideoClip([video] + subtitle_clips)

        return final_video

    def _get_viral_font(self, genre: str = "comedy") -> str:
        """Get most viral font for the genre.

        Args:
            genre: Video genre

        Returns:
            Path to viral font file
        """
        from pathlib import Path

        # Viral fonts in order of preference (Montserrat works, others may not be downloaded)
        viral_fonts = {
            "comedy": ["Montserrat-Black.ttf", "BebasNeue-Regular.ttf", "Anton-Regular.ttf"],
            "terror": ["Montserrat-Black.ttf", "Anton-Regular.ttf", "Oswald-Bold.ttf"],
            "aita": ["Montserrat-Black.ttf", "Poppins-Black.ttf", "Inter-Bold.ttf"],
            "genz_chaos": ["Montserrat-Black.ttf", "BebasNeue-Regular.ttf", "Poppins-Black.ttf"],
            "relationship_drama": ["Montserrat-Black.ttf", "Poppins-Black.ttf", "Inter-Bold.ttf"],
        }

        # Get fonts for genre
        font_list = viral_fonts.get(genre, viral_fonts["comedy"])

        # Check our downloaded viral fonts
        for font_name in font_list:
            font_path = FONTS_DIR / font_name
            if font_path.exists():
                # Verify font is valid before returning
                try:
                    from PIL import ImageFont
                    test_font = ImageFont.truetype(str(font_path), size=10)
                    return str(font_path)
                except Exception as e:
                    print(f"[WARN] Font {font_name} exists but is invalid: {e}")
                    continue

        # Fallback to Windows system fonts (reliable and viral-friendly)
        import platform
        import os

        system = platform.system()

        if system == "Windows":
            windows_fonts = [
                r"C:\Windows\Fonts\impact.ttf",      # Bold, attention-grabbing
                r"C:\Windows\Fonts\arialbd.ttf",     # Clean, readable
                r"C:\Windows\Fonts\verdanab.ttf",    # Good for mobile
            ]
            for font in windows_fonts:
                if os.path.exists(font):
                    print(f"[INFO] Using Windows font: {Path(font).name}")
                    return font

        # Final fallback - try to find any system font
        print("[WARN] No custom fonts found, using system default")
        return None  # MoviePy will use default

    def _apply_screenshot_animation(
        self,
        screenshot: ImageClip,
        animation_type: str = "fade_in",
        duration: float = 0.3
    ) -> ImageClip:
        """Apply animation effect to screenshot.

        Args:
            screenshot: Screenshot clip to animate
            animation_type: Type of animation ("fade_in", "slide_up", "zoom_in")
            duration: Animation duration in seconds

        Returns:
            Animated screenshot clip
        """
        if animation_type == "fade_in":
            # Fade in effect
            def fade_in_effect(get_frame, t):
                frame = get_frame(t)
                if t < duration:
                    alpha = t / duration
                    return (frame * alpha).astype('uint8')
                return frame

            return screenshot.transform(fade_in_effect)

        elif animation_type == "slide_up":
            # Slide up from bottom effect
            original_pos = screenshot.pos
            def slide_position(t):
                if t < duration:
                    progress = t / duration
                    # Ease out effect
                    progress = 1 - (1 - progress) ** 3
                    if callable(original_pos):
                        x, y = original_pos(t)
                    else:
                        x, y = original_pos
                    # Start from bottom of screen
                    start_y = self.height
                    return (x, start_y + (y - start_y) * progress)
                return original_pos

            return screenshot.with_position(slide_position)

        elif animation_type == "zoom_in":
            # Zoom in effect
            def zoom_effect(t):
                if t < duration:
                    progress = t / duration
                    # Start at 0.8x scale, zoom to 1.0x
                    scale = 0.8 + (0.2 * progress)
                    return scale
                return 1.0

            return screenshot.resized(lambda t: zoom_effect(t))

        return screenshot

    def _add_screenshots_with_comments(
        self,
        video: VideoFileClip,
        post_screenshot_path: str,
        comment_screenshots: List[str],
        position: str = "center",
        display_mode: str = "sequential"
    ) -> CompositeVideoClip:
        """Add Reddit post and comment screenshots to video.

        Args:
            video: Base video clip
            post_screenshot_path: Path to main post screenshot PNG
            comment_screenshots: List of comment screenshot paths
            position: Vertical position (top, center, bottom)
            display_mode: Display mode ("sequential", "overlay", "slide")

        Returns:
            Video with screenshot overlays
        """
        all_clips = [video]

        # Calculate timing: divide video duration among post + comments
        total_duration = video.duration
        num_screenshots = 1 + len(comment_screenshots)  # post + comments
        duration_per_screenshot = total_duration / num_screenshots

        # Load and prepare all screenshots
        screenshots_data = [(post_screenshot_path, 0)]  # (path, start_time)

        for i, comment_path in enumerate(comment_screenshots):
            start_time = duration_per_screenshot * (i + 1)
            screenshots_data.append((comment_path, start_time))

        # Add screenshots based on display mode
        if display_mode == "sequential":
            # Show one screenshot at a time (sequential display)
            for idx, (screenshot_path, start_time) in enumerate(screenshots_data):
                screenshot = ImageClip(screenshot_path)

                # Scale to fit
                max_width = self.width - 80
                if screenshot.w > max_width:
                    scale_factor = max_width / screenshot.w
                    screenshot = screenshot.resized(scale_factor)

                max_height = self.height * 0.7
                if screenshot.h > max_height:
                    scale_factor = max_height / screenshot.h
                    screenshot = screenshot.resized(scale_factor)

                # Position
                if position == "top":
                    y_pos = 100
                elif position == "bottom":
                    y_pos = self.height - screenshot.h - 100
                else:  # center
                    y_pos = (self.height - screenshot.h) / 2

                screenshot = screenshot.with_position(("center", y_pos))
                screenshot = screenshot.with_start(start_time)
                screenshot = screenshot.with_duration(duration_per_screenshot)

                # Apply animation (alternate between different animations for variety)
                animations = ["fade_in", "slide_up", "zoom_in"]
                animation_type = animations[idx % len(animations)]
                screenshot = self._apply_screenshot_animation(
                    screenshot,
                    animation_type=animation_type,
                    duration=0.4
                )

                all_clips.append(screenshot)

        elif display_mode == "overlay":
            # Show all screenshots overlaid (stacked vertically with slight offset)
            for idx, (screenshot_path, start_time) in enumerate(screenshots_data):
                screenshot = ImageClip(screenshot_path)

                # Scale smaller for overlay mode
                max_width = self.width - 200
                if screenshot.w > max_width:
                    scale_factor = max_width / screenshot.w
                    screenshot = screenshot.resized(scale_factor)

                max_height = self.height * 0.3  # Smaller for overlay
                if screenshot.h > max_height:
                    scale_factor = max_height / screenshot.h
                    screenshot = screenshot.resized(scale_factor)

                # Stack vertically with slight offset
                y_offset = idx * (screenshot.h + 20)  # 20px gap
                base_y = 150

                screenshot = screenshot.with_position(("center", base_y + y_offset))
                screenshot = screenshot.with_start(0)  # All visible from start
                screenshot = screenshot.with_duration(total_duration)

                # Add fade in staggered
                screenshot = self._apply_screenshot_animation(
                    screenshot,
                    animation_type="fade_in",
                    duration=0.3
                ).with_start(idx * 0.5)  # Stagger by 0.5s

                all_clips.append(screenshot)

        elif display_mode == "slide":
            # Slide transition between screenshots (horizontal slide)
            for idx, (screenshot_path, start_time) in enumerate(screenshots_data):
                screenshot = ImageClip(screenshot_path)

                # Scale to fit
                max_width = self.width - 80
                if screenshot.w > max_width:
                    scale_factor = max_width / screenshot.w
                    screenshot = screenshot.resized(scale_factor)

                max_height = self.height * 0.7
                if screenshot.h > max_height:
                    scale_factor = max_height / screenshot.h
                    screenshot = screenshot.resized(scale_factor)

                # Calculate y position
                if position == "top":
                    y_pos = 100
                elif position == "bottom":
                    y_pos = self.height - screenshot.h - 100
                else:  # center
                    y_pos = (self.height - screenshot.h) / 2

                # Slide transition effect
                transition_duration = 0.5
                def make_slide_position(start_t, y_position):
                    def slide_pos(t):
                        # Slide in from right
                        if t < start_t:
                            return (self.width + 100, y_position)
                        elif t < start_t + transition_duration:
                            progress = (t - start_t) / transition_duration
                            # Ease out cubic
                            progress = 1 - (1 - progress) ** 3
                            x_pos = self.width + 100 + (self.width / 2 - screenshot.w / 2 - (self.width + 100)) * progress
                            return (x_pos, y_position)
                        else:
                            return ("center", y_position)
                    return slide_pos

                screenshot = screenshot.with_position(make_slide_position(start_time, y_pos))
                screenshot = screenshot.with_start(start_time)
                screenshot = screenshot.with_duration(duration_per_screenshot)

                all_clips.append(screenshot)

        # Composite all clips
        final_video = CompositeVideoClip(all_clips)
        return final_video

    def _add_screenshot_overlay(
        self,
        video: VideoFileClip,
        screenshot_path: str,
        position: str = "center",
        animate: bool = True
    ) -> CompositeVideoClip:
        """Add Reddit screenshot overlay to video.

        Args:
            video: Base video clip
            screenshot_path: Path to screenshot PNG
            position: Vertical position (top, center, bottom)
            animate: Whether to apply animation effect

        Returns:
            Video with screenshot overlay
        """
        # Load screenshot as image clip
        screenshot = ImageClip(screenshot_path)

        # Scale screenshot to fit video width (with padding)
        max_width = self.width - 80  # 40px padding on each side
        if screenshot.w > max_width:
            scale_factor = max_width / screenshot.w
            screenshot = screenshot.resized(scale_factor)

        # Also limit height to 70% of video height
        max_height = self.height * 0.7
        if screenshot.h > max_height:
            scale_factor = max_height / screenshot.h
            screenshot = screenshot.resized(scale_factor)

        # Set duration to match video
        screenshot = screenshot.with_duration(video.duration)

        # Position screenshot
        if position == "top":
            y_pos = 100  # 100px from top
        elif position == "bottom":
            y_pos = self.height - screenshot.h - 100  # 100px from bottom
        else:  # center
            y_pos = (self.height - screenshot.h) / 2

        screenshot = screenshot.with_position(("center", y_pos))

        # Apply animation if enabled
        if animate:
            screenshot = self._apply_screenshot_animation(
                screenshot,
                animation_type="fade_in",
                duration=0.5
            )

        # Composite video with screenshot
        final_video = CompositeVideoClip([video, screenshot])

        return final_video

    def _get_random_background(self) -> str:
        """Get random background video from backgrounds directory.

        Returns:
            Path to background video

        Raises:
            FileNotFoundError: If no backgrounds found
        """
        background_files = list(BACKGROUNDS_DIR.glob("*.mp4")) + \
                          list(BACKGROUNDS_DIR.glob("*.mov"))

        if not background_files:
            raise FileNotFoundError(
                f"No background videos found in {BACKGROUNDS_DIR}\n"
                "Please add some MP4 or MOV files to assets/backgrounds/"
            )

        return str(random.choice(background_files))


# CLI testing
if __name__ == "__main__":
    import sys
    from src.generation.tts_generator import TTSGenerator
    from src.generation.subtitle_generator import SubtitleGenerator

    print("=== ContentBot Video Composer Test ===\n")

    # Check for backgrounds
    backgrounds = list(BACKGROUNDS_DIR.glob("*.mp4"))
    if not backgrounds:
        print("[ERROR] No background videos found!")
        print(f"[INFO] Please add MP4 videos to: {BACKGROUNDS_DIR}")
        print("\nYou can:")
        print("- Record Minecraft parkour gameplay")
        print("- Download copyright-free gameplay from YouTube")
        print("- Use Subway Surfers, GTA, or other gameplay")
        print("\nMake sure videos are vertical (9:16) or they'll be auto-cropped")
        sys.exit(1)

    print(f"[OK] Found {len(backgrounds)} background video(s)")

    # Create test audio
    print("\n[TTS] Generating test voiceover...")
    test_text = "Bro you're not gonna believe what just happened. I'm at Starbucks and this dude walks in wearing a full dinosaur costume. The barista doesn't even blink. I'm losing it."

    tts = TTSGenerator()
    audio_path = tts.generate_audio(test_text, output_path="output/test_tts.mp3")
    audio_duration = tts.get_audio_duration(audio_path)

    print(f"[OK] Audio generated: {audio_duration:.1f}s")

    # Generate subtitles
    print("\n[SUBTITLES] Generating subtitles...")
    sub_gen = SubtitleGenerator(words_per_chunk=3)
    subtitles = sub_gen.generate_subtitles(test_text, audio_duration)

    print(f"[OK] Generated {len(subtitles)} subtitle chunks")

    # Create video
    print("\n[VIDEO] Composing video...")
    composer = VideoComposer()

    try:
        video_path = composer.create_video(
            audio_path=audio_path,
            subtitles=subtitles,
            output_path="output/pending_review/test_video.mp4"
        )

        print("\n" + "=" * 60)
        print("[SUCCESS] VIDEO CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"[INFO] Location: {video_path}")
        print(f"[INFO] Duration: {audio_duration:.1f}s")
        print(f"[INFO] Format: {VIDEO_WIDTH}x{VIDEO_HEIGHT} (9:16)")
        print("\n[INFO] Open the video to preview!")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
