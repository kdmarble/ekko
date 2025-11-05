.PHONY: help install test format lint clean package

help:
	@echo "ekko - Development Commands"
	@echo ""
	@echo "make install    - Install ekko locally (editable mode)"
	@echo "make test       - Run all tests"
	@echo "make format     - Format code with black"
	@echo "make lint       - Lint code with flake8"
	@echo "make package    - Build Python package for distribution"
	@echo "make clean      - Remove build artifacts"
	@echo ""

install:
	@echo "Installing ekko in editable mode..."
	cd ekko_package && pip install -e .

test:
	@echo "Running tests..."
	python3 tests/test_setup_wizard.py
	python3 tests/test_provider_switching.py
	python3 tests/test_upgrade_compatibility.py
	@echo ""
	@echo "Note: test_piped_installation.py is disabled (single-file distribution removed)"
	@echo "✓ All enabled tests passed"

format:
	@which black > /dev/null || (echo "Install black: pip install black" && exit 1)
	@echo "Formatting source code..."
	black ekko_package/ekko/*.py ekko_package/ekko/providers/*.py

lint:
	@which flake8 > /dev/null || (echo "Install flake8: pip install flake8" && exit 1)
	@echo "Linting source code..."
	flake8 ekko_package/ekko/*.py ekko_package/ekko/providers/*.py \
		--max-line-length=100 --ignore=E501,W503

package:
	@echo "Building Python package..."
	cd ekko_package && python3 -m build
	@echo "✓ Package built in ekko_package/dist/"

clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf ekko_package/__pycache__
	rm -rf ekko_package/ekko/__pycache__
	rm -rf ekko_package/ekko/providers/__pycache__
	rm -rf ekko_package/build/
	rm -rf ekko_package/dist/
	rm -rf ekko_package/*.egg-info
	rm -rf test_output/
	@echo "✓ Cleaned"
