# Testing Documentation

This document provides quick reference for running tests in this repository.

## Quick Start

### Run Tests for a Project

```bash
cd projects/high-risk-wifi
pip install -r requirements-dev.txt
pytest tests/
```

### Run All Tests with Coverage

```bash
cd projects/high-risk-wifi
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### View Coverage Report

```bash
open htmlcov/index.html
```

## Project Test Suites

### High-Risk WiFi Detection

**Location:** `projects/high-risk-wifi/tests/`

**Test Modules:**
- `test_features.py` - Feature engineering functions
- `test_inference.py` - Inference utilities

**Run Tests:**
```bash
cd projects/high-risk-wifi
pytest tests/ -v
```

**Coverage:**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Suspicious Location Detection

**Location:** `projects/suspicious-location/tests/`

**Test Modules:**
- `test_geo_utils.py` - Geographic calculations
- `test_anomaly_detection.py` - Anomaly detection algorithms

**Run Tests:**
```bash
cd projects/suspicious-location
pytest tests/ -v
```

**Coverage:**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## CI/CD Testing

### Automated Test Runs

Tests run automatically on:
- **Pull Requests** - When Python files are modified
- **Pushes** - To main/master/develop branches

**Workflow:** `.github/workflows/run-tests.yml`

**What Gets Tested:**
- Unit tests for all changed projects
- Multiple Python versions (3.10, 3.11)
- Code coverage reporting
- Test result publishing

### Required Checks

Before PR merge:
- ✅ All unit tests pass
- ✅ Code coverage ≥ 80%
- ✅ No critical linting errors
- ✅ No security vulnerabilities

## Test Configuration

### Pytest Configuration

Each project has a `pytest.ini` file:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_simple_function():
    pass

@pytest.mark.integration
def test_end_to_end():
    pass

@pytest.mark.slow
def test_large_dataset():
    pass
```

Run by marker:
```bash
pytest tests/ -m unit          # Only unit tests
pytest tests/ -m "not slow"    # Skip slow tests
```

## Dependencies

### Production Dependencies

Defined in `setup.py`:
- pyspark
- mlflow
- scikit-learn
- pandas
- numpy

### Development Dependencies

Defined in `requirements-dev.txt`:
- pytest
- pytest-cov
- pytest-mock
- black
- isort
- flake8
- mypy

## Writing Tests

### Basic Test Structure

```python
def test_feature_extraction(spark):
    """Test feature extraction logic."""
    # Arrange
    data = [("2024-01-15 14:30:00",)]
    df = spark.createDataFrame(data, ["timestamp"])

    # Act
    result = extract_features(df)

    # Assert
    assert "hour_of_day" in result.columns
    assert result.first()["hour_of_day"] == 14
```

### Using Fixtures

```python
# conftest.py
@pytest.fixture(scope="session")
def spark_session():
    """Provide Spark session."""
    spark = SparkSession.builder.master("local[1]").getOrCreate()
    yield spark
    spark.stop()

# test_*.py
def test_with_spark(spark_session):
    """Test using fixture."""
    df = spark_session.createDataFrame([(1, "a")], ["id", "value"])
    assert df.count() == 1
```

## Coverage Reports

### Terminal Coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Output:**
```
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
src/__init__.py            1      0   100%
src/features.py           45      5    89%   23-27
src/inference.py          32      0   100%
----------------------------------------------------
TOTAL                     78      5    94%
```

### HTML Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### XML Coverage (for CI)

```bash
pytest tests/ --cov=src --cov-report=xml
```

## Common Commands

### Run All Tests
```bash
pytest tests/
```

### Verbose Output
```bash
pytest tests/ -v
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Specific Test File
```bash
pytest tests/test_features.py
```

### Run Specific Test
```bash
pytest tests/test_features.py::TestTimeFeatures::test_hour_extraction
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Run Last Failed Tests
```bash
pytest tests/ --lf
```

### Run in Parallel
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

## Troubleshooting

### ImportError: No module named 'src'

**Solution:**
```bash
pip install -e .
```

### Spark Session Issues

**Solution:**
```bash
# Ensure Java 11 is installed
java -version

# Use local mode
export PYSPARK_SUBMIT_ARGS="--master local[1]"
```

### Tests Pass Locally but Fail in CI

**Check:**
1. Python version match (use same as CI)
2. Dependencies installed correctly
3. Environment variables set
4. No hardcoded paths

### Slow Tests

**Solutions:**
```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run in parallel
pytest tests/ -n auto

# Use smaller test datasets
```

## Best Practices

1. **Test Naming** - Use descriptive names
   ```python
   # Good
   def test_haversine_distance_returns_zero_for_same_point()

   # Bad
   def test1()
   ```

2. **Test Independence** - Each test should run independently
   ```python
   # Good - Creates own data
   def test_feature():
       data = create_test_data()
       result = process(data)
       assert result == expected

   # Bad - Relies on global state
   def test_feature():
       global shared_data
       result = process(shared_data)
       assert result == expected
   ```

3. **Use Fixtures** - Share setup code
   ```python
   @pytest.fixture
   def sample_data():
       return [1, 2, 3, 4, 5]

   def test_sum(sample_data):
       assert sum(sample_data) == 15
   ```

4. **Mock External Dependencies** - Don't test external services
   ```python
   @patch('module.external_api_call')
   def test_feature(mock_api):
       mock_api.return_value = {"status": "success"}
       result = my_function()
       assert result.status == "success"
   ```

5. **Test Edge Cases** - Not just happy path
   ```python
   def test_divide_by_zero():
       with pytest.raises(ZeroDivisionError):
           divide(10, 0)
   ```

## Additional Resources

- **Detailed Testing Guide:** [docs/testing-guide.md](docs/testing-guide.md)
- **Workflow Documentation:** [.github/workflows/README.md](.github/workflows/README.md)
- **pytest Documentation:** https://docs.pytest.org/
- **PySpark Testing:** https://spark.apache.org/docs/latest/api/python/reference/pyspark.testing.html

## Getting Help

For testing issues:
1. Check this documentation
2. Review example tests in `projects/*/tests/`
3. Check CI logs for specific errors
4. Ask in PR review comments
