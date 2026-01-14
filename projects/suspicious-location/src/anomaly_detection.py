"""
Anomaly detection utilities for location analysis.
"""

import numpy as np
from typing import List, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class LocationAnomalyDetector:
    """
    Anomaly detector for location patterns using Isolation Forest.
    """

    def __init__(self, contamination: float = 0.05, n_estimators: int = 100,
                 random_state: int = 42):
        """
        Initialize anomaly detector.

        Args:
            contamination: Expected proportion of anomalies in dataset
            n_estimators: Number of trees in the forest
            random_state: Random seed for reproducibility
        """
        print(f"Initializing LocationAnomalyDetector with contamination: {contamination}, n_estimators: {n_estimators}, random_state: {random_state}")
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state

        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            max_samples='auto'
        )

    def fit(self, X: np.ndarray) -> 'LocationAnomalyDetector':
        """
        Fit the anomaly detector to training data.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Self for method chaining
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies in data.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Array of predictions (1 for normal, -1 for anomaly)
        """
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores for samples.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Array of anomaly scores (lower = more anomalous)
        """
        X_scaled = self.scaler.transform(X)
        return self.model.score_samples(X_scaled)

    def predict_with_scores(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies and return scores.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Tuple of (predictions, scores)
        """
        predictions = self.predict(X)
        scores = self.score_samples(X)
        return predictions, scores


def classify_risk_level(anomaly_scores: np.ndarray) -> List[str]:
    """
    Classify anomaly scores into risk levels.

    Args:
        anomaly_scores: Array of anomaly scores from Isolation Forest

    Returns:
        List of risk level labels
    """
    # More negative = more anomalous
    neg_scores = -anomaly_scores

    percentiles = np.percentile(neg_scores, [75, 90, 95])

    risk_levels = []
    for score in neg_scores:
        if score >= percentiles[2]:  # Top 5%
            risk_levels.append("critical")
        elif score >= percentiles[1]:  # Top 10%
            risk_levels.append("high")
        elif score >= percentiles[0]:  # Top 25%
            risk_levels.append("medium")
        else:
            risk_levels.append("low")

    return risk_levels
