"""
Setup configuration for high-risk-wifi package.
"""

from setuptools import setup, find_packages

setup(
    name="high-risk-wifi",
    version="0.1.0",
    description="High-risk WiFi detection utilities",
    author="Data Science Team",
    packages=find_packages(),
    install_requires=[
        "pyspark>=3.5.0",
        "mlflow>=2.10.0",
        "scikit-learn>=1.4.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.10",
)
