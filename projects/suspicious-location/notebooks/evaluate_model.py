# Databricks notebook source
# MAGIC %md
# MAGIC # Suspicious Location Model Evaluation
# MAGIC
# MAGIC This notebook evaluates the anomaly detection model on test data.

# COMMAND ----------

import mlflow
import mlflow.sklearn
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "suspicious_location_dev", "Schema")
dbutils.widgets.text("model_name", "suspicious_location_detector", "Model Name")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
model_name = dbutils.widgets.get("model_name")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Test Data and Model

# COMMAND ----------

# Load test data
test_data = spark.table(f"{catalog}.{schema}.location_features_test")
test_pdf = test_data.toPandas()

feature_cols = [col for col in test_pdf.columns if col not in
                ['event_id', 'user_id', 'timestamp', 'is_suspicious', 'latitude', 'longitude']]
X_test = test_pdf[feature_cols]

has_labels = 'is_suspicious' in test_pdf.columns
if has_labels:
    y_test = test_pdf['is_suspicious']

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
y_pred_binary = np.where(y_pred == -1, 1, 0)

# Get anomaly scores
anomaly_scores = model.named_steps['model'].score_samples(
    model.named_steps['scaler'].transform(X_test)
)

# Calculate detection metrics
n_anomalies = sum(y_pred_binary)
anomaly_rate = n_anomalies / len(y_pred_binary)

print(f"Detected Anomalies: {n_anomalies} ({anomaly_rate:.2%})")
print(f"Average Anomaly Score: {anomaly_scores.mean():.4f}")

# If we have ground truth labels
if has_labels:
    # Classification metrics
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_binary))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred_binary)
    print("\nConfusion Matrix:")
    print(cm)

    # AUC-ROC if possible
    if len(np.unique(y_test)) > 1:
        # Use negative anomaly scores as "probability" (more negative = more anomalous)
        auc = roc_auc_score(y_test, -anomaly_scores)
        print(f"\nAUC-ROC: {auc:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Analyze Detection Patterns

# COMMAND ----------

# Add predictions to test data
test_pdf['anomaly_score'] = anomaly_scores
test_pdf['detected_suspicious'] = y_pred_binary

# Analyze score distribution
print("Anomaly Score Statistics:")
print(test_pdf['anomaly_score'].describe())

# Show top suspicious detections
top_detections = test_pdf.nlargest(20, 'anomaly_score')[
    ['user_id', 'timestamp', 'anomaly_score', 'detected_suspicious'] + feature_cols[:5]
]

print("\nTop 20 Suspicious Detections:")
display(top_detections)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log Evaluation Metrics

# COMMAND ----------

with mlflow.start_run(run_name="model_evaluation"):
    mlflow.log_metric("test_anomaly_rate", anomaly_rate)
    mlflow.log_metric("test_avg_score", anomaly_scores.mean())
    mlflow.log_metric("test_samples", len(X_test))

    if has_labels:
        from sklearn.metrics import precision_recall_fscore_support
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred_binary, average='binary'
        )
        mlflow.log_metric("test_precision", precision)
        mlflow.log_metric("test_recall", recall)
        mlflow.log_metric("test_f1", f1)

        if len(np.unique(y_test)) > 1:
            mlflow.log_metric("test_auc", auc)

    mlflow.log_param("model_name", model_name)

    print("Evaluation metrics logged successfully!")
