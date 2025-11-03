.PHONY: help install test demo clean format lint

help:
	@echo "aicmd - Development Commands"
	@echo ""
	@echo "make install    - Install aicmd locally"
	@echo "make demo       - Run demo without installing"
	@echo "make test       - Run tests"
	@echo "make format     - Format code with black"
	@echo "make lint       - Lint code with flake8"
	@echo "make clean      - Remove build artifacts"
	@echo ""

install:
	@echo "Installing aicmd..."
	bash install.sh

demo:
	@echo "Running demo..."
	bash demo.sh

test:
	@echo "Running tests..."
	python3 aicmd.py --help
	python3 aicmd.py --version
	@echo "✓ Basic tests passed"

format:
	@which black > /dev/null || (echo "Install black: pip install black" && exit 1)
	black aicmd.py

lint:
	@which flake8 > /dev/null || (echo "Install flake8: pip install flake8" && exit 1)
	flake8 aicmd.py --max-line-length=100 --ignore=E501,W503

clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf test_output/
	@echo "✓ Cleaned"
