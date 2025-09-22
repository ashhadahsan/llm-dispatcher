"""
LLM-Dispatcher: Intelligent LLM dispatching with performance-based routing.

This package provides intelligent dispatching between different Large Language Models
based on task requirements, performance metrics, token availability, and cost optimization.
"""

from .core.switch_engine import LLMSwitch
from .decorators.switch_decorator import (
    llm_dispatcher,
    llm_stream,
    llm_stream_with_metadata,
    init,
    get_global_switch,
    set_global_switch,
)
from .core.base import LLMProvider, TaskType, Capability, TaskRequest, TaskResponse
from .utils.benchmark_manager import BenchmarkManager
from .config.settings import SwitchConfig

__version__ = "1.0.0"
__author__ = "ashhadahsan"
__email__ = "ashhadahsan@gmail.com"

__all__ = [
    "LLMSwitch",
    "llm_dispatcher",
    "llm_stream",
    "llm_stream_with_metadata",
    "init",
    "get_global_switch",
    "set_global_switch",
    "LLMProvider",
    "TaskType",
    "Capability",
    "TaskRequest",
    "TaskResponse",
    "BenchmarkManager",
    "SwitchConfig",
]
