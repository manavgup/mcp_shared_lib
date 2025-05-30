# MCP Shared Library

A shared library for MCP (Model Context Protocol) components, providing common utilities, models, and tools used across the MCP ecosystem including PR Recommender and Change Analyzer.

## Overview

This library contains shared code and utilities that are used by multiple MCP components:

- Common data models
- Shared tools and utilities
- Error handling mechanisms
- Telemetry functionality
- State management
- Configuration loading

## Directory Structure

- `src/`: Source code
  - `models/`: Data models
  - `tools/`: Tool implementations
  - `utils/`: Utility functions
  - `config/`: Configuration handling
  - `error/`: Error handling
  - `state/`: State management
  - `telemetry/`: Telemetry and monitoring
- `tests/`: Test files
- `docs/`: Documentation
- `config/`: Configuration files

## Installation

```bash
pip install -e .
```

## Usage

```python
# Example importing models
from mcp_shared_lib.models.base_models import BaseModel
from mcp_shared_lib.models.git_models import GitCommit

# Example importing tools
from mcp_shared_lib.tools.base_tool import BaseTool
from mcp_shared_lib.tools.file_grouper_tool import FileGrouperTool

# Example importing utilities
from mcp_shared_lib.utils.file_utils import read_file, write_file
from mcp_shared_lib.utils.git_utils import get_repo_root
```

## Development

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd mcp_shared_lib

# Install development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest
```

## License

[Specify license information]
