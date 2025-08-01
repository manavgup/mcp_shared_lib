"""
Analysis-related test data factories.

This module provides factories for creating realistic analysis results,
risk assessments, and quality metrics.
"""

import random
from datetime import datetime, timedelta
from typing import Any

from .base import BaseFactory, Faker, SequenceMixin


class AnalysisResultFactory(BaseFactory, SequenceMixin):
    """Factory for creating comprehensive analysis results."""

    @classmethod
    def id(cls) -> str:
        """Generate unique analysis ID."""
        return cls.sequence("analysis", "analysis_{n:06d}")

    @staticmethod
    def timestamp() -> datetime:
        """Analysis timestamp."""
        return Faker.date_time()

    @staticmethod
    def status() -> str:
        """Analysis status with realistic distribution."""
        return Faker.weighted_choice(
            ["success", "warning", "error", "partial"], [70, 20, 5, 5]
        )

    @staticmethod
    def duration_ms() -> int:
        """Analysis duration in milliseconds."""
        return Faker.random_int(100, 30000)

    @staticmethod
    def files_analyzed() -> int:
        """Number of files analyzed."""
        return Faker.random_int(1, 100)

    @staticmethod
    def issues_found() -> int:
        """Number of issues found."""
        return Faker.random_int(0, 50)

    @staticmethod
    def warnings_count() -> int:
        """Number of warnings."""
        return Faker.random_int(0, 20)

    @staticmethod
    def errors_count() -> int:
        """Number of errors."""
        return Faker.random_int(0, 10)

    @staticmethod
    def overall_risk_score() -> float:
        """Overall risk score."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def complexity_score() -> float:
        """Code complexity score."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def maintainability_score() -> float:
        """Code maintainability score."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def test_coverage() -> float:
        """Test coverage percentage."""
        return Faker.pyfloat(0.0, 1.0)

    @classmethod
    def create(cls, **kwargs) -> dict[str, Any]:
        """Create analysis result with computed properties."""
        result = super().create(**kwargs)

        # Generate summary based on status
        if result["status"] == "success":
            result[
                "summary"
            ] = f"Analysis completed successfully. {result['files_analyzed']} files analyzed, {result['issues_found']} issues found."
        elif result["status"] == "warning":
            result[
                "summary"
            ] = f"Analysis completed with {result['warnings_count']} warnings."
        elif result["status"] == "error":
            result["summary"] = f"Analysis failed with {result['errors_count']} errors."
        else:
            result[
                "summary"
            ] = f"Analysis partially completed. {result['files_analyzed']} files processed."

        # Generate recommendations based on scores
        recommendations = []
        if result["overall_risk_score"] > 0.7:
            recommendations.append("Consider reviewing high-risk changes carefully")
        if result["complexity_score"] > 0.8:
            recommendations.append("Refactor complex code to improve maintainability")
        if result["test_coverage"] < 0.6:
            recommendations.append("Increase test coverage")
        if result["issues_found"] > 10:
            recommendations.append("Address critical issues before proceeding")

        result["recommendations"] = recommendations or ["No specific recommendations"]

        # Generate detailed breakdown
        result["details"] = {
            "performance": {
                "analysis_duration_ms": result["duration_ms"],
                "memory_used_mb": Faker.random_int(10, 500),
                "cpu_usage_percent": Faker.random_int(5, 95),
            },
            "file_breakdown": {
                "python_files": Faker.random_int(0, result["files_analyzed"]),
                "test_files": Faker.random_int(0, result["files_analyzed"] // 2),
                "config_files": Faker.random_int(0, 5),
                "documentation_files": Faker.random_int(0, 10),
            },
            "quality_gates": {
                "risk_threshold_passed": result["overall_risk_score"] < 0.8,
                "complexity_threshold_passed": result["complexity_score"] < 0.7,
                "coverage_threshold_passed": result["test_coverage"] > 0.7,
            },
        }

        return result

    # Trait methods for different analysis scenarios
    @classmethod
    def trait_successful_analysis(cls) -> dict[str, Any]:
        """Trait for successful analysis."""
        return {
            "status": "success",
            "errors_count": 0,
            "warnings_count": Faker.random_int(0, 3),
            "overall_risk_score": Faker.pyfloat(0.0, 0.6),
            "test_coverage": Faker.pyfloat(0.7, 1.0),
            "duration_ms": Faker.random_int(100, 5000),
        }

    @classmethod
    def trait_analysis_with_warnings(cls) -> dict[str, Any]:
        """Trait for analysis with warnings."""
        return {
            "status": "warning",
            "errors_count": 0,
            "warnings_count": Faker.random_int(3, 15),
            "overall_risk_score": Faker.pyfloat(0.6, 0.8),
            "issues_found": Faker.random_int(5, 20),
        }

    @classmethod
    def trait_failed_analysis(cls) -> dict[str, Any]:
        """Trait for failed analysis."""
        return {
            "status": "error",
            "errors_count": Faker.random_int(1, 5),
            "warnings_count": Faker.random_int(0, 10),
            "files_analyzed": Faker.random_int(0, 20),
            "duration_ms": Faker.random_int(100, 2000),
        }

    @classmethod
    def trait_performance_analysis(cls) -> dict[str, Any]:
        """Trait for performance-focused analysis."""
        return {
            "duration_ms": Faker.random_int(100, 1000),
            "files_analyzed": Faker.random_int(50, 200),
        }

    @classmethod
    def trait_security_analysis(cls) -> dict[str, Any]:
        """Trait for security-focused analysis."""
        return {
            "overall_risk_score": Faker.pyfloat(0.3, 0.9),
            "issues_found": Faker.random_int(2, 15),
        }


class RiskAssessmentFactory(BaseFactory):
    """Factory for creating risk assessment objects."""

    @staticmethod
    def overall_score() -> float:
        """Overall risk score."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def confidence() -> float:
        """Confidence in the assessment."""
        return Faker.pyfloat(0.5, 1.0)

    @classmethod
    def create(cls, **kwargs) -> dict[str, Any]:
        """Create risk assessment with computed properties."""
        assessment = super().create(**kwargs)

        # Determine risk level based on overall score
        if assessment["overall_score"] < 0.3:
            assessment["risk_level"] = "low"
        elif assessment["overall_score"] < 0.7:
            assessment["risk_level"] = "medium"
        else:
            assessment["risk_level"] = "high"

        # Generate risk factors based on the score
        all_factors = [
            "large_change_size",
            "critical_files_modified",
            "low_test_coverage",
            "high_complexity",
            "multiple_contributors",
            "recent_bugs_in_area",
            "external_dependencies_changed",
            "breaking_api_changes",
            "database_schema_changes",
            "security_sensitive_code",
            "performance_critical_path",
            "configuration_changes",
        ]

        # More factors for higher risk
        factor_count = min(
            len(all_factors), max(1, int(assessment["overall_score"] * 8))
        )
        assessment["factors"] = random.sample(all_factors, factor_count)

        # Generate mitigation strategies based on risk factors
        strategies = []
        factor_strategies = {
            "large_change_size": "Break down into smaller, focused commits",
            "critical_files_modified": "Require additional code review for critical files",
            "low_test_coverage": "Add comprehensive test coverage before merging",
            "high_complexity": "Refactor complex code for better maintainability",
            "multiple_contributors": "Coordinate changes between team members",
            "recent_bugs_in_area": "Extra testing in areas with recent bug fixes",
            "external_dependencies_changed": "Test integration with external services",
            "breaking_api_changes": "Update documentation and notify API consumers",
            "database_schema_changes": "Review migration scripts and backup procedures",
            "security_sensitive_code": "Security review and penetration testing",
            "performance_critical_path": "Performance testing and benchmarking",
            "configuration_changes": "Verify configuration in staging environment",
        }

        for factor in assessment["factors"]:
            if factor in factor_strategies:
                strategies.append(factor_strategies[factor])

        assessment["mitigation_strategies"] = strategies or [
            "Monitor closely during deployment"
        ]

        # Generate impact analysis
        assessment["impact_analysis"] = {
            "affected_components": random.sample(
                [
                    "authentication",
                    "api",
                    "database",
                    "ui",
                    "processing",
                    "monitoring",
                    "deployment",
                    "configuration",
                ],
                random.randint(1, 4),
            ),
            "user_facing_changes": assessment["overall_score"] > 0.5,
            "backward_compatibility": assessment["overall_score"] < 0.7,
            "rollback_difficulty": "easy"
            if assessment["overall_score"] < 0.4
            else "medium"
            if assessment["overall_score"] < 0.8
            else "hard",
        }

        return assessment


class QualityMetricsFactory(BaseFactory):
    """Factory for creating code quality metrics."""

    @staticmethod
    def cyclomatic_complexity() -> float:
        """Cyclomatic complexity score."""
        return Faker.pyfloat(1.0, 20.0)

    @staticmethod
    def cognitive_complexity() -> float:
        """Cognitive complexity score."""
        return Faker.pyfloat(0.0, 15.0)

    @staticmethod
    def maintainability_index() -> float:
        """Maintainability index (0-100)."""
        return Faker.pyfloat(0.0, 100.0)

    @staticmethod
    def technical_debt_ratio() -> float:
        """Technical debt ratio."""
        return Faker.pyfloat(0.0, 0.5)

    @staticmethod
    def code_duplication() -> float:
        """Code duplication percentage."""
        return Faker.pyfloat(0.0, 0.3)

    @staticmethod
    def test_coverage() -> float:
        """Test coverage percentage."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def lines_of_code() -> int:
        """Total lines of code."""
        return Faker.random_int(100, 50000)

    @staticmethod
    def comment_ratio() -> float:
        """Comment to code ratio."""
        return Faker.pyfloat(0.0, 0.4)

    @classmethod
    def create(cls, **kwargs) -> dict[str, Any]:
        """Create quality metrics with computed properties."""
        metrics = super().create(**kwargs)

        # Compute overall quality score
        quality_factors = [
            1.0 - (metrics["cyclomatic_complexity"] / 20.0),
            1.0 - (metrics["cognitive_complexity"] / 15.0),
            metrics["maintainability_index"] / 100.0,
            1.0 - metrics["technical_debt_ratio"],
            1.0 - metrics["code_duplication"],
            metrics["test_coverage"],
        ]

        metrics["overall_quality_score"] = sum(quality_factors) / len(quality_factors)

        # Generate quality assessment
        if metrics["overall_quality_score"] > 0.8:
            metrics["quality_assessment"] = "excellent"
        elif metrics["overall_quality_score"] > 0.6:
            metrics["quality_assessment"] = "good"
        elif metrics["overall_quality_score"] > 0.4:
            metrics["quality_assessment"] = "fair"
        else:
            metrics["quality_assessment"] = "poor"

        # Generate improvement suggestions
        suggestions = []
        if metrics["cyclomatic_complexity"] > 10:
            suggestions.append(
                "Reduce cyclomatic complexity by breaking down large functions"
            )
        if metrics["test_coverage"] < 0.8:
            suggestions.append("Increase test coverage")
        if metrics["code_duplication"] > 0.1:
            suggestions.append("Eliminate code duplication through refactoring")
        if metrics["technical_debt_ratio"] > 0.2:
            suggestions.append("Address technical debt issues")
        if metrics["comment_ratio"] < 0.1:
            suggestions.append("Add more inline documentation")

        metrics["improvement_suggestions"] = suggestions

        return metrics


class PerformanceMetricsFactory(BaseFactory):
    """Factory for creating performance analysis metrics."""

    @staticmethod
    def execution_time_ms() -> int:
        """Execution time in milliseconds."""
        return Faker.random_int(10, 5000)

    @staticmethod
    def memory_usage_mb() -> float:
        """Memory usage in megabytes."""
        return Faker.pyfloat(1.0, 1000.0)

    @staticmethod
    def cpu_usage_percent() -> float:
        """CPU usage percentage."""
        return Faker.pyfloat(0.0, 100.0)

    @staticmethod
    def disk_io_mb() -> float:
        """Disk I/O in megabytes."""
        return Faker.pyfloat(0.0, 500.0)

    @staticmethod
    def network_io_mb() -> float:
        """Network I/O in megabytes."""
        return Faker.pyfloat(0.0, 100.0)

    @staticmethod
    def cache_hit_ratio() -> float:
        """Cache hit ratio."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def throughput_ops_per_sec() -> int:
        """Throughput in operations per second."""
        return Faker.random_int(1, 10000)

    @staticmethod
    def error_rate() -> float:
        """Error rate percentage."""
        return Faker.pyfloat(0.0, 0.1)


# Convenience functions for creating analysis-related collections
def create_analysis_results(
    count: int = 1, status: str = None, **kwargs
) -> list[dict[str, Any]]:
    """Create multiple analysis results."""
    results = []

    for _ in range(count):
        if status == "success":
            result = AnalysisResultFactory.with_traits("successful_analysis", **kwargs)
        elif status == "warning":
            result = AnalysisResultFactory.with_traits(
                "analysis_with_warnings", **kwargs
            )
        elif status == "error":
            result = AnalysisResultFactory.with_traits("failed_analysis", **kwargs)
        else:
            result = AnalysisResultFactory.create(**kwargs)

        results.append(result)

    return results


def create_comprehensive_analysis_report(
    files_analyzed: int = 50,
    include_performance: bool = True,
    include_security: bool = True,
) -> dict[str, Any]:
    """Create a comprehensive analysis report."""

    # Main analysis result
    analysis = AnalysisResultFactory.with_traits(
        "successful_analysis", files_analyzed=files_analyzed
    )

    # Risk assessment
    risk_assessment = RiskAssessmentFactory.create()

    # Quality metrics
    quality_metrics = QualityMetricsFactory.create()

    # Performance metrics (if requested)
    performance_metrics = None
    if include_performance:
        performance_metrics = PerformanceMetricsFactory.create()

    # Security analysis (if requested)
    security_analysis = None
    if include_security:
        security_analysis = {
            "vulnerabilities_found": Faker.random_int(0, 5),
            "security_score": Faker.pyfloat(0.6, 1.0),
            "security_issues": [
                "Potential SQL injection vulnerability",
                "Weak cryptographic algorithm detected",
                "Hardcoded credentials found",
            ][: Faker.random_int(0, 3)],
        }

    return {
        "analysis": analysis,
        "risk_assessment": risk_assessment,
        "quality_metrics": quality_metrics,
        "performance_metrics": performance_metrics,
        "security_analysis": security_analysis,
        "generated_at": datetime.now(),
        "report_version": "1.0.0",
    }


def create_trend_analysis(periods: int = 6) -> dict[str, Any]:
    """Create analysis trend data over multiple periods."""
    trends = {
        "periods": [],
        "metrics": {
            "risk_score": [],
            "quality_score": [],
            "test_coverage": [],
            "complexity": [],
        },
    }

    base_date = datetime.now() - timedelta(days=periods * 7)

    for i in range(periods):
        period_date = base_date + timedelta(days=i * 7)
        analysis = AnalysisResultFactory.create()
        quality = QualityMetricsFactory.create()

        trends["periods"].append(period_date.isoformat())
        trends["metrics"]["risk_score"].append(analysis["overall_risk_score"])
        trends["metrics"]["quality_score"].append(quality["overall_quality_score"])
        trends["metrics"]["test_coverage"].append(analysis["test_coverage"])
        trends["metrics"]["complexity"].append(analysis["complexity_score"])

    return trends
