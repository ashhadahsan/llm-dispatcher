"""
Configuration management for LLM-Dispatcher.

This module provides configuration management functionality including
settings, provider configurations, and switching rules.
"""

from .config_loader import ConfigLoader
from .settings import (
    FallbackStrategy,
    OptimizationStrategy,
    ProviderConfig,
    SwitchConfig,
    SwitchingRules,
)

__all__ = [
    "SwitchConfig",
    "ProviderConfig",
    "SwitchingRules",
    "OptimizationStrategy",
    "FallbackStrategy",
    "ConfigLoader",
]
