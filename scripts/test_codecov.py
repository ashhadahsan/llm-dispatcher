#!/usr/bin/env python3
"""
Test script to verify Codecov setup and generate a test coverage report.
"""

import subprocess
import sys
import re
from pathlib import Path


def test_codecov_setup():
    """Test Codecov setup by running coverage and checking output."""
    print("🧪 Testing Codecov setup...")

    try:
        # Run pytest with coverage
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "--cov=src/llm_dispatcher",
                "--cov-report=xml",
                "--cov-report=term-missing",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Check if coverage.xml exists (even if tests fail, coverage can still be generated)
        coverage_xml = Path(__file__).parent.parent / "coverage.xml"
        if coverage_xml.exists():
            print("✅ coverage.xml file created")
            print(f"📊 File size: {coverage_xml.stat().st_size} bytes")
            coverage_success = True
        else:
            print("❌ coverage.xml file not found")
            coverage_success = False
            
        # Check if htmlcov directory exists
        htmlcov_dir = Path(__file__).parent.parent / "htmlcov"
        if htmlcov_dir.exists():
            print("✅ HTML coverage report generated")
        else:
            print("❌ HTML coverage report not found")
            coverage_success = False
            
        # Extract coverage percentage from output (even if tests fail)
        output = result.stdout + result.stderr
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        
        if coverage_match:
            coverage_percentage = int(coverage_match.group(1))
            print(f"📊 Coverage percentage: {coverage_percentage}%")
        else:
            print("⚠️  Could not extract coverage percentage from output")
            
        return coverage_success

    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return False


def check_codecov_config():
    """Check if Codecov configuration files exist."""
    print("\n🔧 Checking Codecov configuration...")

    config_files = ["codecov.yml", ".coveragerc", ".github/workflows/coverage.yml"]

    all_exist = True
    for config_file in config_files:
        file_path = Path(__file__).parent.parent / config_file
        if file_path.exists():
            print(f"✅ {config_file} exists")
        else:
            print(f"❌ {config_file} missing")
            all_exist = False

    return all_exist


def main():
    """Main test function."""
    print("🚀 Codecov Setup Test\n")

    # Check configuration files
    config_ok = check_codecov_config()

    # Test coverage generation
    coverage_ok = test_codecov_setup()

    print("\n📋 Summary:")
    print(f"Configuration files: {'✅ OK' if config_ok else '❌ Missing'}")
    print(f"Coverage generation: {'✅ OK' if coverage_ok else '❌ Failed'}")

    if config_ok and coverage_ok:
        print("\n🎉 Codecov setup is ready!")
        print("\nNext steps:")
        print("1. Push your changes to GitHub")
        print("2. Check the Actions tab for coverage workflow")
        print("3. Visit https://codecov.io/gh/ashhadahsan/llm-dispatcher")
        return True
    else:
        print("\n❌ Codecov setup needs attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
