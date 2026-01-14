# Databricks notebook source
# MAGIC %md
# MAGIC # Suspicious Location Model Training
# MAGIC
# MAGIC This notebook trains an anomaly detection model to identify suspicious location patterns.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

import mlflow
import mlflow.sklearn
from pyspark.sql import SparkSession
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, precision_recall_fscore_support
import pandas as pd
import numpy as np

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "suspicious_location_dev", "Schema")
dbutils.widgets.text("model_name", "suspicious_location_detector", "Model Name")
dbutils.widgets.text("experiment_path", "/Shared/suspicious-location/experiments", "Experiment Path")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
model_name = dbutils.widgets.get("model_name")
experiment_path = dbutils.widgets.get("experiment_path")

# Set MLflow experiment
mlflow.set_experiment(f"{experiment_path}/model-training")

print(f"Training model for: {catalog}.{schema}")
print(f"Model will be registered as: {model_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Training Data

# COMMAND ----------

# Load feature table
training_data = spark.table(f"{catalog}.{schema}.location_features_training")
print(f"Loaded {training_data.count()} training samples")

# Convert to pandas for sklearn
train_pdf = training_data.toPandas()

# Separate features and labels (if available)
feature_cols = [col for col in train_pdf.columns if col not in
                ['event_id', 'user_id', 'timestamp', 'is_suspicious', 'latitude', 'longitude']]
X_train = train_pdf[feature_cols]

# Handle potential missing labels for unsupervised learning
has_labels = 'is_suspicious' in train_pdf.columns
if has_labels:
    y_train = train_pdf['is_suspicious']
else:
    y_train = None

print(f"Feature columns: {feature_cols}")
print(f"Feature shape: {X_train.shape}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train Anomaly Detection Model

# COMMAND ----------

with mlflow.start_run(run_name="isolation_forest_training") as run:
    # Log parameters
    params = {
        "n_estimators": 100,
        "max_samples": "auto",
        "contamination": 0.05,  # Expect 5% anomalies
        "random_state": 42,
        "max_features": 1.0
    }
    mlflow.log_params(params)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Train Isolation Forest
    model = IsolationForest(**params)
    model.fit(X_train_scaled)

    # Get anomaly scores (-1 for anomalies, 1 for normal)
    y_pred = model.predict(X_train_scaled)
    anomaly_scores = model.score_samples(X_train_scaled)

    # Convert predictions: -1 (anomaly) -> 1 (suspicious), 1 (normal) -> 0
    y_pred_binary = np.where(y_pred == -1, 1, 0)

    # Calculate metrics
    n_anomalies = sum(y_pred_binary)
    anomaly_rate = n_anomalies / len(y_pred_binary)

    mlflow.log_metric("detected_anomalies", n_anomalies)
    mlflow.log_metric("anomaly_rate", anomaly_rate)
    mlflow.log_metric("avg_anomaly_score", anomaly_scores.mean())

    # If we have labels, calculate supervised metrics
    if has_labels and y_train is not None:
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_train, y_pred_binary, average='binary'
        )
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        print("Classification Report:")
        print(classification_report(y_train, y_pred_binary))

    # Create a pipeline with scaler and model
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([
        ('scaler', scaler),
        ('model', model)
    ])

    # Log model
    mlflow.sklearn.log_model(
        pipeline,
        "model",
        registered_model_name=model_name,
        input_example=X_train[:5],
        signature=mlflow.models.infer_signature(X_train, y_pred_binary)
    )

    print(f"Model trained successfully!")
    print(f"Detected anomalies: {n_anomalies} ({anomaly_rate:.2%})")
    print(f"Run ID: {run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Analyze Top Suspicious Patterns

# COMMAND ----------

# Add predictions to training data
train_pdf['anomaly_score'] = anomaly_scores
train_pdf['is_anomaly'] = y_pred_binary

# Show top suspicious locations
top_suspicious = train_pdf.nlargest(10, 'anomaly_score')[
    ['user_id', 'timestamp', 'anomaly_score'] + feature_cols[:5]
]

print("Top 10 Most Suspicious Location Patterns:")
display(top_suspicious)
