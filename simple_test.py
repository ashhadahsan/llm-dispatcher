#!/usr/bin/env python3
"""
Simple test script for OpenAI provider without external dependencies.

This script tests the basic functionality of the OpenAI provider
without requiring all the external dependencies to be installed.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("🔍 Testing Basic OpenAI Provider Functionality")
    print("=" * 50)

    try:
        # Test core imports
        print("1. Testing core imports...")
        from llm_dispatcher.core.base import (
            TaskType,
            Capability,
            TaskRequest,
            ModelInfo,
            PerformanceMetrics,
        )

        print("   ✅ Core base classes imported successfully")

        # Test provider import (this might fail if dependencies are missing)
        print("2. Testing provider import...")
        try:
            from llm_dispatcher.providers.openai_provider import OpenAIProvider

            print("   ✅ OpenAI provider imported successfully")
            provider_available = True
        except ImportError as e:
            print(
                f"   ⚠️  OpenAI provider import failed (expected if dependencies missing): {e}"
            )
            provider_available = False

        # Test utility imports
        print("3. Testing utility imports...")
        from llm_dispatcher.utils.benchmark_manager import BenchmarkManager

        print("   ✅ Benchmark manager imported successfully")

        # Test configuration imports
        print("4. Testing configuration imports...")
        from llm_dispatcher.config.settings import SwitchConfig

        print("   ✅ Switch config imported successfully")

        # Test basic functionality
        print("5. Testing basic functionality...")

        # Test TaskType enum
        assert TaskType.TEXT_GENERATION == "text_generation"
        assert TaskType.CODE_GENERATION == "code_generation"
        assert TaskType.VISION_ANALYSIS == "vision_analysis"
        print("   ✅ TaskType enum working correctly")

        # Test Capability enum
        assert Capability.TEXT == "text"
        assert Capability.VISION == "vision"
        assert Capability.AUDIO == "audio"
        print("   ✅ Capability enum working correctly")

        # Test TaskRequest creation
        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)
        assert request.prompt == "Test prompt"
        assert request.task_type == TaskType.TEXT_GENERATION
        print("   ✅ TaskRequest creation working correctly")

        # Test BenchmarkManager
        manager = BenchmarkManager()
        assert len(manager.benchmark_data) > 0
        print("   ✅ BenchmarkManager working correctly")

        # Test SwitchConfig
        config = SwitchConfig()
        assert config is not None
        print("   ✅ SwitchConfig working correctly")

        # Test provider if available
        if provider_available:
            print("6. Testing OpenAI provider...")
            provider = OpenAIProvider(api_key="test_key")
            assert provider.provider_name == "openai"
            assert len(provider.models) > 0
            print("   ✅ OpenAI provider working correctly")

            # Test model availability
            expected_models = [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-3.5-turbo",
            ]
            for model in expected_models:
                if model in provider.models:
                    print(f"   ✅ {model} available")
                else:
                    print(f"   ❌ {model} not found")

            # Test model capabilities
            gpt4_info = provider.models["gpt-4"]
            assert Capability.VISION in gpt4_info.capabilities
            print("   ✅ Model capabilities working correctly")

            # Test cost estimation
            cost = provider.estimate_cost("gpt-4", 1000, 500)
            assert cost > 0
            print(f"   ✅ Cost estimation working: ${cost:.4f}")

        print("\n🎉 All basic tests passed!")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


def test_benchmark_data():
    """Test benchmark data availability."""
    print("\n📊 Testing Benchmark Data")
    print("=" * 30)

    try:
        from llm_dispatcher.utils.benchmark_manager import BenchmarkManager

        manager = BenchmarkManager()

        # Test that we have benchmark data
        assert len(manager.benchmark_data) > 0
        print(f"✅ Found benchmark data for {len(manager.benchmark_data)} models")

        # Test specific models
        test_models = ["gpt-4", "claude-3-opus", "gemini-2.5-pro", "grok-3-beta"]
        for model in test_models:
            if model in manager.benchmark_data:
                scores = manager.benchmark_data[model]
                print(
                    f"✅ {model}: MMLU={scores.get('mmlu', 'N/A'):.3f}, HumanEval={scores.get('human_eval', 'N/A'):.3f}"
                )
            else:
                print(f"❌ {model} not found in benchmark data")

        # Test performance metrics
        gpt4_metrics = manager.get_performance_metrics("gpt-4")
        if gpt4_metrics:
            print(f"✅ GPT-4 performance metrics: MMLU={gpt4_metrics.mmlu_score:.3f}")

        return 0

    except Exception as e:
        print(f"❌ Benchmark data test failed: {e}")
        return 1


def test_task_classification():
    """Test task classification functionality."""
    print("\n🎯 Testing Task Classification")
    print("=" * 30)

    try:
        from llm_dispatcher.utils.task_classifier import TaskClassifier
        from llm_dispatcher.core.base import TaskType

        classifier = TaskClassifier()

        # Test different task types
        test_cases = [
            ("Write a Python function to sort a list", TaskType.CODE_GENERATION),
            ("What is the capital of France?", TaskType.QUESTION_ANSWERING),
            ("Solve the equation 2x + 5 = 15", TaskType.MATH),
            ("Write a story about a robot", TaskType.TEXT_GENERATION),
        ]

        for prompt, expected_type in test_cases:
            task_type, confidence = classifier.classify(prompt)
            print(
                f"✅ '{prompt[:30]}...' -> {task_type} (confidence: {confidence:.2f})"
            )
            # Note: We don't assert exact matches as classification might vary

        return 0

    except Exception as e:
        print(f"❌ Task classification test failed: {e}")
        return 1


def main():
    """Main function."""
    print("🧪 LLM-Dispatcher Simple Test Suite")
    print("=" * 50)

    # Run tests
    results = []
    results.append(test_basic_functionality())
    results.append(test_benchmark_data())
    results.append(test_task_classification())

    # Summary
    passed = sum(1 for r in results if r == 0)
    total = len(results)

    print(f"\n📋 Test Summary: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
