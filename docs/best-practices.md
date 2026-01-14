# Databricks Asset Bundles - Best Practices

## Bundle Organization

### Project Structure

**DO:**
```
project/
├── databricks.yml          # Main config
├── resources/              # Modular resource definitions
│   ├── models.yml
│   ├── experiments.yml
│   ├── jobs.yml
│   ├── pipelines.yml
│   └── serving.yml
├── notebooks/              # All notebooks
├── src/                    # Python packages
└── tests/                  # Unit and integration tests
```

**DON'T:**
- Put all resources in `databricks.yml`
- Mix resource types in single files
- Scatter notebooks across multiple directories

### Naming Conventions

**DO:**
```yaml
# Include environment in resource names
jobs:
  training_job:
    name: "[${bundle.target}] High-Risk WiFi - Training"

# Use descriptive, consistent names
model_name: high_risk_wifi_classifier
experiment_path: /Shared/high-risk-wifi/experiments
```

**DON'T:**
```yaml
# Ambiguous names
name: "job1"

# No environment indicator
name: "Training Job"

# Inconsistent naming
model_name: hrw_model
experiment_path: /Users/me/exp
```

## Environment Management

### Target Configuration

**DO:**
```yaml
targets:
  dev:
    mode: development
    default: true
    workspace:
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
    variables:
      catalog: dev_catalog

  prod:
    mode: production
    workspace:
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: sp-${bundle.name}-prod
    variables:
      catalog: prod_catalog
```

**DON'T:**
```yaml
targets:
  dev:
    mode: production  # Wrong mode for dev

  prod:
    # Missing run_as - running as personal user
    variables:
      catalog: dev_catalog  # Wrong catalog
```

### Variable Management

**DO:**
```yaml
variables:
  catalog:
    description: Unity Catalog name
    default: dev_catalog

  model_name:
    description: Registered model name
    default: my_model

  cluster_node_type:
    description: Cluster instance type
    default: i3.xlarge

# Override per environment
targets:
  prod:
    variables:
      cluster_node_type: i3.2xlarge
```

**DON'T:**
```yaml
variables:
  # No description
  catalog: dev_catalog

  # Hardcoded values without parameterization
resources:
  jobs:
    my_job:
      tasks:
        - new_cluster:
            node_type_id: i3.xlarge  # Should use variable
```

## Security & Permissions

### Service Principals

**DO:**
```yaml
targets:
  prod:
    run_as:
      service_principal_name: sp-my-project-prod

resources:
  model_serving_endpoints:
    my_endpoint:
      permissions:
        - level: CAN_QUERY
          service_principal_name: sp-application-backend
```

**DON'T:**
```yaml
targets:
  prod:
    # Running as personal user in production
    # Missing run_as configuration

resources:
  model_serving_endpoints:
    my_endpoint:
      permissions:
        # Granting query access to user emails
        - level: CAN_QUERY
          user_name: developer@company.com
```

### Least Privilege Access

**DO:**
```yaml
resources:
  models:
    my_model:
      permissions:
        - level: CAN_MANAGE
          group_name: ml-engineers
        - level: CAN_MANAGE_PRODUCTION_VERSIONS
          service_principal_name: sp-deployment
        - level: CAN_READ
          group_name: analysts
```

**DON'T:**
```yaml
resources:
  models:
    my_model:
      permissions:
        # Everyone gets full access
        - level: CAN_MANAGE
          group_name: all-users
```

### Secrets Management

**DO:**
```python
# Use Databricks secrets
api_key = dbutils.secrets.get(scope="my-scope", key="api-key")

# Reference in jobs
tasks:
  - task_key: api_call
    spark_python_task:
      python_file: scripts/call_api.py
    libraries:
      - pypi:
          package: requests
```

**DON'T:**
```python
# Hardcoded credentials
api_key = "sk-1234567890abcdef"

# Credentials in config
base_parameters:
  api_key: "sk-1234567890abcdef"
```

## Job Configuration

### Task Dependencies

**DO:**
```yaml
jobs:
  ml_pipeline:
    tasks:
      - task_key: extract_features
        # ... config

      - task_key: train_model
        depends_on:
          - task_key: extract_features
        # ... config

      - task_key: evaluate_model
        depends_on:
          - task_key: train_model
        # ... config
```

**DON'T:**
```yaml
jobs:
  # Separate jobs instead of tasks
  extract_features:
    # ... config

  train_model:
    # No dependency management
    # ... config
```

### Cluster Configuration

**DO:**
```yaml
# Reuse cluster definitions
x-common-cluster: &ml-cluster
  spark_version: 14.3.x-cpu-ml-scala2.12
  node_type_id: ${var.cluster_node_type}
  spark_conf:
    "spark.databricks.delta.optimizeWrite.enabled": "true"

jobs:
  training:
    tasks:
      - task_key: train
        new_cluster:
          <<: *ml-cluster
          num_workers: 2
```

**DON'T:**
```yaml
jobs:
  job1:
    tasks:
      - new_cluster:
          # Duplicated config
          spark_version: 14.3.x-cpu-ml-scala2.12
          node_type_id: i3.xlarge

  job2:
    tasks:
      - new_cluster:
          # Same config repeated
          spark_version: 14.3.x-cpu-ml-scala2.12
          node_type_id: i3.xlarge
```

### Error Handling

**DO:**
```yaml
jobs:
  my_job:
    max_retries: 3
    retry_on_timeout: true

    email_notifications:
      on_failure:
        - ml-team@company.com
      on_success:
        - []  # No spam on success

    tasks:
      - task_key: critical_task
        timeout_seconds: 7200
```

**DON'T:**
```yaml
jobs:
  my_job:
    # No retry configuration
    # No notifications

    tasks:
      - task_key: long_running
        # No timeout - could run forever
```

## Model Management

### Model Registry

**DO:**
```python
# Log model with signature and examples
import mlflow

signature = mlflow.models.infer_signature(X_train, y_pred)
input_example = X_train[:5]

mlflow.sklearn.log_model(
    model,
    "model",
    registered_model_name=model_name,
    signature=signature,
    input_example=input_example
)
```

**DON'T:**
```python
# No signature or examples
mlflow.sklearn.log_model(model, "model")
```

### Model Versioning

**DO:**
```python
# Clear version progression
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Stage workflow
# None -> Staging -> Production -> Archived

# Promote to staging
client.transition_model_version_stage(
    name=model_name,
    version=version,
    stage="Staging"
)

# After validation, promote to production
client.transition_model_version_stage(
    name=model_name,
    version=version,
    stage="Production",
    archive_existing_versions=True
)
```

**DON'T:**
```python
# Skip staging
client.transition_model_version_stage(
    name=model_name,
    version=version,
    stage="Production"  # Directly to prod
)
```

### Experiment Organization

**DO:**
```yaml
resources:
  experiments:
    model_training:
      name: ${var.experiment_path}/model-training

    model_evaluation:
      name: ${var.experiment_path}/model-evaluation

    hyperparameter_tuning:
      name: ${var.experiment_path}/hyperparameter-tuning
```

**DON'T:**
```yaml
resources:
  experiments:
    everything:
      name: /Users/me/experiments  # All in one
```

## Delta Live Tables

### Data Quality

**DO:**
```python
@dlt.table
@dlt.expect_or_drop("valid_timestamp", "timestamp IS NOT NULL")
@dlt.expect_or_drop("valid_amount", "amount > 0")
@dlt.expect("reasonable_amount", "amount < 1000000")
def clean_data():
    return dlt.read("raw_data")
```

**DON'T:**
```python
@dlt.table
def clean_data():
    # No data quality checks
    return dlt.read("raw_data")
```

### Pipeline Organization

**DO:**
```
notebooks/
├── dlt_bronze.py       # Raw ingestion
├── dlt_silver.py       # Cleaning, validation
├── dlt_gold.py         # Aggregations, features
└── dlt_enrichment.py   # External enrichment
```

**DON'T:**
```
notebooks/
└── dlt_everything.py   # All layers in one file
```

## Testing

### Unit Tests

**DO:**
```python
# tests/test_features.py
import pytest
from src.features import extract_time_features

def test_extract_time_features():
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()

    data = [("2024-01-15 14:30:00",)]
    df = spark.createDataFrame(data, ["timestamp"])

    result = extract_time_features(df)

    assert "hour_of_day" in result.columns
    assert result.first()["hour_of_day"] == 14
```

**DON'T:**
```python
# No tests
# Manual validation only
```

### Integration Tests

**DO:**
```python
# tests/test_pipeline.py
def test_end_to_end_pipeline():
    # Create test data
    # Run pipeline
    # Validate output
    pass
```

**DON'T:**
```python
# Only test in production
```

## Deployment

### Version Control

**DO:**
```bash
# Tag releases
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

# Meaningful commits
git commit -m "feat: Add anomaly detection model"
git commit -m "fix: Handle missing values in features"
```

**DON'T:**
```bash
# No tags
# Vague commits
git commit -m "updates"
git commit -m "fix stuff"
```

### CI/CD

**DO:**
```yaml
# .github/workflows/deploy.yml
- name: Validate
  run: databricks bundle validate -t dev

- name: Deploy to Staging
  if: github.ref == 'refs/heads/develop'
  run: databricks bundle deploy -t staging

- name: Deploy to Prod
  if: github.ref == 'refs/heads/main'
  run: databricks bundle deploy -t prod
  environment: production  # Requires approval
```

**DON'T:**
```yaml
# Direct to prod
- name: Deploy
  run: databricks bundle deploy -t prod
```

### Monitoring

**DO:**
```yaml
jobs:
  my_job:
    email_notifications:
      on_failure:
        - oncall@company.com

    # Add monitoring tasks
    tasks:
      - task_key: validate_output
        depends_on:
          - task_key: main_task
        # Validation logic
```

**DON'T:**
```yaml
jobs:
  my_job:
    # No notifications
    # No validation
```

## Documentation

### Code Documentation

**DO:**
```python
def extract_features(df: DataFrame, config: dict) -> DataFrame:
    """
    Extract features from raw data.

    Args:
        df: Input DataFrame with raw data
        config: Feature configuration dict

    Returns:
        DataFrame with extracted features

    Example:
        >>> df = extract_features(raw_df, {"window": 7})
    """
    pass
```

**DON'T:**
```python
def extract_features(df, config):
    # No documentation
    pass
```

### Bundle Documentation

**DO:**
```
project/
├── README.md              # Project overview
├── docs/
│   ├── deployment.md     # Deployment guide
│   ├── architecture.md   # Architecture docs
│   └── troubleshooting.md
```

**DON'T:**
```
project/
└── README.md  # Minimal or missing docs
```

## Performance Optimization

### Cluster Sizing

**DO:**
```yaml
variables:
  # Different sizes for different workloads
  training_cluster_type: i3.2xlarge
  inference_cluster_type: i3.xlarge
  etl_cluster_type: r5.xlarge

jobs:
  training:
    new_cluster:
      node_type_id: ${var.training_cluster_type}
```

**DON'T:**
```yaml
# Same cluster size for everything
node_type_id: i3.2xlarge  # Expensive for small tasks
```

### Library Management

**DO:**
```yaml
libraries:
  # Pin versions
  - pypi:
      package: mlflow==2.10.0
  - pypi:
      package: scikit-learn==1.4.0
```

**DON'T:**
```yaml
libraries:
  # No version pinning
  - pypi:
      package: mlflow
  - pypi:
      package: scikit-learn
```

## Cost Optimization

### Autoscaling

**DO:**
```yaml
new_cluster:
  autoscale:
    min_workers: 1
    max_workers: 10

  # Auto-terminate
  autotermination_minutes: 30
```

**DON'T:**
```yaml
new_cluster:
  num_workers: 10  # Always 10
  # No auto-termination
```

### Spot Instances

**DO:**
```yaml
new_cluster:
  aws_attributes:
    first_on_demand: 1
    availability: SPOT_WITH_FALLBACK
```

**DON'T:**
```yaml
new_cluster:
  aws_attributes:
    availability: ON_DEMAND  # Always expensive
```

## Summary Checklist

- [ ] Modular YAML organization
- [ ] Consistent naming conventions
- [ ] Service principals for prod
- [ ] Least privilege permissions
- [ ] No hardcoded credentials
- [ ] Task dependencies defined
- [ ] Error handling configured
- [ ] Model signatures included
- [ ] Data quality expectations
- [ ] Unit and integration tests
- [ ] CI/CD pipeline setup
- [ ] Monitoring and alerts
- [ ] Comprehensive documentation
- [ ] Version pinning
- [ ] Cost optimization
