# Databricks notebook source
# MAGIC %md
# MAGIC # Location Feature Engineering
# MAGIC
# MAGIC Extract features from location data for anomaly detection.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window
import math

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "suspicious_location_dev", "Schema")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Silver Layer Data

# COMMAND ----------

location_data = spark.table(f"{catalog}.{schema}.location_events_silver")
print(f"Loaded {location_data.count()} location events")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract Temporal Features

# COMMAND ----------

def extract_temporal_features(df):
    """Extract time-based features."""
    return (
        df
        .withColumn("hour_of_day", F.hour("timestamp"))
        .withColumn("day_of_week", F.dayofweek("timestamp"))
        .withColumn("is_weekend", F.when(F.col("day_of_week").isin([1, 7]), 1).otherwise(0))
        .withColumn("is_night", F.when(F.col("hour_of_day").between(22, 6), 1).otherwise(0))
        .withColumn("is_business_hours", F.when(F.col("hour_of_day").between(9, 17), 1).otherwise(0))
    )

features_df = extract_temporal_features(location_data)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract Movement Features

# COMMAND ----------

# Window for user's location history
user_window = Window.partitionBy("user_id").orderBy("timestamp")

# Calculate movement features
features_df = (
    features_df
    .withColumn("prev_latitude", F.lag("latitude").over(user_window))
    .withColumn("prev_longitude", F.lag("longitude").over(user_window))
    .withColumn("prev_timestamp", F.lag("timestamp").over(user_window))
)

# Calculate distance from previous location (Haversine formula)
@F.udf("double")
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    if any(x is None for x in [lat1, lon1, lat2, lon2]):
        return None

    R = 6371  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat/2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    return R * c

features_df = features_df.withColumn(
    "distance_from_prev_km",
    haversine_distance("prev_latitude", "prev_longitude", "latitude", "longitude")
)

# Calculate time difference
features_df = features_df.withColumn(
    "time_since_prev_hours",
    (F.col("timestamp").cast("long") - F.col("prev_timestamp").cast("long")) / 3600
)

# Calculate velocity
features_df = features_df.withColumn(
    "velocity_kmh",
    F.when(
        F.col("time_since_prev_hours") > 0,
        F.col("distance_from_prev_km") / F.col("time_since_prev_hours")
    ).otherwise(0)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract User Behavior Features

# COMMAND ----------

# User's typical location statistics (last 30 days)
user_stats_window = Window.partitionBy("user_id").orderBy("timestamp").rowsBetween(-720, -1)

features_df = (
    features_df
    .withColumn("user_avg_latitude", F.avg("latitude").over(user_stats_window))
    .withColumn("user_avg_longitude", F.avg("longitude").over(user_stats_window))
    .withColumn("user_std_latitude", F.stddev("latitude").over(user_stats_window))
    .withColumn("user_std_longitude", F.stddev("longitude").over(user_stats_window))
)

# Distance from user's typical location
features_df = features_df.withColumn(
    "distance_from_typical_km",
    haversine_distance("user_avg_latitude", "user_avg_longitude", "latitude", "longitude")
)

# Number of visits to similar location
features_df = features_df.withColumn(
    "location_visit_count",
    F.count("*").over(
        Window.partitionBy("user_id",
                          F.round("latitude", 2),
                          F.round("longitude", 2))
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract Risk Indicators

# COMMAND ----------

features_df = (
    features_df
    # Suspicious velocity (impossibly fast travel)
    .withColumn("impossible_velocity", F.when(F.col("velocity_kmh") > 800, 1).otherwise(0))

    # Far from typical location
    .withColumn("far_from_typical",
                F.when(F.col("distance_from_typical_km") > 100, 1).otherwise(0))

    # New location (never visited before)
    .withColumn("is_new_location", F.when(F.col("location_visit_count") == 1, 1).otherwise(0))

    # Unusual time
    .withColumn("unusual_time",
                F.when((F.col("is_night") == 1) & (F.col("is_weekend") == 0), 1).otherwise(0))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Feature Table

# COMMAND ----------

# Select final features
final_features = features_df.select(
    "event_id",
    "user_id",
    "timestamp",
    "latitude",
    "longitude",
    # Temporal features
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_night",
    "is_business_hours",
    # Movement features
    "distance_from_prev_km",
    "time_since_prev_hours",
    "velocity_kmh",
    # User behavior features
    "distance_from_typical_km",
    "location_visit_count",
    # Risk indicators
    "impossible_velocity",
    "far_from_typical",
    "is_new_location",
    "unusual_time"
).na.fill(0)

# Write to feature table
final_features.write.format("delta").mode("overwrite").saveAsTable(
    f"{catalog}.{schema}.location_features_gold"
)

print(f"Saved {final_features.count()} feature records to {catalog}.{schema}.location_features_gold")
display(final_features.limit(10))
