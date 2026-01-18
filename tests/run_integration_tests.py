#!/usr/bin/env python
"""Convenient test runner for ContentBot integration tests.

Usage:
    python tests/run_integration_tests.py              # Run all fast tests
    python tests/run_integration_tests.py --slow       # Include slow tests
    python tests/run_integration_tests.py --genre comedy # Test one genre
    python tests/run_integration_tests.py --help       # Show options
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd):
    """Run a command and return success status."""
    print(f"\n{'='*70}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Run ContentBot integration tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all fast tests (skip slow ones)
  python tests/run_integration_tests.py

  # Include slow tests (30-60s each)
  python tests/run_integration_tests.py --slow

  # Test specific genre
  python tests/run_integration_tests.py --genre comedy

  # Test specific test class
  python tests/run_integration_tests.py --class TestAllGenres

  # Full verbose output
  python tests/run_integration_tests.py -v

  # With timing information
  python tests/run_integration_tests.py --durations 10
        """
    )

    parser.add_argument(
        "--slow",
        action="store_true",
        help="Include slow tests (30-60s each)"
    )
    parser.add_argument(
        "--genre",
        type=str,
        help="Test specific genre (comedy, terror, aita, genz_chaos, relationship_drama)"
    )
    parser.add_argument(
        "--class",
        dest="test_class",
        type=str,
        help="Run specific test class (e.g., TestAllGenres)"
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Run specific test (e.g., test_comedy_story_full_pipeline_60_seconds)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--durations",
        type=int,
        help="Show N slowest tests"
    )
    parser.add_argument(
        "-s", "--show-output",
        action="store_true",
        help="Show print statements and logging"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run fastest tests only (non-slow)"
    )

    args = parser.parse_args()

    # Build pytest command
    cmd = ["pytest", "tests/integration/test_full_pipeline.py"]

    # Add markers
    if not args.slow and not args.genre and not args.test_class and not args.test:
        # Default: run all except slow tests
        cmd.extend(["-m", "not slow"])
    elif args.slow:
        cmd.extend(["-m", "slow"])
    elif args.quick:
        cmd.extend(["-m", "not slow"])

    # Add test selection
    if args.test:
        cmd.append(f"::{args.test}")
    elif args.test_class:
        cmd.append(f"::{args.test_class}")
    elif args.genre:
        cmd.append(
            f"::TestAllGenres::test_genre_produces_valid_video[{args.genre}]"
        )

    # Add output options
    if args.verbose or args.show_output:
        cmd.append("-v")
    if args.show_output:
        cmd.append("-s")
    if args.durations:
        cmd.extend([f"--durations={args.durations}"])

    # Run tests
    success = run_command(cmd)

    # Summary
    print(f"\n{'='*70}")
    if success:
        print("SUCCESS: All tests passed!")
    else:
        print("FAILURE: Some tests failed.")
        print("\nCommon issues:")
        print("  1. GROQ_API_KEY not set in .env")
        print("  2. No background videos in assets/backgrounds/")
        print("  3. Network timeout (Groq API slow)")
        print("\nSee tests/TESTING.md for detailed documentation")

    print(f"{'='*70}\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
