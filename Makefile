.PHONY: help build install test format lint clean package

help:
	@echo "ekko - Development Commands"
	@echo ""
	@echo "make build      - Build single-file distribution"
	@echo "make install    - Install ekko locally"
	@echo "make test       - Run all tests"
	@echo "make format     - Format code with black"
	@echo "make lint       - Lint code with flake8"
	@echo "make package    - Build Python package"
	@echo "make clean      - Remove build artifacts"
	@echo ""

build:
	@echo "Building single-file distribution..."
	python3 build.py

install:
	@echo "Installing ekko..."
	bash install-ekko.sh

test:
	@echo "Building single-file distribution..."
	python3 build.py
	@echo ""
	@echo "Running tests..."
	python3 ekko.py --help
	python3 ekko.py --version
	@echo ""
	python3 tests/test_setup_wizard.py
	python3 tests/test_piped_installation.py
	python3 tests/test_provider_switching.py
	python3 tests/test_upgrade_compatibility.py
	@echo ""
	@echo "✓ All tests passed"

format:
	@which black > /dev/null || (echo "Install black: pip install black" && exit 1)
	@echo "Formatting modular source..."
	black ekko_package/ekko/*.py ekko_package/ekko/providers/*.py
	@echo "Rebuilding single-file distribution..."
	python3 build.py

lint:
	@which flake8 > /dev/null || (echo "Install flake8: pip install flake8" && exit 1)
	@echo "Linting modular source..."
	flake8 ekko_package/ekko/*.py ekko_package/ekko/providers/*.py \
		--max-line-length=100 --ignore=E501,W503
	@echo "Linting generated single-file..."
	flake8 ekko.py --max-line-length=100 --ignore=E501,W503

package:
	@echo "Building Python package..."
	cd ekko_package && python3 setup.py sdist bdist_wheel
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
