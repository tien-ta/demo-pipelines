# High-Risk WiFi Detection

Databricks Asset Bundle for detecting high-risk WiFi connections using machine learning.

## Overview

This project implements an end-to-end ML pipeline for identifying potentially risky WiFi networks based on various signal, security, and contextual features.

## Project Structure

```
high-risk-wifi/
├── databricks.yml              # Main bundle configuration
├── resources/                  # Resource definitions
│   ├── models.yml             # MLflow model registry
│   ├── experiments.yml        # MLflow experiments
│   ├── jobs.yml               # Databricks jobs
│   ├── model_serving.yml      # Model serving endpoints
│   └── pipelines.yml          # Delta Live Tables
├── notebooks/                  # Databricks notebooks
│   ├── train_model.py         # Model training
│   ├── evaluate_model.py      # Model evaluation
│   ├── batch_inference.py     # Batch scoring
│   ├── dlt_wifi_bronze.py     # Bronze layer DLT
│   ├── dlt_wifi_silver.py     # Silver layer DLT
│   └── dlt_wifi_gold.py       # Gold layer DLT
├── src/                        # Python source code
│   ├── __init__.py
│   ├── features.py            # Feature engineering
│   └── inference.py           # Inference utilities
└── setup.py                    # Package setup
```

## Components

### Data Pipeline (Delta Live Tables)
- **Bronze Layer**: Raw WiFi connection data ingestion
- **Silver Layer**: Cleaned and validated data
- **Gold Layer**: Feature-engineered data ready for ML

### ML Lifecycle
- **Experiments**: Track model training experiments
- **Model Registry**: Version and manage trained models
- **Model Serving**: Real-time inference endpoint
- **Batch Inference**: Scheduled batch scoring jobs

### Jobs
- **Model Training**: Daily retraining on new data
- **Batch Inference**: Hourly scoring of new connections

## Deployment

### Deploy to Development
```bash
databricks bundle deploy -t dev
```

### Deploy to Staging
```bash
databricks bundle deploy -t staging
```

### Deploy to Production
```bash
databricks bundle deploy -t prod
```

## Running Jobs

```bash
# Run training job
databricks bundle run model_training_job -t dev

# Run inference job
databricks bundle run batch_inference_job -t dev
```

## Model Features

The model uses the following feature categories:
- **Time-based**: hour of day, day of week, weekend indicator
- **Security**: encryption type, open network detection
- **Signal**: strength, quality, frequency band
- **Historical**: connection patterns, SSID reputation

## Permissions

The bundle manages permissions for:
- Model registry access
- Experiment tracking
- Job execution
- Endpoint querying
- Pipeline management

## Requirements

- Databricks Runtime 14.3 LTS ML or higher
- Unity Catalog enabled
- Appropriate service principals configured for production
