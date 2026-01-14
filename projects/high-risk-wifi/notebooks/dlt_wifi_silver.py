# Databricks notebook source
import dlt
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Layer - Cleaned and Validated WiFi Data

# COMMAND ----------

@dlt.table(
    name="wifi_connections_silver",
    comment="Cleaned and validated WiFi connection data",
    table_properties={
        "quality": "silver"
    }
)
@dlt.expect_or_drop("valid_timestamp", "timestamp IS NOT NULL")
@dlt.expect_or_drop("valid_ssid", "ssid IS NOT NULL AND ssid != ''")
@dlt.expect_or_drop("valid_signal_strength", "signal_strength BETWEEN -100 AND 0")
def wifi_connections_silver():
    """
    Clean and validate bronze WiFi data.
    """
    return (
        dlt.read_stream("wifi_connections_bronze")
        .select(
            F.col("connection_id"),
            F.to_timestamp("timestamp").alias("timestamp"),
            F.col("ssid"),
            F.col("bssid"),
            F.col("signal_strength").cast("int"),
            F.col("security_type"),
            F.col("frequency").cast("int"),
            F.col("location_lat").cast("double"),
            F.col("location_lon").cast("double"),
            F.col("device_id")
        )
        .dropDuplicates(["connection_id"])
    )
