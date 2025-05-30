"""
Utility functions and helpers for the MCP project.
"""
from .file_utils import (
    normalize_path,
    get_relative_path,
    get_file_extension,
    get_directory,
    filter_files_by_extension,
    group_files_by_directory,
    find_common_parent_directory
)

from .git_utils import (
    is_git_repo,
    get_git_root,
    get_current_branch,
    get_changed_files,
    get_file_diff,
    get_commit_history,
    create_branch,
    checkout_branch,
    commit_changes
)

from .logging_utils import (
    configure_logger,
    get_logger,
    ProgressTracker,
    log_execution_time
)

__all__ = [
    # File utils
    'normalize_path',
    'get_relative_path',
    'get_file_extension',
    'get_directory',
    'filter_files_by_extension',
    'group_files_by_directory',
    'find_common_parent_directory',
    
    # Git utils
    'is_git_repo',
    'get_git_root',
    'get_current_branch',
    'get_changed_files',
    'get_file_diff',
    'get_commit_history',
    'create_branch',
    'checkout_branch',
    'commit_changes',
    
    # Logging utils
    'configure_logger',
    'get_logger',
    'ProgressTracker',
    'log_execution_time'
]
