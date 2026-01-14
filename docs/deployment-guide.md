# Deployment Guide

This guide covers deploying Databricks Asset Bundles across environments.

## Prerequisites

### 1. Install Databricks CLI

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Verify installation
databricks --version
```

### 2. Configure Authentication

```bash
# Configure workspace connection
databricks configure --profile dev

# Enter when prompted:
# - Host: https://your-workspace.cloud.databricks.com
# - Token: your-personal-access-token
```

Create profiles for each environment:
```bash
databricks configure --profile dev
databricks configure --profile staging
databricks configure --profile prod
```

### 3. Verify Access

```bash
databricks workspace ls / --profile dev
```

## Pre-Deployment Setup

### 1. Unity Catalog Configuration

Ensure catalogs exist:
```sql
-- Run in Databricks SQL or notebook
CREATE CATALOG IF NOT EXISTS dev_catalog;
CREATE CATALOG IF NOT EXISTS staging_catalog;
CREATE CATALOG IF NOT EXISTS prod_catalog;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS dev_catalog.high_risk_wifi_dev;
CREATE SCHEMA IF NOT EXISTS dev_catalog.suspicious_location_dev;
```

### 2. Service Principal Setup (Staging/Prod)

```bash
# Create service principal (via Databricks admin)
# https://your-workspace.cloud.databricks.com/#settings/accounts/serviceprincipals

# Grant workspace access
databricks service-principals list

# Note the application ID for databricks.yml configuration
```

### 3. Group Configuration

Create required groups:
- `data-science-team`
- `ml-engineers`
- `data-engineering-team`
- `analytics-team`
- `security-team`

Add users to appropriate groups via workspace admin panel.

## Development Deployment

### Initial Deployment

```bash
# Navigate to project
cd projects/high-risk-wifi

# Validate configuration
databricks bundle validate -t dev

# Deploy to development
databricks bundle deploy -t dev
```

### What Happens During Deployment?

1. **Validation**: Bundle config is validated
2. **Artifact Upload**: Notebooks and wheels are uploaded
3. **Resource Creation**: Jobs, models, experiments created
4. **Permission Application**: Access controls applied
5. **Verification**: Deployment success confirmed

### Verify Deployment

```bash
# List deployed resources
databricks workspace ls ~/.bundle/high-risk-wifi/dev

# Check job creation
databricks jobs list --profile dev | grep high-risk-wifi

# View bundle summary
databricks bundle summary -t dev
```

### Run Development Jobs

```bash
# Run training job
databricks bundle run model_training_job -t dev

# Monitor job
databricks runs list --profile dev

# Get run output
databricks runs get-output --run-id <run-id> --profile dev
```

## Staging Deployment

### Update Configuration

Edit `databricks.yml` with staging details:
```yaml
targets:
  staging:
    mode: production
    workspace:
      host: https://your-workspace.cloud.databricks.com
      root_path: /Shared/.bundle/${bundle.name}/staging
    variables:
      catalog: staging_catalog
      schema: high_risk_wifi_staging
    run_as:
      service_principal_name: sp-high-risk-wifi-staging
```

### Deploy to Staging

```bash
# Validate staging config
databricks bundle validate -t staging

# Deploy to staging
databricks bundle deploy -t staging --profile staging
```

### Staging Testing

```bash
# Run staging jobs
databricks bundle run model_training_job -t staging --profile staging

# Monitor results
databricks runs list --profile staging

# Verify model registration
databricks models list --profile staging | grep high_risk_wifi
```

### Promote Model to Staging

```python
# In Databricks notebook or via API
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get latest version
model_name = "high_risk_wifi_classifier"
latest_version = client.get_latest_versions(model_name, stages=["None"])[0]

# Transition to Staging
client.transition_model_version_stage(
    name=model_name,
    version=latest_version.version,
    stage="Staging"
)
```

## Production Deployment

### Pre-Production Checklist

- [ ] Staging deployment successful
- [ ] Model validated in staging
- [ ] Service principal configured
- [ ] Production catalog/schemas created
- [ ] Permissions reviewed
- [ ] Monitoring configured
- [ ] Rollback plan documented

### Deploy to Production

```bash
# Final validation
databricks bundle validate -t prod --profile prod

# Deploy to production
databricks bundle deploy -t prod --profile prod
```

### Promote Model to Production

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Verify staging model performance
model_name = "high_risk_wifi_classifier"
staging_models = client.get_latest_versions(model_name, stages=["Staging"])

# Transition to Production
client.transition_model_version_stage(
    name=model_name,
    version=staging_models[0].version,
    stage="Production",
    archive_existing_versions=True  # Archive old production versions
)
```

### Enable Production Jobs

```bash
# Production jobs start paused by default
# Enable via workspace UI or API
databricks jobs update --job-id <job-id> --pause-status UNPAUSED --profile prod
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy Databricks Bundle

on:
  push:
    branches:
      - main
      - develop

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Databricks CLI
        run: |
          curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

      - name: Validate Bundle
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          cd projects/high-risk-wifi
          databricks bundle validate -t dev

  deploy-staging:
    needs: validate
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Staging
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST_STAGING }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_STAGING }}
        run: |
          cd projects/high-risk-wifi
          databricks bundle deploy -t staging

  deploy-prod:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Production
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST_PROD }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_PROD }}
        run: |
          cd projects/high-risk-wifi
          databricks bundle deploy -t prod
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - deploy-staging
  - deploy-prod

variables:
  PROJECT_DIR: projects/high-risk-wifi

validate:
  stage: validate
  script:
    - curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    - cd $PROJECT_DIR
    - databricks bundle validate -t dev
  only:
    - branches

deploy-staging:
  stage: deploy-staging
  script:
    - cd $PROJECT_DIR
    - databricks bundle deploy -t staging
  environment:
    name: staging
  only:
    - develop

deploy-prod:
  stage: deploy-prod
  script:
    - cd $PROJECT_DIR
    - databricks bundle deploy -t prod
  environment:
    name: production
  when: manual
  only:
    - main
```

## Rollback Procedures

### Rollback Model Version

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get previous production version
model_name = "high_risk_wifi_classifier"
all_versions = client.search_model_versions(f"name='{model_name}'")

# Find previous production version (now archived)
previous_version = [v for v in all_versions if v.current_stage == "Archived"][0]

# Promote back to production
client.transition_model_version_stage(
    name=model_name,
    version=previous_version.version,
    stage="Production",
    archive_existing_versions=True
)
```

### Rollback Bundle Deployment

```bash
# Redeploy previous git commit
git checkout <previous-commit>
databricks bundle deploy -t prod --profile prod
git checkout main
```

### Emergency Job Pause

```bash
# Pause jobs immediately
databricks jobs update --job-id <job-id> --pause-status PAUSED --profile prod

# Disable serving endpoint
databricks serving-endpoints update --name <endpoint-name> --enable-routing false
```

## Monitoring Deployments

### Check Bundle Status

```bash
# View deployed resources
databricks bundle summary -t prod

# List workspace files
databricks workspace ls /Shared/.bundle/high-risk-wifi/prod
```

### Monitor Jobs

```bash
# List recent runs
databricks runs list --limit 10 --profile prod

# Get run details
databricks runs get --run-id <run-id> --profile prod
```

### Monitor Models

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get production model
models = client.get_latest_versions("high_risk_wifi_classifier", stages=["Production"])
for model in models:
    print(f"Version: {model.version}")
    print(f"Stage: {model.current_stage}")
    print(f"Status: {model.status}")
```

### Monitor Endpoints

```bash
# Get endpoint status
databricks serving-endpoints get --name high-risk-wifi-prod

# View endpoint metrics (via workspace UI)
# https://your-workspace.cloud.databricks.com/#mlflow/endpoints/high-risk-wifi-prod
```

## Troubleshooting

### Validation Errors

```bash
# Run with debug output
databricks bundle validate -t dev --debug

# Check specific resource
databricks bundle validate -t dev --output json | jq '.resources.jobs'
```

### Permission Denied

```bash
# Check service principal permissions
databricks service-principals get <application-id>

# Verify group membership
databricks groups list-members --group-name ml-engineers

# Check Unity Catalog grants
SHOW GRANTS ON CATALOG staging_catalog;
```

### Resource Already Exists

```bash
# Bundle tries to create existing resource
# Solution: Import existing resource or delete manually

# Delete existing job
databricks jobs delete --job-id <job-id>

# Redeploy bundle
databricks bundle deploy -t dev
```

### Deployment Timeout

```bash
# Increase timeout for large bundles
databricks bundle deploy -t prod --timeout 30m
```

## Best Practices

### 1. Version Control
- Tag releases: `git tag v1.0.0`
- Semantic versioning
- Changelog maintenance

### 2. Testing
- Validate in dev first
- Test in staging with production-like data
- Manual approval for production

### 3. Monitoring
- Set up job failure alerts
- Monitor model performance
- Track endpoint latency

### 4. Documentation
- Document deployment steps
- Maintain runbooks
- Record configuration changes

### 5. Security
- Rotate service principal credentials
- Review permissions regularly
- Audit access logs

### 6. Disaster Recovery
- Regular backups
- Documented rollback procedures
- Test recovery process

## Next Steps

- Set up CI/CD pipeline
- Configure monitoring and alerting
- Review security best practices
- Establish deployment schedule
