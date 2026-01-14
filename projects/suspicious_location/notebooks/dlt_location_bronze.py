# Databricks notebook source
import dlt
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC # Bronze Layer - Raw Location Event Data

# COMMAND ----------

@dlt.table(
    name="location_events_bronze",
    comment="Raw location event data from source systems",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.zOrderCols": "timestamp,user_id"
    }
)
def location_events_bronze():
    """
    Ingest raw location event data from cloud storage.
    """
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/tmp/location_schema")
        .load("/mnt/source/location-events/")
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("source_file", F.input_file_name())
    )
