"""
ekko - AI-powered command line assistant
"""

# Version is managed by setuptools_scm and read from git tags
try:
    from ._version import version as __version__
except ImportError:
    # Fallback version for development when not installed
    __version__ = "0.0.0.dev0"

__author__ = "kdmarble"
__license__ = "MIT"
