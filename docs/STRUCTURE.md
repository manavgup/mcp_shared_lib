# MCP Shared Library Structure

This document outlines the structure of the MCP Shared Library codebase.

## Directory Organization

- `src/`: Main source code
  - `models/`: Data models and schemas
    - Base models for shared entities
    - Specific models for different domain concepts
  - `tools/`: Implementation of shared tools
    - Base tool classes
    - Specialized tools for different operations
  - `utils/`: Utility functions and helpers
    - File operations
    - Git utilities
    - Logging utilities
  - `config/`: Configuration management
    - Configuration loading and validation
  - `error/`: Error handling
    - Exception classes
    - Error handling utilities
  - `state/`: State management
    - State persistence
    - State retrieval
  - `telemetry/`: Telemetry and monitoring
    - Metrics collection
    - Performance monitoring
  - `lib/`: Legacy compatibility modules
    - Legacy error handling
    - Legacy state management
    - Legacy telemetry 

- `config/`: Configuration files
  - Default configurations
  - Environment-specific configurations

- `docs/`: Documentation
  - Architecture documents
  - API documentation
  - Usage guides

## Package Organization

The library is organized as a Python package with the following structure:

```
mcp_shared_lib/
├── src/
│   ├── __init__.py
│   ├── models/
│   ├── tools/
│   ├── utils/
│   ├── config/
│   ├── error/
│   ├── state/
│   ├── telemetry/
│   └── lib/
├── config/
├── docs/
└── tests/
```

## Import Patterns

Code should be imported using the following patterns:

```python
# Importing models
from mcp_shared_lib.models.base_models import BaseModel
from mcp_shared_lib.models.git_models import GitCommit

# Importing tools
from mcp_shared_lib.tools.base_tool import BaseTool
from mcp_shared_lib.tools.file_grouper_tool import FileGrouperTool

# Importing utilities
from mcp_shared_lib.utils.file_utils import read_file, write_file
```

## Dependency Management

Dependencies are managed through the `pyproject.toml` file, with development dependencies specified as optional dependencies under the `[project.optional-dependencies]` section.
