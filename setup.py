"""
Setup script for LLM-Dispatcher package.

This script provides easy setup and installation of the LLM-Dispatcher package
with all its dependencies and configuration.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def install_dependencies() -> bool:
    """Install package dependencies."""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -e .", "Installing LLM-Dispatcher package"),
        ("pip install -e .[dev]", "Installing development dependencies"),
    ]

    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def setup_pre_commit() -> bool:
    """Setup pre-commit hooks."""
    return run_command("pre-commit install", "Setting up pre-commit hooks")


def run_tests() -> bool:
    """Run the test suite."""
    return run_command("pytest tests/ -v", "Running tests")


def create_config_file() -> bool:
    """Create a default configuration file."""
    config_path = Path("~/.llm-dispatcher/config.yaml")
    config_path = config_path.expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        try:
            import shutil

            shutil.copy("examples/config.yaml", config_path)
            print(f"✅ Created default configuration at {config_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
            return False
    else:
        print(f"✅ Configuration file already exists at {config_path}")
        return True


def create_env_template() -> bool:
    """Create environment variables template."""
    env_path = Path(".env.template")

    env_content = """# LLM-Dispatcher Environment Variables Template
# Copy this file to .env and fill in your API keys

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API Key  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Google API Key
GOOGLE_API_KEY=your-google-api-key-here

# Optional: Custom configuration
LLM_DISPATCHER_CONFIG_PATH=~/.llm-dispatcher/config.yaml
LLM_DISPATCHER_LOG_LEVEL=INFO
LLM_DISPATCHER_DATA_DIR=~/.llm-dispatcher
"""

    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"✅ Created environment template at {env_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create env template: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up LLM-Dispatcher package...")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Setup pre-commit hooks
    setup_pre_commit()

    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but continuing setup...")

    # Create configuration files
    create_config_file()
    create_env_template()

    print("\n" + "=" * 50)
    print("🎉 LLM-Dispatcher setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env and add your API keys")
    print("2. Review the configuration at ~/.llm-dispatcher/config.yaml")
    print("3. Try running the example: python examples/basic_usage.py")
    print("\n📚 Documentation:")
    print("- README.md: Basic usage and examples")
    print("- examples/: More usage examples")
    print("- tests/: Test suite and examples")
    print("\n🔧 Development:")
    print("- Run tests: pytest tests/")
    print("- Format code: black src/ tests/")
    print("- Type check: mypy src/")
    print("\nHappy coding with LLM-Dispatcher! 🚀")


if __name__ == "__main__":
    main()
