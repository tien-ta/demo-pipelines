# Databricks notebook source
import dlt
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC # Bronze Layer - Raw WiFi Connection Data

# COMMAND ----------

@dlt.table(
    name="wifi_connections_bronze",
    comment="Raw WiFi connection data from source systems",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.zOrderCols": "timestamp"
    }
)
def wifi_connections_bronze():
    """
    Ingest raw WiFi connection data from cloud storage.
    """
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/tmp/wifi_schema")
        .load("/mnt/source/wifi-connections/")
        .withColumn("ingestion_timestamp", F.current_timestamp())
    )
