"""
Core switching engine for intelligent LLM selection.

This module implements the main switching logic that makes intelligent decisions
about which LLM to use based on performance metrics, cost optimization, and other factors.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .base import (
    LLMProvider,
    TaskRequest,
    TaskResponse,
    TaskType,
    ModelInfo,
    PerformanceMetrics,
    Capability,
)
from ..utils.benchmark_manager import BenchmarkManager
from ..utils.cost_calculator import CostCalculator
from ..utils.performance_monitor import PerformanceMonitor
from ..config.settings import SwitchConfig, OptimizationStrategy, FallbackStrategy

logger = logging.getLogger(__name__)


@dataclass
class SwitchDecision:
    """Represents a decision about which LLM to use."""

    provider: str
    model: str
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_latency: float
    fallback_options: List[Tuple[str, str]]  # (provider, model) pairs
    decision_factors: Dict[str, float]  # Individual factor scores


class LLMSwitch:
    """
    Main switching engine that intelligently selects LLMs based on various factors.

    This class provides the core intelligence for selecting the best LLM for each
    request based on performance metrics, cost optimization, and real-time factors.
    """

    def __init__(
        self, providers: Dict[str, LLMProvider], config: Optional[SwitchConfig] = None
    ):
        self.providers = providers
        self.config = config or SwitchConfig()
        self.benchmark_manager = BenchmarkManager()
        self.cost_calculator = CostCalculator()
        self.performance_monitor = PerformanceMonitor()

        # Decision weights based on optimization strategy
        self.weights = self._get_decision_weights()

        # Performance history
        self.performance_history: Dict[str, List[float]] = {}

        # Initialize fallback strategies
        self._initialize_fallback_strategies()

    def _get_decision_weights(self) -> Dict[str, float]:
        """Get decision weights based on optimization strategy."""
        strategy = self.config.switching_rules.optimization_strategy

        weight_configs = {
            OptimizationStrategy.PERFORMANCE: {
                "performance": 0.6,
                "cost": 0.1,
                "latency": 0.1,
                "availability": 0.1,
                "reliability": 0.1,
            },
            OptimizationStrategy.COST: {
                "performance": 0.2,
                "cost": 0.5,
                "latency": 0.1,
                "availability": 0.1,
                "reliability": 0.1,
            },
            OptimizationStrategy.SPEED: {
                "performance": 0.2,
                "cost": 0.1,
                "latency": 0.5,
                "availability": 0.1,
                "reliability": 0.1,
            },
            OptimizationStrategy.RELIABILITY: {
                "performance": 0.2,
                "cost": 0.1,
                "latency": 0.1,
                "availability": 0.2,
                "reliability": 0.4,
            },
            OptimizationStrategy.BALANCED: {
                "performance": 0.3,
                "cost": 0.2,
                "latency": 0.2,
                "availability": 0.15,
                "reliability": 0.15,
            },
        }

        return weight_configs.get(
            strategy, weight_configs[OptimizationStrategy.BALANCED]
        )

    def _initialize_fallback_strategies(self) -> None:
        """Initialize fallback strategies based on configuration."""
        self.fallback_strategies = {
            FallbackStrategy.PERFORMANCE_PRIORITY: self._get_performance_fallback_chain,
            FallbackStrategy.COST_PRIORITY: self._get_cost_fallback_chain,
            FallbackStrategy.SPEED_PRIORITY: self._get_speed_fallback_chain,
            FallbackStrategy.RELIABILITY_PRIORITY: self._get_reliability_fallback_chain,
        }

    async def select_llm(
        self, request: TaskRequest, constraints: Optional[Dict[str, Any]] = None
    ) -> SwitchDecision:
        """
        Select the best LLM for the given request.

        Args:
            request: The task request
            constraints: Optional constraints (max_cost, max_latency, etc.)

        Returns:
            SwitchDecision with the selected LLM and reasoning
        """
        constraints = constraints or {}

        # Get candidate models
        candidates = await self._get_candidates(request, constraints)

        if not candidates:
            raise ValueError("No suitable LLMs found for the request")

        # Score each candidate
        scored_candidates = []
        for provider_name, model_name in candidates:
            score, reasoning, factors = await self._score_candidate(
                provider_name, model_name, request, constraints
            )
            scored_candidates.append(
                (provider_name, model_name, score, reasoning, factors)
            )

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[2], reverse=True)

        # Select the best option
        best_provider, best_model, best_score, best_reasoning, best_factors = (
            scored_candidates[0]
        )

        # Prepare fallback options
        fallback_options = [
            (provider, model) for provider, model, _, _, _ in scored_candidates[1:3]
        ]

        # Estimate cost and latency
        provider = self.providers[best_provider]
        estimated_cost = provider.estimate_cost(
            best_model,
            provider.estimate_tokens(request.prompt),
            provider.estimate_tokens(""),  # Rough estimate
        )

        estimated_latency = self._estimate_latency(best_provider, best_model, request)

        return SwitchDecision(
            provider=best_provider,
            model=best_model,
            confidence=best_score,
            reasoning=best_reasoning,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            fallback_options=fallback_options,
            decision_factors=best_factors,
        )

    async def _get_candidates(
        self, request: TaskRequest, constraints: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """Get candidate LLMs for the request."""
        candidates = []

        # Get preferred providers for this task type
        preferred_providers = self.config.switching_rules.task_routing.get(
            request.task_type.value, list(self.providers.keys())
        )

        for provider_name in preferred_providers:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]
            suitable_models = provider.get_models_for_task(request.task_type)

            for model_name in suitable_models:
                # Check constraints
                if self._meets_constraints(provider, model_name, constraints):
                    candidates.append((provider_name, model_name))

        return candidates

    def _meets_constraints(
        self, provider: LLMProvider, model: str, constraints: Dict[str, Any]
    ) -> bool:
        """Check if a model meets the given constraints."""
        if "max_cost" in constraints:
            estimated_cost = provider.estimate_cost(
                model, provider.estimate_tokens(""), provider.estimate_tokens("")
            )
            if estimated_cost > constraints["max_cost"]:
                return False

        if "max_latency" in constraints:
            model_info = provider.get_model_info(model)
            if model_info and model_info.latency_ms:
                if model_info.latency_ms > constraints["max_latency"]:
                    return False

        if "required_capabilities" in constraints:
            model_info = provider.get_model_info(model)
            if model_info:
                required_caps = constraints["required_capabilities"]
                if not all(cap in model_info.capabilities for cap in required_caps):
                    return False

        # Check global constraints
        if self.config.switching_rules.max_latency_ms:
            model_info = provider.get_model_info(model)
            if model_info and model_info.latency_ms:
                if model_info.latency_ms > self.config.switching_rules.max_latency_ms:
                    return False

        if self.config.switching_rules.max_cost_per_request:
            estimated_cost = provider.estimate_cost(
                model, provider.estimate_tokens(""), provider.estimate_tokens("")
            )
            if estimated_cost > self.config.switching_rules.max_cost_per_request:
                return False

        return True

    async def _score_candidate(
        self,
        provider_name: str,
        model_name: str,
        request: TaskRequest,
        constraints: Dict[str, Any],
    ) -> Tuple[float, str, Dict[str, float]]:
        """Score a candidate LLM."""
        provider = self.providers[provider_name]
        model_info = provider.get_model_info(model_name)

        if not model_info:
            return 0.0, "Model not found", {}

        factors = {}
        reasoning_parts = []

        # Performance score
        perf_score = provider.get_performance_score(model_name, request.task_type)
        factors["performance"] = perf_score
        reasoning_parts.append(f"Performance: {perf_score:.2f}")

        # Cost score (lower is better)
        estimated_cost = provider.estimate_cost(
            model_name,
            provider.estimate_tokens(request.prompt),
            provider.estimate_tokens(""),  # Rough estimate
        )
        cost_score = max(0, 1 - (estimated_cost / 0.01))  # Normalize
        factors["cost"] = cost_score
        reasoning_parts.append(f"Cost: ${estimated_cost:.4f}")

        # Latency score (lower is better)
        latency = self._estimate_latency(provider_name, model_name, request)
        latency_score = max(0, 1 - (latency / 5000))  # Normalize to 5s max
        factors["latency"] = latency_score
        reasoning_parts.append(f"Latency: {latency:.0f}ms")

        # Availability score (based on recent performance)
        availability_score = self._get_availability_score(provider_name, model_name)
        factors["availability"] = availability_score
        reasoning_parts.append(f"Availability: {availability_score:.2f}")

        # Reliability score (based on error rate)
        reliability_score = self._get_reliability_score(provider_name, model_name)
        factors["reliability"] = reliability_score
        reasoning_parts.append(f"Reliability: {reliability_score:.2f}")

        # Calculate weighted score
        total_score = sum(
            factors[metric] * self.weights[metric] for metric in self.weights
        )

        reasoning = f"Score: {total_score:.2f} ({', '.join(reasoning_parts)})"

        return total_score, reasoning, factors

    def _estimate_latency(
        self, provider_name: str, model_name: str, request: TaskRequest
    ) -> float:
        """Estimate latency for a request."""
        provider = self.providers[provider_name]
        model_info = provider.get_model_info(model_name)

        if not model_info or not model_info.latency_ms:
            return 1000  # Default estimate

        base_latency = model_info.latency_ms

        # Adjust based on input length
        input_tokens = provider.estimate_tokens(request.prompt)
        if input_tokens > 1000:
            base_latency *= 1.2
        if input_tokens > 5000:
            base_latency *= 1.5

        # Adjust based on task complexity
        if request.task_type in [
            TaskType.REASONING,
            TaskType.MATH,
            TaskType.CODE_GENERATION,
        ]:
            base_latency *= 1.3

        if request.images:
            base_latency *= 1.5  # Vision tasks take longer

        return base_latency

    def _get_availability_score(self, provider_name: str, model_name: str) -> float:
        """Get availability score based on recent performance."""
        key = f"{provider_name}:{model_name}"
        if key not in self.performance_history:
            return 0.8  # Default score

        recent_scores = self.performance_history[key][-10:]  # Last 10 requests
        if not recent_scores:
            return 0.8

        return sum(recent_scores) / len(recent_scores)

    def _get_reliability_score(self, provider_name: str, model_name: str) -> float:
        """Get reliability score based on error rate."""
        # Get from performance monitor if available
        try:
            stats = self.performance_monitor.get_performance_stats(
                provider_name, model_name
            )
            return stats.success_rate
        except:
            # Fallback to default scores
            reliability_scores = {"openai": 0.95, "anthropic": 0.93, "google": 0.90}
            return reliability_scores.get(provider_name, 0.85)

    async def execute_with_fallback(
        self, request: TaskRequest, constraints: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """
        Execute a request with automatic fallback if the primary LLM fails.
        """
        decision = await self.select_llm(request, constraints)

        # Try primary choice
        try:
            provider = self.providers[decision.provider]
            response = await provider.generate(request, decision.model)

            # Record performance
            self._record_performance(decision.provider, decision.model, 1.0)
            self.performance_monitor.record_request(
                decision.provider, decision.model, response.latency_ms, True
            )

            return response

        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}")

            # Try fallback options
            for fallback_provider, fallback_model in decision.fallback_options:
                try:
                    provider = self.providers[fallback_provider]
                    response = await provider.generate(request, fallback_model)

                    # Record performance
                    self._record_performance(fallback_provider, fallback_model, 0.8)
                    self.performance_monitor.record_request(
                        fallback_provider, fallback_model, response.latency_ms, True
                    )

                    logger.info(
                        f"Fallback successful: {fallback_provider}:{fallback_model}"
                    )
                    return response

                except Exception as fallback_error:
                    logger.warning(f"Fallback failed: {fallback_error}")
                    continue

            # All options failed
            raise RuntimeError("All LLM options failed")

    def _record_performance(self, provider: str, model: str, score: float):
        """Record performance for a model."""
        key = f"{provider}:{model}"
        if key not in self.performance_history:
            self.performance_history[key] = []

        self.performance_history[key].append(score)

        # Keep only recent history
        if len(self.performance_history[key]) > 100:
            self.performance_history[key] = self.performance_history[key][-100:]

    def _get_performance_fallback_chain(
        self, task_type: TaskType
    ) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing performance."""
        rankings = self.benchmark_manager.get_task_performance_ranking(task_type)
        return [(provider, model) for model, score in rankings[:3]]

    def _get_cost_fallback_chain(self, task_type: TaskType) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing cost efficiency."""
        cost_rankings = self.cost_calculator.get_cost_efficiency_ranking()
        return [(provider, model) for model, score in cost_rankings[:3]]

    def _get_speed_fallback_chain(self, task_type: TaskType) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing speed."""
        speed_rankings = self.benchmark_manager.get_speed_ranking()
        return [(provider, model) for model, latency in speed_rankings[:3]]

    def _get_reliability_fallback_chain(
        self, task_type: TaskType
    ) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing reliability."""
        reliability_rankings = self.benchmark_manager.get_reliability_ranking()
        return [(provider, model) for model, score in reliability_rankings[:3]]

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and health."""
        status = {
            "total_providers": len(self.providers),
            "enabled_providers": len(
                [
                    p
                    for p in self.providers.values()
                    if hasattr(p, "enabled") and p.enabled
                ]
            ),
            "total_models": sum(len(p.models) for p in self.providers.values()),
            "optimization_strategy": self.config.switching_rules.optimization_strategy,
            "fallback_strategy": self.config.switching_rules.fallback_strategy,
            "provider_health": {},
            "performance_summary": self.performance_monitor.get_system_overview(),
        }

        # Get health status for each provider
        for provider_name, provider in self.providers.items():
            status["provider_health"][provider_name] = provider.get_health_status()

        return status

    def update_config(self, new_config: SwitchConfig) -> None:
        """Update the configuration."""
        self.config = new_config
        self.weights = self._get_decision_weights()
        self._initialize_fallback_strategies()

    def get_decision_weights(self) -> Dict[str, float]:
        """Get current decision weights."""
        return self.weights.copy()

    def set_decision_weights(self, weights: Dict[str, float]) -> None:
        """Set custom decision weights."""
        self.weights = weights.copy()
