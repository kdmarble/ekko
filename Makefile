.PHONY: help install test demo clean format lint

help:
	@echo "ekko - Development Commands"
	@echo ""
	@echo "make install    - Install ekko locally"
	@echo "make demo       - Run demo without installing"
	@echo "make test       - Run tests"
	@echo "make format     - Format code with black"
	@echo "make lint       - Lint code with flake8"
	@echo "make clean      - Remove build artifacts"
	@echo ""

install:
	@echo "Installing ekko..."
	bash install-ekko.sh

demo:
	@echo "Running demo..."
	bash demo.sh

test:
	@echo "Running tests..."
	python3 ekko.py --help
	python3 ekko.py --version
	@echo "✓ Basic tests passed"

format:
	@which black > /dev/null || (echo "Install black: pip install black" && exit 1)
	black ekko.py

lint:
	@which flake8 > /dev/null || (echo "Install flake8: pip install flake8" && exit 1)
	flake8 ekko.py --max-line-length=100 --ignore=E501,W503

clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf test_output/
	@echo "✓ Cleaned"
