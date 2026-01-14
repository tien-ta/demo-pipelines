# Dry-Run Mode for GitHub Actions

## Overview

The GitHub Actions workflows in this repository run in **dry-run mode** by default. This means:

- ✅ Databricks CLI commands are **printed** but **not executed**
- ✅ YAML validation and syntax checks still run
- ✅ Python code compilation and linting still run
- ✅ Unit tests still execute
- ⚠️ Actual Databricks bundle validation is **skipped**

## Why Dry-Run Mode?

Dry-run mode allows you to:

1. **Test workflows** without Databricks workspace credentials
2. **Validate structure** without requiring active Databricks connection
3. **Run in public repositories** without exposing credentials
4. **Demonstrate CI/CD** patterns without infrastructure requirements

## What Runs in Dry-Run Mode

### ✅ Always Runs (Real Execution)

These validations execute fully:

- **YAML Syntax Validation** - Parses all YAML files
- **Python Syntax Checking** - Compiles notebooks and source code
- **Code Quality Checks** - Black, isort, flake8, mypy
- **Unit Tests** - Full pytest execution with coverage
- **Security Scanning** - Bandit, secret detection, dependency scanning
- **File Structure Validation** - Checks required files exist

### 📋 Prints Only (Dry-Run)

These commands print what would run:

- **`databricks bundle validate`** - Prints command, skips execution
- **`databricks bundle deploy`** - Would print if added
- **`databricks bundle run`** - Would print if added

## Example Output

### Dry-Run Command
```bash
echo "Running: databricks bundle validate -t dev"
echo "✓ Bundle validation (dry-run mode - no actual validation performed)"
```

### Output in GitHub Actions
```
Validating bundle configuration for high-risk-wifi (dev environment)
Running: databricks bundle validate -t dev
✓ Bundle validation (dry-run mode - no actual validation performed)
```

## Enabling Real Databricks Validation

To enable actual Databricks CLI execution:

### 1. Add Databricks Credentials

Add GitHub secrets:
- `DATABRICKS_HOST` - Your workspace URL
- `DATABRICKS_TOKEN` - Personal access token or service principal token

### 2. Update Workflow

Replace dry-run steps with actual execution:

```yaml
# Before (Dry-Run)
- name: Validate bundle syntax (dev)
  run: |
    echo "Running: databricks bundle validate -t dev"
    echo "✓ Bundle validation (dry-run mode)"

# After (Real Execution)
- name: Install Databricks CLI
  run: |
    curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    databricks --version

- name: Validate bundle syntax (dev)
  env:
    DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
    DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
  run: |
    echo "Validating bundle configuration (dev environment)"
    databricks bundle validate -t dev
```

### 3. Per-Environment Configuration

For different environments:

```yaml
- name: Validate bundle syntax (dev)
  env:
    DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST_DEV }}
    DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_DEV }}
  run: databricks bundle validate -t dev

- name: Validate bundle syntax (staging)
  env:
    DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST_STAGING }}
    DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN_STAGING }}
  run: databricks bundle validate -t staging
```

## Current Workflow Behavior

### `validate-bundles.yml`
- ✅ Detects changed projects
- ✅ Validates YAML syntax
- ✅ Checks Python notebook syntax
- ✅ Validates resource definitions
- ✅ Checks required files
- 📋 **Dry-run:** Databricks bundle validate

### `validate-python.yml`
- ✅ Black formatting check
- ✅ isort import sorting
- ✅ flake8 linting
- ✅ mypy type checking

### `run-tests.yml`
- ✅ Unit test execution
- ✅ Coverage reporting
- ✅ Multiple Python versions

### `security-scan.yml`
- ✅ Bandit security scanning
- ✅ Hardcoded secret detection
- ✅ Dependency vulnerability scanning

## Benefits of This Approach

### For Development
- ✅ No Databricks workspace needed for PR validation
- ✅ Works in forked repositories
- ✅ Fast feedback on syntax and structure
- ✅ No credential management overhead

### For Demonstrations
- ✅ Shows complete CI/CD workflow patterns
- ✅ Demonstrates best practices
- ✅ Safe to run in public repositories
- ✅ No infrastructure costs

### For Learning
- ✅ Understand workflow structure
- ✅ See validation steps clearly
- ✅ Test changes without risk
- ✅ Easy to experiment

## Transitioning to Production

When ready for production use:

1. **Setup Credentials**
   ```bash
   # GitHub repository settings > Secrets and variables > Actions
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=dapi...
   ```

2. **Update Workflows**
   - Remove dry-run echo statements
   - Add Databricks CLI installation
   - Add environment variables
   - Enable actual command execution

3. **Test Incrementally**
   - Start with dev environment
   - Validate in staging
   - Enable for production last

4. **Monitor Results**
   - Check workflow runs
   - Review validation output
   - Adjust as needed

## Local Testing

To test Databricks commands locally:

```bash
# Install Databricks CLI
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Configure authentication
databricks configure

# Test bundle validation
cd projects/high-risk-wifi
databricks bundle validate -t dev
```

## Summary

| Check Type | Mode | Notes |
|------------|------|-------|
| YAML Syntax | ✅ Real | Fully validated |
| Python Syntax | ✅ Real | All code compiled |
| Unit Tests | ✅ Real | Full execution |
| Code Quality | ✅ Real | Linting enforced |
| Security Scan | ✅ Real | Vulnerabilities detected |
| Databricks Validate | 📋 Dry-run | Prints command only |
| Databricks Deploy | 📋 Dry-run | Not included (would print) |

## Questions?

For questions about dry-run mode:
1. Check this documentation
2. Review workflow YAML files
3. See example outputs in Actions tab
4. Refer to Databricks CLI documentation
