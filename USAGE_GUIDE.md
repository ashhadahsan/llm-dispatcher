# 🚀 LLM-Dispatcher Usage Guide

## ✅ **System Status: FULLY FUNCTIONAL**

Your LLM-Dispatcher is now working perfectly with both OpenAI and Gemini providers!

## 🎯 **Quick Start Examples**

### 1. **Basic Text Generation**

```python
import asyncio
from llm_dispatcher.decorators.switch_decorator import init, llm_dispatcher
from llm_dispatcher.core.base import TaskType

# Initialize
switch = init(
    openai_api_key="your-openai-key",
    google_api_key="your-google-key"
)

@llm_dispatcher(task_type=TaskType.TEXT_GENERATION)
async def generate_text(prompt: str) -> str:
    return prompt

# Use it
result = await generate_text("Write a story about AI")
print(result)
```

### 2. **Code Generation with Cost Limits**

```python
from llm_dispatcher.decorators.switch_decorator import for_code_generation

@for_code_generation(max_cost=0.05, max_latency=3000)
async def generate_code(description: str) -> str:
    return description

result = await generate_code("Create a Python function to sort a list")
```

### 3. **Math Problems with Speed Optimization**

```python
from llm_dispatcher.decorators.switch_decorator import for_math, speed_optimized

@speed_optimized(max_latency=2000)
async def solve_math(problem: str) -> str:
    return problem

result = await solve_math("What is 15 * 23?")
```

### 4. **Reasoning Tasks with Provider Selection**

```python
from llm_dispatcher.decorators.switch_decorator import for_reasoning

@for_reasoning(providers=["openai", "google"])
async def reason_about(topic: str) -> str:
    return topic

result = await reason_about("Explain quantum computing")
```

## 🔧 **Advanced Configuration**

### **Custom Optimization Strategies**

```python
from llm_dispatcher.config.settings import OptimizationStrategy

# Cost-optimized
@llm_dispatcher(optimization_strategy=OptimizationStrategy.COST)
async def cheap_generation(prompt: str) -> str:
    return prompt

# Speed-optimized
@llm_dispatcher(optimization_strategy=OptimizationStrategy.SPEED)
async def fast_generation(prompt: str) -> str:
    return prompt

# Performance-optimized
@llm_dispatcher(optimization_strategy=OptimizationStrategy.PERFORMANCE)
async def quality_generation(prompt: str) -> str:
    return prompt
```

### **Fallback Configuration**

```python
@llm_dispatcher(
    fallback_enabled=True,
    providers=["openai", "google"],  # Try these in order
    max_cost=0.10,
    max_latency=5000
)
async def reliable_generation(prompt: str) -> str:
    return prompt
```

## 📊 **Monitoring & Analytics**

### **System Status**

```python
# Get system status
status = switch.get_system_status()
print(f"Providers: {status['total_providers']}")
print(f"Models: {status['total_models']}")

# Get decision weights
weights = switch.get_decision_weights()
print(f"Decision weights: {weights}")
```

### **Task Routing Analysis**

```python
from llm_dispatcher.core.base import TaskRequest

# See which model would be selected
request = TaskRequest(
    prompt="Write a story",
    task_type=TaskType.TEXT_GENERATION
)

decision = await switch.select_llm(request)
print(f"Selected: {decision.provider}:{decision.model}")
print(f"Confidence: {decision.confidence}")
print(f"Reasoning: {decision.reasoning}")
```

## 🎨 **Multimodal Support**

### **Image Analysis**

```python
@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
async def analyze_image(prompt: str, images: list) -> str:
    return prompt

# Use with base64 encoded images
result = await analyze_image("Describe this image", [base64_image])
```

### **Audio Processing**

```python
@llm_dispatcher(task_type=TaskType.AUDIO_TRANSCRIPTION)
async def transcribe_audio(prompt: str, audio: str) -> str:
    return prompt

# Use with base64 encoded audio
result = await transcribe_audio("Transcribe this audio", base64_audio)
```

## 🔄 **Streaming Responses**

### **Basic Streaming**

```python
from llm_dispatcher.decorators.switch_decorator import llm_stream

@llm_stream(task_type=TaskType.TEXT_GENERATION)
async def stream_text(prompt: str):
    async for chunk in _stream_generator():
        yield chunk

# Use it
async for chunk in stream_text("Write a long story"):
    print(chunk, end="")
```

### **Streaming with Metadata**

```python
from llm_dispatcher.decorators.switch_decorator import llm_stream_with_metadata

@llm_stream_with_metadata(task_type=TaskType.TEXT_GENERATION)
async def stream_with_metadata(prompt: str):
    async for metadata in _stream_generator():
        yield metadata

# Use it
async for metadata in stream_with_metadata("Write a story"):
    print(f"Chunk {metadata['chunk_index']}: {metadata['chunk']}")
```

## 🛠️ **Production Setup**

### **Environment Variables**

```bash
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

### **Configuration File**

```yaml
# config.yaml
switching_rules:
  optimization_strategy: "balanced"
  max_latency_ms: 5000
  max_cost_per_request: 0.10
  fallback_enabled: true

monitoring:
  enable_monitoring: true
  performance_window_hours: 24
```

### **Error Handling**

```python
try:
    result = await generate_text("Your prompt")
except Exception as e:
    print(f"Error: {e}")
    # Handle fallback or retry logic
```

## 📈 **Performance Tips**

### **1. Cost Optimization**

- Use `cost_optimized()` decorator for budget-conscious applications
- Set `max_cost` limits on decorators
- Monitor usage with analytics

### **2. Speed Optimization**

- Use `speed_optimized()` decorator for real-time applications
- Set `max_latency` limits
- Choose faster models for simple tasks

### **3. Reliability**

- Enable fallback mechanisms
- Use multiple providers
- Monitor system health

### **4. Quality**

- Use `performance_optimized()` for best quality
- Choose appropriate task types
- Use specialized models for specific tasks

## 🔍 **Debugging**

### **Enable Debug Logging**

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Check Provider Status**

```python
for provider_name, provider in switch.providers.items():
    print(f"{provider_name}: {len(provider.models)} models")
    for model_name in list(provider.models.keys())[:3]:
        model_info = provider.get_model_info(model_name)
        print(f"  {model_name}: {model_info.capabilities}")
```

### **Test Individual Providers**

```python
# Test specific provider
openai_provider = switch.providers["openai"]
result = await openai_provider.generate(request, "gpt-4")
```

## 🎯 **Best Practices**

1. **Always use appropriate task types** for better model selection
2. **Set cost and latency limits** to control spending and performance
3. **Enable fallback** for production reliability
4. **Monitor usage** with the analytics system
5. **Use streaming** for long responses to improve user experience
6. **Test with different providers** to find the best fit for your use case

## 🚀 **Ready to Use!**

Your LLM-Dispatcher is now fully functional and ready for production use. The system intelligently selects the best model for each task, handles fallbacks automatically, and provides comprehensive monitoring and analytics.

Happy coding! 🎉
