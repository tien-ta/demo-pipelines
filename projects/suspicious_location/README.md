# Suspicious Location Detection

Databricks Asset Bundle for detecting suspicious location patterns and anomalies using machine learning.

## Overview

This project implements an end-to-end ML pipeline for identifying potentially suspicious location events based on user movement patterns, velocity analysis, geographic context, and behavioral anomalies.

## Project Structure

```
suspicious-location/
├── databricks.yml              # Main bundle configuration
├── resources/                  # Resource definitions
│   ├── models.yml             # MLflow model registry
│   ├── experiments.yml        # MLflow experiments
│   ├── jobs.yml               # Databricks jobs
│   ├── model_serving.yml      # Model serving endpoints
│   └── pipelines.yml          # Delta Live Tables
├── notebooks/                  # Databricks notebooks
│   ├── train_model.py         # Anomaly detection model training
│   ├── evaluate_model.py      # Model evaluation
│   ├── extract_features.py    # Feature engineering
│   ├── batch_inference.py     # Batch scoring
│   ├── alert_critical.py      # Critical alert generation
│   ├── dlt_location_bronze.py # Bronze layer DLT
│   ├── dlt_location_silver.py # Silver layer DLT
│   ├── dlt_location_gold.py   # Gold layer DLT
│   └── dlt_geo_enrichment.py  # Geographic enrichment
├── src/                        # Python source code
│   ├── __init__.py
│   ├── geo_utils.py           # Geographic calculations
│   └── anomaly_detection.py   # Anomaly detection utilities
└── setup.py                    # Package setup
```

## Components

### Data Pipeline (Delta Live Tables)
- **Bronze Layer**: Raw location event data ingestion
- **Silver Layer**: Cleaned and validated location data
- **Gold Layer**: Feature-engineered data with movement patterns
- **Geo Enrichment**: Geographic context and risk zones

### ML Lifecycle
- **Experiments**: Track anomaly detection experiments
- **Model Registry**: Version and manage trained models
- **Model Serving**: Real-time anomaly scoring endpoint
- **Batch Inference**: Scheduled scoring with alerting

### Jobs
- **Location Analysis**: Daily pattern analysis and model training
- **Real-time Scoring**: 15-minute batch scoring with critical alerts

## Key Features

### Movement Analysis
- **Velocity Detection**: Identify impossibly fast travel
- **Distance Tracking**: Monitor distance from typical locations
- **Travel Patterns**: Analyze user movement over time

### Temporal Analysis
- **Time-based Features**: Hour, day of week, business hours
- **Unusual Timing**: Detect activity at unusual times
- **Pattern Deviation**: Compare to historical behavior

### Geographic Context
- **Geofencing**: Detect presence in restricted zones
- **Location Frequency**: Track visits to specific areas
- **POI Proximity**: Distance to key points of interest

### Anomaly Detection
- **Isolation Forest**: Unsupervised anomaly detection
- **Risk Scoring**: Continuous risk score calculation
- **Alert Thresholds**: Multi-level alert system (low/medium/high/critical)

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
# Run location analysis job
databricks bundle run location_analysis_job -t dev

# Run real-time scoring job
databricks bundle run realtime_scoring_job -t dev
```

## Model Features

The anomaly detection model uses:
- **Temporal**: hour_of_day, day_of_week, is_weekend, is_night, is_business_hours
- **Movement**: distance_from_prev_km, velocity_kmh, time_since_prev_hours
- **Behavioral**: distance_from_typical_km, location_visit_count
- **Risk Indicators**: impossible_velocity, far_from_typical, is_new_location, unusual_time

## Alert System

Critical alerts are generated when:
- Anomaly score exceeds configured threshold (default: 0.9)
- Impossible travel velocity detected (>800 km/h)
- Significant deviation from typical behavior

Alerts include:
- User identification
- Event details and timestamp
- Anomaly score and risk level
- Movement characteristics (velocity, distance)

## Permissions

The bundle manages permissions for:
- Model registry access (data-science-team, ml-engineers, security-team)
- Experiment tracking
- Job execution
- Real-time endpoint querying (security services)
- Pipeline management

## Requirements

- Databricks Runtime 14.3 LTS ML or higher
- Unity Catalog enabled
- Appropriate service principals configured for production
- Location event data source configured
