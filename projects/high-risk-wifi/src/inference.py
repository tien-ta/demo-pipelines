"""
Inference utilities for WiFi risk detection.
"""

import mlflow
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from typing import List


class WiFiRiskInference:
    """
    Class for performing inference with WiFi risk models.
    """

    def __init__(self, model_name: str, model_stage: str = "Production"):
        """
        Initialize inference class.

        Args:
            model_name: Name of registered model
            model_stage: Model stage (Production, Staging, None)
        """
        self.model_name = model_name
        self.model_stage = model_stage
        self.model_uri = f"models:/{model_name}/{model_stage}"

    def predict(self, df: DataFrame, feature_cols: List[str]) -> DataFrame:
        """
        Run batch inference on DataFrame.

        Args:
            df: Input DataFrame with features
            feature_cols: List of feature column names

        Returns:
            DataFrame with predictions
        """
        # Load model as Spark UDF
        from pyspark.sql import SparkSession
        spark = SparkSession.getActiveSession()

        model_udf = mlflow.pyfunc.spark_udf(
            spark,
            self.model_uri,
            result_type="double"
        )

        # Apply model
        predictions = (
            df
            .withColumn("risk_score", model_udf(*feature_cols))
            .withColumn("is_high_risk", F.when(F.col("risk_score") > 0.5, True).otherwise(False))
            .withColumn("risk_level",
                F.when(F.col("risk_score") > 0.8, "critical")
                .when(F.col("risk_score") > 0.6, "high")
                .when(F.col("risk_score") > 0.4, "medium")
                .otherwise("low")
            )
            .withColumn("inference_timestamp", F.current_timestamp())
        )

        return predictions

    def predict_batch(self, input_table: str, output_table: str, feature_cols: List[str]):
        """
        Run batch inference from input table to output table.

        Args:
            input_table: Fully qualified input table name
            output_table: Fully qualified output table name
            feature_cols: List of feature column names
        """
        from pyspark.sql import SparkSession
        spark = SparkSession.getActiveSession()

        # Read input
        df = spark.table(input_table)

        # Run inference
        predictions = self.predict(df, feature_cols)

        # Write output
        predictions.write.format("delta").mode("append").saveAsTable(output_table)

        return predictions.count()
