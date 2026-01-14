"""
Unit tests for anomaly detection utilities.
"""

import pytest
import numpy as np
from sklearn.datasets import make_classification

from src.anomaly_detection import (
    LocationAnomalyDetector,
    classify_risk_level
)


class TestLocationAnomalyDetector:
    """Tests for LocationAnomalyDetector class."""

    def test_initialization_default(self):
        """Test detector initialization with defaults."""
        detector = LocationAnomalyDetector()

        assert detector.contamination == 0.05
        assert detector.n_estimators == 100
        assert detector.random_state == 42

    def test_initialization_custom(self):
        """Test detector initialization with custom parameters."""
        detector = LocationAnomalyDetector(
            contamination=0.1,
            n_estimators=50,
            random_state=123
        )

        assert detector.contamination == 0.1
        assert detector.n_estimators == 50
        assert detector.random_state == 123

    def test_fit_returns_self(self):
        """Test that fit returns self for chaining."""
        detector = LocationAnomalyDetector()
        X = np.random.randn(100, 5)

        result = detector.fit(X)

        assert result is detector

    def test_fit_and_predict(self):
        """Test fit and predict workflow."""
        # Create test data with clear normal and anomaly patterns
        np.random.seed(42)
        X_normal = np.random.randn(100, 5)
        X_anomaly = np.random.randn(10, 5) * 10  # Far from normal

        # Fit on normal data
        detector = LocationAnomalyDetector(contamination=0.1)
        detector.fit(X_normal)

        # Predict on mixed data
        X_test = np.vstack([X_normal[:10], X_anomaly[:5]])
        predictions = detector.predict(X_test)

        # Check predictions shape
        assert predictions.shape == (15,)

        # Check predictions are -1 or 1
        assert all(p in [-1, 1] for p in predictions)

    def test_score_samples(self):
        """Test anomaly score generation."""
        np.random.seed(42)
        X = np.random.randn(100, 5)

        detector = LocationAnomalyDetector()
        detector.fit(X)

        scores = detector.score_samples(X)

        # Check scores shape
        assert scores.shape == (100,)

        # Check scores are numeric
        assert np.all(np.isfinite(scores))

    def test_predict_with_scores(self):
        """Test predict_with_scores method."""
        np.random.seed(42)
        X = np.random.randn(100, 5)

        detector = LocationAnomalyDetector()
        detector.fit(X)

        predictions, scores = detector.predict_with_scores(X)

        # Check both outputs
        assert predictions.shape == (100,)
        assert scores.shape == (100,)
        assert all(p in [-1, 1] for p in predictions)
        assert np.all(np.isfinite(scores))

    def test_scaler_fit_transform(self):
        """Test that scaler is properly fitted."""
        np.random.seed(42)
        X = np.random.randn(100, 5) * 10 + 5  # Non-normalized data

        detector = LocationAnomalyDetector()
        detector.fit(X)

        # Scaler should be fitted
        assert hasattr(detector.scaler, 'mean_')
        assert hasattr(detector.scaler, 'scale_')

        # Check scaler transforms correctly
        X_scaled = detector.scaler.transform(X[:5])
        assert X_scaled.shape == (5, 5)

    def test_consistent_predictions(self):
        """Test that predictions are consistent with same random state."""
        np.random.seed(42)
        X = np.random.randn(100, 5)

        detector1 = LocationAnomalyDetector(random_state=42)
        detector2 = LocationAnomalyDetector(random_state=42)

        detector1.fit(X)
        detector2.fit(X)

        pred1 = detector1.predict(X)
        pred2 = detector2.predict(X)

        np.testing.assert_array_equal(pred1, pred2)


class TestClassifyRiskLevel:
    """Tests for risk level classification."""

    def test_classify_risk_level_distribution(self):
        """Test risk level classification distribution."""
        # Create scores with known distribution
        np.random.seed(42)
        scores = np.random.randn(1000)

        risk_levels = classify_risk_level(scores)

        # Check that we have all risk levels
        unique_levels = set(risk_levels)
        expected_levels = {"low", "medium", "high", "critical"}
        assert unique_levels == expected_levels

        # Count should roughly match percentiles
        counts = {level: risk_levels.count(level) for level in expected_levels}

        # Critical should be ~5% (top 5%)
        assert 30 < counts["critical"] < 70  # ~50 with some tolerance

        # High should be ~5% (90-95th percentile)
        assert 30 < counts["high"] < 70

        # Medium should be ~15% (75-90th percentile)
        assert 100 < counts["medium"] < 200

        # Low should be ~75% (below 75th percentile)
        assert 700 < counts["low"] < 800

    def test_classify_risk_level_extreme_scores(self):
        """Test classification with extreme scores."""
        scores = np.array([10.0, 5.0, 0.0, -5.0, -10.0])

        risk_levels = classify_risk_level(scores)

        # Most negative should be critical (highest risk)
        assert risk_levels[4] == "critical"

        # Most positive should be low (lowest risk)
        assert risk_levels[0] == "low"

    def test_classify_risk_level_uniform(self):
        """Test classification with uniform scores."""
        scores = np.ones(100)

        risk_levels = classify_risk_level(scores)

        # All scores are same, so classification should work
        assert len(risk_levels) == 100
        assert all(level in ["low", "medium", "high", "critical"] for level in risk_levels)

    def test_classify_risk_level_output_type(self):
        """Test that output is a list of strings."""
        scores = np.random.randn(10)

        risk_levels = classify_risk_level(scores)

        assert isinstance(risk_levels, list)
        assert all(isinstance(level, str) for level in risk_levels)
        assert len(risk_levels) == 10
