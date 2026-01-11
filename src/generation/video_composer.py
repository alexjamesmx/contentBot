"""Video composition - combine background, audio, and subtitles."""
import random
import tempfile
import os
import re
from pathlib import Path
from typing import Optional, List, Tuple, Callable

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)

from src.utils.config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    BACKGROUNDS_DIR,
    PENDING_DIR,
    FONTS_DIR,
    REUSE_EXISTING_FILES
)


class ProgressLogger:
    """Custom logger to track MoviePy rendering progress.

    Wraps proglog.ProgressBarLogger to ensure full compatibility.
    """

    def __init__(self, duration: float, progress_callback: Optional[Callable] = None):
        from proglog import ProgressBarLogger
        self.proglog_logger = ProgressBarLogger()
        self.duration = duration
        self.progress_callback = progress_callback
        self.last_progress = 0

    def __call__(self, *args, **kwargs):
        """Make logger callable - delegate to proglog logger."""
        return self.proglog_logger(*args, **kwargs)

    def __getattr__(self, name):
        """Delegate all unknown methods to proglog logger."""
        return getattr(self.proglog_logger, name)

    def bars_callback(self, bar, attr, value, old_value=None):
        """Override to track progress."""
        if self.progress_callback and attr == 'index':
            # Calculate progress based on frame index
            if hasattr(bar, 'total') and bar.total:
                progress = int((value / bar.total) * 100)
                if progress != self.last_progress:
                    self.last_progress = progress
                    self.progress_callback(progress, f"Rendering frame {value}/{bar.total}")

        # Call parent implementation
        return self.proglog_logger.bars_callback(bar, attr, value, old_value)


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
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Create final video with all components.

        Args:
            audio_path: Path to audio file
            background_video: Path to background video (random if None)
            subtitles: List of (start, end, text) tuples
            output_path: Output path (auto-generated if None)
            story_metadata: Optional story info for filename
            genre: Video genre for font/styling
            progress_callback: Optional callback for progress updates

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

        # Add text subtitles if provided
        if subtitles:
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

        # Use truly unique temp audio file to prevent Windows file locking issues
        # Create temp file in system temp directory with unique name
        temp_fd, temp_audio = tempfile.mkstemp(suffix='.m4a', prefix='contentbot_')
        os.close(temp_fd)  # Close file descriptor, MoviePy will handle the file

        # Create progress logger if callback provided
        logger = ProgressLogger(audio_duration, progress_callback) if progress_callback else 'bar'

        try:
            video_with_subtitles.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                audio_bitrate='192k',
                temp_audiofile=temp_audio,
                remove_temp=True,
                logger=logger,
                preset='slow',
                bitrate='8000k',
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',
                    '-profile:v', 'high',
                    '-level', '4.2',
                    '-crf', '18',
                    '-movflags', '+faststart'
                ]
            )
        finally:
            # Ensure temp file is cleaned up even if there's an error
            if os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass  # Ignore cleanup errors

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
            clip = clip.subclipped(0, target_duration)
        elif clip.duration > target_duration:
            # Randomly cut from the middle to keep interesting parts
            max_start = clip.duration - target_duration
            if max_start > 0:
                random_start = random.random() * max_start
                clip = clip.subclipped(random_start, random_start + target_duration)
            else:
                clip = clip.subclipped(0, target_duration)
        else:
            # Exact match, no modification needed
            pass

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

        # Safe zone positioning (based on 2025 TikTok/Shorts standards)
        # Bottom 420px reserved for UI elements
        safe_bottom_margin = 420

        for i, (start, end, text) in enumerate(subtitles):
            # Create text clip using PIL directly to avoid MoviePy stroke cropping bug
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np

            # Font setup
            pil_font = ImageFont.truetype(font_path, size=72)

            # Measure text with stroke padding
            stroke_w = 4
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), text.upper(), font=pil_font, stroke_width=stroke_w)
            text_width = bbox[2] - bbox[0] + stroke_w * 2
            text_height = bbox[3] - bbox[1] + stroke_w * 2

            # Create image with padding
            img_width = min(text_width + 20, self.width - 100)
            img_height = text_height + 20

            # Render text
            img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Center text in image
            x = (img_width - text_width) // 2 + stroke_w
            y = (img_height - text_height) // 2 + stroke_w

            # Draw text with stroke
            text_col = (255, 255, 0) if text_color == 'yellow' else (255, 255, 255)
            draw.text((x, y), text.upper(), font=pil_font, fill=text_col,
                     stroke_width=stroke_w, stroke_fill=(0, 0, 0))

            # Convert to MoviePy clip
            from moviepy import ImageClip
            txt_clip = ImageClip(np.array(img))

            # CRITICAL: Get actual text height BEFORE positioning
            text_height = txt_clip.h if txt_clip.h else 100

            # SIMPLER APPROACH: Use tuple positioning (center, bottom) with negative offset
            # This positions from the bottom edge instead of top
            # Format: ('center', height - offset) where offset is how far from bottom
            y_from_bottom = -safe_bottom_margin  # Negative = from bottom

            # Alternative: Calculate exact pixel position to ensure no cutoff
            # Add extra 50px padding just to be absolutely sure
            y_position = self.height - safe_bottom_margin - text_height - 50

            print(f"[SUBTITLE {i+1}] Text: '{text[:40]}'")
            print(f"  Text height: {text_height}px")
            print(f"  Y-position (from top): {y_position}px")
            print(f"  Expected bottom edge: {y_position + text_height}px")
            print(f"  Distance from bottom: {self.height - (y_position + text_height)}px")
            print(f"  Safe? {'YES' if (self.height - (y_position + text_height)) >= safe_bottom_margin else 'NO - TOO LOW!'}")

            txt_clip = txt_clip.with_position(('center', y_position))
            txt_clip = txt_clip.with_start(start)
            txt_clip = txt_clip.with_duration(end - start)

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
