# Databricks Infrastructure as Code Demo

This repository demonstrates Databricks Asset Bundles (DAB) for managing ML infrastructure as code.

## Overview

Each directory in `projects/` contains a complete Databricks bundle for a specific ML use case, managing:
- **Models**: MLflow model registry and versioning
- **Experiments**: MLflow experiment tracking
- **Inference**: Real-time serving endpoints and batch scoring
- **Notebooks**: Training, evaluation, and inference notebooks
- **Pipelines**: Delta Live Tables for data processing
- **Permissions**: Granular access control for all resources
- **Jobs**: Scheduled and triggered workflows

## Projects

### 1. High-Risk WiFi Detection (`projects/high_risk_wifi/`)
ML pipeline for identifying high-risk WiFi connections based on security, signal, and contextual features.

**Key Components:**
- Random Forest classification model
- Delta Live Tables (Bronze → Silver → Gold)
- Model serving endpoint for real-time predictions
- Scheduled training and batch inference jobs

**Use Cases:**
- Security monitoring
- Network risk assessment
- User safety alerts

### 2. Suspicious Location Detection (`projects/suspicious_location/`)
Anomaly detection pipeline for identifying suspicious location patterns and impossible travel.

**Key Components:**
- Isolation Forest anomaly detection
- Geographic feature engineering (velocity, distance, geofencing)
- Critical alert system
- Real-time scoring with alerting

**Use Cases:**
- Fraud detection
- Security monitoring
- Compliance verification

## Repository Structure

```
demo-pipelines/
├── README.md                    # This file
├── docs/                        # Shared documentation
│   ├── bundle-guide.md         # Guide to Databricks bundles
│   ├── deployment-guide.md     # Deployment instructions
│   └── best-practices.md       # Best practices
└── projects/                    # Individual project bundles
    ├── high_risk_wifi/
    │   ├── databricks.yml      # Bundle configuration
    │   ├── resources/          # Resource definitions (YAML)
    │   ├── notebooks/          # Databricks notebooks
    │   ├── src/                # Python source code
    │   └── README.md           # Project documentation
    └── suspicious_location/
        ├── databricks.yml
        ├── resources/
        ├── notebooks/
        ├── src/
        └── README.md
```

## Quick Start

### Prerequisites
- Databricks CLI installed (`curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh`)
- Databricks workspace configured
- Unity Catalog enabled

### Deploy a Project

```bash
# Navigate to a project
cd projects/high_risk_wifi

# Deploy to development
databricks bundle deploy -t dev

# Deploy to staging
databricks bundle deploy -t staging

# Deploy to production
databricks bundle deploy -t prod
```

### Run Jobs

```bash
# Run training job
databricks bundle run model_training_job -t dev

# Run inference job
databricks bundle run batch_inference_job -t dev
```

### Validate Configuration

```bash
# Validate bundle configuration
databricks bundle validate -t dev

# View bundle resources
databricks bundle schema
```

## Bundle Configuration

Each bundle defines three environments (targets):

### Development (`dev`)
- Mode: `development`
- Workspace path: `~/.bundle/{bundle.name}/dev`
- Use: Active development and experimentation
- Runs as: Current user

### Staging (`staging`)
- Mode: `production`
- Workspace path: `/Shared/.bundle/{bundle.name}/staging`
- Use: Pre-production testing
- Runs as: Service principal

### Production (`prod`)
- Mode: `production`
- Workspace path: `/Shared/.bundle/{bundle.name}/prod`
- Use: Production workloads
- Runs as: Service principal

## Managed Resources

### MLflow Models
- Versioned model registry
- Stage transitions (Staging → Production)
- Model permissions and access control

### Experiments
- Organized experiment tracking
- Team collaboration
- Metric and parameter logging

### Model Serving
- Real-time inference endpoints
- Auto-scaling and traffic management
- Query permissions

### Jobs
- Scheduled workflows (training, inference)
- Task dependencies and orchestration
- Email notifications on failure

### Delta Live Tables
- Bronze → Silver → Gold pipelines
- Data quality expectations
- Continuous or triggered execution

### Permissions
Granular access control at multiple levels:
- Bundle-level permissions
- Resource-specific permissions (models, experiments, jobs, endpoints)
- Environment-specific service principals

## Environment Variables

Configure these for your workspace:

```bash
# Databricks workspace
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"

# Unity Catalog
export CATALOG_DEV="dev_catalog"
export CATALOG_STAGING="staging_catalog"
export CATALOG_PROD="prod_catalog"

# Service Principals (for staging/prod)
export SP_STAGING="sp-project-staging"
export SP_PROD="sp-project-prod"
```

## Development Workflow

### 1. Local Development
```bash
cd projects/your-project
databricks bundle deploy -t dev
databricks bundle run your_job -t dev
```

### 2. Testing in Staging
```bash
databricks bundle deploy -t staging
databricks bundle run your_job -t staging
```

### 3. Production Release
```bash
# Review changes
databricks bundle validate -t prod

# Deploy to production
databricks bundle deploy -t prod
```

## Best Practices

### Bundle Organization
- One bundle per logical ML project
- Separate concerns (training vs. inference)
- Use modular YAML files in `resources/`

### Environment Management
- Keep dev/staging/prod configurations similar
- Use variables for environment-specific values
- Service principals for production execution

### Security
- Never commit credentials
- Use service principals in prod
- Implement least-privilege access
- Regular permission audits

### CI/CD Integration
- Validate bundles in CI
- Automated deployment to staging
- Manual approval for production
- Version control all bundle files

## Common Tasks

### Update Model Version
```bash
# Deploy with new model version
databricks bundle deploy -t prod
```

### Add New Resource
1. Create YAML file in `resources/`
2. Add to `include:` in `databricks.yml`
3. Deploy: `databricks bundle deploy`

### Change Permissions
1. Edit permissions in resource YAML
2. Validate: `databricks bundle validate`
3. Deploy: `databricks bundle deploy`

### Monitor Jobs
```bash
# List runs
databricks runs list --job-name "[dev] Your Job Name"

# Get run output
databricks runs get-output --run-id <run-id>
```

## Troubleshooting

### Bundle Validation Errors
```bash
databricks bundle validate -t dev
```

### Permission Denied
- Check service principal configuration
- Verify Unity Catalog permissions
- Review resource-level permissions

### Job Failures
- Check job run logs in workspace UI
- Verify cluster configuration
- Check library dependencies

## Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Delta Live Tables](https://docs.databricks.com/delta-live-tables/)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/)

## Contributing

When adding new projects:
1. Create new directory under `projects/`
2. Copy bundle structure from existing project
3. Update `databricks.yml` with project-specific config
4. Document in project README.md
5. Add to this main README

## License

This is a demo repository for educational purposes.