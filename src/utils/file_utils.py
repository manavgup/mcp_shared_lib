"""
Utility functions for file path handling and file operations.
"""
import os
from pathlib import Path
from typing import List, Set, Dict, Any, Optional, Union

def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a file path for consistent handling.
    
    Args:
        path: The path to normalize (string or Path object)
        
    Returns:
        A normalized Path object
    """
    if isinstance(path, str):
        path = Path(path)
    return path.resolve()

def get_relative_path(path: Union[str, Path], base_dir: Union[str, Path]) -> Path:
    """
    Get a path relative to a base directory.
    
    Args:
        path: The path to convert
        base_dir: The base directory
        
    Returns:
        A Path object relative to the base directory
    """
    path = normalize_path(path)
    base_dir = normalize_path(base_dir)
    
    try:
        return path.relative_to(base_dir)
    except ValueError:
        # If path is not relative to base_dir, return the original path
        return path

def get_file_extension(path: Union[str, Path]) -> str:
    """
    Extract the file extension from a path.
    
    Args:
        path: The file path
        
    Returns:
        The file extension (with dot) or empty string if no extension
    """
    path = normalize_path(path)
    return path.suffix

def get_directory(path: Union[str, Path]) -> Path:
    """
    Get the directory containing a file.
    
    Args:
        path: The file path
        
    Returns:
        The directory containing the file as a Path object
    """
    path = normalize_path(path)
    return path.parent

def filter_files_by_extension(files: List[Union[str, Path]], extensions: List[str]) -> List[Path]:
    """
    Filter a list of files by their extensions.
    
    Args:
        files: List of file paths
        extensions: List of extensions to include (with or without dot)
        
    Returns:
        List of filtered file paths as Path objects
    """
    # Normalize extensions to include the dot
    normalized_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    result = []
    for file in files:
        path = normalize_path(file)
        if path.suffix in normalized_extensions:
            result.append(path)
    
    return result

def group_files_by_directory(files: List[Union[str, Path]]) -> Dict[Path, List[Path]]:
    """
    Group files by their parent directory.
    
    Args:
        files: List of file paths
        
    Returns:
        Dictionary mapping directories to lists of files
    """
    result: Dict[Path, List[Path]] = {}
    
    for file in files:
        path = normalize_path(file)
        directory = path.parent
        
        if directory not in result:
            result[directory] = []
        
        result[directory].append(path)
    
    return result

def find_common_parent_directory(paths: List[Union[str, Path]]) -> Optional[Path]:
    """
    Find the common parent directory of a list of paths.
    
    Args:
        paths: List of file or directory paths
        
    Returns:
        The common parent directory as a Path object, or None if no common parent
    """
    if not paths:
        return None
        
    # Convert all paths to Path objects and resolve them
    resolved_paths = [normalize_path(p) for p in paths]
    
    # Start with the parent of the first path
    common_parent = resolved_paths[0].parent
    
    # Check if all other paths have this as an ancestor
    while str(common_parent) != '/':
        if all(str(p).startswith(str(common_parent)) for p in resolved_paths):
            return common_parent
        common_parent = common_parent.parent
    
    # If we get here, only the root directory is common
    return Path('/')
