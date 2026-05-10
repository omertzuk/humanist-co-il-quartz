#!/usr/bin/env python3
"""
WordPress to Quartz conversion pipeline.
Runs extract_authors, extract_posts, and extract_specific_page in sequence.

Usage:
  python3 run_conversion.py              # Run full pipeline
  python3 run_conversion.py --only authors   # Run only authors extraction
  python3 run_conversion.py --only posts     # Run only posts extraction
  python3 run_conversion.py --only pages     # Run only pages extraction
  python3 run_conversion.py --clean          # Delete existing output before running
  python3 run_conversion.py --dry-run        # Parse and validate without writing files
"""

import sys
import os
import time
import shutil
from pathlib import Path
import argparse

# Resolve project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Add script directory to Python path for imports
sys.path.insert(0, str(SCRIPT_DIR))

# Change to project root so all relative paths work correctly
os.chdir(PROJECT_ROOT)

# Import extraction modules
import extract_authors
import extract_posts
import extract_specific_page


class StepResult:
    """Holds the result of a conversion step."""
    def __init__(self, name, status="pending", files_written=0, elapsed_time=0.0, error=None):
        self.name = name
        self.status = status  # "success", "failed", "skipped"
        self.files_written = files_written
        self.elapsed_time = elapsed_time
        self.error = error


def clean_output_directories():
    """Delete output directories before running conversion."""
    dirs_to_clean = [
        PROJECT_ROOT / "content" / "מאמרים",
        PROJECT_ROOT / "content" / "כותבים",
        PROJECT_ROOT / "content" / "עמודים",
    ]

    print("Cleaning output directories...")
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ Deleted {dir_path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  · Skipped {dir_path.relative_to(PROJECT_ROOT)} (does not exist)")
    print()


def run_step(step_name, step_func, step_number, total_steps, dry_run=False):
    """
    Run a single conversion step with timing and error handling.

    Args:
        step_name: Human-readable name for the step
        step_func: Function to call (should return count of files written)
        step_number: Current step number (1-indexed)
        total_steps: Total number of steps
        dry_run: If True, skip actual file writing (not implemented in extraction scripts)

    Returns:
        StepResult object
    """
    print(f"→ Step {step_number}/{total_steps}: {step_name}...")
    print()

    start_time = time.time()

    try:
        # Call the extraction function
        files_written = step_func()

        if files_written is None:
            files_written = 0

        elapsed = time.time() - start_time

        print()
        print(f"✓ {step_name} completed: {files_written} files written in {elapsed:.1f}s")
        print()

        return StepResult(
            name=step_name,
            status="success",
            files_written=files_written,
            elapsed_time=elapsed
        )

    except Exception as e:
        elapsed = time.time() - start_time

        print()
        print(f"✗ {step_name} failed after {elapsed:.1f}s")
        print(f"  Error: {e}")
        print()

        return StepResult(
            name=step_name,
            status="failed",
            files_written=0,
            elapsed_time=elapsed,
            error=str(e)
        )


def print_summary_table(results, total_time):
    """Print a summary table of all conversion steps."""
    # Calculate column widths
    max_name_width = max(len(r.name) for r in results)
    name_width = max(max_name_width, len("Step")) + 2

    # Print table header
    print("=" * 70)
    print(f"{'Step':<{name_width}} | {'Status':<8} | {'Files':<8} | {'Time':<8}")
    print("-" * 70)

    # Print each step
    for result in results:
        status_icon = "✓" if result.status == "success" else "✗" if result.status == "failed" else "·"
        status_str = f"{status_icon} {result.status}"
        files_str = str(result.files_written) if result.status == "success" else "-"
        time_str = f"{result.elapsed_time:.1f}s"

        print(f"{result.name:<{name_width}} | {status_str:<8} | {files_str:<8} | {time_str:<8}")

    # Print totals
    print("-" * 70)
    total_files = sum(r.files_written for r in results if r.status == "success")
    print(f"{'Total':<{name_width}} | {'':<8} | {total_files:<8} | {total_time:.1f}s")
    print("=" * 70)

    # Print any errors
    errors = [r for r in results if r.status == "failed"]
    if errors:
        print()
        print("Errors encountered:")
        for error_result in errors:
            print(f"  • {error_result.name}: {error_result.error}")


def main():
    parser = argparse.ArgumentParser(
        description="WordPress to Quartz conversion pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_conversion.py              # Run full pipeline
  python3 run_conversion.py --only authors   # Run only authors extraction
  python3 run_conversion.py --clean          # Clean output before running
  python3 run_conversion.py --dry-run        # Validate without writing (not fully implemented)
        """
    )

    parser.add_argument(
        '--only',
        choices=['authors', 'posts', 'pages'],
        help='Run only the specified extraction step'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Delete existing output directories before running'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse and validate without writing files (not fully implemented)'
    )

    args = parser.parse_args()

    # Print header
    print()
    print("=" * 70)
    print("WordPress to Quartz Conversion Pipeline")
    print("=" * 70)
    print()
    print(f"Project root: {PROJECT_ROOT}")
    print()

    # Clean output directories if requested
    if args.clean:
        clean_output_directories()

    if args.dry_run:
        print("⚠ Dry-run mode: validation only (file writing not fully disabled in extraction scripts)")
        print()

    # Define conversion steps
    steps = []

    if args.only is None or args.only == 'authors':
        steps.append(('extract_authors', extract_authors.main))

    if args.only is None or args.only == 'posts':
        steps.append(('extract_posts', extract_posts.main))

    if args.only is None or args.only == 'pages':
        steps.append(('extract_pages', lambda: extract_specific_page.main(page_title=None)))

    # Run pipeline
    results = []
    pipeline_start = time.time()

    for i, (step_name, step_func) in enumerate(steps, 1):
        result = run_step(step_name, step_func, i, len(steps), dry_run=args.dry_run)
        results.append(result)

    pipeline_elapsed = time.time() - pipeline_start

    # Print summary
    print()
    print_summary_table(results, pipeline_elapsed)
    print()

    # Exit with error code if any step failed
    failed_count = sum(1 for r in results if r.status == "failed")
    if failed_count > 0:
        print(f"⚠ Pipeline completed with {failed_count} error(s)")
        sys.exit(1)
    else:
        print("✓ Pipeline completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
