#!/usr/bin/env python3
"""
Example usage of LLM-Dispatcher for your own projects.

This script shows practical examples of how to use the LLM-Dispatcher
in your applications with different optimization strategies.
"""

import asyncio
import os
from llm_dispatcher.decorators.switch_decorator import (
    init,
    llm_dispatcher,
    for_text_generation,
    for_code_generation,
    for_math,
    for_reasoning,
    cost_optimized,
    speed_optimized,
)
from llm_dispatcher.core.base import TaskType
from llm_dispatcher.config.settings import OptimizationStrategy


# Example 1: Content Generation for a Blog
@for_text_generation(max_cost=0.05)
async def generate_blog_post(topic: str) -> str:
    """Generate a blog post about a given topic."""
    return f"Write a comprehensive blog post about {topic}"


# Example 2: Code Generation for Development
@for_code_generation(max_latency=3000)
async def generate_function(description: str) -> str:
    """Generate Python code based on description."""
    return f"Create a Python function that {description}"


# Example 3: Math Problem Solver
@for_math(providers=["openai", "google"])
async def solve_problem(problem: str) -> str:
    """Solve mathematical problems."""
    return f"Solve this math problem step by step: {problem}"


# Example 4: Research Assistant
@for_reasoning(optimization_strategy=OptimizationStrategy.PERFORMANCE)
async def research_topic(topic: str) -> str:
    """Research and explain a complex topic."""
    return f"Provide a detailed explanation of {topic} with examples"


# Example 5: Cost-Effective Content Generation
@cost_optimized(max_cost=0.02)
async def generate_cheap_content(prompt: str) -> str:
    """Generate content with cost optimization."""
    return prompt


# Example 6: Fast Response System
@speed_optimized(max_latency=2000)
async def quick_response(question: str) -> str:
    """Generate quick responses for real-time applications."""
    return f"Provide a concise answer to: {question}"


async def main():
    """Main example function."""
    print("🚀 LLM-Dispatcher Example Usage")
    print("=" * 40)

    # Initialize with your API keys
    switch = init(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    print("✅ LLM-Dispatcher initialized!")

    # Example 1: Blog Post Generation
    print("\n📝 Example 1: Blog Post Generation")
    try:
        blog_post = await generate_blog_post("artificial intelligence in healthcare")
        print(f"Generated: {blog_post[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Code Generation
    print("\n💻 Example 2: Code Generation")
    try:
        code = await generate_function("calculates the factorial of a number")
        print(f"Generated code: {code[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Math Problem Solving
    print("\n🧮 Example 3: Math Problem Solving")
    try:
        solution = await solve_problem("2x + 5 = 15")
        print(f"Solution: {solution[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Example 4: Research
    print("\n🔬 Example 4: Research Assistant")
    try:
        research = await research_topic("quantum computing")
        print(f"Research: {research[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Example 5: Cost-Effective Generation
    print("\n💰 Example 5: Cost-Effective Generation")
    try:
        cheap_content = await generate_cheap_content(
            "Write a short summary of machine learning"
        )
        print(f"Cost-effective content: {cheap_content[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Example 6: Fast Response
    print("\n⚡ Example 6: Fast Response")
    try:
        quick_answer = await quick_response("What is Python?")
        print(f"Quick answer: {quick_answer[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Show system status
    print("\n📊 System Status:")
    status = switch.get_system_status()
    print(f"  Providers: {status.get('total_providers', 'N/A')}")
    print(f"  Models: {status.get('total_models', 'N/A')}")

    print("\n✅ All examples completed!")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
        exit(1)

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("   Set it with: export GOOGLE_API_KEY='your-key'")
        exit(1)

    # Run examples
    asyncio.run(main())
