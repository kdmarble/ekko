"""
Setup script for ekko package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __init__.py
version = "1.2.0-dev"
init_file = Path(__file__).parent / "ekko" / "__init__.py"
with open(init_file, "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read README
readme_file = Path(__file__).parent.parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="ekko",
    version=version,
    description="AI-powered command line assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kdmarble",
    author_email="",
    url="https://github.com/kdmarble/ekko",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "typer>=0.9.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ekko=ekko.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    keywords="cli ai llm command-line assistant anthropic ollama",
    project_urls={
        "Bug Reports": "https://github.com/kdmarble/ekko/issues",
        "Source": "https://github.com/kdmarble/ekko",
    },
)
