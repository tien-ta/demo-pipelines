# Databricks notebook source
import dlt
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Layer - Cleaned and Validated Location Data

# COMMAND ----------

@dlt.table(
    name="location_events_silver",
    comment="Cleaned and validated location event data",
    table_properties={
        "quality": "silver"
    }
)
@dlt.expect_or_drop("valid_timestamp", "timestamp IS NOT NULL")
@dlt.expect_or_drop("valid_user_id", "user_id IS NOT NULL AND user_id != ''")
@dlt.expect_or_drop("valid_latitude", "latitude BETWEEN -90 AND 90")
@dlt.expect_or_drop("valid_longitude", "longitude BETWEEN -180 AND 180")
@dlt.expect("reasonable_accuracy", "accuracy_meters < 1000")
def location_events_silver():
    """
    Clean and validate bronze location data.
    """
    return (
        dlt.read_stream("location_events_bronze")
        .select(
            F.col("event_id"),
            F.col("user_id"),
            F.to_timestamp("timestamp").alias("timestamp"),
            F.col("latitude").cast("double"),
            F.col("longitude").cast("double"),
            F.col("accuracy_meters").cast("double"),
            F.col("altitude_meters").cast("double"),
            F.col("speed_mps").cast("double"),
            F.col("bearing_degrees").cast("double"),
            F.col("device_id"),
            F.col("app_version"),
            F.col("source_file"),
            F.col("ingestion_timestamp")
        )
        .dropDuplicates(["event_id", "user_id"])
        .withColumn("processing_timestamp", F.current_timestamp())
    )
