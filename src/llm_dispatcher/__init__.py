"""
LLM-Dispatcher: Intelligent LLM dispatching with performance-based routing.

This package provides intelligent dispatching between different Large Language Models
based on task requirements, performance metrics, token availability, and cost optimization.
"""

from .config.config_loader import get_config, init_config
from .config.settings import SwitchConfig
from .core.base import Capability, LLMProvider, TaskRequest, TaskResponse, TaskType
from .core.switch_engine import LLMSwitch
from .decorators.switch_decorator import (
    get_global_switch,
    init,
    llm_dispatcher,
    llm_stream,
    llm_stream_with_metadata,
    set_global_switch,
)
from .exceptions import (
    BudgetExceededError,
    CacheError,
    CacheMissError,
    CacheStorageError,
    ConfigurationError,
    ContentFilterError,
    CostLimitExceededError,
    FallbackExhaustedError,
    InvalidConfigurationError,
    InvalidRequestError,
    LLMDispatcherError,
    MissingConfigurationError,
    ModelContextLengthExceededError,
    ModelError,
    ModelNotFoundError,
    ModelUnsupportedError,
    NoAvailableProvidersError,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderQuotaExceededError,
    ProviderRateLimitError,
    ProviderServiceUnavailableError,
    ProviderTimeoutError,
    RequestError,
    RequestTimeoutError,
    SecurityError,
    UnauthorizedAccessError,
)
from .utils.benchmark_manager import BenchmarkManager

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version
except ImportError:  # pragma: no cover - py<3.8 fallback
    from importlib_metadata import (  # type: ignore[no-redef,assignment]
        PackageNotFoundError,
    )
    from importlib_metadata import version as _pkg_version  # type: ignore[no-redef]

try:
    __version__ = _pkg_version("llm-dispatcher")
except PackageNotFoundError:  # pragma: no cover - source checkout without install
    __version__ = "0.0.0+unknown"

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
    "init_config",
    "get_config",
    # Exceptions
    "LLMDispatcherError",
    "ProviderError",
    "ProviderConnectionError",
    "ProviderAuthenticationError",
    "ProviderRateLimitError",
    "ProviderQuotaExceededError",
    "ProviderTimeoutError",
    "ProviderServiceUnavailableError",
    "ModelError",
    "ModelNotFoundError",
    "ModelUnsupportedError",
    "ModelContextLengthExceededError",
    "ConfigurationError",
    "InvalidConfigurationError",
    "MissingConfigurationError",
    "RequestError",
    "InvalidRequestError",
    "RequestTimeoutError",
    "CostLimitExceededError",
    "BudgetExceededError",
    "FallbackExhaustedError",
    "NoAvailableProvidersError",
    "CacheError",
    "CacheMissError",
    "CacheStorageError",
    "SecurityError",
    "ContentFilterError",
    "UnauthorizedAccessError",
]
