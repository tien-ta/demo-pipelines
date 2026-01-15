"""
Feature engineering utilities for WiFi risk detection.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def extract_time_features(df: DataFrame, timestamp_col: str = "timestamp") -> DataFrame:
    """
    Extract time-based features from timestamp column.

    Args:
        df: Input DataFrame
        timestamp_col: Name of timestamp column

    Returns:
        DataFrame with additional time features
    """
    return (
        df
        .withColumn("hour_of_day", F.hour(timestamp_col))
        .withColumn("day_of_week", F.dayofweek(timestamp_col))
        .withColumn("is_weekend", F.when(F.col("day_of_week").isin([1, 7]), 1).otherwise(0))
        .withColumn("is_night", F.when(F.col("hour_of_day").between(22, 6), 1).otherwise(0))
    )


def extract_security_features(df: DataFrame) -> DataFrame:
    """
    Extract security-related features.

    Args:
        df: Input DataFrame with security_type column

    Returns:
        DataFrame with additional security features
    """
    return (
        df
        .withColumn("is_open_network", F.when(F.col("security_type") == "OPEN", 1).otherwise(0))
        .withColumn("is_wep", F.when(F.col("security_type") == "WEP", 1).otherwise(0))
        .withColumn("is_wpa", F.when(F.col("security_type").like("%WPA%"), 1).otherwise(0))
    )


def extract_signal_features(df: DataFrame) -> DataFrame:
    """
    Extract signal strength features.

    Args:
        df: Input DataFrame with signal_strength column

    Returns:
        DataFrame with additional signal features
    """
    return (
        df
        .withColumn("signal_quality",
            F.when(F.col("signal_strength") > -50, 4)  # excellent
            .when(F.col("signal_strength") > -60, 3)   # good
            .when(F.col("signal_strength") > -70, 2)   # fair
            .otherwise(1)                               # poor
        )
        .withColumn("is_weak_signal", F.when(F.col("signal_strength") < -70, 1).otherwise(0))
    )


def calculate_risk_score(signal_quality: int, is_open_network: int, is_wep: int) -> float:
    """
    Calculate a simple risk score based on network characteristics.

    Args:
        signal_quality: Signal quality rating (1-4)
        is_open_network: 1 if network is open, 0 otherwise
        is_wep: 1 if network uses WEP, 0 otherwise

    Returns:
        Risk score between 0 and 1
    """
    risk_score = 0.0

    # Open networks increase risk
    if is_open_network:
        risk_score += 0.5

    # WEP is insecure
    if is_wep:
        risk_score += 0.3

    # Weak signal might indicate spoofing
    if signal_quality <= 2:
        risk_score += 0.2

    return min(risk_score, 1.0)
