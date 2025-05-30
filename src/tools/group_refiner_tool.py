"""
Group refiner tool for refining and balancing PR groups.
"""
import re
import json
from typing import List, Dict, Any, Set, Optional, Type
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from mcp_shared_lib.src.utils.logging_utils import get_logger
from mcp_shared_lib.src.tools.base_tool import BaseRepoTool
from mcp_shared_lib.src.models.grouping_models import PRGroupingStrategy, PRGroup, PRValidationResult, GroupingStrategyType

logger = get_logger(__name__)

class GroupRefinerToolSchema(BaseModel):
    """Input schema for GroupRefiner using primitive types."""
    pr_grouping_strategy_json: str = Field(..., description="JSON string of the PRGroupingStrategy to refine.")
    pr_validation_result_json: str = Field(..., description="JSON string of the PRValidationResult containing issues.")
    original_repository_analysis_json: Optional[str] = Field(None, description="JSON string of the original RepositoryAnalysis (required for final refinement).")

class GroupRefinerTool(BaseRepoTool):
    name: str = "Group Refiner Tool"
    description: str = "Refines proposed PR groups based on validation results, fixing issues like duplicates, empty groups, and ensuring completeness in the final run."
    args_schema: Type[BaseModel] = GroupRefinerToolSchema

    def _run(
        self,
        pr_grouping_strategy_json: str,
        pr_validation_result_json: str,
        original_repository_analysis_json: Optional[str] = None
    ) -> str:
        logger.info(f"GroupRefinerTool received pr_grouping_strategy_json: {pr_grouping_strategy_json[:100]}...")
        logger.info(f"GroupRefinerTool received pr_validation_result_json: {pr_validation_result_json[:100]}...")
        if original_repository_analysis_json:
            logger.info(f"GroupRefinerTool received original_repository_analysis_json: {original_repository_analysis_json[:100]}...")
        
        try:
            if not self._validate_json_string(pr_grouping_strategy_json):
                raise ValueError("Invalid pr_grouping_strategy_json provided")
            if not self._validate_json_string(pr_validation_result_json):
                raise ValueError("Invalid pr_validation_result_json provided")
            if original_repository_analysis_json and not self._validate_json_string(original_repository_analysis_json):
                raise ValueError("Invalid original_repository_analysis_json provided")
            
            grouping_strategy = PRGroupingStrategy.model_validate_json(pr_grouping_strategy_json)
            validation_result = PRValidationResult.model_validate_json(pr_validation_result_json)
            
            original_file_paths = set()
            if original_repository_analysis_json:
                file_paths = self._extract_file_paths(original_repository_analysis_json)
                original_file_paths = set(file_paths)

            is_final_refinement = original_repository_analysis_json is not None
            logger.info(f"Refining {len(grouping_strategy.groups)} groups. Final refinement: {is_final_refinement}")

            if validation_result.is_valid and not is_final_refinement:
                logger.info("No validation issues found for this batch, no refinement needed.")
                return grouping_strategy.model_dump_json(indent=2)

            refined_groups = list(grouping_strategy.groups)
            processed_issues: Set[str] = set()

            empty_group_titles = set()
            for issue in validation_result.issues:
                if issue.issue_type == "Empty Group":
                    empty_group_titles.update(issue.affected_groups)
                    processed_issues.add(json.dumps(issue.model_dump()))

            if empty_group_titles:
                logger.info(f"Removing empty groups: {empty_group_titles}")
                refined_groups = [g for g in refined_groups if g.title not in empty_group_titles]

            duplicate_issue_found = False
            files_to_reassign: Dict[str, List[str]] = {}
            for issue in validation_result.issues:
                if issue.issue_type == "Duplicate Files":
                    duplicate_issue_found = True
                    processed_issues.add(json.dumps(issue.model_dump()))
                    temp_files_in_groups: Dict[str, List[str]] = {}
                    for group in refined_groups:
                        for file_path in group.files:
                            if file_path not in temp_files_in_groups:
                                temp_files_in_groups[file_path] = []
                            temp_files_in_groups[file_path].append(group.title)
                    duplicates = {fp: titles for fp, titles in temp_files_in_groups.items() if len(titles) > 1}
                    files_to_reassign = duplicates
                    break

            if files_to_reassign:
                logger.warning(f"Handling duplicate files: {list(files_to_reassign.keys())}")
                seen_files_in_refinement: Set[str] = set()
                temp_refined_groups: List[PRGroup] = []
                for group in refined_groups:
                    original_files = list(group.files)
                    files_for_this_group = []
                    for file_path in original_files:
                        if file_path in files_to_reassign:
                            if file_path not in seen_files_in_refinement:
                                files_for_this_group.append(file_path)
                                seen_files_in_refinement.add(file_path)
                        else:
                            files_for_this_group.append(file_path)
                            seen_files_in_refinement.add(file_path)
                    if files_for_this_group:
                        group.files = files_for_this_group
                        temp_refined_groups.append(group)
                    else:
                        logger.info(f"Group '{group.title}' became empty after resolving duplicates and was removed.")
                refined_groups = temp_refined_groups

            if is_final_refinement:
                logger.info("Performing final completeness check.")
                current_grouped_files: Set[str] = set()
                for group in refined_groups:
                    current_grouped_files.update(group.files)

                still_ungrouped = list(original_file_paths - current_grouped_files)
                logger.info(f"Files still ungrouped after initial refinement: {len(still_ungrouped)}")

                if still_ungrouped:
                    misc_group_exists = False
                    for group in refined_groups:
                        if group.title.lower() == "chore: miscellaneous remaining changes":
                            logger.info(f"Adding {len(still_ungrouped)} files to existing miscellaneous group.")
                            existing_misc_files = set(group.files)
                            new_misc_files = [f for f in still_ungrouped if f not in existing_misc_files]
                            group.files.extend(new_misc_files)
                            misc_group_exists = True
                            break
                    if not misc_group_exists:
                        logger.info(f"Creating new miscellaneous group for {len(still_ungrouped)} files.")
                        refined_groups.append(PRGroup(
                            title="Chore: Miscellaneous remaining changes",
                            files=still_ungrouped,
                            rationale="Contains changes that could not be automatically assigned to a more specific group during batch processing and merging.",
                            estimated_size=len(still_ungrouped)
                        ))

                    for issue in validation_result.issues:
                        if issue.issue_type == "Ungrouped Files":
                            processed_issues.add(json.dumps(issue.model_dump()))

            refined_explanation = grouping_strategy.explanation + "\nRefinements applied based on validation results."
            if not validation_result.is_valid:
                refined_explanation += f"\nAddressed issues: {', '.join(issue.issue_type for issue in validation_result.issues if json.dumps(issue.model_dump()) in processed_issues)}"
            if is_final_refinement:
                refined_explanation += "\nFinal completeness check performed."

            final_strategy = PRGroupingStrategy(
                strategy_type=grouping_strategy.strategy_type,
                groups=refined_groups,
                explanation=refined_explanation,
                estimated_review_complexity=grouping_strategy.estimated_review_complexity,
                ungrouped_files=[]
            )

            if is_final_refinement and original_file_paths:
                final_grouped_files: Set[str] = set()
                for group in final_strategy.groups:
                    final_grouped_files.update(group.files)
                missed_files = original_file_paths - final_grouped_files
                if missed_files:
                    logger.error(f"CRITICAL REFINEMENT ERROR: {len(missed_files)} files are still missing after final refinement: {list(missed_files)[:5]}")
                    final_strategy.explanation += f"\nWARNING: {len(missed_files)} files missing after final refinement!"

            return final_strategy.model_dump_json(indent=2)

        except ValidationError as ve:
            error_msg = f"Validation error during refinement: {str(ve)}"
            logger.error(error_msg, exc_info=True)
            try:
                input_strategy = PRGroupingStrategy.model_validate_json(pr_grouping_strategy_json)
                input_strategy.explanation += f"\n\n!! REFINEMENT FAILED: {error_msg} !!"
                if not isinstance(input_strategy.strategy_type, GroupingStrategyType):
                    input_strategy.strategy_type = GroupingStrategyType.MIXED
                return input_strategy.model_dump_json(indent=2)
            except:
                error_strategy = PRGroupingStrategy(
                    strategy_type=GroupingStrategyType.MIXED,
                    groups=[],
                    explanation=f"Refinement failed critically: {error_msg}. Input strategy could not be parsed.",
                    ungrouped_files=[]
                )
                return error_strategy.model_dump_json(indent=2)
        except Exception as e:
            error_msg = f"Unexpected error during refinement: {str(e)}"
            logger.error(error_msg, exc_info=True)
            try:
                input_strategy = PRGroupingStrategy.model_validate_json(pr_grouping_strategy_json)
                input_strategy.explanation += f"\n\n!! REFINEMENT FAILED: {error_msg} !!"
                if not isinstance(input_strategy.strategy_type, GroupingStrategyType):
                    input_strategy.strategy_type = GroupingStrategyType.MIXED
                return input_strategy.model_dump_json(indent=2)
            except:
                error_strategy = PRGroupingStrategy(
                    strategy_type=GroupingStrategyType.MIXED,
                    groups=[],
                    explanation=f"Refinement failed critically: {error_msg}. Input strategy could not be parsed.",
                    ungrouped_files=[]
                )
                return error_strategy.model_dump_json(indent=2)
