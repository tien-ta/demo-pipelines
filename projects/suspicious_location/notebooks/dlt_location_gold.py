# Databricks notebook source
import dlt
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %md
# MAGIC # Gold Layer - Feature-Enriched Location Data

# COMMAND ----------

@dlt.table(
    name="location_features_gold",
    comment="Feature-engineered location data ready for ML",
    table_properties={
        "quality": "gold"
    }
)
def location_features_gold():
    """
    Create features for anomaly detection from silver location data.
    """
    df = dlt.read("location_events_silver")

    # Time-based features
    df = df.withColumn("hour_of_day", F.hour("timestamp"))
    df = df.withColumn("day_of_week", F.dayofweek("timestamp"))
    df = df.withColumn("is_weekend", F.when(F.col("day_of_week").isin([1, 7]), 1).otherwise(0))
    df = df.withColumn("is_night", F.when(F.col("hour_of_day").between(22, 6), 1).otherwise(0))
    df = df.withColumn("is_business_hours", F.when(F.col("hour_of_day").between(9, 17), 1).otherwise(0))

    # User movement window
    user_window = Window.partitionBy("user_id").orderBy("timestamp")

    # Previous location
    df = df.withColumn("prev_latitude", F.lag("latitude").over(user_window))
    df = df.withColumn("prev_longitude", F.lag("longitude").over(user_window))
    df = df.withColumn("prev_timestamp", F.lag("timestamp").over(user_window))

    # Distance calculation (simplified - use UDF for precise Haversine)
    df = df.withColumn("lat_diff", F.abs(F.col("latitude") - F.col("prev_latitude")))
    df = df.withColumn("lon_diff", F.abs(F.col("longitude") - F.col("prev_longitude")))
    df = df.withColumn("distance_from_prev_km",
                      (F.col("lat_diff") + F.col("lon_diff")) * 111)  # Rough approximation

    # Time since previous
    df = df.withColumn("time_since_prev_hours",
                      (F.col("timestamp").cast("long") - F.col("prev_timestamp").cast("long")) / 3600)

    # Velocity
    df = df.withColumn("velocity_kmh",
                      F.when(F.col("time_since_prev_hours") > 0,
                            F.col("distance_from_prev_km") / F.col("time_since_prev_hours")
                      ).otherwise(0))

    # User statistics (rolling window)
    stats_window = Window.partitionBy("user_id").orderBy("timestamp").rowsBetween(-100, -1)

    df = df.withColumn("user_avg_latitude", F.avg("latitude").over(stats_window))
    df = df.withColumn("user_avg_longitude", F.avg("longitude").over(stats_window))

    # Distance from typical location
    df = df.withColumn("lat_from_typical", F.abs(F.col("latitude") - F.col("user_avg_latitude")))
    df = df.withColumn("lon_from_typical", F.abs(F.col("longitude") - F.col("user_avg_longitude")))
    df = df.withColumn("distance_from_typical_km",
                      (F.col("lat_from_typical") + F.col("lon_from_typical")) * 111)

    # Location frequency
    df = df.withColumn("location_visit_count",
                      F.count("*").over(
                          Window.partitionBy("user_id",
                                           F.round("latitude", 2),
                                           F.round("longitude", 2))
                      ))

    # Risk indicators
    df = df.withColumn("impossible_velocity", F.when(F.col("velocity_kmh") > 800, 1).otherwise(0))
    df = df.withColumn("far_from_typical", F.when(F.col("distance_from_typical_km") > 100, 1).otherwise(0))
    df = df.withColumn("is_new_location", F.when(F.col("location_visit_count") == 1, 1).otherwise(0))
    df = df.withColumn("unusual_time",
                      F.when((F.col("is_night") == 1) & (F.col("is_weekend") == 0), 1).otherwise(0))

    return df.na.fill(0)
