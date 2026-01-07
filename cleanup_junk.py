"""Cleanup junk/temporary files from output directory"""
from pathlib import Path

PENDING_DIR = Path("output/pending_review")

# Patterns to delete
JUNK_PATTERNS = [
    "temp_*",
    "NUL",
    "nul",
    "*.tmp",
    "*.temp",
    "*_temp.*"
]

def cleanup_junk():
    """Remove junk files from output directory"""
    removed = []

    for pattern in JUNK_PATTERNS:
        for file in PENDING_DIR.glob(pattern):
            if file.is_file():
                try:
                    file.unlink()
                    removed.append(file.name)
                except Exception as e:
                    print(f"Failed to remove {file.name}: {e}")

    if removed:
        print(f"Cleaned up {len(removed)} junk files:")
        for name in removed:
            print(f"  - {name}")
    else:
        print("No junk files found")

if __name__ == "__main__":
    cleanup_junk()
