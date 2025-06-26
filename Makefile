.PHONY: help install test clean train preprocess deploy lint format

# Default target
help:
	@echo "AI Intrusion Detection System - Available Commands:"
	@echo "=================================================="
	@echo "install     - Install the package and dependencies"
	@echo "test        - Run unit tests"
	@echo "clean       - Clean up temporary files"
	@echo "preprocess  - Run data preprocessing"
	@echo "train       - Train the advanced Random Forest model"
	@echo "deploy      - Test model deployment"
	@echo "lint        - Run code linting"
	@echo "format      - Format code with black"
	@echo "notebook    - Start Jupyter Lab"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest black flake8

# Testing
test:
	python -m pytest tests/ -v

# Data processing
preprocess:
	cd src && python preprocess_data.py

# Model training
train:
	cd src && python train_advanced_rf.py

# Deployment testing
deploy:
	cd src && python deploy_model.py

# Code quality
lint:
	flake8 src/ tests/ --max-line-length=88

format:
	black src/ tests/ --line-length=88

# Jupyter
notebook:
	jupyter lab notebooks/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Full pipeline
full-pipeline: clean preprocess train deploy test
	@echo "✅ Full pipeline completed successfully!"

# Setup development environment
setup-dev: install-dev
	@echo "🔧 Development environment setup complete!"
	@echo "📚 Run 'make help' to see available commands"
