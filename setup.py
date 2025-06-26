#!/usr/bin/env python3
"""
Setup script for AI Intrusion Detection System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-intrusion-detection",
    version="1.0.0",
    author="Saineel Gutta",
    author_email="team@example.com",
    description="An advanced machine learning-based intrusion detection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/AI-Intrusion-Detection-System",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.4.0", "black>=23.0.0", "flake8>=6.0.0"],
        "jupyter": ["jupyter>=1.0.0", "jupyterlab>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "intrusion-detect=src.deploy_model:main",
            "train-ids=src.train_advanced_rf:main",
            "preprocess-ids=src.preprocess_data:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
)
