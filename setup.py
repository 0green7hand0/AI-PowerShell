"""Setup script for AI PowerShell Assistant"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    with open(this_directory / "requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="ai-powershell-assistant",
    version="0.1.0",
    description="An intelligent MCP server for PowerShell command assistance using local AI models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI PowerShell Assistant Team",
    author_email="",
    url="https://github.com/0green7hand0/AI-PowerShell",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-powershell-assistant=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="powershell ai mcp assistant automation",
    project_urls={
        "Bug Reports": "https://github.com/0green7hand0/AI-PowerShell/issues",
        "Source": "https://github.com/0green7hand0/AI-PowerShell",
    },
)
