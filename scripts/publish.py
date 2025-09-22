#!/usr/bin/env python3
"""
Script to build and publish LLM-Dispatcher to PyPI.

This script automates the process of building and publishing the package
to PyPI, including version checking, building, and uploading.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    return result


def check_git_status():
    """Check if git working directory is clean."""
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("Error: Git working directory is not clean.")
        print("Please commit or stash your changes before publishing.")
        sys.exit(1)


def check_version():
    """Check if version is properly updated."""
    # Read version from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    with open(pyproject_path) as f:
        content = f.read()

    # Extract version
    for line in content.split("\n"):
        if line.strip().startswith("version = "):
            version = line.split('"')[1]
            break
    else:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)

    print(f"Current version: {version}")
    return version


def build_package():
    """Build the package."""
    print("Building package...")

    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info/", check=False)

    # Build package
    run_command("python -m build")

    print("Package built successfully!")


def upload_to_pypi(test=False):
    """Upload package to PyPI."""
    if test:
        print("Uploading to TestPyPI...")
        run_command("python -m twine upload --repository testpypi dist/*")
    else:
        print("Uploading to PyPI...")
        run_command("python -m twine upload dist/*")


def main():
    parser = argparse.ArgumentParser(
        description="Build and publish LLM-Dispatcher to PyPI"
    )
    parser.add_argument(
        "--test", action="store_true", help="Upload to TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--skip-checks", action="store_true", help="Skip git status and version checks"
    )
    parser.add_argument(
        "--build-only", action="store_true", help="Only build, don't upload"
    )

    args = parser.parse_args()

    print("LLM-Dispatcher PyPI Publisher")
    print("=" * 40)

    # Check prerequisites
    if not args.skip_checks:
        print("Checking prerequisites...")
        check_git_status()
        version = check_version()

        # Confirm version
        confirm = input(f"Publish version {version}? (y/N): ")
        if confirm.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    # Build package
    build_package()

    # Upload to PyPI
    if not args.build_only:
        if args.test:
            print("Uploading to TestPyPI...")
            print("You can test the package with:")
            print(
                f"pip install --index-url https://test.pypi.org/simple/ llm-dispatcher"
            )
        else:
            print("Uploading to PyPI...")
            print("This will make the package available to everyone!")

        confirm = input("Continue with upload? (y/N): ")
        if confirm.lower() == "y":
            upload_to_pypi(test=args.test)
            print("Upload completed successfully!")
        else:
            print("Upload cancelled.")
    else:
        print("Build completed. Package is ready in dist/")

    print("Done!")


if __name__ == "__main__":
    main()
