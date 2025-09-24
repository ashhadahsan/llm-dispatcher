#!/usr/bin/env python3
"""
Script to update coverage badge in README.md with current test coverage.

This script runs pytest with coverage and updates the coverage badge
in the README.md file with the current coverage percentage.
"""

import subprocess
import re
import sys
from pathlib import Path


def get_coverage_percentage():
    """Run pytest with coverage and extract the percentage."""
    try:
        # Run pytest with coverage
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "--cov=src/llm_dispatcher",
                "--cov-report=term-missing",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Extract coverage percentage from output
        output = result.stdout + result.stderr
        coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)

        if coverage_match:
            return int(coverage_match.group(1))
        else:
            print("Could not find coverage percentage in output:")
            print(output)
            return None

    except Exception as e:
        print(f"Error running coverage: {e}")
        return None


def update_readme_badge(coverage_percentage):
    """Update the coverage badge in README.md."""
    readme_path = Path(__file__).parent.parent / "README.md"

    if not readme_path.exists():
        print("README.md not found!")
        return False

    # Read current README
    with open(readme_path, "r") as f:
        content = f.read()

    # Determine badge color based on coverage
    if coverage_percentage >= 90:
        color = "brightgreen"
    elif coverage_percentage >= 80:
        color = "green"
    elif coverage_percentage >= 70:
        color = "yellowgreen"
    elif coverage_percentage >= 60:
        color = "yellow"
    elif coverage_percentage >= 50:
        color = "orange"
    else:
        color = "red"

    # Create new badge
    new_badge = f"[![Coverage](https://img.shields.io/badge/coverage-{coverage_percentage}%25-{color}.svg)](https://github.com/ashhadahsan/llm-dispatcher)"

    # Replace the coverage badge
    pattern = r"\[!\[Coverage\]\(https://img\.shields\.io/badge/coverage-\d+%25-\w+\.svg\)\]\(https://github\.com/ashhadahsan/llm-dispatcher\)"
    replacement = new_badge

    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)

        # Write updated README
        with open(readme_path, "w") as f:
            f.write(content)

        print(f"Updated coverage badge to {coverage_percentage}%")
        return True
    else:
        print("Could not find coverage badge pattern in README.md")
        return False


def main():
    """Main function."""
    print("Running test coverage...")
    coverage = get_coverage_percentage()

    if coverage is None:
        print("Failed to get coverage percentage")
        sys.exit(1)

    print(f"Current coverage: {coverage}%")

    if update_readme_badge(coverage):
        print("README.md updated successfully!")
    else:
        print("Failed to update README.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
