"""
Unit tests for feature engineering functions.
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime

from src.features import (
    extract_time_features,
    extract_security_features,
    extract_signal_features
)


@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for testing."""
    return SparkSession.builder \
        .master("local[1]") \
        .appName("test_features") \
        .getOrCreate()


class TestTimeFeatures:
    """Tests for time-based feature extraction."""

    def test_extract_time_features_hour(self, spark):
        """Test hour of day extraction."""
        data = [("2024-01-15 14:30:00",)]
        df = spark.createDataFrame(data, ["timestamp"])
        df = df.withColumn("timestamp", F.to_timestamp("timestamp"))

        result = extract_time_features(df)

        assert "hour_of_day" in result.columns
        assert result.first()["hour_of_day"] == 14

    def test_extract_time_features_day_of_week(self, spark):
        """Test day of week extraction."""
        # 2024-01-15 is a Monday (day 2)
        data = [("2024-01-15 14:30:00",)]
        df = spark.createDataFrame(data, ["timestamp"])
        df = df.withColumn("timestamp", F.to_timestamp("timestamp"))

        result = extract_time_features(df)

        assert "day_of_week" in result.columns
        assert result.first()["day_of_week"] == 2

    def test_extract_time_features_weekend(self, spark):
        """Test weekend detection."""
        # Saturday
        data_weekend = [("2024-01-13 14:30:00",)]
        df_weekend = spark.createDataFrame(data_weekend, ["timestamp"])
        df_weekend = df_weekend.withColumn("timestamp", F.to_timestamp("timestamp"))

        # Monday
        data_weekday = [("2024-01-15 14:30:00",)]
        df_weekday = spark.createDataFrame(data_weekday, ["timestamp"])
        df_weekday = df_weekday.withColumn("timestamp", F.to_timestamp("timestamp"))

        result_weekend = extract_time_features(df_weekend)
        result_weekday = extract_time_features(df_weekday)

        assert result_weekend.first()["is_weekend"] == 1
        assert result_weekday.first()["is_weekend"] == 0

    def test_extract_time_features_night(self, spark):
        """Test night time detection."""
        # Night time (23:00)
        data_night = [("2024-01-15 23:00:00",)]
        df_night = spark.createDataFrame(data_night, ["timestamp"])
        df_night = df_night.withColumn("timestamp", F.to_timestamp("timestamp"))

        # Day time (14:00)
        data_day = [("2024-01-15 14:00:00",)]
        df_day = spark.createDataFrame(data_day, ["timestamp"])
        df_day = df_day.withColumn("timestamp", F.to_timestamp("timestamp"))

        result_night = extract_time_features(df_night)
        result_day = extract_time_features(df_day)

        assert result_night.first()["is_night"] == 1
        assert result_day.first()["is_night"] == 0


class TestSecurityFeatures:
    """Tests for security-based feature extraction."""

    def test_open_network_detection(self, spark):
        """Test open network detection."""
        data = [
            ("OPEN",),
            ("WPA2",),
        ]
        df = spark.createDataFrame(data, ["security_type"])

        result = extract_security_features(df)

        rows = result.collect()
        assert rows[0]["is_open_network"] == 1
        assert rows[1]["is_open_network"] == 0

    def test_wep_detection(self, spark):
        """Test WEP network detection."""
        data = [
            ("WEP",),
            ("WPA2",),
        ]
        df = spark.createDataFrame(data, ["security_type"])

        result = extract_security_features(df)

        rows = result.collect()
        assert rows[0]["is_wep"] == 1
        assert rows[1]["is_wep"] == 0

    def test_wpa_detection(self, spark):
        """Test WPA network detection."""
        data = [
            ("WPA2",),
            ("WPA3",),
            ("WEP",),
        ]
        df = spark.createDataFrame(data, ["security_type"])

        result = extract_security_features(df)

        rows = result.collect()
        assert rows[0]["is_wpa"] == 1
        assert rows[1]["is_wpa"] == 1
        assert rows[2]["is_wpa"] == 0


class TestSignalFeatures:
    """Tests for signal strength feature extraction."""

    def test_signal_quality_excellent(self, spark):
        """Test excellent signal quality detection."""
        data = [(-45,)]
        df = spark.createDataFrame(data, ["signal_strength"])

        result = extract_signal_features(df)

        assert result.first()["signal_quality"] == 4

    def test_signal_quality_good(self, spark):
        """Test good signal quality detection."""
        data = [(-55,)]
        df = spark.createDataFrame(data, ["signal_strength"])

        result = extract_signal_features(df)

        assert result.first()["signal_quality"] == 3

    def test_signal_quality_fair(self, spark):
        """Test fair signal quality detection."""
        data = [(-65,)]
        df = spark.createDataFrame(data, ["signal_strength"])

        result = extract_signal_features(df)

        assert result.first()["signal_quality"] == 2

    def test_signal_quality_poor(self, spark):
        """Test poor signal quality detection."""
        data = [(-75,)]
        df = spark.createDataFrame(data, ["signal_strength"])

        result = extract_signal_features(df)

        assert result.first()["signal_quality"] == 1

    def test_weak_signal_detection(self, spark):
        """Test weak signal detection."""
        data = [
            (-75,),
            (-60,),
        ]
        df = spark.createDataFrame(data, ["signal_strength"])

        result = extract_signal_features(df)

        rows = result.collect()
        assert rows[0]["is_weak_signal"] == 1
        assert rows[1]["is_weak_signal"] == 0
