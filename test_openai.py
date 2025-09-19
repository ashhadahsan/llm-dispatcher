#!/usr/bin/env python3
"""
Simple test runner for OpenAI provider tests.

This script runs the OpenAI provider tests and provides a quick way
to verify that the OpenAI integration is working correctly.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_openai_tests():
    """Run OpenAI provider tests."""
    print("🧪 Running OpenAI Provider Tests")
    print("=" * 50)
    
    # Test files to run
    test_files = [
        "tests/test_environment.py",
        "tests/test_basic.py::TestOpenAIProviderBasics",
        "tests/test_openai_provider.py",
        "tests/test_openai_examples.py"
    ]
    
    # Base pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--disable-warnings",  # Disable warnings for cleaner output
    ]
    
    # Add test files
    cmd.extend(test_files)
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print("\n✅ All OpenAI tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    return result.returncode

def run_quick_openai_test():
    """Run a quick test to verify OpenAI provider can be imported and initialized."""
    print("🔍 Quick OpenAI Provider Test")
    print("=" * 30)
    
    try:
        # Test imports
        print("Testing imports...")
        from llm_dispatcher.providers.openai_provider import OpenAIProvider
        from llm_dispatcher.core.base import TaskRequest, TaskType
        print("✅ Imports successful")
        
        # Test initialization
        print("Testing provider initialization...")
        provider = OpenAIProvider(api_key="test_key")
        print("✅ Provider initialization successful")
        
        # Test models
        print("Testing model availability...")
        expected_models = ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        for model in expected_models:
            if model in provider.models:
                print(f"✅ {model} available")
            else:
                print(f"❌ {model} not found")
        
        # Test task request creation
        print("Testing task request creation...")
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )
        print("✅ Task request creation successful")
        
        # Test model selection
        print("Testing model selection...")
        code_models = provider.get_models_for_task(TaskType.CODE_GENERATION)
        vision_models = provider.get_models_for_task(TaskType.VISION_ANALYSIS)
        print(f"✅ Code models: {len(code_models)}")
        print(f"✅ Vision models: {len(vision_models)}")
        
        # Test cost estimation
        print("Testing cost estimation...")
        cost = provider.estimate_cost("gpt-4", 1000, 500)
        print(f"✅ Cost estimation: ${cost:.4f}")
        
        print("\n🎉 Quick test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Quick test failed: {e}")
        return 1

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        return run_quick_openai_test()
    else:
        return run_openai_tests()

if __name__ == "__main__":
    sys.exit(main())
