# GitHub Actions Workflows

This directory contains CI/CD workflows for validating Databricks Asset Bundles.

## ⚠️ Dry-Run Mode

**Important:** Databricks CLI commands run in **dry-run mode** by default (commands are printed but not executed). This allows the workflows to run without Databricks credentials.

**See:** [DRY_RUN_MODE.md](DRY_RUN_MODE.md) for details and how to enable real execution.

## Workflows

We have **3 main workflows** that validate different aspects of the codebase:

### 1. Validate Databricks Bundles (`validate-bundles.yml`)

**Trigger:** Pull requests that modify files in `projects/`

**What it does:**
- Detects which projects have changes
- Validates bundle configuration for all environments (dev/staging/prod)
- Checks Python package builds
- Validates Python notebook syntax
- Validates YAML syntax
- Verifies required files exist
- Validates resource definitions

**Validation Steps:**
1. **Bundle Validation** - Databricks bundle validate for dev/staging/prod
2. **Python Package** - Builds wheel packages if `setup.py` exists
3. **Notebook Syntax** - Compiles all `.py` notebooks
4. **YAML Syntax** - Validates all YAML files
5. **Required Files** - Checks for `databricks.yml` and `README.md`
6. **Resource Definitions** - Validates resource YAML structure

**Outputs:**
- ✅ Validation passed - All checks successful
- ❌ Validation failed - See job logs for details
- Summary posted to PR

### 2. Python Tests & Quality (`run-tests.yml`)

**Trigger:** Pull requests that modify Python files in `projects/`

**What it does:**
- Combines code quality checks AND unit tests in single workflow
- Checks code formatting with Black
- Validates import sorting with isort
- Lints code with flake8
- Type checks with mypy
- Runs unit tests with pytest
- Generates coverage reports

**All Checks Performed:**
1. **Black** - Code formatting (PEP 8 compliance)
2. **isort** - Import statement organization
3. **flake8** - Linting and complexity checks
4. **mypy** - Static type checking
5. **pytest** - Unit test execution with coverage

**Benefits:**
- Single workflow = no duplicate dependency installation
- Runs on Python 3.10 and 3.11
- Comprehensive quality gate before merge

**Outputs:**
- ✅ All checks and tests passed
- ❌ Issues found - See job logs for details
- Coverage report and test results

### 3. Security Scan (`security-scan.yml`)

**Trigger:** Pull requests that modify Python files or dependencies

**What it does:**
- Scans code for security vulnerabilities with Bandit
- Checks for hardcoded secrets
- Scans dependencies for known vulnerabilities

**Security Checks:**
1. **Bandit** - Python security issue scanner
2. **Secret Detection** - Finds hardcoded credentials
3. **Dependency Scanning** - Checks for vulnerable packages

**Patterns Detected:**
- Hardcoded passwords
- API keys in code
- Secret tokens
- AWS credentials
- Other sensitive data

**Outputs:**
- ✅ No security issues found
- ⚠️ Warnings - Review findings
- ❌ Critical issues - Must fix before merge
- Bandit report uploaded as artifact

## Running Locally

### Validate Bundle
```bash
cd projects/your-project
databricks bundle validate -t dev
databricks bundle validate -t staging
databricks bundle validate -t prod
```

### Check Python Code Quality
```bash
cd projects/your-project

# Install tools
pip install black isort flake8 mypy pytest

# Format code
black src/
isort src/

# Lint
flake8 src/
mypy src/

# Test
pytest tests/
```

### Run Security Scan
```bash
cd projects/your-project

# Install tools
pip install bandit safety

# Scan for security issues
bandit -r src/
bandit -r notebooks/

# Check dependencies
pip install -e .
safety check
```

## Workflow Configuration

### Environment Variables

Workflows use the following:
- `GITHUB_TOKEN` - Automatically provided
- No Databricks credentials needed for validation

### Adding New Projects

When adding a new project:
1. Create directory under `projects/`
2. Include `databricks.yml`
3. Workflows will automatically detect and validate

### Customizing Validation

To customize validation for specific projects, modify:
- `validate-bundles.yml` - Bundle validation steps
- `validate-python.yml` - Code quality tools
- `security-scan.yml` - Security scanning rules

### Matrix Strategy

Workflows use matrix strategy to run in parallel:
```yaml
strategy:
  matrix:
    project:
      - high-risk-wifi
      - suspicious-location
```

Add new projects to the matrix when created.

## Troubleshooting

### Bundle Validation Fails

**Error:** `Bundle validation failed`

**Solutions:**
1. Run locally: `databricks bundle validate -t dev`
2. Check YAML syntax
3. Verify variable references
4. Ensure all included files exist

### Python Quality Checks Fail

**Error:** `Code formatting issues`

**Solutions:**
```bash
# Auto-fix formatting
black src/
isort src/

# Check what would change
black --check --diff src/
```

### Security Scan Warnings

**Error:** `Hardcoded secrets detected`

**Solutions:**
1. Use `dbutils.secrets.get(scope="...", key="...")`
2. Use environment variables
3. Never commit credentials

### YAML Validation Fails

**Error:** `YAML syntax error`

**Solutions:**
1. Check indentation (use spaces, not tabs)
2. Validate quotes and special characters
3. Use online YAML validator
4. Check for duplicate keys

## Best Practices

1. **Always validate locally** before pushing
2. **Run formatters** (black, isort) before committing
3. **Review security warnings** even if they don't block
4. **Keep dependencies updated** to avoid vulnerabilities
5. **Add tests** for new functionality
6. **Document changes** in PR description

## CI/CD Pipeline Flow

```
PR Created/Updated
    ↓
[Detect Changed Projects]
    ↓
Parallel Validation:
├─ [Bundle Validation]
│   ├─ dev environment
│   ├─ staging environment
│   └─ prod environment
├─ [Python Quality]
│   ├─ Black (formatting)
│   ├─ isort (imports)
│   ├─ flake8 (linting)
│   └─ mypy (types)
└─ [Security Scan]
    ├─ Bandit (vulnerabilities)
    ├─ Secret detection
    └─ Dependency scan
    ↓
[Validation Summary]
    ↓
✅ All Checks Pass → Ready to Merge
❌ Checks Fail → Review and Fix
```

## Required Status Checks

For branch protection, require:
- ✅ `Validation Summary`
- ✅ `Validate Bundle` (all projects)
- ✅ `Security Scan` (all projects)
- ⚠️ `Python Code Quality` (recommended but not blocking)

## Support

For issues with workflows:
1. Check workflow run logs in GitHub Actions tab
2. Review this README
3. Test locally using commands above
4. Open issue in repository
