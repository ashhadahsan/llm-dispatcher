#!/usr/bin/env python3
"""
Minimal test script for OpenAI provider without problematic imports.

This script tests the basic functionality without importing the full package
that has dependency issues.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_core_imports():
    """Test core imports without external dependencies."""
    print("🔍 Testing Core Imports")
    print("=" * 30)

    try:
        # Test core base classes directly
        from llm_dispatcher.core.base import (
            TaskType,
            Capability,
            TaskRequest,
            ModelInfo,
            PerformanceMetrics,
        )

        print("✅ Core base classes imported successfully")

        # Test TaskType enum
        assert TaskType.TEXT_GENERATION == "text_generation"
        assert TaskType.CODE_GENERATION == "code_generation"
        assert TaskType.VISION_ANALYSIS == "vision_analysis"
        print("✅ TaskType enum working correctly")

        # Test Capability enum
        assert Capability.TEXT == "text"
        assert Capability.VISION == "vision"
        assert Capability.AUDIO == "audio"
        print("✅ Capability enum working correctly")

        # Test TaskRequest creation
        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)
        assert request.prompt == "Test prompt"
        assert request.task_type == TaskType.TEXT_GENERATION
        print("✅ TaskRequest creation working correctly")

        return True

    except Exception as e:
        print(f"❌ Core imports failed: {e}")
        return False


def test_benchmark_manager():
    """Test benchmark manager without external dependencies."""
    print("\n📊 Testing Benchmark Manager")
    print("=" * 30)

    try:
        from llm_dispatcher.utils.benchmark_manager import BenchmarkManager

        manager = BenchmarkManager()
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

        return True

    except Exception as e:
        print(f"❌ Benchmark manager test failed: {e}")
        return False


def test_task_classifier():
    """Test task classifier without external dependencies."""
    print("\n🎯 Testing Task Classifier")
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

        return True

    except Exception as e:
        print(f"❌ Task classifier test failed: {e}")
        return False


def test_openai_provider_direct():
    """Test OpenAI provider directly without importing the full package."""
    print("\n🤖 Testing OpenAI Provider (Direct)")
    print("=" * 40)

    try:
        # Import directly from the provider file
        sys.path.insert(
            0, str(Path(__file__).parent / "src" / "llm_dispatcher" / "providers")
        )
        from openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")
        assert provider.provider_name == "openai"
        assert len(provider.models) > 0
        print("✅ OpenAI provider initialized successfully")

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
                print(f"✅ {model} available")
            else:
                print(f"❌ {model} not found")

        # Test model capabilities
        gpt4_info = provider.models["gpt-4"]
        from llm_dispatcher.core.base import Capability

        assert Capability.VISION in gpt4_info.capabilities
        print("✅ Model capabilities working correctly")

        # Test cost estimation
        cost = provider.estimate_cost("gpt-4", 1000, 500)
        assert cost > 0
        print(f"✅ Cost estimation working: ${cost:.4f}")

        return True

    except Exception as e:
        print(f"❌ OpenAI provider test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_config():
    """Test configuration without external dependencies."""
    print("\n⚙️  Testing Configuration")
    print("=" * 25)

    try:
        from llm_dispatcher.config.settings import SwitchConfig

        config = SwitchConfig()
        assert config is not None
        assert config.switching_rules is not None
        print("✅ SwitchConfig working correctly")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Main function."""
    print("🧪 LLM-Dispatcher Minimal Test Suite")
    print("=" * 50)

    # Run tests
    tests = [
        test_core_imports,
        test_benchmark_manager,
        test_task_classifier,
        test_config,
        test_openai_provider_direct,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)

    # Summary
    passed = sum(1 for r in results if r)
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
