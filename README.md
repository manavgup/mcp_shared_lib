# MCP Shared Library

Shared models and services for MCP (Model Context Protocol) components.

## Overview

This library provides common data models, services, and utilities used by:
- `mcp_local_repo_analyzer` - Git repository analysis tools
- `mcp_pr_recommender` - PR recommendation engine

## Installation

```bash
cd mcp_shared_lib
poetry install
```

## Usage

### Models

```python
from mcp_shared_lib.models import FileStatus, WorkingDirectoryChanges, RiskAssessment

# Create a file status
file_status = FileStatus(
    path="src/main.py",
    status_code="M",
    lines_added=10,
    lines_deleted=5
)
```

### Services

```python
from mcp_shared_lib.services import GitClient, ChangeDetector
from mcp_shared_lib.config import GitAnalyzerSettings

# Setup services
settings = GitAnalyzerSettings()
git_client = GitClient(settings)
change_detector = ChangeDetector(git_client)

# Use services
repo = LocalRepository(path=".", name="my-repo", current_branch="main", head_commit="abc123")
changes = await change_detector.detect_working_directory_changes(repo)
```

## Architecture

```
mcp_shared_lib/
├── models/          # Data models
│   ├── git/         # Git-related models
│   ├── analysis/    # Analysis models
│   ├── pr/          # PR models (Phase 2)
│   └── base/        # Base classes
├── services/        # Business logic services
│   ├── git/         # Git services
│   └── pr/          # PR services (Phase 2)
├── tools/           # Tool base classes
├── utils/           # Utility functions
└── config/          # Configuration management
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
poetry run isort .
```

### Type Checking

```bash
poetry run mypy .
```

## Migration Status

- ✅ Phase 1: Foundation setup (models from mcp_local_repo_analyzer)
- ⏳ Phase 2: PR models migration (from mcp_pr_recommender)
- ⏳ Phase 3: Service migration
- ⏳ Phase 4: Repository updates
- ⏳ Phase 5: Testing & cleanup
