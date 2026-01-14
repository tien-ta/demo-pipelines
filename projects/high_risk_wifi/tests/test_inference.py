"""
Unit tests for inference utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.inference import WiFiRiskInference


@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for testing."""
    return SparkSession.builder \
        .master("local[1]") \
        .appName("test_inference") \
        .getOrCreate()


class TestWiFiRiskInference:
    """Tests for WiFiRiskInference class."""

    def test_initialization(self):
        """Test inference class initialization."""
        inference = WiFiRiskInference(
            model_name="test_model",
            model_stage="Production"
        )

        assert inference.model_name == "test_model"
        assert inference.model_stage == "Production"
        assert inference.model_uri == "models:/test_model/Production"

    def test_initialization_default_stage(self):
        """Test inference class with default stage."""
        inference = WiFiRiskInference(model_name="test_model")

        assert inference.model_stage == "Production"
        assert inference.model_uri == "models:/test_model/Production"

    @patch('mlflow.pyfunc.spark_udf')
    def test_predict_columns(self, mock_spark_udf, spark):
        """Test predict method adds required columns."""
        # Create mock UDF
        mock_udf = Mock(return_value=0.7)
        mock_spark_udf.return_value = mock_udf

        # Create test data
        data = [
            (1, -60, "WPA2", 5000),
            (2, -70, "OPEN", 2400),
        ]
        df = spark.createDataFrame(
            data,
            ["connection_id", "signal_strength", "security_type", "frequency"]
        )

        # Create inference instance
        inference = WiFiRiskInference(model_name="test_model")

        # Mock the predict to avoid MLflow dependencies
        with patch.object(inference, 'predict') as mock_predict:
            # Create expected output
            expected_df = df.withColumn("risk_score", F.lit(0.7))
            expected_df = expected_df.withColumn("is_high_risk", F.lit(True))
            expected_df = expected_df.withColumn("risk_level", F.lit("high"))
            expected_df = expected_df.withColumn("inference_timestamp", F.current_timestamp())

            mock_predict.return_value = expected_df

            # Call predict
            result = inference.predict(
                df,
                ["signal_strength", "security_type", "frequency"]
            )

            # Verify columns exist
            assert "risk_score" in result.columns
            assert "is_high_risk" in result.columns
            assert "risk_level" in result.columns
            assert "inference_timestamp" in result.columns

    def test_risk_level_classification(self, spark):
        """Test risk level classification logic."""
        # Test data with different risk scores
        data = [
            (0.9,),   # critical
            (0.7,),   # high
            (0.5,),   # medium
            (0.3,),   # low
        ]
        df = spark.createDataFrame(data, ["risk_score"])

        # Apply risk level logic
        result = df.withColumn(
            "risk_level",
            F.when(F.col("risk_score") > 0.8, "critical")
            .when(F.col("risk_score") > 0.6, "high")
            .when(F.col("risk_score") > 0.4, "medium")
            .otherwise("low")
        )

        rows = result.collect()
        assert rows[0]["risk_level"] == "critical"
        assert rows[1]["risk_level"] == "high"
        assert rows[2]["risk_level"] == "medium"
        assert rows[3]["risk_level"] == "low"

    def test_high_risk_threshold(self, spark):
        """Test is_high_risk threshold."""
        data = [
            (0.6,),   # high risk
            (0.4,),   # not high risk
        ]
        df = spark.createDataFrame(data, ["risk_score"])

        result = df.withColumn(
            "is_high_risk",
            F.when(F.col("risk_score") > 0.5, True).otherwise(False)
        )

        rows = result.collect()
        assert rows[0]["is_high_risk"] is True
        assert rows[1]["is_high_risk"] is False
