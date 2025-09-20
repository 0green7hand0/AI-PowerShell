"""Main entry point for the AI PowerShell Assistant MCP Server"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from startup_system import main as startup_main


if __name__ == "__main__":
    # Use the comprehensive startup system
    exit_code = asyncio.run(startup_main())
    sys.exit(exit_code)