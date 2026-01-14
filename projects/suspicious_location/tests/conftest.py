"""
Pytest configuration and shared fixtures.
"""

import pytest
import numpy as np


@pytest.fixture
def sample_coordinates():
    """Sample geographic coordinates for testing."""
    return {
        'nyc': (40.7128, -74.0060),
        'la': (34.0522, -118.2437),
        'london': (51.5074, -0.1278),
        'paris': (48.8566, 2.3522),
        'tokyo': (35.6762, 139.6503),
    }


@pytest.fixture
def sample_features():
    """Sample feature matrix for testing."""
    np.random.seed(42)
    return np.random.randn(100, 10)


@pytest.fixture
def sample_anomaly_data():
    """Sample data with known anomalies."""
    np.random.seed(42)
    normal_data = np.random.randn(90, 5)
    anomaly_data = np.random.randn(10, 5) * 5 + 10
    return np.vstack([normal_data, anomaly_data])
