from setuptools import setup, find_packages

setup(
    name="merlin-mlm-dashboard",
    version="1.0.0",
    description="Merlin MLM Operations Dashboard with ML-powered Warehouse Prediction",
    author="Amjad",
    author_email="amjad@merlin.com",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.57.0",
        "pandas==2.0.3",
        "numpy==1.24.3",
        "scikit-learn==1.8.0",
        "openpyxl==3.1.2",
    ],
    python_requires=">=3.8",
)
