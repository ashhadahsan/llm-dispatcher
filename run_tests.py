#!/usr/bin/env python3
"""
Test runner script for LLM-Dispatcher package.

This script provides an easy way to run tests with different configurations
and options.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_tests(
    test_path=None,
    verbose=False,
    coverage=False,
    integration=False,
    provider=None,
    markers=None,
    parallel=False,
):
    """Run tests with specified options."""

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test path
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    # Add verbosity
    if verbose:
        cmd.append("-v")

    # Add coverage
    if coverage:
        cmd.extend(
            [
                "--cov=src/llm_dispatcher",
                "--cov-report=html",
                "--cov-report=term-missing",
            ]
        )

    # Add integration tests
    if integration:
        cmd.append("-m")
        cmd.append("integration")

    # Add provider-specific tests
    if provider:
        cmd.append("-m")
        cmd.append(provider)

    # Add custom markers
    if markers:
        cmd.append("-m")
        cmd.append(markers)

    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])

    # Add other useful options
    cmd.extend(
        [
            "--tb=short",  # Shorter traceback format
            "--strict-markers",  # Strict marker checking
            "--disable-warnings",  # Disable warnings for cleaner output
        ]
    )

    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)

    # Run the tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run LLM-Dispatcher tests")

    parser.add_argument(
        "test_path", nargs="?", help="Specific test file or directory to run"
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Run with coverage reporting"
    )

    parser.add_argument(
        "-i",
        "--integration",
        action="store_true",
        help="Run integration tests (requires real API keys)",
    )

    parser.add_argument(
        "-p",
        "--provider",
        choices=["openai", "anthropic", "google"],
        help="Run tests for specific provider",
    )

    parser.add_argument(
        "-m",
        "--markers",
        help="Run tests with specific markers (e.g., 'slow', 'not slow')",
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)",
    )

    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests (no integration tests)",
    )

    parser.add_argument(
        "--openai-only", action="store_true", help="Run only OpenAI tests"
    )

    args = parser.parse_args()

    # Handle special cases
    if args.unit_only:
        args.markers = "not integration"
    elif args.openai_only:
        args.provider = "openai"

    # Check for required dependencies
    if args.parallel:
        try:
            import pytest_xdist
        except ImportError:
            print("Error: pytest-xdist is required for parallel execution")
            print("Install it with: pip install pytest-xdist")
            return 1

    if args.coverage:
        try:
            import pytest_cov
        except ImportError:
            print("Error: pytest-cov is required for coverage reporting")
            print("Install it with: pip install pytest-cov")
            return 1

    # Run the tests
    return run_tests(
        test_path=args.test_path,
        verbose=args.verbose,
        coverage=args.coverage,
        integration=args.integration,
        provider=args.provider,
        markers=args.markers,
        parallel=args.parallel,
    )


if __name__ == "__main__":
    sys.exit(main())
