"""
Pytest configuration and shared fixtures.
"""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark_session():
    """
    Create a Spark session for the entire test session.
    """
    spark = SparkSession.builder \
        .master("local[1]") \
        .appName("high-risk-wifi-tests") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.default.parallelism", "1") \
        .getOrCreate()

    yield spark

    spark.stop()


@pytest.fixture(scope="function")
def spark(spark_session):
    """
    Provide Spark session to individual tests.
    """
    return spark_session
