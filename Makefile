.PHONY: help install test test-cov test-watch format lint fix clean package

help:
	@echo "ekko - Development Commands"
	@echo ""
	@echo "make install     - Install ekko locally with dev dependencies"
	@echo "make test        - Run all tests with pytest"
	@echo "make test-cov    - Run tests with coverage report"
	@echo "make test-watch  - Run tests in watch mode (requires pytest-watch)"
	@echo "make format      - Format code with ruff"
	@echo "make lint        - Lint code with ruff"
	@echo "make fix         - Auto-fix linting issues with ruff"
	@echo "make package     - Build Python package for distribution"
	@echo "make clean       - Remove build artifacts"
	@echo ""

install:
	@echo "Installing ekko in editable mode with dev dependencies..."
	cd ekko_package && pip install -e .[dev]

test:
	@echo "Running tests with pytest..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=ekko --cov-report=html --cov-report=term

test-watch:
	@echo "Running tests in watch mode..."
	@which ptw > /dev/null || (echo "Install pytest-watch: pip install pytest-watch" && exit 1)
	ptw tests/ -- -v

format:
	@which ruff > /dev/null || (echo "Install ruff: pip install ruff" && exit 1)
	@echo "Formatting source code with ruff..."
	ruff format ekko_package/ekko/*.py ekko_package/ekko/providers/*.py

lint:
	@which ruff > /dev/null || (echo "Install ruff: pip install ruff" && exit 1)
	@echo "Linting source code with ruff..."
	ruff check ekko_package/ekko/*.py ekko_package/ekko/providers/*.py

fix:
	@which ruff > /dev/null || (echo "Install ruff: pip install ruff" && exit 1)
	@echo "Auto-fixing linting issues with ruff..."
	ruff check --fix ekko_package/ekko/*.py ekko_package/ekko/providers/*.py

package:
	@echo "Building Python package..."
	cd ekko_package && python3 -m build
	@echo "✓ Package built in ekko_package/dist/"

clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf ekko_package/__pycache__
	rm -rf ekko_package/ekko/__pycache__
	rm -rf ekko_package/ekko/providers/__pycache__
	rm -rf ekko_package/build/
	rm -rf ekko_package/dist/
	rm -rf ekko_package/*.egg-info
	rm -rf tests/__pycache__
	rm -rf test_output/
	@echo "✓ Cleaned"
