# Testing Guide

This guide covers testing practices and procedures for Databricks bundle projects.

## Test Structure

Each project should have a `tests/` directory with the following structure:

```
project/
├── src/               # Source code
├── tests/             # Test directory
│   ├── __init__.py   # Makes tests a package
│   ├── conftest.py   # Shared fixtures
│   ├── test_*.py     # Test modules
│   └── integration/  # Integration tests (optional)
└── pytest.ini        # Pytest configuration
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation.

**Location:** `tests/test_*.py`

**Example:**
```python
def test_extract_time_features(spark):
    """Test time feature extraction."""
    data = [("2024-01-15 14:30:00",)]
    df = spark.createDataFrame(data, ["timestamp"])
    df = df.withColumn("timestamp", F.to_timestamp("timestamp"))

    result = extract_time_features(df)

    assert "hour_of_day" in result.columns
    assert result.first()["hour_of_day"] == 14
```

### Integration Tests

Test multiple components working together.

**Location:** `tests/integration/test_*.py`

**Example:**
```python
@pytest.mark.integration
def test_end_to_end_pipeline(spark):
    """Test complete data pipeline."""
    # Create input data
    # Run through bronze -> silver -> gold
    # Validate final output
    pass
```

## Running Tests Locally

### Prerequisites

```bash
cd projects/your-project

# Install dependencies
pip install -r requirements-dev.txt

# Or install project in development mode
pip install -e .
pip install pytest pytest-cov
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_features.py
```

### Run Specific Test

```bash
pytest tests/test_features.py::TestTimeFeatures::test_extract_time_features_hour
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Run Only Fast Tests

```bash
pytest tests/ -m "not slow"
```

### Run Integration Tests

```bash
pytest tests/ -m integration
```

## Writing Good Tests

### Test Naming

Follow these conventions:
- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<what>_<expected>`

**Examples:**
```python
# Good
def test_haversine_distance_same_point()
def test_calculate_velocity_zero_time()
def test_anomaly_detector_fit_returns_self()

# Avoid
def test1()
def test_function()
def test_it_works()
```

### Test Structure (AAA Pattern)

```python
def test_feature():
    # Arrange - Set up test data
    data = create_test_data()

    # Act - Execute the code being tested
    result = process_data(data)

    # Assert - Verify the results
    assert result == expected_value
```

### Use Fixtures

Share common setup across tests:

```python
# conftest.py
@pytest.fixture
def spark():
    """Create Spark session for testing."""
    return SparkSession.builder \
        .master("local[1]") \
        .appName("tests") \
        .getOrCreate()

@pytest.fixture
def sample_data():
    """Sample test data."""
    return [
        ("user1", 40.7128, -74.0060),
        ("user2", 34.0522, -118.2437),
    ]

# test_*.py
def test_with_fixtures(spark, sample_data):
    """Test using fixtures."""
    df = spark.createDataFrame(sample_data, ["user", "lat", "lon"])
    assert df.count() == 2
```

### Parameterized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("signal,expected_quality", [
    (-45, 4),  # excellent
    (-55, 3),  # good
    (-65, 2),  # fair
    (-75, 1),  # poor
])
def test_signal_quality(signal, expected_quality):
    result = classify_signal(signal)
    assert result == expected_quality
```

### Mocking External Dependencies

Don't test external services:

```python
from unittest.mock import Mock, patch

@patch('mlflow.pyfunc.spark_udf')
def test_predict_without_mlflow(mock_spark_udf, spark):
    """Test prediction logic without MLflow."""
    mock_udf = Mock(return_value=0.7)
    mock_spark_udf.return_value = mock_udf

    # Test your code
    result = run_inference(data)

    assert "risk_score" in result.columns
```

## PySpark Testing

### Setup

Use local Spark for testing:

```python
@pytest.fixture(scope="session")
def spark_session():
    """Session-scoped Spark session."""
    spark = SparkSession.builder \
        .master("local[1]") \
        .appName("tests") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.default.parallelism", "1") \
        .getOrCreate()

    yield spark
    spark.stop()
```

### Testing DataFrames

```python
def test_dataframe_transformation(spark):
    """Test DataFrame transformation."""
    # Create test data
    data = [("Alice", 25), ("Bob", 30)]
    df = spark.createDataFrame(data, ["name", "age"])

    # Apply transformation
    result = df.filter(F.col("age") > 26)

    # Assert
    assert result.count() == 1
    assert result.first()["name"] == "Bob"
```

### Comparing DataFrames

```python
from pyspark.testing.utils import assertDataFrameEqual

def test_dataframe_equality(spark):
    """Test DataFrames are equal."""
    df1 = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "value"])
    df2 = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "value"])

    assertDataFrameEqual(df1, df2)
```

## Coverage Requirements

### Minimum Coverage

- Overall: 80%
- Critical modules: 90%
- Utilities: 70%

### Check Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Coverage Configuration

Add to `pytest.ini`:

```ini
[pytest]
addopts =
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Pull requests modifying Python code
- Pushes to main/master/develop branches

**Workflow:** `.github/workflows/run-tests.yml`

**Runs:**
- Python 3.10 and 3.11
- All projects with changes
- Full coverage reporting

### Required Checks

Before merging:
- ✅ All tests pass
- ✅ Coverage ≥ 80%
- ✅ No linting errors
- ✅ No security issues

## Test Data

### Creating Test Data

Keep test data small and focused:

```python
# Good - Minimal data
def test_feature():
    data = [(1, "test")]
    df = spark.createDataFrame(data, ["id", "value"])
    # ...

# Avoid - Too much data
def test_feature():
    data = [(i, f"value_{i}") for i in range(10000)]
    df = spark.createDataFrame(data, ["id", "value"])
    # ...
```

### Test Data Files

For larger test datasets:

```
tests/
├── data/
│   ├── sample_wifi.json
│   ├── sample_locations.csv
│   └── expected_output.parquet
└── test_*.py
```

Load in tests:

```python
import json
from pathlib import Path

def test_with_file_data():
    test_dir = Path(__file__).parent
    with open(test_dir / "data/sample_wifi.json") as f:
        data = json.load(f)
    # ...
```

## Performance Testing

### Mark Slow Tests

```python
@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset."""
    # Expensive test
    pass
```

Run without slow tests:
```bash
pytest tests/ -m "not slow"
```

### Benchmark Tests

```python
import time

def test_performance():
    """Test performance is acceptable."""
    start = time.time()

    # Run operation
    result = expensive_operation()

    duration = time.time() - start

    assert duration < 5.0  # Should complete in < 5 seconds
```

## Common Issues

### Spark Session Issues

**Problem:** Spark session not starting

**Solution:**
```python
# Ensure Java is installed
# Use local mode for tests
spark = SparkSession.builder.master("local[1]").getOrCreate()
```

### Import Errors

**Problem:** Cannot import src modules

**Solution:**
```bash
# Install project in development mode
pip install -e .
```

### Fixture Scope Issues

**Problem:** Fixture recreated too often

**Solution:**
```python
# Use appropriate scope
@pytest.fixture(scope="session")  # Once per test session
@pytest.fixture(scope="module")   # Once per test module
@pytest.fixture(scope="function")  # Once per test function (default)
```

## Best Practices

### DO

- ✅ Write tests for all public functions
- ✅ Use descriptive test names
- ✅ Test edge cases and error conditions
- ✅ Keep tests independent
- ✅ Use fixtures for common setup
- ✅ Mock external dependencies
- ✅ Aim for 80%+ coverage

### DON'T

- ❌ Test implementation details
- ❌ Write flaky tests
- ❌ Share state between tests
- ❌ Test external services directly
- ❌ Ignore test failures
- ❌ Skip writing tests for "simple" code
- ❌ Commit commented-out tests

## Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [PySpark testing](https://spark.apache.org/docs/latest/api/python/reference/pyspark.testing.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Tools
- pytest - Test framework
- pytest-cov - Coverage plugin
- pytest-mock - Mocking plugin
- pytest-xdist - Parallel test execution

### Examples

See existing tests:
- `projects/high-risk-wifi/tests/`
- `projects/suspicious-location/tests/`

## Getting Help

For testing questions:
1. Check this guide
2. Review example tests
3. Check pytest documentation
4. Ask team in PR review
