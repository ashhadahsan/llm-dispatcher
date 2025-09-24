# 🚀 LLM-Dispatcher Setup Guide

## Quick Start with OpenAI and Gemini

### 1. Set Up API Keys

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-openai-key-here"

# Set your Google/Gemini API key
export GOOGLE_API_KEY="your-google-key-here"
# OR
export GEMINI_API_KEY="your-gemini-key-here"
```

### 2. Install Dependencies

```bash
# Install required packages
pip install openai anthropic google-generativeai python-dotenv
```

### 3. Run Basic Test

```bash
# Test basic setup (no API calls)
python simple_test.py

# Test with actual API calls
python test_openai_gemini.py
```

## 🔧 Missing Functions Fixed

I've identified and fixed the following missing functions:

### ✅ Fixed in `switch_engine.py`:

- **`_get_provider()`** - Was missing but referenced in multiple places
- **Fallback chain methods** - Fixed provider lookup logic
- **Streaming methods** - Added constraints parameter support

### ✅ Fixed in `switch_decorator.py`:

- **Standalone helper functions** - Added `_detect_task_type()`, `_prepare_request()`, `_extract_prompt()`
- **Streaming decorators** - Fixed method signatures and error handling
- **Constraint handling** - Improved parameter mapping

## 🧪 Testing Your Setup

### Basic Test (No API Calls)

```python
python simple_test.py
```

This will:

- ✅ Check API keys are set
- ✅ Initialize the dispatcher
- ✅ Show available providers and models
- ✅ Test task routing logic
- ✅ Display system status

### Full Test (With API Calls)

```python
python test_openai_gemini.py
```

This will:

- ✅ Test all basic functionality
- ✅ Make actual API calls to test generation
- ✅ Test fallback mechanisms
- ✅ Test cost and speed optimization
- ✅ Show detailed results

## 📝 Example Usage

### Basic Text Generation

```python
from llm_dispatcher.decorators.switch_decorator import init, llm_dispatcher
from llm_dispatcher.core.base import TaskType

# Initialize
switch = init(
    openai_api_key="your-openai-key",
    google_api_key="your-google-key"
)

# Use decorator
@llm_dispatcher(task_type=TaskType.TEXT_GENERATION)
async def generate_text(prompt: str) -> str:
    return prompt

# Generate text
result = await generate_text("Write a story about AI")
print(result)
```

### Code Generation

```python
from llm_dispatcher.decorators.switch_decorator import for_code_generation

@for_code_generation(max_latency=5000)
async def generate_code(description: str) -> str:
    return description

result = await generate_code("Create a Python function to sort a list")
```

### Cost Optimization

```python
from llm_dispatcher.decorators.switch_decorator import cost_optimized

@cost_optimized(max_cost=0.02)
async def cheap_generation(prompt: str) -> str:
    return prompt
```

## 🔍 Troubleshooting

### Common Issues:

1. **"LLM-Dispatcher not initialized"**

   - Make sure you call `init()` before using decorators
   - Check that API keys are properly set

2. **"No suitable LLMs found"**

   - Verify your API keys are valid
   - Check that providers are properly initialized

3. **Import errors**
   - Make sure you're running from the project root
   - Check that all dependencies are installed

### Debug Mode:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 What's Working Now

### ✅ Core Features:

- **Provider Integration**: OpenAI, Anthropic, Google
- **Task Routing**: Automatic model selection based on task type
- **Fallback System**: Automatic failover between providers
- **Cost Optimization**: Budget-aware model selection
- **Speed Optimization**: Latency-aware model selection
- **Multimodal Support**: Images and audio processing
- **Streaming**: Real-time response streaming

### ✅ Decorators:

- `@llm_dispatcher()` - Main decorator
- `@for_text_generation()` - Text generation optimized
- `@for_code_generation()` - Code generation optimized
- `@for_math()` - Math problems optimized
- `@for_reasoning()` - Reasoning tasks optimized
- `@cost_optimized()` - Cost-efficient selection
- `@speed_optimized()` - Speed-optimized selection
- `@llm_stream()` - Streaming responses
- `@llm_stream_with_metadata()` - Streaming with metadata

### ✅ Analytics & Monitoring:

- **Performance Tracking**: Latency, success rates, costs
- **Usage Analytics**: Provider preferences, task patterns
- **System Health**: Real-time health monitoring
- **Alerting**: Configurable alerts for issues

## 🎯 Next Steps

1. **Run the tests** to verify everything works
2. **Try different task types** to see model selection
3. **Experiment with optimization strategies**
4. **Set up monitoring** for production use
5. **Configure fallback strategies** for reliability

## 💡 Tips

- Start with `simple_test.py` to verify setup
- Use `cost_optimized` for budget-conscious applications
- Use `speed_optimized` for real-time applications
- Enable fallback for production reliability
- Monitor usage with the analytics system

Happy coding! 🚀
