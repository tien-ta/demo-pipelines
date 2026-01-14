# Databricks notebook source
# MAGIC %md
# MAGIC # Suspicious Location Batch Inference
# MAGIC
# MAGIC Score location events for suspicious patterns.

# COMMAND ----------

import mlflow
import mlflow.pyfunc
from pyspark.sql import functions as F

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "suspicious_location_dev", "Schema")
dbutils.widgets.text("model_name", "suspicious_location_detector", "Model Name")
dbutils.widgets.text("input_table", "location_events_raw", "Input Table")
dbutils.widgets.text("output_table", "location_risk_scores", "Output Table")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
model_name = dbutils.widgets.get("model_name")
input_table = dbutils.widgets.get("input_table")
output_table = dbutils.widgets.get("output_table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Model and Data

# COMMAND ----------

# Load the production model
model_uri = f"models:/{model_name}/Production"
loaded_model = mlflow.sklearn.load_model(model_uri)

# Load input features
input_df = spark.table(f"{catalog}.{schema}.{input_table}")
print(f"Loaded {input_df.count()} records for inference")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prepare Features

# COMMAND ----------

# Feature columns (must match training)
feature_cols = [
    "hour_of_day", "day_of_week", "is_weekend", "is_night", "is_business_hours",
    "distance_from_prev_km", "time_since_prev_hours", "velocity_kmh",
    "distance_from_typical_km", "location_visit_count",
    "impossible_velocity", "far_from_typical", "is_new_location", "unusual_time"
]

# Convert to pandas for sklearn inference
input_pdf = input_df.select(["event_id", "user_id", "timestamp"] + feature_cols).toPandas()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Inference

# COMMAND ----------

import numpy as np

# Extract features
X = input_pdf[feature_cols]

# Make predictions
predictions = loaded_model.predict(X)
anomaly_scores = loaded_model.named_steps['model'].score_samples(
    loaded_model.named_steps['scaler'].transform(X)
)

# Convert to binary (1 = suspicious, 0 = normal)
predictions_binary = np.where(predictions == -1, 1, 0)

# Add to dataframe
input_pdf['anomaly_score'] = anomaly_scores
input_pdf['is_suspicious'] = predictions_binary
input_pdf['risk_level'] = pd.cut(
    -anomaly_scores,  # Negative so higher = more suspicious
    bins=[float('-inf'), -0.5, -0.3, 0],
    labels=['low', 'medium', 'high']
)
input_pdf['inference_timestamp'] = pd.Timestamp.now()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Results

# COMMAND ----------

# Convert back to Spark DataFrame
results_df = spark.createDataFrame(input_pdf)

# Write to output table
results_df.write.format("delta").mode("append").saveAsTable(
    f"{catalog}.{schema}.{output_table}"
)

# Summary statistics
suspicious_count = sum(predictions_binary)
total_count = len(predictions_binary)
suspicious_rate = suspicious_count / total_count

print(f"Results saved to {catalog}.{schema}.{output_table}")
print(f"Detected {suspicious_count} suspicious locations out of {total_count} ({suspicious_rate:.2%})")

# Show top suspicious results
display(
    results_df
    .orderBy(F.desc("anomaly_score"))
    .select("event_id", "user_id", "timestamp", "anomaly_score", "is_suspicious", "risk_level")
    .limit(20)
)
