"""Extensive debugging for subtitle positioning issue."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from moviepy import TextClip
from pathlib import Path

# Test parameters matching production
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FONT_SIZE = 72
TEXT_WIDTH = VIDEO_WIDTH - 200  # 880px
SAFE_BOTTOM_MARGIN = 420

# Find font
fonts_dir = Path('assets/fonts')
font_path = None
for font_name in ['Montserrat-Black.ttf', 'Impact.ttf']:
    test_path = fonts_dir / font_name
    if test_path.exists():
        font_path = str(test_path)
        break

if not font_path:
    # Try system font
    import platform
    if platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/impact.ttf'

print("=== SUBTITLE POSITIONING DEBUG ===\n")
print(f"Video dimensions: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
print(f"Font: {font_path}")
print(f"Font size: {FONT_SIZE}px")
print(f"Text width: {TEXT_WIDTH}px")
print(f"Safe bottom margin: {SAFE_BOTTOM_MARGIN}px")
print("\n" + "="*60 + "\n")

# Test different text samples
test_texts = [
    "Y'ALL TO",
    "Y'ALL TRYING TO",
    "Y'ALL TRYING TO TELL ME",
    "THIS IS A SHORT TEST",
    "THIS IS A MUCH LONGER TEST WITH MORE WORDS",
]

for i, text in enumerate(test_texts, 1):
    print(f"TEST {i}: '{text}'")
    print(f"Length: {len(text)} characters")

    # Create TextClip with EXACT production settings
    try:
        txt_clip = TextClip(
            text=text.upper(),
            font=font_path,
            font_size=FONT_SIZE,
            color='yellow',
            stroke_color='black',
            stroke_width=4,
            size=(TEXT_WIDTH, None),
            method='caption',
            text_align='center',
            horizontal_align='center',
            vertical_align='bottom'
        )

        # Get actual rendered dimensions
        clip_width = txt_clip.w
        clip_height = txt_clip.h

        # Calculate position (matching production code)
        text_height = clip_height if clip_height else 100
        y_position = max(
            VIDEO_HEIGHT - SAFE_BOTTOM_MARGIN - text_height,
            VIDEO_HEIGHT * 0.6
        )

        # Calculate where text actually ends
        text_bottom = y_position + text_height
        distance_from_bottom = VIDEO_HEIGHT - text_bottom

        print(f"  Rendered dimensions: {clip_width}w x {clip_height}h")
        print(f"  Y-position (from top): {y_position}px")
        print(f"  Text bottom edge: {text_bottom}px")
        print(f"  Distance from video bottom: {distance_from_bottom}px")
        print(f"  Is text cut off? {distance_from_bottom < SAFE_BOTTOM_MARGIN}")
        print(f"  Safe zone margin maintained? {'✓ YES' if distance_from_bottom >= SAFE_BOTTOM_MARGIN else '✗ NO - CUT OFF'}")

        # Check if text wraps to multiple lines
        estimated_chars_per_line = TEXT_WIDTH / (FONT_SIZE * 0.6)  # Rough estimate
        estimated_lines = max(1, len(text) / estimated_chars_per_line)
        print(f"  Estimated lines: {estimated_lines:.1f}")
        print(f"  Actual height suggests: {clip_height / FONT_SIZE:.1f} lines")

        txt_clip.close()

    except Exception as e:
        print(f"  ERROR: {e}")

    print()

print("="*60)
print("\nKEY FINDINGS:")
print("1. If 'Distance from video bottom' < 420px, text IS cut off")
print("2. If height > font_size * 1.5, text wrapped to multiple lines")
print("3. MoviePy 'caption' mode adds extra padding/spacing")
print("\nRECOMMENDATIONS:")
print("- If text is multi-line, need LARGER bottom margin")
print("- Current calculation: y = height - margin - text_height")
print("- Problem: text_height might be WRONG or margin too small")
print("- Solution: Increase margin OR change positioning method")
