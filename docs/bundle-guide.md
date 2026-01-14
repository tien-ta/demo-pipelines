# Databricks Asset Bundles Guide

## What are Databricks Asset Bundles?

Databricks Asset Bundles (DAB) are a declarative Infrastructure-as-Code (IaC) framework for managing Databricks resources. They enable you to:

- Define all resources in YAML configuration files
- Version control your infrastructure
- Deploy consistently across environments
- Manage permissions declaratively
- Orchestrate complex workflows

## Bundle Structure

### Core Components

#### 1. `databricks.yml` (Main Configuration)
The root configuration file that defines:
- Bundle metadata (name, version)
- Environment targets (dev, staging, prod)
- Variables and their defaults
- Include directives for modular configs

```yaml
bundle:
  name: my-project

variables:
  catalog:
    description: Unity Catalog name
    default: dev_catalog

targets:
  dev:
    mode: development
    default: true
  prod:
    mode: production

include:
  - resources/*.yml
```

#### 2. `resources/` Directory
Contains YAML files defining specific resources:
- `models.yml` - MLflow model registry
- `experiments.yml` - MLflow experiments
- `jobs.yml` - Databricks jobs
- `model_serving.yml` - Serving endpoints
- `pipelines.yml` - Delta Live Tables

#### 3. `notebooks/` Directory
Databricks notebooks (.py or .sql files) used in jobs and pipelines.

#### 4. `src/` Directory
Python packages and modules imported by notebooks and jobs.

## Resource Types

### MLflow Models

```yaml
resources:
  models:
    my_model:
      name: ${var.model_name}
      description: Model description
      tags:
        - key: team
          value: data-science
      permissions:
        - level: CAN_MANAGE
          group_name: ml-team
```

**Permissions Levels:**
- `CAN_READ` - View model metadata
- `CAN_MANAGE_STAGING_VERSIONS` - Transition to Staging
- `CAN_MANAGE_PRODUCTION_VERSIONS` - Transition to Production
- `CAN_MANAGE` - Full control

### MLflow Experiments

```yaml
resources:
  experiments:
    training_experiment:
      name: /Shared/my-project/training
      description: Model training experiments
      permissions:
        - level: CAN_MANAGE
          group_name: data-scientists
        - level: CAN_READ
          group_name: analysts
```

**Permissions Levels:**
- `CAN_READ` - View experiments and runs
- `CAN_EDIT` - Create runs, log metrics
- `CAN_MANAGE` - Full control

### Jobs

```yaml
resources:
  jobs:
    training_job:
      name: "[${bundle.target}] Model Training"

      schedule:
        quartz_cron_expression: "0 0 2 * * ?"
        timezone_id: "America/Los_Angeles"

      tasks:
        - task_key: train
          notebook_task:
            notebook_path: ../notebooks/train.py
            base_parameters:
              catalog: ${var.catalog}

          new_cluster:
            spark_version: 14.3.x-cpu-ml-scala2.12
            node_type_id: i3.xlarge
            num_workers: 2

          libraries:
            - pypi:
                package: mlflow==2.10.0

      permissions:
        - level: CAN_MANAGE
          group_name: ml-engineers
```

**Permissions Levels:**
- `CAN_VIEW` - View job configuration
- `CAN_MANAGE_RUN` - Trigger job runs
- `CAN_MANAGE` - Full control

### Model Serving Endpoints

```yaml
resources:
  model_serving_endpoints:
    my_endpoint:
      name: my-model-${bundle.target}

      config:
        served_entities:
          - entity_name: ${var.model_name}
            entity_version: "1"
            workload_size: Small
            scale_to_zero_enabled: true

      permissions:
        - level: CAN_QUERY
          service_principal_name: sp-application
        - level: CAN_MANAGE
          group_name: ml-engineers
```

**Permissions Levels:**
- `CAN_VIEW` - View endpoint configuration
- `CAN_QUERY` - Make inference requests
- `CAN_MANAGE` - Full control

### Delta Live Tables

```yaml
resources:
  pipelines:
    data_pipeline:
      name: "[${bundle.target}] Data Pipeline"
      target: ${var.catalog}.${var.schema}
      catalog: ${var.catalog}

      clusters:
        - label: default
          node_type_id: i3.xlarge
          num_workers: 2

      libraries:
        - notebook:
            path: ../notebooks/dlt_bronze.py
        - notebook:
            path: ../notebooks/dlt_silver.py

      continuous: false
      development: ${{ bundle.target == 'dev' }}

      permissions:
        - level: CAN_MANAGE
          group_name: data-engineers
```

**Permissions Levels:**
- `CAN_VIEW` - View pipeline configuration
- `CAN_RUN` - Trigger pipeline runs
- `CAN_MANAGE` - Full control

## Variables and Parameterization

### Defining Variables

```yaml
variables:
  catalog:
    description: Unity Catalog name
    default: dev_catalog

  cluster_node_type:
    description: Cluster node type
    default: i3.xlarge
```

### Using Variables

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: process
          notebook_task:
            base_parameters:
              catalog: ${var.catalog}  # Reference variable

          new_cluster:
            node_type_id: ${var.cluster_node_type}
```

### Environment-Specific Values

```yaml
targets:
  dev:
    variables:
      catalog: dev_catalog
      cluster_node_type: i3.xlarge

  prod:
    variables:
      catalog: prod_catalog
      cluster_node_type: i3.2xlarge
```

## Targets (Environments)

### Development Target

```yaml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://workspace.cloud.databricks.com
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
```

**Characteristics:**
- Runs as current user
- Personal workspace paths
- Relaxed validation
- Fast iteration

### Production Target

```yaml
targets:
  prod:
    mode: production
    workspace:
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: sp-my-project-prod
```

**Characteristics:**
- Runs as service principal
- Shared workspace paths
- Strict validation
- Immutable deployments

## Permissions Management

### Group-Based Permissions

```yaml
permissions:
  - level: CAN_MANAGE
    group_name: data-science-team

  - level: CAN_VIEW
    group_name: analysts
```

### Service Principal Permissions

```yaml
permissions:
  - level: CAN_QUERY
    service_principal_name: sp-application-backend
```

### User Permissions

```yaml
permissions:
  - level: CAN_MANAGE
    user_name: user@company.com
```

## Deployment Workflow

### 1. Validate Bundle

```bash
databricks bundle validate -t dev
```

Checks:
- YAML syntax
- Resource definitions
- Variable references
- Permission configurations

### 2. Deploy Bundle

```bash
databricks bundle deploy -t dev
```

Actions:
- Creates/updates resources
- Applies permissions
- Uploads notebooks and libraries
- Configures jobs and pipelines

### 3. Run Jobs

```bash
databricks bundle run job_name -t dev
```

### 4. View Deployed Resources

```bash
databricks workspace ls ~/.bundle/my-project/dev
```

## Advanced Features

### Conditional Configuration

```yaml
development: ${{ bundle.target == 'dev' }}
```

### Multi-File Configuration

```yaml
# databricks.yml
include:
  - resources/models.yml
  - resources/jobs.yml
  - resources/pipelines.yml
```

### Artifacts

```yaml
artifacts:
  libraries:
    type: whl
    path: ./dist

  notebooks:
    type: notebook
    path: ./notebooks
```

### Task Dependencies

```yaml
tasks:
  - task_key: extract
    # ... task config

  - task_key: transform
    depends_on:
      - task_key: extract
    # ... task config
```

## Best Practices

### 1. Modular Configuration
Split resources into separate YAML files:
- One file per resource type
- Easier to maintain
- Better version control

### 2. Use Variables
- Parameterize environment-specific values
- Define sensible defaults
- Override per target

### 3. Service Principals in Production
- Never use personal accounts in prod
- Dedicated service principals per project
- Proper permission scoping

### 4. Version Control
- Commit all bundle files
- Never commit credentials
- Use `.gitignore` for sensitive files

### 5. Testing Strategy
- Validate in dev first
- Test in staging
- Deploy to prod with approval

### 6. Documentation
- Document bundle purpose
- Explain resource relationships
- Maintain deployment guides

### 7. Naming Conventions
- Include environment in names: `[${bundle.target}]`
- Use descriptive resource names
- Consistent naming across bundles

## Common Patterns

### Multi-Stage ML Pipeline

```yaml
jobs:
  ml_pipeline:
    tasks:
      - task_key: feature_engineering
        # ...

      - task_key: train_model
        depends_on:
          - task_key: feature_engineering

      - task_key: evaluate_model
        depends_on:
          - task_key: train_model

      - task_key: register_model
        depends_on:
          - task_key: evaluate_model
```

### Blue-Green Deployment

```yaml
# Model serving with traffic routing
config:
  served_entities:
    - entity_name: model
      entity_version: "1"

  traffic_config:
    routes:
      - served_model_name: model-1
        traffic_percentage: 90
      - served_model_name: model-2
        traffic_percentage: 10
```

### Shared Configuration

```yaml
# common.yml
x-common-cluster: &common-cluster
  spark_version: 14.3.x-cpu-ml-scala2.12
  node_type_id: i3.xlarge

# Use in jobs
resources:
  jobs:
    job1:
      tasks:
        - new_cluster:
            <<: *common-cluster
            num_workers: 2
```

## Troubleshooting

### Validation Errors
```bash
databricks bundle validate -t dev --debug
```

### Deployment Failures
- Check workspace permissions
- Verify service principal access
- Review Unity Catalog permissions

### Resource Conflicts
- Ensure unique resource names per environment
- Use `${bundle.target}` in names

### Permission Issues
- Verify group membership
- Check service principal roles
- Review Unity Catalog grants

## Migration from Existing Resources

### 1. Export Configuration
Document existing resources:
- Job configurations
- Cluster settings
- Notebook paths

### 2. Create Bundle
Define resources in YAML:
```yaml
resources:
  jobs:
    existing_job:
      name: "[${bundle.target}] Existing Job"
      # ... copy configuration
```

### 3. Deploy in Dev
```bash
databricks bundle deploy -t dev
```

### 4. Validate
Compare deployed resources with original.

### 5. Migrate Other Environments
After validation, deploy to staging/prod.

## Next Steps

- Review example bundles in `projects/`
- Read deployment guide (`deployment-guide.md`)
- Explore best practices (`best-practices.md`)
- Try deploying a simple bundle
