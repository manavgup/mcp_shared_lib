import os
import logging
import json
import time
import subprocess
from typing import List, Dict, Any, Optional, ClassVar, Union, Type
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from mcp_shared_lib.src.utils.logging_utils import get_logger
from mcp_shared_lib.src.utils.git_utils import (
    get_changed_files,
    get_file_diff,
    is_git_repo,
    get_git_root
)
from mcp_shared_lib.src.tools.base_tool import BaseRepoTool
from mcp_shared_lib.src.models.git_models import FileStatusType
from mcp_shared_lib.src.models.pr_suggestion_models import PRSuggestion, PullRequestGroup
from mcp_shared_lib.src.models.analysis_models import RepositoryAnalysis, DirectorySummary, FileChange
from mcp_shared_lib.src.models.tool_models import GitAnalysisToolInput, GitAnalysisOutput, LineChanges

logger = get_logger(__name__)

# Create output directory if it doesn't exist
OUTPUT_DIR = "tool_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_changed_file_list(repo_path: Union[str, Path]) -> List[str]:
    """
    Get list of changed files in a git repository.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        List of changed file paths
    """
    if not is_git_repo(repo_path):
        logger.error(f"{repo_path} is not a git repository")
        return []
        
    return get_changed_files(repo_path)

def get_changed_files_stats(repo_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Get statistics for changed files in a git repository.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        List of dictionaries with file path, added lines, deleted lines
    """
    if not is_git_repo(repo_path):
        logger.error(f"{repo_path} is not a git repository")
        return []
        
    # Get changed files first
    files = get_changed_files(repo_path)
    
    # Now get stats for each file
    stats = []
    for file_path in files:
        try:
            # Use git diff --numstat to get added/deleted lines
            result = subprocess.run(
                ["git", "-C", str(repo_path), "diff", "--numstat", "--", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse output (format: added deleted filename)
                parts = result.stdout.strip().split()
                if len(parts) >= 3:
                    stats.append({
                        "file_path": file_path,
                        "added": int(parts[0]) if parts[0] != "-" else 0,
                        "deleted": int(parts[1]) if parts[1] != "-" else 0
                    })
                else:
                    stats.append({
                        "file_path": file_path,
                        "added": 0,
                        "deleted": 0
                    })
            else:
                stats.append({
                    "file_path": file_path,
                    "added": 0,
                    "deleted": 0
                })
        except Exception as e:
            logger.error(f"Error getting stats for {file_path}: {e}")
            stats.append({
                "file_path": file_path,
                "added": 0,
                "deleted": 0
            })
    
    return stats

class GitAnalysisTool(BaseRepoTool):
    """Tool for analyzing git changes."""
    name: str = "analyze_git_changes"
    description: str = "Analyze changes in a Git repository to understand what files have changed and how"
    args_schema: Type = GitAnalysisToolInput
    
    # Store quick mode flag as a class variable
    _use_quick_mode: ClassVar[bool] = False
    
    def __init__(self, repo_path: Optional[str] = None, use_quick_mode: bool = False):
        """
        Initialize the tool with repository path.
        
        Args:
            repo_path: Path to the git repository
            use_quick_mode: If True, uses faster methods with fewer details
        """
        super().__init__()
        if repo_path:
            self._repo_path = repo_path
        self.set_quick_mode(use_quick_mode)
    
    def set_quick_mode(self, use_quick_mode: bool) -> None:
        """Set the quick mode flag."""
        self.__class__._use_quick_mode = use_quick_mode
        
    def get_quick_mode(self) -> bool:
        """Get the quick mode flag."""
        return getattr(self.__class__, '_use_quick_mode', False)
    
    def verify_git_file_count(self, repo_path: str) -> int:
        """Directly verify the number of changed files using git command."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            if result.returncode != 0:
                logger.error(f"Error running git command: {result.stderr}")
                return 0
                
            files = [f for f in result.stdout.splitlines() if f.strip()]
            return len(files)
        except Exception as e:
            logger.error(f"Error verifying file count: {e}")
            return 0
    
    def _run(self, repo_path: Optional[str] = None, query: Optional[str] = None) -> str:
        """Run the tool with smarter chunking."""
        # Use provided repo_path or default to self.repo_path
        actual_repo_path = repo_path or self._repo_path
        
        logger.info(f"Analyzing git changes in {actual_repo_path}")
        
        # Add timing metrics
        start_time = time.time()
        
        try:
            # Verify actual file count first
            file_count_start = time.time()
            actual_file_count = self.verify_git_file_count(actual_repo_path)
            file_count_end = time.time()
            logger.info(f"Verified file count: {actual_file_count} files in {file_count_end - file_count_start:.2f}s")
            
            # Get all file stats first (lightweight operation)
            file_stats_start = time.time()
            all_file_stats = get_changed_files_stats(actual_repo_path)
            file_stats_end = time.time()
            logger.info(f"Retrieved stats for {len(all_file_stats)} files in {file_stats_end - file_stats_start:.2f}s")
            
            # Get a complete listing of all directories with changes
            all_directories = {}
            for stat in all_file_stats:
                file_path = stat['file_path']
                directory = os.path.dirname(file_path) or "root"
                if directory not in all_directories:
                    all_directories[directory] = []
                all_directories[directory].append(file_path)
            
            # Process files in a smarter way to avoid context window limitations
            MAX_FILES_PER_DIRECTORY = 3  # Limit files per directory to ensure representation
            MAX_TOTAL_FILES = 50         # Limit total files to stay under context window
            
            # Select representative files from each directory
            selected_files = []
            for directory, files in all_directories.items():
                # Take up to MAX_FILES_PER_DIRECTORY from each directory
                selected_files.extend(files[:MAX_FILES_PER_DIRECTORY])
                # Break if we've reached our total limit
                if len(selected_files) >= MAX_TOTAL_FILES:
                    break
            
            # Further trim if we still have too many
            selected_files = selected_files[:MAX_TOTAL_FILES]
            
            logger.info(f"Selected {len(selected_files)} representative files for detailed analysis")
            
            # Process only the selected files with full diffs
            file_processing_start = time.time()
            changes_data = []
            
            # Create a mapping of file path to stats for easier lookup
            file_stats_map = {item['file_path']: item for item in all_file_stats}
            
            # Process selected files with diffs in batches
            MAX_BATCH_SIZE = 10
            file_batches = [selected_files[i:i+MAX_BATCH_SIZE] 
                        for i in range(0, len(selected_files), MAX_BATCH_SIZE)]
            
            for batch in file_batches:
                batch_results = []
                for file_path in batch:
                    try:
                        # Get diff with limited context to reduce size
                        diff = get_file_diff(actual_repo_path, file_path)
                        
                        # Get stats for this file
                        stats = file_stats_map.get(file_path, {'added': 0, 'deleted': 0})
                        
                        # Create FileChange object
                        file_change = FileChange(
                            path=file_path,
                            changes=LineChanges(
                                added=stats['added'],
                                deleted=stats['deleted']
                            ),
                            # Truncate very large diffs
                            diff=diff[:1000] + "..." if len(diff) > 1000 else diff
                        )
                        changes_data.append(file_change)
                    except Exception as e:
                        logger.error(f"Error processing diff for {file_path}: {e}")
            
            file_processing_end = time.time()
            logger.info(f"Processed {len(changes_data)} files with diffs in {file_processing_end - file_processing_start:.2f}s")
            
            # Create complete directory summaries for ALL files, not just the ones with diffs
            dir_groups = {}
            for stat in all_file_stats:
                file_path = stat['file_path']
                directory = os.path.dirname(file_path) or "root"
                if directory not in dir_groups:
                    dir_groups[directory] = []
                dir_groups[directory].append(file_path)
            
            # Create directory summaries
            directory_summaries = []
            for dir_name, files in dir_groups.items():
                directory_summaries.append(DirectorySummary(
                    path=dir_name,
                    file_count=len(files),
                    total_changes=sum(file_stats_map.get(f, {}).get('added', 0) + 
                                      file_stats_map.get(f, {}).get('deleted', 0) 
                                      for f in files),
                    extensions={Path(f).suffix: 1 for f in files}
                ))
            
            # Create analysis result with CORRECT total files count
            analysis = RepositoryAnalysis(
                repo_path=actual_repo_path,
                file_changes=changes_data,
                directory_summaries=directory_summaries,
                total_files_changed=actual_file_count,
                total_lines_changed=sum(stats['added'] + stats['deleted'] for stats in all_file_stats)
            )
            
            end_time = time.time()
            logger.info(f"Analysis completed in {end_time - start_time:.2f} seconds")
            
            return analysis.model_dump_json(indent=2)
            
        except Exception as e:
            logger.exception(f"Error analyzing git changes: {e}")
            error_result = {"error": str(e)}
            return json.dumps(error_result)


class QuickGitAnalysisTool(BaseRepoTool):
    """A faster version of GitAnalysisTool that skips full diffs."""
    name: str = "quick_git_analysis"
    description: str = "Quickly analyze changes in a Git repository (file paths and stats only, no diffs)"
    args_schema: Type = GitAnalysisToolInput
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize with quick mode enabled."""
        super().__init__()
        if repo_path:
            self._repo_path = repo_path
    
    def verify_git_file_count(self, repo_path: str) -> int:
        """Directly verify the number of changed files using git command."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            if result.returncode != 0:
                logger.error(f"Error running git command: {result.stderr}")
                return 0
                
            files = [f for f in result.stdout.splitlines() if f.strip()]
            return len(files)
        except Exception as e:
            logger.error(f"Error verifying file count: {e}")
            return 0
    
    def _run(self, repo_path: Optional[str] = None, query: Optional[str] = None) -> str:
        """Run the tool with quick mode."""
        # Use provided repo_path or default to self.repo_path
        actual_repo_path = repo_path or self._repo_path
        
        logger.info(f"Quick analyzing git changes in {actual_repo_path}")
        
        # Add timing metrics
        start_time = time.time()
        
        # Use a different cache file for quick mode
        output_file = os.path.join(OUTPUT_DIR, "quick_git_analysis_output.json")
        if os.path.exists(output_file):
            logger.info(f"Using cached quick git analysis from {output_file}")
            try:
                with open(output_file, 'r') as f:
                    cached_content = f.read()
                    logger.info(f"Using cached quick result (from {time.time() - start_time:.2f}s)")
                    return cached_content
            except Exception as e:
                logger.error(f"Error reading cached quick git analysis: {e}")
        
        try:
            # Verify actual file count first
            actual_file_count = self.verify_git_file_count(actual_repo_path)
            logger.info(f"Actual git file count: {actual_file_count}")
            
            # Get just file stats (faster)
            logger.info("Using quick mode for file analysis")
            file_stats = get_changed_files_stats(actual_repo_path)
            
            # Convert stats to FileChange objects (without full diffs)
            changes_data = []
            for stat in file_stats:
                changes_data.append(FileChange(
                    path=stat['file_path'],
                    changes=LineChanges(
                        added=stat['added'],
                        deleted=stat['deleted']
                    ),
                    diff=""  # No diff in quick mode
                ))
            
            # Group by directory for additional information
            dir_groups = {}
            for change in changes_data:
                # Extract directory from file path
                directory = os.path.dirname(change.path) or "root"
                if directory not in dir_groups:
                    dir_groups[directory] = []
                dir_groups[directory].append(change)
            
            # Create directory summaries
            directory_summaries = []
            for dir_name, files in dir_groups.items():
                directory_summaries.append(DirectorySummary(
                    path=dir_name,
                    file_count=len(files),
                    total_changes=sum(f.changes.added + f.changes.deleted for f in files if f.changes),
                    extensions={Path(f.path).suffix: 1 for f in files if f.path}
                ))
            
            # Create analysis result
            analysis = RepositoryAnalysis(
                repo_path=actual_repo_path,
                file_changes=changes_data,
                directory_summaries=directory_summaries,
                total_files_changed=actual_file_count,
                total_lines_changed=sum(c.changes.added + c.changes.deleted for c in changes_data if c.changes)
            )
            
            end_time = time.time()
            logger.info(f"Quick analysis completed in {end_time - start_time:.2f} seconds")
            
            # Save result to file for caching
            try:
                with open(output_file, 'w') as f:
                    json_content = analysis.model_dump_json(indent=2)
                    f.write(json_content)
                    logger.info(f"Saved quick analysis to {output_file}")
            except Exception as e:
                logger.error(f"Error saving quick analysis result: {e}")
            
            return analysis.model_dump_json(indent=2)
            
        except Exception as e:
            logger.exception(f"Error in quick git analysis: {e}")
            error_result = {"error": str(e)}
            
            # Save error to file
            try:
                with open(output_file, 'w') as f:
                    json.dump(error_result, f, indent=2)
            except Exception as file_e:
                logger.error(f"Error saving quick error result: {file_e}")
                
            return json.dumps(error_result)
