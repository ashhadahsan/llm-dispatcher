"""
Advanced caching systems for LLM-Dispatcher.

Provides response caching and (optionally) semantic caching.
"""

from .cache_manager import (
    CacheManager,
    CachePolicy,
    LRUPolicy,
    SizePolicy,
    TTLPolicy,
)
from .semantic_cache import SemanticCache

__all__ = [
    "CacheManager",
    "CachePolicy",
    "LRUPolicy",
    "TTLPolicy",
    "SizePolicy",
    "SemanticCache",
]
