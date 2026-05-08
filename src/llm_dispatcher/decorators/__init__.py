"""
Decorator system for LLM-Dispatcher.

This module provides decorators for easy integration of intelligent LLM dispatching
into existing code with minimal configuration.
"""

from .switch_decorator import LLMSwitchDecorator, llm_dispatcher, route

__all__ = [
    "llm_dispatcher",
    "route",
    "LLMSwitchDecorator",
]
