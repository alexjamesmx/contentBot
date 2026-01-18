"""Debug the actual MoviePy rendering issue."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from pathlib import Path
import numpy as np

print("=== DEBUGGING MOVIEPY RENDERING ISSUE ===\n")

# Video settings
WIDTH = 1080
HEIGHT = 1920

# Create background
background = ColorClip(size=(WIDTH, HEIGHT), color=(50, 50, 50), duration=3)

# Font
font_path = str(Path('assets/fonts/Montserrat-Black.ttf'))

# HYPOTHESIS: The issue might be with CompositeVideoClip size
# Let's test if the composite is somehow smaller than expected

print("Creating text clip...")
txt_clip = TextClip(
    text="TESTING SUBTITLE",
    font=font_path,
    font_size=72,
    color='yellow',
    stroke_color='black',
    stroke_width=4,
    size=(WIDTH - 200, None),
    method='caption',
    text_align='center'
)

print(f"Text clip size: {txt_clip.w}x{txt_clip.h}")
print(f"Background size: {background.w}x{background.h}")

# Position at 700px from bottom
y_pos = HEIGHT - 700
print(f"Y-position: {y_pos}px from top")

txt_clip = txt_clip.with_position(('center', y_pos))
txt_clip = txt_clip.with_duration(3)

# Create composite
print("\nCreating composite...")
final = CompositeVideoClip([background, txt_clip], size=(WIDTH, HEIGHT))

print(f"Final video size: {final.w}x{final.h}")

# CRITICAL: Check if final video has the right size
if final.h != HEIGHT:
    print(f"⚠️  WARNING: Final video height is {final.h}, not {HEIGHT}!")
    print("This might be why subtitles are cut off!")

# Get a frame and check actual dimensions
print("\nChecking actual frame dimensions...")
frame = final.get_frame(1.0)
print(f"Actual frame shape: {frame.shape}")  # (height, width, channels)

if frame.shape[0] != HEIGHT:
    print(f"⚠️  PROBLEM FOUND: Frame height is {frame.shape[0]}, not {HEIGHT}!")
    print("The video is being cropped or resized!")

# Export
output_path = Path('output/pending_review/debug_test.mp4')
print(f"\nExporting to {output_path}...")
final.write_videofile(str(output_path), fps=30, codec='libx264', audio=False)

print("\n✓ Done! Check debug_test.mp4")
print("\nDIAGNOSIS:")
if frame.shape[0] != HEIGHT:
    print("- The video is NOT 1920px tall as expected")
    print("- MoviePy might be auto-cropping or the composite size is wrong")
    print("- FIX: Need to explicitly set size in CompositeVideoClip")
else:
    print("- Video dimensions are correct")
    print("- The issue must be something else")

final.close()
txt_clip.close()
background.close()
