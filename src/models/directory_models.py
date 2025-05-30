# directory_models.py
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from .base_models import BaseModel

class DirectorySummary(BaseModel):
    path: str = Field(..., description="Directory path")
    file_count: int = Field(0, description="Number of files in the directory")
    total_changes: int = Field(0, description="Total number of changes in the directory")
    extensions: Dict[str, int] = Field(default_factory=dict, description="File extension counts in the directory")

class DirectoryComplexity(BaseModel):
    """Represents complexity analysis for a directory."""
    path: str = Field(..., description="Directory path")
    file_count: int = Field(default=0, description="Number of files in this directory")
    changed_file_count: int = Field(default=0, description="Number of changed files in this directory")
    extension_counts: Dict[str, int] = Field(default_factory=dict, description="Count of file extensions in this directory")
    estimated_complexity: float = Field(default=0.0, description="Estimated complexity score (0-10)")

class ParentChildRelation(BaseModel):
    """Represents a parent-child directory relationship."""
    parent: str = Field(..., description="Path of the parent directory")
    child: str = Field(..., description="Path of the child directory")

class PotentialFeatureDirectory(BaseModel):
    """Represents a directory identified as potentially feature-related."""
    directory: str = Field(..., description="Path of the directory")
    is_diverse: bool = Field(..., description="Indicates if the directory contains diverse file types")
    is_cross_cutting: bool = Field(..., description="Indicates if the directory is related to multiple others")
    file_types: List[str] = Field(..., description="List of file extensions found in the directory")
    related_directories: List[str] = Field(..., description="List of related directory paths")
    confidence: float = Field(..., description="Confidence score (0-1) that this represents a feature")

class DirectoryAnalysisResult(BaseModel):
    """Results of analyzing the directory structure of changes."""
    directory_count: int = Field(..., description="Total number of directories with changes")
    max_depth: int = Field(..., description="Maximum depth of changed directories in the hierarchy")
    avg_files_per_directory: float = Field(..., description="Average number of changed files per directory")
    directory_complexity: List[DirectoryComplexity] = Field(..., description="Complexity analysis for each directory")
    parent_child_relationships: List[ParentChildRelation] = Field(..., description="Identified parent-child relationships between changed directories")
    potential_feature_directories: List[PotentialFeatureDirectory] = Field(..., description="Directories identified as potentially feature-related")
    error: Optional[str] = Field(None, description="Optional field to report errors during analysis.")
