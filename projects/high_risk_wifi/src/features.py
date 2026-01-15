"""
Feature engineering utilities for WiFi risk detection.

This module provides functions for extracting features from WiFi connection data.
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
