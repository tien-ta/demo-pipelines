# Databricks notebook source
# MAGIC %md
# MAGIC # Critical Location Alert System
# MAGIC
# MAGIC Generate alerts for critical suspicious location detections.

# COMMAND ----------

from pyspark.sql import functions as F
import json

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "suspicious_location_dev", "Schema")
dbutils.widgets.text("alert_threshold", "0.9", "Alert Threshold")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
alert_threshold = float(dbutils.widgets.get("alert_threshold"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Recent Suspicious Detections

# COMMAND ----------

# Get detections from last hour
recent_detections = spark.table(f"{catalog}.{schema}.location_risk_scores").filter(
    (F.col("inference_timestamp") >= F.expr("current_timestamp() - interval 1 hour")) &
    (F.col("is_suspicious") == 1)
)

print(f"Found {recent_detections.count()} suspicious detections in last hour")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Identify Critical Alerts

# COMMAND ----------

# Filter for critical threshold (using negative anomaly score)
critical_alerts = recent_detections.filter(
    -F.col("anomaly_score") > alert_threshold
).select(
    "event_id",
    "user_id",
    "timestamp",
    "anomaly_score",
    "risk_level",
    "velocity_kmh",
    "distance_from_typical_km",
    "impossible_velocity",
    "inference_timestamp"
).orderBy(F.desc("anomaly_score"))

critical_count = critical_alerts.count()
print(f"Found {critical_count} CRITICAL alerts requiring immediate attention")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Alert Notifications

# COMMAND ----------

if critical_count > 0:
    # Collect critical alerts
    alerts_list = critical_alerts.limit(50).collect()

    # Format alert message
    alert_message = f"""
    🚨 CRITICAL LOCATION ALERTS 🚨

    Time: {pd.Timestamp.now()}
    Critical Detections: {critical_count}
    Threshold: {alert_threshold}

    Top 10 Critical Alerts:
    """

    for i, alert in enumerate(alerts_list[:10], 1):
        alert_message += f"""
    {i}. User: {alert.user_id}
       Event: {alert.event_id}
       Time: {alert.timestamp}
       Anomaly Score: {alert.anomaly_score:.4f}
       Velocity: {alert.velocity_kmh:.1f} km/h
       Distance from Typical: {alert.distance_from_typical_km:.1f} km
       Impossible Travel: {alert.impossible_velocity}
    """

    print(alert_message)

    # Save alerts to table
    critical_alerts.write.format("delta").mode("append").saveAsTable(
        f"{catalog}.{schema}.critical_location_alerts"
    )

    # TODO: Send to alerting system (PagerDuty, Slack, etc.)
    # Example: send_to_slack(alert_message)
    # Example: send_to_pagerduty(critical_alerts)

else:
    print("✅ No critical alerts at this time")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Dashboard

# COMMAND ----------

# Alert summary
display(
    recent_detections
    .groupBy("risk_level")
    .agg(
        F.count("*").alias("count"),
        F.avg("anomaly_score").alias("avg_anomaly_score"),
        F.max("velocity_kmh").alias("max_velocity")
    )
    .orderBy("risk_level")
)
