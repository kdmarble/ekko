#!/usr/bin/env python3
"""
Build script to create single-file ekko.py for distribution

This allows us to:
1. Develop with modular structure for maintainability
2. Distribute as single file for easy curl | bash installation
"""

import sys
import re
from pathlib import Path


def read_module(file_path: Path) -> str:
    """
    Read a module file and extract its content.

    Args:
        file_path: Path to the module file

    Returns:
        Module content as string
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Remove module docstring if it's the first thing
    content = re.sub(r'^"""[\s\S]*?"""\s*\n', "", content, count=1)

    # Remove imports from within ekko package
    content = re.sub(r"^from ekko\..*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^import ekko\..*$", "", content, flags=re.MULTILINE)

    return content


def build_single_file():
    """Build single-file ekko.py from modular source."""
    print("🔨 Building single-file ekko.py...")

    package_dir = Path(__file__).parent / "ekko_package" / "ekko"
    output_file = Path(__file__).parent / "ekko.py"

    # Read version from __init__.py
    init_file = package_dir / "__init__.py"
    version = "1.2.0-dev"  # Default
    with open(init_file, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

    # Start building the single file
    output = []

    # Header
    output.append("#!/usr/bin/env python3")
    output.append('"""')
    output.append("ekko - AI-powered command line assistant")
    output.append("Supports Anthropic API and Ollama")
    output.append('"""')
    output.append("")

    # Standard library imports
    output.append("import sys")
    output.append("import os")
    output.append("import json")
    output.append("import subprocess")
    output.append("import re")
    output.append("from pathlib import Path")
    output.append("from typing import Dict, Any")
    output.append("from abc import ABC, abstractmethod")
    output.append("")

    # Check for requests
    output.append("try:")
    output.append("    import requests")
    output.append("except ImportError:")
    output.append('    print("Error: requests module not found. Install with: pip install requests")')
    output.append("    sys.exit(1)")
    output.append("")
    output.append("")

    # Add base provider
    output.append("# " + "=" * 76)
    output.append("# Base Provider Interface")
    output.append("# " + "=" * 76)
    output.append("")
    base_content = read_module(package_dir / "providers" / "base.py")
    output.append(base_content.strip())
    output.append("")
    output.append("")

    # Add Anthropic provider
    output.append("# " + "=" * 76)
    output.append("# Anthropic Provider")
    output.append("# " + "=" * 76)
    output.append("")
    anthropic_content = read_module(package_dir / "providers" / "anthropic.py")
    # Remove the import of LLMProvider
    anthropic_content = re.sub(
        r"^from ekko\.providers\.base import LLMProvider\s*$",
        "",
        anthropic_content,
        flags=re.MULTILINE,
    )
    output.append(anthropic_content.strip())
    output.append("")
    output.append("")

    # Add Ollama provider
    output.append("# " + "=" * 76)
    output.append("# Ollama Provider")
    output.append("# " + "=" * 76)
    output.append("")
    ollama_content = read_module(package_dir / "providers" / "ollama.py")
    ollama_content = re.sub(
        r"^from ekko\.providers\.base import LLMProvider\s*$",
        "",
        ollama_content,
        flags=re.MULTILINE,
    )
    output.append(ollama_content.strip())
    output.append("")
    output.append("")

    # Add provider registry (manually since it's in __init__.py)
    output.append("# " + "=" * 76)
    output.append("# Provider Registry")
    output.append("# " + "=" * 76)
    output.append("")
    output.append("PROVIDERS = {")
    output.append('    "anthropic": AnthropicProvider,')
    output.append('    "ollama": OllamaProvider,')
    output.append("}")
    output.append("")
    output.append("")
    output.append("def get_provider(provider_name: str, **kwargs):")
    output.append('    """Get a provider instance by name."""')
    output.append("    provider_class = PROVIDERS.get(provider_name.lower())")
    output.append("    if not provider_class:")
    output.append('        available = ", ".join(PROVIDERS.keys())')
    output.append("        raise ValueError(")
    output.append('            f"Unknown provider \'{provider_name}\'. Available: {available}"')
    output.append("        )")
    output.append("    return provider_class(**kwargs)")
    output.append("")
    output.append("")

    # Add config management
    output.append("# " + "=" * 76)
    output.append("# Configuration Management")
    output.append("# " + "=" * 76)
    output.append("")
    config_content = read_module(package_dir / "config.py")
    config_content = re.sub(
        r"^from ekko\.providers import PROVIDERS\s*$",
        "",
        config_content,
        flags=re.MULTILINE,
    )
    output.append(config_content.strip())
    output.append("")
    output.append("")

    # Add command generator
    output.append("# " + "=" * 76)
    output.append("# Command Generator")
    output.append("# " + "=" * 76)
    output.append("")
    generator_content = read_module(package_dir / "generator.py")
    generator_content = re.sub(
        r"^from ekko\.providers import get_provider\s*$",
        "",
        generator_content,
        flags=re.MULTILINE,
    )
    output.append(generator_content.strip())
    output.append("")
    output.append("")

    # Add CLI (main function)
    output.append("# " + "=" * 76)
    output.append("# Command Line Interface")
    output.append("# " + "=" * 76)
    output.append("")
    cli_content = read_module(package_dir / "cli.py")
    # Replace version import with literal
    cli_content = re.sub(
        r"from ekko import __version__\s*", "", cli_content, flags=re.MULTILINE
    )
    cli_content = re.sub(
        r"from ekko\.config import Config\s*", "", cli_content, flags=re.MULTILINE
    )
    cli_content = re.sub(
        r"from ekko\.generator import CommandGenerator\s*",
        "",
        cli_content,
        flags=re.MULTILINE,
    )
    cli_content = cli_content.replace("f\"ekko v{__version__}\"", f'\"ekko v{version}\"')

    # Remove the if __name__ == "__main__" block from cli.py since we'll add it separately
    cli_content = re.sub(
        r'if __name__ == "__main__":\s+main\(\)\s*',
        "",
        cli_content,
        flags=re.MULTILINE | re.DOTALL
    )

    output.append(cli_content.strip())
    output.append("")
    output.append("")

    # Add entry point
    output.append('if __name__ == "__main__":')
    output.append("    main()")
    output.append("")

    # Write to file
    final_content = "\n".join(output)

    # Clean up multiple blank lines
    final_content = re.sub(r"\n{3,}", "\n\n", final_content)

    # Remove blank lines at the start of file
    final_content = final_content.lstrip("\n")

    with open(output_file, "w") as f:
        f.write(final_content)

    # Make executable
    output_file.chmod(0o755)

    print(f"✅ Built single-file distribution: {output_file}")
    print(f"   Version: {version}")
    print(f"   Size: {len(final_content)} bytes")

    # Run a quick test
    print("\n🧪 Testing built file...")
    import subprocess

    result = subprocess.run(
        ["python3", str(output_file), "--version"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"✅ Test passed: {result.stdout.strip()}")
    else:
        print(f"❌ Test failed: {result.stderr}")
        return False

    return True


if __name__ == "__main__":
    success = build_single_file()
    sys.exit(0 if success else 1)
