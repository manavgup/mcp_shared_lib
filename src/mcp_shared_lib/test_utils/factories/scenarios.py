"""
Test scenario factories for creating complex, realistic test environments.

This module provides factories for creating comprehensive test scenarios
that combine multiple components (git, files, analysis, etc.) into
realistic testing environments.
"""

from datetime import datetime
from typing import Any, Optional

from .analysis import AnalysisResultFactory, RiskAssessmentFactory
from .base import BaseFactory, Faker
from .files import create_file_changes
from .git import GitRepositoryStateFactory
from .recommendations import create_pr_recommendation_set


class TestScenarioFactory(BaseFactory):
    """Factory for creating comprehensive test scenarios."""

    @staticmethod
    def scenario_name() -> str:
        """Generate scenario name."""
        return Faker.random_element(
            [
                "simple_feature_addition",
                "complex_refactoring",
                "bug_fix_with_tests",
                "documentation_update",
                "performance_optimization",
                "security_enhancement",
                "database_migration",
                "api_breaking_change",
                "ui_overhaul",
                "integration_update",
            ]
        )

    @staticmethod
    def complexity_level() -> str:
        """Generate complexity level."""
        return Faker.weighted_choice(
            ["simple", "moderate", "complex", "very_complex"], [30, 40, 25, 5]
        )

    @staticmethod
    def expected_duration_hours() -> int:
        """Generate expected scenario duration."""
        return Faker.random_int(1, 40)

    @staticmethod
    def team_size() -> int:
        """Generate team size for scenario."""
        return Faker.random_int(1, 8)

    @classmethod
    def create(cls, **kwargs) -> dict[str, Any]:
        """Create comprehensive test scenario."""
        scenario = super().create(**kwargs)

        # Generate scenario-specific data based on complexity
        complexity = scenario["complexity_level"]

        if complexity == "simple":
            scenario.update(cls._create_simple_scenario())
        elif complexity == "moderate":
            scenario.update(cls._create_moderate_scenario())
        elif complexity == "complex":
            scenario.update(cls._create_complex_scenario())
        else:  # very_complex
            scenario.update(cls._create_very_complex_scenario())

        # Add common scenario metadata
        scenario["created_at"] = datetime.now()
        scenario["scenario_id"] = Faker.uuid4()

        return scenario

    @classmethod
    def _create_simple_scenario(cls) -> dict[str, Any]:
        """Create a simple scenario."""
        return {
            "file_changes": create_file_changes(
                count=Faker.random_int(1, 5), risk_distribution="low"
            ),
            "repository_state": GitRepositoryStateFactory.with_traits("clean"),
            "analysis_result": AnalysisResultFactory.with_traits("successful_analysis"),
            "expected_prs": 1,
            "estimated_review_time_hours": Faker.random_int(1, 4),
            "risk_factors": ["minimal_risk"],
            "success_criteria": [
                "All tests pass",
                "No merge conflicts",
                "Code review approved",
            ],
        }

    @classmethod
    def _create_moderate_scenario(cls) -> dict[str, Any]:
        """Create a moderate complexity scenario."""
        return {
            "file_changes": create_file_changes(
                count=Faker.random_int(5, 15), risk_distribution="mixed"
            ),
            "repository_state": GitRepositoryStateFactory.create(),
            "analysis_result": AnalysisResultFactory.create(),
            "expected_prs": Faker.random_int(2, 4),
            "estimated_review_time_hours": Faker.random_int(4, 12),
            "risk_factors": ["moderate_complexity", "multiple_files"],
            "success_criteria": [
                "All tests pass",
                "Performance benchmarks met",
                "Security review completed",
                "Documentation updated",
            ],
        }

    @classmethod
    def _create_complex_scenario(cls) -> dict[str, Any]:
        """Create a complex scenario."""
        return {
            "file_changes": create_file_changes(
                count=Faker.random_int(15, 30), risk_distribution="mixed"
            ),
            "repository_state": GitRepositoryStateFactory.with_traits("dirty"),
            "analysis_result": AnalysisResultFactory.with_traits(
                "analysis_with_warnings"
            ),
            "expected_prs": Faker.random_int(4, 8),
            "estimated_review_time_hours": Faker.random_int(12, 24),
            "risk_factors": [
                "high_complexity",
                "critical_files_modified",
                "external_dependencies",
                "breaking_changes",
            ],
            "success_criteria": [
                "All tests pass",
                "Integration tests pass",
                "Performance impact assessed",
                "Security audit completed",
                "Rollback plan prepared",
                "Stakeholder approval obtained",
            ],
        }

    @classmethod
    def _create_very_complex_scenario(cls) -> dict[str, Any]:
        """Create a very complex scenario."""
        return {
            "file_changes": create_file_changes(
                count=Faker.random_int(30, 60), risk_distribution="high"
            ),
            "repository_state": GitRepositoryStateFactory.with_traits("large"),
            "analysis_result": AnalysisResultFactory.with_traits("failed_analysis"),
            "expected_prs": Faker.random_int(8, 15),
            "estimated_review_time_hours": Faker.random_int(24, 80),
            "risk_factors": [
                "very_high_complexity",
                "architectural_changes",
                "database_schema_changes",
                "api_breaking_changes",
                "multi_service_impact",
                "performance_critical",
            ],
            "success_criteria": [
                "All tests pass",
                "Integration tests pass",
                "End-to-end tests pass",
                "Performance benchmarks met",
                "Security audit passed",
                "Architecture review approved",
                "Database migration tested",
                "Rollback procedures verified",
                "Monitoring and alerting updated",
                "Documentation comprehensive",
            ],
        }


class WorkflowScenarioFactory(BaseFactory):
    """Factory for creating workflow-specific test scenarios."""

    @staticmethod
    def workflow_type() -> str:
        """Generate workflow type."""
        return Faker.random_element(
            [
                "feature_development",
                "hotfix_deployment",
                "release_preparation",
                "maintenance_update",
                "emergency_patch",
                "refactoring_sprint",
                "security_update",
            ]
        )

    @staticmethod
    def stage() -> str:
        """Generate current workflow stage."""
        return Faker.random_element(
            [
                "planning",
                "development",
                "testing",
                "review",
                "staging",
                "deployment",
                "monitoring",
                "complete",
            ]
        )

    @classmethod
    def create(cls, **kwargs) -> dict[str, Any]:
        """Create workflow scenario with stage-specific data."""
        scenario = super().create(**kwargs)

        workflow_type = scenario["workflow_type"]
        stage = scenario["stage"]

        # Add workflow-specific data
        scenario.update(cls._get_workflow_data(workflow_type))
        scenario.update(cls._get_stage_data(stage))

        return scenario

    @classmethod
    def _get_workflow_data(cls, workflow_type: str) -> dict[str, Any]:
        """Get data specific to workflow type."""
        workflow_configs = {
            "feature_development": {
                "typical_duration_days": Faker.random_int(5, 21),
                "required_reviews": 2,
                "testing_requirements": ["unit", "integration", "e2e"],
                "deployment_strategy": "gradual_rollout",
            },
            "hotfix_deployment": {
                "typical_duration_days": Faker.random_int(1, 3),
                "required_reviews": 1,
                "testing_requirements": ["unit", "critical_path"],
                "deployment_strategy": "immediate",
            },
            "release_preparation": {
                "typical_duration_days": Faker.random_int(7, 14),
                "required_reviews": 3,
                "testing_requirements": ["unit", "integration", "e2e", "performance"],
                "deployment_strategy": "blue_green",
            },
            "maintenance_update": {
                "typical_duration_days": Faker.random_int(2, 7),
                "required_reviews": 1,
                "testing_requirements": ["unit", "integration"],
                "deployment_strategy": "rolling_update",
            },
        }

        return workflow_configs.get(
            workflow_type,
            {
                "typical_duration_days": Faker.random_int(3, 10),
                "required_reviews": 2,
                "testing_requirements": ["unit", "integration"],
                "deployment_strategy": "standard",
            },
        )

    @classmethod
    def _get_stage_data(cls, stage: str) -> dict[str, Any]:
        """Get data specific to workflow stage."""
        stage_configs = {
            "planning": {
                "completion_percentage": Faker.random_int(0, 20),
                "deliverables": ["requirements", "design_docs", "task_breakdown"],
                "blockers": [],
            },
            "development": {
                "completion_percentage": Faker.random_int(20, 70),
                "deliverables": ["code_changes", "unit_tests"],
                "blockers": ["dependency_issues", "unclear_requirements"],
            },
            "testing": {
                "completion_percentage": Faker.random_int(70, 90),
                "deliverables": ["test_results", "bug_reports"],
                "blockers": ["test_environment_issues", "test_data_setup"],
            },
            "review": {
                "completion_percentage": Faker.random_int(85, 95),
                "deliverables": ["code_review", "security_review"],
                "blockers": ["reviewer_availability", "review_feedback"],
            },
            "deployment": {
                "completion_percentage": Faker.random_int(95, 100),
                "deliverables": ["deployment_plan", "rollback_plan"],
                "blockers": ["deployment_window", "infrastructure_readiness"],
            },
        }

        return stage_configs.get(
            stage,
            {
                "completion_percentage": Faker.random_int(0, 100),
                "deliverables": [],
                "blockers": [],
            },
        )


# Convenience functions for creating scenario collections
def create_repository_with_realistic_state(
    total_commits: Optional[int] = None, total_branches: Optional[int] = None, **kwargs
) -> dict[str, Any]:
    """Create a repository with realistic state and history."""
    if total_commits is None:
        total_commits = Faker.random_int(50, 500)
    if total_branches is None:
        total_branches = Faker.random_int(3, 10)

    repo = GitRepositoryStateFactory.create(
        total_commits=total_commits, total_branches=total_branches, **kwargs
    )

    # Add realistic commit history
    # repo['commit_history'] = create_git_commit_history(
    #     count=min(total_commits, 50)
    # )

    # Add risk assessment for current state
    repo["risk_assessment"] = RiskAssessmentFactory.create()

    return repo


def create_scenario_suite(scenario_types: list[str] = None) -> dict[str, Any]:
    """Create a comprehensive suite of test scenarios."""
    if scenario_types is None:
        scenario_types = [
            "simple_feature_addition",
            "complex_refactoring",
            "bug_fix_with_tests",
            "performance_optimization",
        ]

    scenarios = {}
    for scenario_type in scenario_types:
        scenarios[scenario_type] = TestScenarioFactory.create(
            scenario_name=scenario_type
        )

    return {
        "scenarios": scenarios,
        "suite_metadata": {
            "created_at": datetime.now(),
            "total_scenarios": len(scenarios),
            "estimated_total_time_hours": sum(
                s.get("estimated_review_time_hours", 0) for s in scenarios.values()
            ),
            "complexity_distribution": {
                level: len(
                    [
                        s
                        for s in scenarios.values()
                        if s.get("complexity_level") == level
                    ]
                )
                for level in ["simple", "moderate", "complex", "very_complex"]
            },
        },
    }


def create_integration_test_scenario(
    services: list[str] = None, data_flows: list[str] = None
) -> dict[str, Any]:
    """Create scenario for integration testing across services."""
    if services is None:
        services = ["analyzer", "recommender", "api_gateway", "database"]
    if data_flows is None:
        data_flows = [
            "analysis_to_recommendations",
            "api_to_storage",
            "user_to_results",
        ]

    return {
        "scenario_type": "integration_test",
        "services_involved": services,
        "data_flows": data_flows,
        "test_data": {
            "repository": create_repository_with_realistic_state(),
            "file_changes": create_file_changes(count=10),
            "expected_recommendations": create_pr_recommendation_set(count=3),
        },
        "validation_points": [
            "data_consistency_across_services",
            "api_response_formats",
            "error_handling_behavior",
            "performance_under_load",
        ],
        "environment_requirements": {
            "databases": ["postgresql", "redis"],
            "external_services": ["git_provider", "ci_system"],
            "infrastructure": ["kubernetes", "monitoring"],
        },
        "expected_duration_minutes": Faker.random_int(15, 60),
        "cleanup_requirements": [
            "reset_test_databases",
            "clear_cache_entries",
            "restore_git_state",
        ],
    }


def create_performance_test_scenario(scale_factor: str = "medium") -> dict[str, Any]:
    """Create scenario for performance testing."""
    scale_configs = {
        "small": {
            "repositories": 5,
            "files_per_repo": 50,
            "concurrent_users": 10,
            "duration_minutes": 5,
        },
        "medium": {
            "repositories": 20,
            "files_per_repo": 200,
            "concurrent_users": 50,
            "duration_minutes": 15,
        },
        "large": {
            "repositories": 100,
            "files_per_repo": 1000,
            "concurrent_users": 200,
            "duration_minutes": 30,
        },
    }

    config = scale_configs.get(scale_factor, scale_configs["medium"])

    return {
        "scenario_type": "performance_test",
        "scale_factor": scale_factor,
        "load_configuration": config,
        "test_repositories": [
            create_repository_with_realistic_state(
                total_commits=Faker.random_int(100, 1000)
            )
            for _ in range(config["repositories"])
        ],
        "performance_targets": {
            "analysis_time_p95_ms": 5000,
            "recommendation_time_p95_ms": 2000,
            "memory_usage_max_mb": 1024,
            "error_rate_max_percent": 1.0,
        },
        "monitoring_metrics": [
            "response_time",
            "throughput",
            "error_rate",
            "memory_usage",
            "cpu_usage",
            "database_connections",
        ],
        "ramp_up_strategy": {
            "initial_users": config["concurrent_users"] // 10,
            "increment_users": config["concurrent_users"] // 5,
            "increment_interval_seconds": 30,
        },
    }
