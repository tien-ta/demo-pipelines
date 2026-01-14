# Databricks notebook source
# MAGIC %md
# MAGIC # High-Risk WiFi Model Training
# MAGIC
# MAGIC This notebook trains a machine learning model to identify high-risk WiFi connections.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

import mlflow
import mlflow.sklearn
from pyspark.sql import SparkSession
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd

# Get parameters
dbutils.widgets.text("catalog", "dev_catalog", "Catalog")
dbutils.widgets.text("schema", "high_risk_wifi_dev", "Schema")
dbutils.widgets.text("model_name", "high_risk_wifi_classifier", "Model Name")
dbutils.widgets.text("experiment_path", "/Shared/high-risk-wifi/experiments", "Experiment Path")

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
training_data = spark.table(f"{catalog}.{schema}.wifi_features_training")
print(f"Loaded {training_data.count()} training samples")

# Convert to pandas for sklearn
train_pdf = training_data.toPandas()

# Separate features and target
feature_cols = [col for col in train_pdf.columns if col not in ['connection_id', 'is_high_risk', 'label']]
X_train = train_pdf[feature_cols]
y_train = train_pdf['is_high_risk']

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train Model

# COMMAND ----------

with mlflow.start_run(run_name="random_forest_training") as run:
    # Log parameters
    params = {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": 42
    }
    mlflow.log_params(params)

    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_train)
    y_pred_proba = model.predict_proba(X_train)[:, 1]

    # Log metrics
    auc = roc_auc_score(y_train, y_pred_proba)
    mlflow.log_metric("train_auc", auc)

    # Log model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name=model_name,
        input_example=X_train[:5],
        signature=mlflow.models.infer_signature(X_train, y_pred)
    )

    print(f"Model trained successfully!")
    print(f"Training AUC: {auc:.4f}")
    print(f"Run ID: {run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Validation

# COMMAND ----------

print("Classification Report:")
print(classification_report(y_train, y_pred))
