# Databricks notebook source
import dlt
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %md
# MAGIC # Gold Layer - Feature-Enriched WiFi Data

# COMMAND ----------

@dlt.table(
    name="wifi_features_gold",
    comment="Feature-engineered WiFi data ready for ML",
    table_properties={
        "quality": "gold"
    }
)
def wifi_features_gold():
    """
    Create features for machine learning from silver WiFi data.
    """
    df = dlt.read("wifi_connections_silver")

    # Time-based features
    df = df.withColumn("hour_of_day", F.hour("timestamp"))
    df = df.withColumn("day_of_week", F.dayofweek("timestamp"))
    df = df.withColumn("is_weekend", F.when(F.col("day_of_week").isin([1, 7]), 1).otherwise(0))

    # Security features
    df = df.withColumn("is_open_network", F.when(F.col("security_type") == "OPEN", 1).otherwise(0))
    df = df.withColumn("is_wep", F.when(F.col("security_type") == "WEP", 1).otherwise(0))

    # Signal features
    df = df.withColumn("signal_quality",
        F.when(F.col("signal_strength") > -50, "excellent")
        .when(F.col("signal_strength") > -60, "good")
        .when(F.col("signal_strength") > -70, "fair")
        .otherwise("poor")
    )

    # Frequency features
    df = df.withColumn("is_5ghz", F.when(F.col("frequency") > 5000, 1).otherwise(0))

    # Historical features (connection count per SSID)
    window_spec = Window.partitionBy("ssid")
    df = df.withColumn("ssid_connection_count", F.count("*").over(window_spec))

    return df
