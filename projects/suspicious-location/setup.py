"""
Setup configuration for suspicious-location package.
"""

from setuptools import setup, find_packages

setup(
    name="suspicious-location",
    version="0.1.0",
    description="Suspicious location detection utilities",
    author="Data Science Team",
    packages=find_packages(),
    install_requires=[
        "pyspark>=3.5.0",
        "mlflow>=2.10.0",
        "scikit-learn>=1.4.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "geopy>=2.4.0",
        "hdbscan>=0.8.33",
    ],
    python_requires=">=3.10",
)
