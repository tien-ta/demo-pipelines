# Databricks notebook source
import dlt
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC # Geographic Enrichment Layer

# COMMAND ----------

@dlt.table(
    name="location_geo_enriched",
    comment="Location data enriched with geographic context",
    table_properties={
        "quality": "gold"
    }
)
def location_geo_enriched():
    """
    Enrich location data with geographic information.

    This could include:
    - Country/city reverse geocoding
    - Point of interest proximity
    - Geofence zone detection
    - Risk zone classification
    """
    df = dlt.read("location_events_silver")

    # TODO: Add geofencing logic
    # Example: Detect if location is within restricted zones
    df = df.withColumn("in_restricted_zone", F.lit(False))

    # TODO: Add reverse geocoding
    # Example: Use external API or reference tables to get country/city
    df = df.withColumn("country_code", F.lit("UNKNOWN"))
    df = df.withColumn("city", F.lit("UNKNOWN"))

    # TODO: Add POI proximity
    # Example: Distance to nearest office, airport, border crossing
    df = df.withColumn("distance_to_nearest_office_km", F.lit(0.0))

    # Geographic risk score based on known risk areas
    df = df.withColumn("geographic_risk_score",
                      F.when(F.col("in_restricted_zone"), 1.0)
                      .otherwise(0.0))

    return df
