# Databricks notebook source
# MAGIC %md
# MAGIC # High-Risk WiFi Batch Inference
# MAGIC
# MAGIC This notebook performs batch inference on new WiFi connection data.

# COMMAND ----------

import mlflow
import mlflow.pyfunc
from pyspark.sql import functions as F
from datetime import datetime

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "high_risk_wifi_dev", "Schema")
dbutils.widgets.text("model_name", "high_risk_wifi_classifier", "Model Name")
dbutils.widgets.text("input_table", "wifi_connections_raw", "Input Table")
dbutils.widgets.text("output_table", "wifi_risk_scores", "Output Table")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
model_name = dbutils.widgets.get("model_name")
input_table = dbutils.widgets.get("input_table")
output_table = dbutils.widgets.get("output_table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Model and Data

# COMMAND ----------

# Load the model
model_uri = f"models:/{model_name}/Production"
model = mlflow.pyfunc.spark_udf(spark, model_uri, result_type="double")

# Load input data
input_df = spark.table(f"{catalog}.{schema}.{input_table}")
print(f"Loaded {input_df.count()} records for inference")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Inference

# COMMAND ----------

# Get feature columns
feature_cols = [col for col in input_df.columns if col not in ['connection_id', 'timestamp']]

# Apply model
predictions_df = input_df.withColumn(
    "risk_score",
    model(*feature_cols)
).withColumn(
    "is_high_risk",
    F.when(F.col("risk_score") > 0.5, True).otherwise(False)
).withColumn(
    "inference_timestamp",
    F.current_timestamp()
)

print(f"Generated {predictions_df.count()} predictions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Results

# COMMAND ----------

# Write to output table
predictions_df.write.format("delta").mode("append").saveAsTable(
    f"{catalog}.{schema}.{output_table}"
)

print(f"Results saved to {catalog}.{schema}.{output_table}")

# Show sample results
display(predictions_df.orderBy(F.desc("risk_score")).limit(10))
