"""
Utility functions for git operations.
"""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set, Union

from mcp_shared_lib.src.utils.logging_utils import get_logger
from .file_utils import normalize_path

logger = get_logger(__name__)

def is_git_repo(path: Union[str, Path]) -> bool:
    """
    Check if the specified path is a git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is a git repository, False otherwise
    """
    path = normalize_path(path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception as e:
        logger.error(f"Error checking if {path} is a git repository: {e}")
        return False

def get_git_root(path: Union[str, Path]) -> Optional[Path]:
    """
    Get the root directory of a git repository.
    
    Args:
        path: Path within a git repository
        
    Returns:
        The root directory of the git repository, or None if not a git repository
    """
    path = normalize_path(path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return Path(result.stdout.strip())
        return None
    except Exception as e:
        logger.error(f"Error getting git root for {path}: {e}")
        return None

def get_current_branch(repo_path: Union[str, Path]) -> Optional[str]:
    """
    Get the current git branch.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        The current branch name, or None if not a git repository or an error occurs
    """
    repo_path = normalize_path(repo_path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        logger.error(f"Error getting current branch for {repo_path}: {e}")
        return None

def get_changed_files(repo_path: Union[str, Path], base_ref: str = "HEAD") -> List[str]:
    """
    Get a list of files changed in the current branch compared to the base reference.
    
    Args:
        repo_path: Path to the git repository
        base_ref: Base reference to compare with (default: HEAD)
        
    Returns:
        List of changed file paths relative to the repository root
    """
    repo_path = normalize_path(repo_path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "diff", "--name-only", base_ref],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return []
    except Exception as e:
        logger.error(f"Error getting changed files for {repo_path}: {e}")
        return []

def get_file_diff(repo_path: Union[str, Path], file_path: Union[str, Path], base_ref: str = "HEAD") -> str:
    """
    Get the diff for a specific file.
    
    Args:
        repo_path: Path to the git repository
        file_path: Path to the file (relative to the repository root)
        base_ref: Base reference to compare with (default: HEAD)
        
    Returns:
        The diff content as a string
    """
    repo_path = normalize_path(repo_path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "diff", base_ref, "--", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception as e:
        logger.error(f"Error getting diff for {file_path} in {repo_path}: {e}")
        return ""

def get_commit_history(repo_path: Union[str, Path], max_count: int = 10) -> List[Dict[str, str]]:
    """
    Get the commit history for a repository.
    
    Args:
        repo_path: Path to the git repository
        max_count: Maximum number of commits to retrieve
        
    Returns:
        List of commit dictionaries with 'hash', 'author', 'date', and 'message' keys
    """
    repo_path = normalize_path(repo_path)
    
    try:
        result = subprocess.run(
            [
                "git", "-C", str(repo_path), "log", 
                f"--max-count={max_count}", 
                "--format=%H|%an|%ad|%s"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            commits = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
            
            return commits
        return []
    except Exception as e:
        logger.error(f"Error getting commit history for {repo_path}: {e}")
        return []

def create_branch(repo_path: Union[str, Path], branch_name: str) -> bool:
    """
    Create a new git branch.
    
    Args:
        repo_path: Path to the git repository
        branch_name: Name of the branch to create
        
    Returns:
        True if the branch was created successfully, False otherwise
    """
    repo_path = normalize_path(repo_path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "checkout", "-b", branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error creating branch {branch_name} in {repo_path}: {e}")
        return False

def checkout_branch(repo_path: Union[str, Path], branch_name: str) -> bool:
    """
    Checkout an existing git branch.
    
    Args:
        repo_path: Path to the git repository
        branch_name: Name of the branch to checkout
        
    Returns:
        True if the branch was checked out successfully, False otherwise
    """
    repo_path = normalize_path(repo_path)
    
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "checkout", branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error checking out branch {branch_name} in {repo_path}: {e}")
        return False

def commit_changes(repo_path: Union[str, Path], message: str, files: Optional[List[Union[str, Path]]] = None) -> bool:
    """
    Commit changes to git.
    
    Args:
        repo_path: Path to the git repository
        message: Commit message
        files: Optional list of files to commit (if None, all changes will be committed)
        
    Returns:
        True if the changes were committed successfully, False otherwise
    """
    repo_path = normalize_path(repo_path)
    
    try:
        # Add files
        add_cmd = ["git", "-C", str(repo_path), "add"]
        if files:
            add_cmd.extend([str(f) for f in files])
        else:
            add_cmd.append(".")
            
        add_result = subprocess.run(
            add_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if add_result.returncode != 0:
            logger.error(f"Error adding files in {repo_path}: {add_result.stderr}")
            return False
            
        # Commit changes
        commit_result = subprocess.run(
            ["git", "-C", str(repo_path), "commit", "-m", message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        return commit_result.returncode == 0
    except Exception as e:
        logger.error(f"Error committing changes in {repo_path}: {e}")
        return False
