"""
LLM-Dispatcher: Intelligent LLM dispatching with performance-based routing.

This package provides intelligent dispatching between different Large Language Models
based on task requirements, performance metrics, token availability, and cost optimization.
"""

from .core.switch_engine import LLMSwitch
from .decorators.switch_decorator import llm_dispatcher
from .core.base import LLMProvider, TaskType, Capability, TaskRequest, TaskResponse
from .utils.benchmark_manager import BenchmarkManager
from .config.settings import SwitchConfig

__version__ = "0.1.0"
__author__ = "ashhadahsan"
__email__ = "ashhadahsan@gmaio.com"

__all__ = [
    "LLMSwitch",
    "llm_dispatcher",
    "LLMProvider",
    "TaskType",
    "Capability",
    "TaskRequest",
    "TaskResponse",
    "BenchmarkManager",
    "SwitchConfig",
]
