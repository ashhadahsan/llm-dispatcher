"""
Machine learning-based routing optimization for LLM-Dispatcher.

This module provides ML-powered routing optimization that learns from
performance patterns and dynamically adjusts routing decisions.
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json

from ..core.base import TaskRequest, TaskResponse, TaskType
from ..monitoring.metrics_collector import MetricsCollector, MetricType

logger = logging.getLogger(__name__)


@dataclass
class RoutingFeatures:
    """Features used for ML routing optimization."""

    # Request features
    prompt_length: int
    task_type_encoded: int
    temperature: float
    max_tokens: int

    # Time features
    hour_of_day: int
    day_of_week: int
    is_weekend: bool

    # Historical features
    avg_latency_provider: float
    avg_cost_provider: float
    success_rate_provider: float
    recent_load_provider: float

    # System features
    current_load: float
    available_providers: int
    queue_length: int


@dataclass
class RoutingPrediction:
    """Routing prediction result."""

    provider: str
    model: str
    confidence: float
    predicted_latency: float
    predicted_cost: float
    predicted_quality: float
    reasoning: str


class MLRoutingOptimizer:
    """
    Machine learning-based routing optimizer.

    This class uses ML models to predict the best routing decisions
    based on historical performance data and current system state.
    """

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector

        # ML Models
        self.latency_model: Optional[RandomForestRegressor] = None
        self.cost_model: Optional[GradientBoostingRegressor] = None
        self.quality_model: Optional[LinearRegression] = None
        self.routing_model: Optional[RandomForestRegressor] = None

        # Preprocessing
        self.scaler = StandardScaler()
        self.task_encoder = LabelEncoder()

        # Training data
        self.training_data: List[Dict[str, Any]] = []
        self.model_accuracy: Dict[str, float] = {}

        # Model parameters
        self.min_training_samples = 100
        self.model_update_interval = timedelta(hours=6)
        self.last_model_update = datetime.now() - timedelta(days=1)

        # Feature importance tracking
        self.feature_importance: Dict[str, Dict[str, float]] = {}

    async def initialize(self) -> None:
        """Initialize the ML optimizer."""
        try:
            # Load existing models if available
            await self._load_models()

            # Start background training task
            asyncio.create_task(self._training_loop())

            logger.info("ML routing optimizer initialized")

        except Exception as e:
            logger.error(f"Error initializing ML optimizer: {e}")

    async def predict_optimal_routing(
        self,
        request: TaskRequest,
        available_providers: List[str],
        current_metrics: Dict[str, Any],
    ) -> List[RoutingPrediction]:
        """Predict optimal routing for a request."""

        # Generate features
        features = await self._generate_features(
            request, available_providers, current_metrics
        )

        if not self._models_ready():
            # Fallback to rule-based routing
            return await self._fallback_routing(request, available_providers)

        predictions = []

        for provider in available_providers:
            try:
                # Prepare feature vector for this provider
                feature_vector = self._prepare_feature_vector(features, provider)

                if feature_vector is None:
                    continue

                # Make predictions
                predicted_latency = self._predict_latency(feature_vector)
                predicted_cost = self._predict_cost(feature_vector)
                predicted_quality = self._predict_quality(feature_vector)

                # Calculate confidence based on model accuracy
                confidence = self._calculate_confidence(provider)

                # Generate reasoning
                reasoning = self._generate_reasoning(
                    provider, predicted_latency, predicted_cost, predicted_quality
                )

                # Get best model for this provider
                best_model = await self._get_best_model_for_provider(
                    provider, request.task_type
                )

                prediction = RoutingPrediction(
                    provider=provider,
                    model=best_model,
                    confidence=confidence,
                    predicted_latency=predicted_latency,
                    predicted_cost=predicted_cost,
                    predicted_quality=predicted_quality,
                    reasoning=reasoning,
                )

                predictions.append(prediction)

            except Exception as e:
                logger.error(f"Error predicting for provider {provider}: {e}")
                continue

        # Sort by predicted performance score
        predictions.sort(
            key=lambda x: self._calculate_performance_score(x), reverse=True
        )

        return predictions

    async def _generate_features(
        self,
        request: TaskRequest,
        available_providers: List[str],
        current_metrics: Dict[str, Any],
    ) -> RoutingFeatures:
        """Generate features for ML prediction."""

        # Request features
        prompt_length = len(request.prompt)
        task_type_encoded = self._encode_task_type(request.task_type)

        # Time features
        now = datetime.now()
        hour_of_day = now.hour
        day_of_week = now.weekday()
        is_weekend = day_of_week >= 5

        # Historical features (aggregated across providers)
        historical_data = await self._get_historical_features(available_providers)

        # System features
        current_load = current_metrics.get("current_load", 0.5)
        queue_length = current_metrics.get("queue_length", 0)

        return RoutingFeatures(
            prompt_length=prompt_length,
            task_type_encoded=task_type_encoded,
            temperature=request.temperature,
            max_tokens=request.max_tokens or 1000,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            avg_latency_provider=historical_data.get("avg_latency", 1000),
            avg_cost_provider=historical_data.get("avg_cost", 0.01),
            success_rate_provider=historical_data.get("success_rate", 0.95),
            recent_load_provider=historical_data.get("recent_load", 0.5),
            current_load=current_load,
            available_providers=len(available_providers),
            queue_length=queue_length,
        )

    def _prepare_feature_vector(
        self, features: RoutingFeatures, provider: str
    ) -> Optional[np.ndarray]:
        """Prepare feature vector for ML model."""
        try:
            # Convert features to array
            feature_array = np.array(
                [
                    features.prompt_length,
                    features.task_type_encoded,
                    features.temperature,
                    features.max_tokens,
                    features.hour_of_day,
                    features.day_of_week,
                    float(features.is_weekend),
                    features.avg_latency_provider,
                    features.avg_cost_provider,
                    features.success_rate_provider,
                    features.recent_load_provider,
                    features.current_load,
                    features.available_providers,
                    features.queue_length,
                ]
            )

            # Reshape for single prediction
            return feature_array.reshape(1, -1)

        except Exception as e:
            logger.error(f"Error preparing feature vector: {e}")
            return None

    def _predict_latency(self, feature_vector: np.ndarray) -> float:
        """Predict latency using ML model."""
        if self.latency_model is None:
            return 1000.0  # Default latency

        try:
            prediction = self.latency_model.predict(feature_vector)[0]
            return max(0, prediction)  # Ensure non-negative
        except Exception as e:
            logger.error(f"Error predicting latency: {e}")
            return 1000.0

    def _predict_cost(self, feature_vector: np.ndarray) -> float:
        """Predict cost using ML model."""
        if self.cost_model is None:
            return 0.01  # Default cost

        try:
            prediction = self.cost_model.predict(feature_vector)[0]
            return max(0, prediction)  # Ensure non-negative
        except Exception as e:
            logger.error(f"Error predicting cost: {e}")
            return 0.01

    def _predict_quality(self, feature_vector: np.ndarray) -> float:
        """Predict quality score using ML model."""
        if self.quality_model is None:
            return 0.8  # Default quality

        try:
            prediction = self.quality_model.predict(feature_vector)[0]
            return max(0, min(1, prediction))  # Clamp to [0, 1]
        except Exception as e:
            logger.error(f"Error predicting quality: {e}")
            return 0.8

    def _calculate_confidence(self, provider: str) -> float:
        """Calculate prediction confidence based on model accuracy."""
        if provider in self.model_accuracy:
            return self.model_accuracy[provider]
        return 0.7  # Default confidence

    def _calculate_performance_score(self, prediction: RoutingPrediction) -> float:
        """Calculate overall performance score for ranking."""
        # Weighted combination of predictions
        # Higher quality and lower cost/latency is better
        latency_score = max(
            0, 1 - (prediction.predicted_latency / 10000)
        )  # Normalize to 10s
        cost_score = max(0, 1 - (prediction.predicted_cost / 0.1))  # Normalize to $0.1
        quality_score = prediction.predicted_quality

        # Weighted average
        performance_score = latency_score * 0.3 + cost_score * 0.2 + quality_score * 0.5

        return performance_score * prediction.confidence

    async def _get_best_model_for_provider(
        self, provider: str, task_type: TaskType
    ) -> str:
        """Get the best model for a provider and task type."""
        # This would integrate with the existing provider logic
        # For now, return a default model
        model_mapping = {
            "openai": "gpt-4",
            "anthropic": "claude-3-sonnet",
            "google": "gemini-2.5-pro",
        }
        return model_mapping.get(provider, "gpt-4")

    def _generate_reasoning(
        self, provider: str, latency: float, cost: float, quality: float
    ) -> str:
        """Generate human-readable reasoning for the prediction."""
        reasons = []

        if latency < 1000:
            reasons.append("fast response time")
        elif latency > 5000:
            reasons.append("slower response expected")

        if cost < 0.01:
            reasons.append("cost-effective")
        elif cost > 0.05:
            reasons.append("higher cost")

        if quality > 0.9:
            reasons.append("high quality expected")
        elif quality < 0.7:
            reasons.append("moderate quality expected")

        if not reasons:
            reasons.append("balanced performance")

        return f"{provider}: {', '.join(reasons)}"

    async def _get_historical_features(self, providers: List[str]) -> Dict[str, float]:
        """Get historical performance features."""
        try:
            # Get recent metrics for all providers
            recent_metrics = await self.metrics_collector.get_metrics(
                start_time=datetime.now() - timedelta(hours=1)
            )

            if not recent_metrics:
                return {
                    "avg_latency": 1000,
                    "avg_cost": 0.01,
                    "success_rate": 0.95,
                    "recent_load": 0.5,
                }

            # Aggregate metrics
            latencies = [
                m.value for m in recent_metrics if m.metric_type == MetricType.LATENCY
            ]
            costs = [
                m.value for m in recent_metrics if m.metric_type == MetricType.COST
            ]
            errors = [
                m.value
                for m in recent_metrics
                if m.metric_type == MetricType.ERROR_RATE
            ]

            avg_latency = sum(latencies) / len(latencies) if latencies else 1000
            avg_cost = sum(costs) / len(costs) if costs else 0.01
            success_rate = 1 - (sum(errors) / len(errors)) if errors else 0.95
            recent_load = len(recent_metrics) / 60  # requests per minute

            return {
                "avg_latency": avg_latency,
                "avg_cost": avg_cost,
                "success_rate": success_rate,
                "recent_load": recent_load,
            }

        except Exception as e:
            logger.error(f"Error getting historical features: {e}")
            return {
                "avg_latency": 1000,
                "avg_cost": 0.01,
                "success_rate": 0.95,
                "recent_load": 0.5,
            }

    def _encode_task_type(self, task_type: TaskType) -> int:
        """Encode task type to numeric value."""
        task_mapping = {
            TaskType.TEXT_GENERATION: 0,
            TaskType.CODE_GENERATION: 1,
            TaskType.QUESTION_ANSWERING: 2,
            TaskType.SUMMARIZATION: 3,
            TaskType.TRANSLATION: 4,
            TaskType.CLASSIFICATION: 5,
            TaskType.REASONING: 6,
            TaskType.MATH: 7,
            TaskType.VISION_ANALYSIS: 8,
            TaskType.AUDIO_TRANSCRIPTION: 9,
        }
        return task_mapping.get(task_type, 0)

    def _models_ready(self) -> bool:
        """Check if ML models are ready for prediction."""
        return (
            self.latency_model is not None
            and self.cost_model is not None
            and self.quality_model is not None
            and len(self.training_data) >= self.min_training_samples
        )

    async def _fallback_routing(
        self, request: TaskRequest, available_providers: List[str]
    ) -> List[RoutingPrediction]:
        """Fallback routing when ML models are not ready."""
        predictions = []

        for provider in available_providers:
            # Use simple heuristics
            if provider == "openai":
                predicted_latency = 1500
                predicted_cost = 0.02
                predicted_quality = 0.9
            elif provider == "anthropic":
                predicted_latency = 2000
                predicted_cost = 0.015
                predicted_quality = 0.85
            elif provider == "google":
                predicted_latency = 1200
                predicted_cost = 0.01
                predicted_quality = 0.8
            else:
                predicted_latency = 2000
                predicted_cost = 0.02
                predicted_quality = 0.8

            best_model = await self._get_best_model_for_provider(
                provider, request.task_type
            )

            prediction = RoutingPrediction(
                provider=provider,
                model=best_model,
                confidence=0.6,  # Lower confidence for fallback
                predicted_latency=predicted_latency,
                predicted_cost=predicted_cost,
                predicted_quality=predicted_quality,
                reasoning=f"{provider}: fallback routing",
            )

            predictions.append(prediction)

        return predictions

    async def record_routing_result(
        self,
        request: TaskRequest,
        prediction: RoutingPrediction,
        actual_response: TaskResponse,
    ) -> None:
        """Record the result of a routing decision for training."""
        training_sample = {
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(request.prompt),
            "task_type": request.task_type.value,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "provider": prediction.provider,
            "model": prediction.model,
            "predicted_latency": prediction.predicted_latency,
            "predicted_cost": prediction.predicted_cost,
            "predicted_quality": prediction.predicted_quality,
            "actual_latency": actual_response.latency_ms,
            "actual_cost": actual_response.cost,
            "actual_quality": self._estimate_actual_quality(actual_response),
            "success": actual_response.finish_reason == "stop",
        }

        self.training_data.append(training_sample)

        # Keep only recent data (last 10000 samples)
        if len(self.training_data) > 10000:
            self.training_data = self.training_data[-10000:]

    def _estimate_actual_quality(self, response: TaskResponse) -> float:
        """Estimate actual quality from response."""
        # Simple quality estimation based on response characteristics
        content_length = len(response.content)
        latency = response.latency_ms

        # Base quality score
        quality = 0.8

        # Adjust based on content length
        if content_length > 100:
            quality += 0.1
        elif content_length < 20:
            quality -= 0.2

        # Adjust based on latency (faster is better, up to a point)
        if latency < 1000:
            quality += 0.05
        elif latency > 5000:
            quality -= 0.1

        return max(0, min(1, quality))

    async def _training_loop(self) -> None:
        """Background task for model training."""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour

                # Check if we need to retrain
                if (
                    datetime.now() - self.last_model_update > self.model_update_interval
                    and len(self.training_data) >= self.min_training_samples
                ):
                    await self._train_models()

            except Exception as e:
                logger.error(f"Error in training loop: {e}")
                await asyncio.sleep(300)

    async def _train_models(self) -> None:
        """Train ML models on collected data."""
        try:
            logger.info("Training ML routing models...")

            if len(self.training_data) < self.min_training_samples:
                logger.warning(f"Not enough training data: {len(self.training_data)}")
                return

            # Convert to DataFrame
            df = pd.DataFrame(self.training_data)

            # Prepare features and targets
            feature_columns = [
                "prompt_length",
                "temperature",
                "max_tokens",
                "predicted_latency",
                "predicted_cost",
                "predicted_quality",
            ]

            X = df[feature_columns].fillna(0)
            y_latency = df["actual_latency"].fillna(1000)
            y_cost = df["actual_cost"].fillna(0.01)
            y_quality = df["actual_quality"].fillna(0.8)

            # Split data
            X_train, X_test, y_latency_train, y_latency_test = train_test_split(
                X, y_latency, test_size=0.2, random_state=42
            )

            # Train latency model
            self.latency_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.latency_model.fit(X_train, y_latency_train)

            # Train cost model
            self.cost_model = GradientBoostingRegressor(
                n_estimators=100, random_state=42
            )
            self.cost_model.fit(X_train, y_cost.iloc[X_train.index])

            # Train quality model
            self.quality_model = LinearRegression()
            self.quality_model.fit(X_train, y_quality.iloc[X_train.index])

            # Evaluate models
            latency_pred = self.latency_model.predict(X_test)
            cost_pred = self.cost_model.predict(X_test)
            quality_pred = self.quality_model.predict(X_test)

            latency_r2 = r2_score(y_latency_test, latency_pred)
            cost_r2 = r2_score(y_cost.iloc[X_test.index], cost_pred)
            quality_r2 = r2_score(y_quality.iloc[X_test.index], quality_pred)

            self.model_accuracy = {
                "latency": latency_r2,
                "cost": cost_r2,
                "quality": quality_r2,
            }

            # Store feature importance
            self.feature_importance = {
                "latency": dict(
                    zip(feature_columns, self.latency_model.feature_importances_)
                ),
                "cost": dict(
                    zip(feature_columns, self.cost_model.feature_importances_)
                ),
                "quality": dict(zip(feature_columns, abs(self.quality_model.coef_))),
            }

            # Save models
            await self._save_models()

            self.last_model_update = datetime.now()

            logger.info(
                f"Models trained successfully. R² scores - Latency: {latency_r2:.3f}, "
                f"Cost: {cost_r2:.3f}, Quality: {quality_r2:.3f}"
            )

        except Exception as e:
            logger.error(f"Error training models: {e}")

    async def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            model_data = {
                "latency_model": (
                    joblib.dumps(self.latency_model) if self.latency_model else None
                ),
                "cost_model": (
                    joblib.dumps(self.cost_model) if self.cost_model else None
                ),
                "quality_model": (
                    joblib.dumps(self.quality_model) if self.quality_model else None
                ),
                "model_accuracy": self.model_accuracy,
                "feature_importance": self.feature_importance,
                "last_update": self.last_model_update.isoformat(),
            }

            # Save to file (in practice, use proper model storage)
            with open("ml_models.json", "w") as f:
                json.dump(model_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    async def _load_models(self) -> None:
        """Load trained models from disk."""
        try:
            with open("ml_models.json", "r") as f:
                model_data = json.load(f)

            if model_data.get("latency_model"):
                self.latency_model = joblib.loads(model_data["latency_model"])
            if model_data.get("cost_model"):
                self.cost_model = joblib.loads(model_data["cost_model"])
            if model_data.get("quality_model"):
                self.quality_model = joblib.loads(model_data["quality_model"])

            self.model_accuracy = model_data.get("model_accuracy", {})
            self.feature_importance = model_data.get("feature_importance", {})

            if model_data.get("last_update"):
                self.last_model_update = datetime.fromisoformat(
                    model_data["last_update"]
                )

            logger.info("ML models loaded successfully")

        except FileNotFoundError:
            logger.info("No existing models found, will train from scratch")
        except Exception as e:
            logger.error(f"Error loading models: {e}")

    def get_model_stats(self) -> Dict[str, Any]:
        """Get ML model statistics."""
        return {
            "models_ready": self._models_ready(),
            "training_samples": len(self.training_data),
            "model_accuracy": self.model_accuracy,
            "feature_importance": self.feature_importance,
            "last_update": self.last_model_update.isoformat(),
            "next_update": (
                self.last_model_update + self.model_update_interval
            ).isoformat(),
        }
