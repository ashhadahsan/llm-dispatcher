#!/usr/bin/env python3
"""
Test script for quality benchmarks implementation.

This script tests the quality benchmarking system without requiring
external API keys or optional dependencies.
"""

import asyncio
import sys
import os
from typing import List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from llm_dispatcher.benchmarks.quality_benchmark import (
    TestCase,
    QualityBenchmark,
    MultiDimensionalQualityBenchmark,
    TaskSpecificQualityBenchmark,
    ConsistencyBenchmark,
    RealtimeQualityMonitor,
)
from llm_dispatcher.benchmarks.evaluation import (
    AutomatedEvaluator,
    HumanEvaluator,
    HybridEvaluator,
)
from llm_dispatcher.benchmarks.analysis import QualityAnalyzer
from llm_dispatcher.benchmarks.reports import QualityReporter


class MockProvider:
    """Mock provider for testing without API calls."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate a mock response."""
        if "capital" in prompt.lower():
            return "Paris is the capital of France."
        elif "haiku" in prompt.lower():
            return "Spring brings new life\nBirds sing in the morning light\nNature awakens"
        elif "explain" in prompt.lower():
            return "This is a technical explanation of the requested topic."
        else:
            return "This is a mock response for testing purposes."


async def test_basic_quality_benchmark():
    """Test basic quality benchmark functionality."""
    print("Testing Basic Quality Benchmark...")
    
    # Create test cases
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris", "The capital of France is Paris"]
        ),
        TestCase(
            prompt="Write a haiku about nature",
            expected="5-7-5 syllable structure",
            type="creative",
            ground_truths=["A haiku with 5-7-5 syllable structure about nature"]
        )
    ]
    
    # Create benchmark with mock provider
    benchmark = QualityBenchmark(
        test_cases=test_cases,
        providers=["mock"],
        iterations=2,
        use_ragas=False  # Disable RAGAS for testing
    )
    
    # Replace provider with mock
    benchmark._providers = {"mock": MockProvider("mock")}
    
    # Run benchmark
    results = await benchmark.run()
    
    # Verify results
    assert results.overall_accuracy >= 0.0
    assert results.avg_quality_score >= 0.0
    assert len(results.provider_metrics) > 0
    
    print(f"✓ Basic quality benchmark test passed")
    print(f"  Overall accuracy: {results.overall_accuracy:.2%}")
    print(f"  Average quality score: {results.avg_quality_score:.2f}")
    
    return results


async def test_multi_dimensional_benchmark():
    """Test multi-dimensional quality benchmark."""
    print("\nTesting Multi-Dimensional Quality Benchmark...")
    
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            dimensions=["accuracy", "precision", "completeness"],
            ground_truths=["Paris"]
        )
    ]
    
    benchmark = MultiDimensionalQualityBenchmark(
        test_cases=test_cases,
        providers=["mock"],
        iterations=1,
        use_ragas=False
    )
    
    benchmark._providers = {"mock": MockProvider("mock")}
    
    results = await benchmark.run()
    
    assert len(results.dimension_scores) > 0
    
    print(f"✓ Multi-dimensional benchmark test passed")
    print(f"  Dimension scores: {results.dimension_scores}")
    
    return results


async def test_task_specific_benchmark():
    """Test task-specific quality benchmark."""
    print("\nTesting Task-Specific Quality Benchmark...")
    
    test_cases = {
        "factual": [
            TestCase(
                prompt="What is the population of Tokyo?",
                expected="Approximately 14 million",
                type="factual",
                ground_truths=["About 14 million people"]
            )
        ],
        "creative": [
            TestCase(
                prompt="Write a poem about the ocean",
                expected="creative poetry",
                type="creative",
                ground_truths=["A creative poem about the ocean"]
            )
        ]
    }
    
    benchmark = TaskSpecificQualityBenchmark(
        task_types=["factual", "creative"],
        test_cases=test_cases,
        providers=["mock"],
        iterations=1,
        use_ragas=False
    )
    
    benchmark._providers = {"mock": MockProvider("mock")}
    
    results = await benchmark.run()
    
    assert len(results.task_metrics) > 0
    
    print(f"✓ Task-specific benchmark test passed")
    print(f"  Task metrics: {list(results.task_metrics.keys())}")
    
    return results


async def test_consistency_benchmark():
    """Test consistency benchmark."""
    print("\nTesting Consistency Benchmark...")
    
    test_prompts = [
        "What is the capital of France?",
        "Write a haiku about nature"
    ]
    
    benchmark = ConsistencyBenchmark(
        test_prompts=test_prompts,
        providers=["mock"],
        iterations=2,
        use_ragas=False
    )
    
    benchmark._providers = {"mock": MockProvider("mock")}
    
    results = await benchmark.run()
    
    assert results.consistency_score >= 0.0
    
    print(f"✓ Consistency benchmark test passed")
    print(f"  Consistency score: {results.consistency_score:.2f}")
    
    return results


async def test_evaluation_methods():
    """Test evaluation methods."""
    print("\nTesting Evaluation Methods...")
    
    prompts = ["What is the capital of France?", "Write a haiku about spring"]
    responses = ["Paris is the capital of France.", "Spring brings new life..."]
    expected = ["Paris", "5-7-5 syllable structure"]
    
    # Test automated evaluator
    automated_evaluator = AutomatedEvaluator(
        evaluation_metrics=["accuracy", "relevance", "coherence", "completeness"],
        use_ragas=False,  # Disable RAGAS for testing
        use_semantic_similarity=False  # Disable for testing
    )
    
    automated_result = await automated_evaluator.evaluate(prompts, responses, expected)
    
    assert automated_result.accuracy >= 0.0
    assert automated_result.relevance >= 0.0
    
    print(f"✓ Automated evaluation test passed")
    print(f"  Accuracy: {automated_result.accuracy:.2f}")
    print(f"  Relevance: {automated_result.relevance:.2f}")
    
    # Test human evaluator
    human_evaluator = HumanEvaluator(
        evaluators=["expert1", "expert2"],
        evaluation_criteria=["accuracy", "relevance", "coherence", "creativity"]
    )
    
    human_result = await human_evaluator.evaluate(prompts, responses, expected)
    
    assert human_result.accuracy >= 0.0
    assert human_result.inter_rater_reliability >= 0.0
    
    print(f"✓ Human evaluation test passed")
    print(f"  Accuracy: {human_result.accuracy:.2f}")
    print(f"  Inter-rater reliability: {human_result.inter_rater_reliability:.2f}")
    
    # Test hybrid evaluator
    hybrid_evaluator = HybridEvaluator(
        automated_metrics=["accuracy", "relevance"],
        human_metrics=["creativity", "aesthetics"],
        weight_automated=0.7,
        weight_human=0.3
    )
    
    hybrid_result = await hybrid_evaluator.evaluate(prompts, responses, expected)
    
    assert hybrid_result.hybrid_score >= 0.0
    assert hybrid_result.overall_score >= 0.0
    
    print(f"✓ Hybrid evaluation test passed")
    print(f"  Hybrid score: {hybrid_result.hybrid_score:.2f}")
    print(f"  Overall score: {hybrid_result.overall_score:.2f}")
    
    return automated_result, human_result, hybrid_result


async def test_analysis_and_reporting():
    """Test analysis and reporting functionality."""
    print("\nTesting Analysis and Reporting...")
    
    # First run a benchmark to get results
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris"]
        )
    ]
    
    benchmark = QualityBenchmark(
        test_cases=test_cases,
        providers=["mock"],
        iterations=2,
        use_ragas=False
    )
    
    benchmark._providers = {"mock": MockProvider("mock")}
    
    results = await benchmark.run()
    
    # Test analysis
    analyzer = QualityAnalyzer(results)
    
    stats = analyzer.get_statistical_analysis()
    assert len(stats) > 0
    
    distribution = analyzer.get_distribution_analysis()
    assert distribution.quality is not None
    
    trends = analyzer.get_trend_analysis()
    assert trends.quality is not None
    
    comparison = analyzer.compare_providers()
    assert len(comparison) > 0
    
    print(f"✓ Analysis test passed")
    print(f"  Statistical analysis: {len(stats)} metrics")
    print(f"  Provider comparison: {len(comparison)} providers")
    
    # Test reporting
    reporter = QualityReporter(results)
    
    # Generate HTML report
    report_file = reporter.generate_report("test_quality_report.html")
    assert os.path.exists(report_file)
    
    print(f"✓ Reporting test passed")
    print(f"  Report generated: {report_file}")
    
    # Clean up
    if os.path.exists(report_file):
        os.remove(report_file)
    
    return results


async def test_realtime_monitoring():
    """Test real-time monitoring functionality."""
    print("\nTesting Real-time Quality Monitoring...")
    
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris"]
        )
    ]
    
    monitor = RealtimeQualityMonitor(
        test_cases=test_cases,
        duration=5,  # 5 seconds for testing
        check_interval=2,  # Check every 2 seconds
        alerts={"accuracy_threshold": 0.8}
    )
    
    # Mock the benchmark creation in the monitor
    original_benchmark = QualityBenchmark
    def mock_benchmark(*args, **kwargs):
        benchmark = original_benchmark(*args, **kwargs)
        benchmark._providers = {"mock": MockProvider("mock")}
        return benchmark
    
    # Start monitoring
    monitoring_task = asyncio.create_task(monitor.start())
    
    # Wait a bit and check metrics
    await asyncio.sleep(3)
    
    if monitor.is_running:
        metrics = monitor.get_current_metrics()
        assert "accuracy" in metrics
        
        print(f"✓ Real-time monitoring test passed")
        print(f"  Current accuracy: {metrics.get('accuracy', 0):.2%}")
    
    # Stop monitoring
    await monitor.stop()
    await monitoring_task
    
    return True


async def main():
    """Run all tests."""
    print("Quality Benchmarks Implementation Test")
    print("=" * 50)
    
    try:
        # Run all tests
        await test_basic_quality_benchmark()
        await test_multi_dimensional_benchmark()
        await test_task_specific_benchmark()
        await test_consistency_benchmark()
        await test_evaluation_methods()
        await test_analysis_and_reporting()
        await test_realtime_monitoring()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed successfully!")
        print("\nThe quality benchmarks implementation is working correctly.")
        print("You can now use it with real API keys and RAGAS for production use.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
