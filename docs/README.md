# LLM-Dispatcher Documentation

Welcome to LLM-Dispatcher, the intelligent LLM dispatching system that automatically selects the best Large Language Model for your tasks based on performance metrics, cost optimization, and real-time conditions.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Quick Start

### Installation

```bash
pip install llm-dispatcher
```

### Basic Setup

```python
import llm_dispatcher

# Initialize with your API keys
llm_dispatcher.init(
    openai_api_key="your-openai-key",
    anthropic_api_key="your-anthropic-key",
    google_api_key="your-google-key"
)

# Use the decorator for automatic LLM selection
@llm_dispatcher.llm_dispatcher()
def generate_text(prompt: str) -> str:
    return prompt

# Generate text with automatic provider selection
result = generate_text("Explain quantum computing in simple terms")
print(result)
```

## Installation

### Requirements

- Python 3.8+
- API keys for at least one LLM provider

### Install from PyPI

```bash
pip install llm-dispatcher
```

### Install from Source

```bash
git clone https://github.com/your-username/llm-dispatcher.git
cd llm-dispatcher
pip install -e .
```

### Optional Dependencies

For enhanced features, install optional dependencies:

```bash
# For multimodal support
pip install pillow librosa soundfile pydub

# For advanced caching
pip install redis faiss-cpu

# For ML routing optimization
pip install scikit-learn

# For monitoring and analytics
pip install sqlite3  # Built-in with Python
```

## Basic Usage

### Simple Text Generation

```python
import llm_dispatcher

# Initialize the dispatcher
llm_dispatcher.init(
    openai_api_key="your-key",
    anthropic_api_key="your-key"
)

# Basic text generation
@llm_dispatcher.llm_dispatcher()
def explain_concept(concept: str) -> str:
    return concept

result = explain_concept("machine learning")
```

### Task-Specific Routing

```python
from llm_dispatcher import TaskType

# Code generation with specific task type
@llm_dispatcher.llm_dispatcher(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    return description

# Reasoning tasks
@llm_dispatcher.llm_dispatcher(task_type=TaskType.REASONING)
def solve_problem(problem: str) -> str:
    return problem

# Vision analysis
@llm_dispatcher.llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(image_description: str) -> str:
    return image_description
```

### Optimization Strategies

```python
from llm_dispatcher import OptimizationStrategy

# Cost-optimized generation
@llm_dispatcher.llm_dispatcher(
    optimization_strategy=OptimizationStrategy.COST
)
def generate_cheap_text(prompt: str) -> str:
    return prompt

# Speed-optimized generation
@llm_dispatcher.llm_dispatcher(
    optimization_strategy=OptimizationStrategy.SPEED
)
def generate_fast_text(prompt: str) -> str:
    return prompt

# Balanced optimization (default)
@llm_dispatcher.llm_dispatcher(
    optimization_strategy=OptimizationStrategy.BALANCED
)
def generate_balanced_text(prompt: str) -> str:
    return prompt
```

## Advanced Features

### Streaming Responses

```python
# Basic streaming
@llm_dispatcher.llm_stream()
async def stream_text(prompt: str):
    async for chunk in _stream_generator():
        yield chunk

# Streaming with metadata
@llm_dispatcher.llm_stream_with_metadata()
async def stream_with_info(prompt: str):
    async for metadata in _stream_generator():
        yield metadata

# Example usage
async def main():
    async for chunk in stream_text("Tell me a story"):
        print(chunk, end="", flush=True)
```

### Multimodal Support

```python
from llm_dispatcher.multimodal import MultimodalAnalyzer, MediaValidator

# Initialize multimodal components
analyzer = MultimodalAnalyzer()
validator = MediaValidator()

# Analyze multimodal content
media_data = {
    "image": image_bytes,
    "audio": audio_bytes
}

analysis = analyzer.analyze_multimodal_content(media_data)
print(f"Recommended providers: {analysis.task_recommendation.recommended_providers}")
```

### Custom Providers

```python
from llm_dispatcher import LLMProvider, TaskRequest, TaskResponse

class CustomProvider(LLMProvider):
    def __init__(self):
        super().__init__("custom_provider")

    async def _make_api_call(self, request: TaskRequest) -> TaskResponse:
        # Implement your custom API call logic
        return TaskResponse(
            content="Custom response",
            model_used="custom-model",
            provider="custom_provider",
            tokens_used=100,
            cost=0.001,
            latency_ms=500,
            finish_reason="stop"
        )

# Use custom provider
custom_provider = CustomProvider()
switch = LLMSwitch(providers=[custom_provider])
```

### Caching System

```python
from llm_dispatcher.caching import CacheManager, SemanticCache

# Initialize cache manager
cache_manager = CacheManager(
    cache_dir="./cache",
    max_size_mb=100,
    cleanup_interval=3600
)

# Start caching
cache_manager.start()

# Semantic caching
semantic_cache = SemanticCache(
    cache_dir="./semantic_cache",
    similarity_threshold=0.8
)

# Check for similar responses
similar_response = semantic_cache.find_best_similar_response("Your prompt here")
```

### Performance Monitoring

```python
from llm_dispatcher.monitoring import AnalyticsEngine, MonitoringDashboard

# Initialize analytics
analytics = AnalyticsEngine()

# Record request metrics
await analytics.record_request(
    provider="openai",
    model="gpt-4",
    task_type="text_generation",
    success=True,
    latency_ms=1200,
    cost=0.003
)

# Generate performance report
report = analytics.generate_performance_report()
print(f"Success rate: {report.success_rate:.1%}")
print(f"Average latency: {report.average_latency_ms:.0f}ms")

# Start monitoring dashboard
dashboard = MonitoringDashboard(analytics)
await dashboard.start()
```

## Configuration

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"

# Configuration
export LLM_DISPATCHER_MAX_COST=1.0
export LLM_DISPATCHER_MAX_LATENCY=5000
export LLM_DISPATCHER_CACHE_ENABLED=true
```

### Configuration File

Create a `config.yaml` file:

```yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    enabled: true
    models:
      - "gpt-4"
      - "gpt-3.5-turbo"

  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    enabled: true
    models:
      - "claude-3-opus"
      - "claude-3-sonnet"

switching_rules:
  optimization_strategy: "balanced"
  fallback_strategy: "performance_based"
  max_cost_per_request: 1.0
  max_latency_ms: 5000
  enable_caching: true

monitoring:
  enable_analytics: true
  retention_days: 90
  real_time_updates: true
```

### Programmatic Configuration

```python
from llm_dispatcher import SwitchConfig, ProviderConfig

# Create custom configuration
config = SwitchConfig(
    providers={
        "openai": ProviderConfig(
            api_key="your-key",
            enabled=True,
            models=["gpt-4", "gpt-3.5-turbo"]
        )
    },
    switching_rules={
        "optimization_strategy": "cost",
        "max_cost_per_request": 0.5,
        "enable_caching": True
    }
)

# Initialize with custom config
switch = LLMSwitch(config=config)
```

## API Reference

### Core Classes

#### LLMSwitch

Main switching engine for intelligent LLM selection.

```python
class LLMSwitch:
    def __init__(self, providers: List[LLMProvider], config: SwitchConfig)
    async def execute_with_fallback(self, request: TaskRequest) -> TaskResponse
    async def execute_stream(self, request: TaskRequest) -> AsyncGenerator[str, None]
    def select_llm(self, request: TaskRequest) -> SwitchDecision
    def get_system_status(self) -> Dict[str, Any]
```

#### TaskRequest

Request structure for LLM tasks.

```python
@dataclass
class TaskRequest:
    prompt: str
    task_type: TaskType
    images: Optional[List[bytes]] = None
    audio: Optional[bytes] = None
    structured_output: Optional[Dict[str, Any]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
```

#### TaskResponse

Response structure from LLM providers.

```python
@dataclass
class TaskResponse:
    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost: float
    latency_ms: float
    finish_reason: str
```

### Decorators

#### @llm_dispatcher

Main decorator for LLM dispatching.

```python
@llm_dispatcher(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    fallback_enabled: bool = True,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None
)
```

#### @llm_stream

Decorator for streaming responses.

```python
@llm_stream(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    chunk_callback: Optional[callable] = None,
    metadata_callback: Optional[callable] = None
)
```

### Enums

#### TaskType

```python
class TaskType(Enum):
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    VISION_ANALYSIS = "vision_analysis"
    MATH = "math"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
```

#### OptimizationStrategy

```python
class OptimizationStrategy(Enum):
    COST = "cost"
    SPEED = "speed"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
```

## Examples

### Example 1: Content Generation Pipeline

```python
import llm_dispatcher
from llm_dispatcher import TaskType, OptimizationStrategy

# Initialize
llm_dispatcher.init(
    openai_api_key="your-key",
    anthropic_api_key="your-key"
)

# Content generation with different strategies
@llm_dispatcher.llm_dispatcher(
    task_type=TaskType.TEXT_GENERATION,
    optimization_strategy=OptimizationStrategy.PERFORMANCE
)
def generate_high_quality_content(topic: str) -> str:
    return topic

# Code generation
@llm_dispatcher.llm_dispatcher(
    task_type=TaskType.CODE_GENERATION,
    optimization_strategy=OptimizationStrategy.SPEED
)
def generate_code(description: str) -> str:
    return description

# Cost-optimized summarization
@llm_dispatcher.llm_dispatcher(
    task_type=TaskType.SUMMARIZATION,
    optimization_strategy=OptimizationStrategy.COST
)
def summarize_text(text: str) -> str:
    return text

# Usage
content = generate_high_quality_content("AI ethics")
code = generate_code("Create a Python function to sort a list")
summary = summarize_text("Long article text here...")
```

### Example 2: Streaming Chat Application

```python
import asyncio
import llm_dispatcher

@llm_dispatcher.llm_stream()
async def chat_stream(message: str):
    async for chunk in _stream_generator():
        yield chunk

async def chat_interface():
    print("Chat with AI (type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break

        print("AI: ", end="", flush=True)
        async for chunk in chat_stream(user_input):
            print(chunk, end="", flush=True)
        print()  # New line after response

# Run the chat interface
asyncio.run(chat_interface())
```

### Example 3: Multimodal Analysis

```python
from llm_dispatcher.multimodal import MultimodalAnalyzer, MediaValidator
from PIL import Image

# Initialize components
analyzer = MultimodalAnalyzer()
validator = MediaValidator()

# Load and validate media
image = Image.open("example.jpg")
image_bytes = image.tobytes()

validation_result = validator.validate_media(image_bytes)
if validation_result.is_valid:
    print(f"Image validated. Security score: {validation_result.security_score}")

    # Analyze multimodal content
    media_data = {"image": image_bytes}
    analysis = analyzer.analyze_multimodal_content(
        media_data,
        task_description="Analyze this image for objects and scenes"
    )

    print(f"Recommended providers: {analysis.task_recommendation.recommended_providers}")
    print(f"Estimated cost: ${analysis.task_recommendation.estimated_cost:.4f}")
else:
    print("Image validation failed:", validation_result.issues)
```

### Example 4: Performance Monitoring

```python
import asyncio
from llm_dispatcher.monitoring import AnalyticsEngine, MonitoringDashboard

async def monitoring_example():
    # Initialize analytics
    analytics = AnalyticsEngine()

    # Simulate some requests
    for i in range(10):
        await analytics.record_request(
            provider="openai",
            model="gpt-4",
            task_type="text_generation",
            success=True,
            latency_ms=1000 + i * 100,
            cost=0.003 + i * 0.001,
            tokens_used=100 + i * 10
        )

    # Generate performance report
    report = analytics.generate_performance_report()
    print(f"Total requests: {report.total_requests}")
    print(f"Success rate: {report.success_rate:.1%}")
    print(f"Average latency: {report.average_latency_ms:.0f}ms")
    print(f"Total cost: ${report.total_cost:.4f}")

    # Analyze usage patterns
    patterns = analytics.analyze_usage_patterns(days=7)
    print(f"Peak hours: {patterns.peak_hours}")
    print(f"Task distribution: {patterns.task_distribution}")

    # Assess system health
    health = analytics.assess_system_health()
    print(f"System health score: {health.overall_health_score:.2f}")
    print(f"Status: {health.status}")

    # Start monitoring dashboard
    dashboard = MonitoringDashboard(analytics)
    await dashboard.start()

    # Keep dashboard running
    try:
        await asyncio.sleep(60)  # Run for 1 minute
    finally:
        await dashboard.stop()

# Run the example
asyncio.run(monitoring_example())
```

### Example 5: Custom Provider Integration

```python
import httpx
from llm_dispatcher import LLMProvider, TaskRequest, TaskResponse, TaskType

class HuggingFaceProvider(LLMProvider):
    def __init__(self, api_key: str):
        super().__init__("huggingface")
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models"

    async def _make_api_call(self, request: TaskRequest) -> TaskResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/microsoft/DialoGPT-medium",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"inputs": request.prompt}
            )

            if response.status_code == 200:
                result = response.json()
                return TaskResponse(
                    content=result[0]["generated_text"],
                    model_used="microsoft/DialoGPT-medium",
                    provider="huggingface",
                    tokens_used=len(request.prompt.split()),
                    cost=0.0,  # Free tier
                    latency_ms=response.elapsed.total_seconds() * 1000,
                    finish_reason="stop"
                )
            else:
                raise Exception(f"HuggingFace API error: {response.status_code}")

# Use custom provider
hf_provider = HuggingFaceProvider("your-hf-key")
switch = LLMSwitch(providers=[hf_provider])

# Make requests through the custom provider
request = TaskRequest(
    prompt="Hello, how are you?",
    task_type=TaskType.TEXT_GENERATION
)

response = await switch.execute_with_fallback(request)
print(f"Response: {response.content}")
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error**: `RuntimeError: LLM-Dispatcher not initialized. Call llm_dispatcher.init() first.`

**Solution**: Make sure to initialize the dispatcher with your API keys:

```python
llm_dispatcher.init(
    openai_api_key="your-key",
    anthropic_api_key="your-key"
)
```

#### 2. No Suitable Provider Found

**Error**: `ValueError: No suitable LLM found for the request`

**Solution**: Check that:

- At least one provider is properly configured
- The requested task type is supported by available providers
- Cost/latency constraints are not too restrictive

#### 3. Import Errors

**Error**: `ImportError: No module named 'llm_dispatcher'`

**Solution**: Install the package:

```bash
pip install llm-dispatcher
```

#### 4. Streaming Issues

**Error**: `TypeError: 'async_generator' object is not iterable`

**Solution**: Use async iteration for streaming:

```python
async for chunk in stream_function():
    print(chunk)
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('llm_dispatcher').setLevel(logging.DEBUG)
```

### Performance Issues

If you experience slow performance:

1. **Check latency constraints**: Reduce `max_latency_ms` if too high
2. **Enable caching**: Set `enable_caching=True` in configuration
3. **Optimize provider selection**: Use cost or speed optimization strategies
4. **Monitor resources**: Check system resources and provider quotas

### Getting Help

- **Documentation**: Check this documentation for detailed information
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Email**: Contact support at support@llm-dispatcher.com

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/your-username/llm-dispatcher.git
cd llm-dispatcher
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/
```

### Code Style

We use Black for code formatting and flake8 for linting:

```bash
black src/
flake8 src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Acknowledgments

- OpenAI for providing excellent LLM APIs
- Anthropic for Claude models
- Google for Gemini models
- The open-source community for inspiration and contributions
