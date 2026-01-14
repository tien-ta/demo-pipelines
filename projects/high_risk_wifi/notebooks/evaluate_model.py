# Databricks notebook source
# MAGIC %md
# MAGIC # High-Risk WiFi Model Evaluation
# MAGIC
# MAGIC This notebook evaluates the trained model on test data.

# COMMAND ----------

import mlflow
import mlflow.sklearn
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import pandas as pd
import matplotlib.pyplot as plt

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "high_risk_wifi_dev", "Schema")
dbutils.widgets.text("model_name", "high_risk_wifi_classifier", "Model Name")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
model_name = dbutils.widgets.get("model_name")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Test Data and Model

# COMMAND ----------

# Load test data
test_data = spark.table(f"{catalog}.{schema}.wifi_features_test")
test_pdf = test_data.toPandas()

feature_cols = [col for col in test_pdf.columns if col not in ['connection_id', 'is_high_risk', 'label']]
X_test = test_pdf[feature_cols]
y_test = test_pdf['is_high_risk']

# Load latest model version
model_uri = f"models:/{model_name}/latest"
model = mlflow.sklearn.load_model(model_uri)

print(f"Loaded model: {model_name}")
print(f"Test samples: {len(X_test)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evaluate Model Performance

# COMMAND ----------

# Make predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Calculate metrics
test_auc = roc_auc_score(y_test, y_pred_proba)

print(f"Test AUC: {test_auc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(cm)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log Evaluation Metrics

# COMMAND ----------

with mlflow.start_run(run_name="model_evaluation"):
    mlflow.log_metric("test_auc", test_auc)
    mlflow.log_param("model_name", model_name)
    mlflow.log_param("test_samples", len(X_test))

    print("Evaluation metrics logged successfully!")
