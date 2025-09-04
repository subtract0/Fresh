"""
Product Manager Agent System

Autonomous Product Manager that applies product thinking to feature development.
Implements problem-first analysis, RICE scoring, and product documentation.
"""
from __future__ import annotations
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ProblemSeverity(Enum):
    LOW = 1
    MEDIUM = 5  
    HIGH = 8
    CRITICAL = 10


class ImpactLevel(Enum):
    MINIMAL = 0.25
    LOW = 0.5
    MEDIUM = 1.0
    HIGH = 2.0
    MASSIVE = 3.0


@dataclass
class ProblemAnalysis:
    """Analysis of a user/business problem."""
    problem_statement: str
    affected_users: List[str]
    severity_score: int  # 1-10
    frequency: str  # daily, weekly, monthly, rare
    cost_of_not_solving: str
    current_workarounds: List[str]
    five_why_analysis: List[str]
    evidence: List[str]


@dataclass
class SolutionValidation:
    """Validation of a proposed solution."""
    core_capability: str
    key_differentiator: str
    technical_approach: str
    alternatives_considered: List[Dict[str, str]]
    unique_insight: str
    why_now: str


@dataclass
class RICEScore:
    """RICE prioritization score."""
    reach: int  # Users affected per quarter
    impact: float  # Impact score (0.25-3.0)
    confidence: float  # Confidence percentage (0-1.0)
    effort: float  # Person-months
    score: float = field(init=False)
    
    def __post_init__(self):
        self.score = (self.reach * self.impact * self.confidence) / self.effort


@dataclass
class UserStory:
    """Structured user story."""
    persona: str
    action: str
    benefit: str
    acceptance_criteria: List[str]
    edge_cases: List[str]
    error_states: List[str]


@dataclass
class ProductRequirement:
    """Product requirement with priority and metrics."""
    requirement_id: str
    description: str
    priority: str  # P0, P1, P2
    success_metric: str
    measurement_method: str
    dependency: Optional[str] = None


@dataclass
class FeatureSpecification:
    """Complete feature specification."""
    feature_name: str
    problem_analysis: ProblemAnalysis
    solution_validation: SolutionValidation
    user_story: UserStory
    requirements: List[ProductRequirement]
    rice_score: RICEScore
    effort_estimate: Dict[str, float]  # engineering, design, qa days
    success_metrics: Dict[str, Any]
    dependencies: List[str]
    risks: List[Dict[str, str]]


class ProductManagerAgent:
    """Autonomous Product Manager Agent."""
    
    def __init__(self):
        self.name = "ProductManager"
        self.version = "3.0.0"
        self.color = "blue"
        
    def analyze_feature_request(self, feature_data: Dict[str, Any]) -> FeatureSpecification:
        """Complete product analysis of a feature request."""
        
        # Step 1: Problem Analysis
        problem = self._extract_and_validate_problem(feature_data)
        if problem.severity_score < 6:
            raise ValueError(f"Problem severity too low ({problem.severity_score}/10). Archive for future.")
        
        # Step 2: Solution Validation
        solution = self._validate_solution(feature_data, problem)
        
        # Step 3: User Story Creation
        user_story = self._create_user_story(feature_data, problem)
        
        # Step 4: Requirements Definition
        requirements = self._define_requirements(feature_data, problem, solution)
        
        # Step 5: RICE Scoring
        rice_score = self._calculate_rice_score(feature_data, problem, solution)
        
        # Step 6: Effort Estimation
        effort = self._estimate_effort(requirements)
        
        # Step 7: Success Metrics
        metrics = self._define_success_metrics(problem, solution)
        
        # Step 8: Risk Assessment
        risks = self._assess_risks(feature_data, solution)
        
        return FeatureSpecification(
            feature_name=feature_data.get('name', 'Unknown Feature'),
            problem_analysis=problem,
            solution_validation=solution,
            user_story=user_story,
            requirements=requirements,
            rice_score=rice_score,
            effort_estimate=effort,
            success_metrics=metrics,
            dependencies=feature_data.get('dependencies', []),
            risks=risks
        )
    
    def _extract_and_validate_problem(self, feature_data: Dict[str, Any]) -> ProblemAnalysis:
        """Extract and validate the core problem."""
        
        # Extract problem from feature data
        description = feature_data.get('description', '')
        issues = feature_data.get('issues', [])
        
        # Generate problem statement
        if 'not accessible' in ' '.join(issues).lower():
            problem_statement = f"Users cannot access {feature_data.get('name')} functionality through standard interfaces"
            affected_users = ["developers", "power users", "automation tools"]
            severity = 7
        elif 'lacks test' in ' '.join(issues).lower():
            problem_statement = f"Lack of test coverage for {feature_data.get('name')} creates reliability and maintainability risks"
            affected_users = ["developers", "qa engineers", "users depending on reliability"]
            severity = 6
        elif 'not necessary' in ' '.join(issues).lower():
            problem_statement = f"Feature {feature_data.get('name')} may be adding unnecessary complexity"
            affected_users = ["developers", "users facing complexity"]
            severity = 4
        else:
            problem_statement = f"Feature {feature_data.get('name')} has quality issues that impact usability"
            affected_users = ["end users", "developers"]
            severity = 6
        
        # 5-Why Analysis
        five_why = self._generate_five_why_analysis(problem_statement)
        
        return ProblemAnalysis(
            problem_statement=problem_statement,
            affected_users=affected_users,
            severity_score=severity,
            frequency="daily" if severity >= 7 else "weekly",
            cost_of_not_solving="Development inefficiency, user frustration, technical debt",
            current_workarounds=["Manual processes", "Alternative tools", "Skipping functionality"],
            five_why_analysis=five_why,
            evidence=[f"Feature inventory shows: {', '.join(issues)}"]
        )
    
    def _generate_five_why_analysis(self, problem: str) -> List[str]:
        """Generate 5-Why root cause analysis."""
        if "not accessible" in problem.lower():
            return [
                "Why 1: Feature is not accessible - No CLI/API interface provided",
                "Why 2: No interface provided - Feature was implemented without integration",
                "Why 3: Implemented without integration - Development focused on core logic only",
                "Why 4: Focused on core logic only - No requirement for accessibility defined",
                "Why 5: No requirement defined - Product requirements not established upfront"
            ]
        elif "test coverage" in problem.lower():
            return [
                "Why 1: Lacks test coverage - Tests not written during development",
                "Why 2: Tests not written - No TDD process followed",
                "Why 3: No TDD process - Testing not prioritized in workflow",
                "Why 4: Testing not prioritized - Quality gates not established",
                "Why 5: Quality gates missing - Development process needs strengthening"
            ]
        else:
            return [
                "Why 1: Feature has quality issues - Implementation not complete",
                "Why 2: Implementation incomplete - Requirements not fully specified",
                "Why 3: Requirements not specified - Product planning insufficient",
                "Why 4: Product planning insufficient - Process needs improvement",
                "Why 5: Process needs improvement - Systematic approach required"
            ]
    
    def _validate_solution(self, feature_data: Dict[str, Any], problem: ProblemAnalysis) -> SolutionValidation:
        """Validate the proposed solution approach."""
        
        feature_name = feature_data.get('name', 'Unknown')
        
        if "not accessible" in problem.problem_statement.lower():
            return SolutionValidation(
                core_capability=f"Provide CLI and programmatic access to {feature_name}",
                key_differentiator="Makes existing functionality accessible to users and automation",
                technical_approach="Add CLI commands and API endpoints with proper documentation",
                alternatives_considered=[
                    {"option": "Keep as library only", "rejected": "Limits accessibility"},
                    {"option": "GUI interface", "rejected": "Not suitable for automation"},
                    {"option": "CLI + API", "selected": "Provides maximum accessibility"}
                ],
                unique_insight="Accessibility is a feature quality multiplier",
                why_now="Feature inventory shows many unhooked features blocking user value"
            )
        else:
            return SolutionValidation(
                core_capability=f"Improve quality and reliability of {feature_name}",
                key_differentiator="Addresses quality debt systematically",
                technical_approach="Add comprehensive testing and documentation",
                alternatives_considered=[
                    {"option": "Remove feature", "rejected": "Still has user value"},
                    {"option": "Keep as-is", "rejected": "Quality debt accumulates"},
                    {"option": "Quality improvement", "selected": "Maintains value while improving quality"}
                ],
                unique_insight="Quality improvements compound over time",
                why_now="Technical debt is impacting development velocity"
            )
    
    def _create_user_story(self, feature_data: Dict[str, Any], problem: ProblemAnalysis) -> UserStory:
        """Create structured user story."""
        
        feature_name = feature_data.get('name', 'feature')
        
        if "not accessible" in problem.problem_statement.lower():
            return UserStory(
                persona="developer",
                action=f"access {feature_name} functionality via CLI/API",
                benefit="integrate it into my workflow and automation",
                acceptance_criteria=[
                    f"Given I need {feature_name}, when I run the CLI command, then I get expected output",
                    "Given I want to automate, when I call the API, then I get programmatic access",
                    "Given I need help, when I run --help, then I see usage documentation"
                ],
                edge_cases=[
                    "Handle invalid parameters gracefully with clear error messages",
                    "Handle network failures with retry logic",
                    "Handle missing dependencies with helpful guidance"
                ],
                error_states=[
                    "When parameters are invalid, display usage help",
                    "When service unavailable, show retry suggestion",
                    "When permissions insufficient, show access requirements"
                ]
            )
        else:
            return UserStory(
                persona="user",
                action=f"rely on {feature_name} to work correctly",
                benefit="focus on my work without worrying about tool reliability",
                acceptance_criteria=[
                    f"Given I use {feature_name}, when I provide valid input, then I get correct output",
                    "Given an error occurs, when I see the message, then I understand what went wrong",
                    "Given I need documentation, when I look it up, then I find clear instructions"
                ],
                edge_cases=[
                    "Handle edge cases without crashing",
                    "Graceful degradation when dependencies unavailable",
                    "Clear error messages for all failure modes"
                ],
                error_states=[
                    "When input invalid, show clear validation errors",
                    "When system error, provide actionable guidance",
                    "When timeout, explain and suggest retry"
                ]
            )
    
    def _define_requirements(self, feature_data: Dict[str, Any], problem: ProblemAnalysis, 
                           solution: SolutionValidation) -> List[ProductRequirement]:
        """Define structured requirements with priorities."""
        
        requirements = []
        feature_name = feature_data.get('name', 'feature')
        
        if "not accessible" in problem.problem_statement.lower():
            requirements.extend([
                ProductRequirement(
                    requirement_id="REQ-001",
                    description=f"Provide CLI command for {feature_name}",
                    priority="P0",
                    success_metric="CLI command available and functional",
                    measurement_method="Manual testing of CLI help and basic usage"
                ),
                ProductRequirement(
                    requirement_id="REQ-002", 
                    description="Include comprehensive help documentation",
                    priority="P0",
                    success_metric="Help text explains all options and usage",
                    measurement_method="Documentation review and user testing"
                ),
                ProductRequirement(
                    requirement_id="REQ-003",
                    description="Handle errors gracefully with clear messages",
                    priority="P1",
                    success_metric="Error messages are actionable",
                    measurement_method="Error scenario testing"
                )
            ])
        
        # Common requirements
        requirements.extend([
            ProductRequirement(
                requirement_id="REQ-004",
                description="Maintain backward compatibility",
                priority="P0",
                success_metric="Existing functionality unchanged",
                measurement_method="Regression testing"
            ),
            ProductRequirement(
                requirement_id="REQ-005",
                description="Include comprehensive test coverage",
                priority="P1",
                success_metric="Test coverage >90%",
                measurement_method="Code coverage analysis"
            )
        ])
        
        return requirements
    
    def _calculate_rice_score(self, feature_data: Dict[str, Any], problem: ProblemAnalysis, 
                            solution: SolutionValidation) -> RICEScore:
        """Calculate RICE prioritization score."""
        
        # Estimate reach based on feature type and user base
        if "not accessible" in problem.problem_statement.lower():
            reach = 50  # Developers who could use this feature
        elif "test coverage" in problem.problem_statement.lower():
            reach = 10  # Mainly impacts development team
        else:
            reach = 25  # Mixed user impact
        
        # Impact based on problem severity
        if problem.severity_score >= 8:
            impact = ImpactLevel.HIGH.value
        elif problem.severity_score >= 6:
            impact = ImpactLevel.MEDIUM.value
        else:
            impact = ImpactLevel.LOW.value
        
        # Confidence based on evidence quality
        confidence = 0.8  # High confidence in feature inventory analysis
        
        # Effort estimation in person-months
        effort = 0.25  # ~1 week for typical hookup work
        
        return RICEScore(
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort
        )
    
    def _estimate_effort(self, requirements: List[ProductRequirement]) -> Dict[str, float]:
        """Estimate effort by discipline."""
        
        base_effort = len([req for req in requirements if req.priority == "P0"]) * 1.0
        
        return {
            "engineering": base_effort * 2.0,  # 2 days per P0 requirement
            "design": base_effort * 0.5,      # 0.5 days per P0 requirement  
            "qa": base_effort * 1.0           # 1 day per P0 requirement
        }
    
    def _define_success_metrics(self, problem: ProblemAnalysis, solution: SolutionValidation) -> Dict[str, Any]:
        """Define success metrics for the feature."""
        
        if "not accessible" in problem.problem_statement.lower():
            return {
                "primary_metric": {
                    "name": "CLI usage adoption",
                    "baseline": "0 users (feature not accessible)",
                    "target": ">5 developers using CLI within 30 days",
                    "measurement": "CLI usage analytics"
                },
                "secondary_metrics": {
                    "documentation_views": "Track help command usage",
                    "error_rate": "<5% of CLI invocations result in errors",
                    "time_to_value": "<2 minutes from discovery to first successful use"
                }
            }
        else:
            return {
                "primary_metric": {
                    "name": "Feature quality score",
                    "baseline": f"Current: {problem.severity_score}/10",
                    "target": ">8/10 quality score",
                    "measurement": "Feature inventory quality assessment"
                },
                "secondary_metrics": {
                    "bug_reports": "Reduce related bug reports by 50%",
                    "test_coverage": "Achieve >90% test coverage",
                    "documentation_completeness": "100% of public APIs documented"
                }
            }
    
    def _assess_risks(self, feature_data: Dict[str, Any], solution: SolutionValidation) -> List[Dict[str, str]]:
        """Assess risks for the feature implementation."""
        
        return [
            {
                "risk": "Low adoption",
                "probability": "Medium", 
                "impact": "Low",
                "mitigation": "Include in documentation and examples"
            },
            {
                "risk": "Breaking changes",
                "probability": "Low",
                "impact": "High", 
                "mitigation": "Comprehensive regression testing"
            },
            {
                "risk": "Maintenance overhead",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Automated testing and clear documentation"
            }
        ]
    
    def prioritize_features(self, features: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], RICEScore]]:
        """Prioritize multiple features using RICE scoring."""
        
        scored_features = []
        
        for feature in features:
            try:
                spec = self.analyze_feature_request(feature)
                scored_features.append((feature, spec.rice_score))
            except ValueError:
                # Skip features that don't meet minimum criteria
                continue
        
        # Sort by RICE score descending
        scored_features.sort(key=lambda x: x[1].score, reverse=True)
        
        return scored_features
    
    def generate_product_roadmap(self, features: List[Dict[str, Any]], time_horizon: int = 90) -> Dict[str, Any]:
        """Generate a product roadmap based on prioritized features."""
        
        prioritized = self.prioritize_features(features)
        
        # Group by effort and impact
        quick_wins = [f for f, score in prioritized if score.effort <= 0.5 and score.impact >= 1.0]
        major_projects = [f for f, score in prioritized if score.effort > 0.5 and score.impact >= 2.0]
        fill_ins = [f for f, score in prioritized if score.effort <= 0.5 and score.impact < 1.0]
        
        return {
            "roadmap_period": f"{time_horizon} days",
            "strategic_themes": [
                "Feature Accessibility: Make existing functionality discoverable and usable",
                "Quality Improvement: Reduce technical debt and improve reliability", 
                "User Experience: Streamline workflows and reduce friction"
            ],
            "now_0_30_days": {
                "focus": "Quick wins with immediate user impact",
                "features": [f.get('name') for f in quick_wins[:5]]
            },
            "next_30_60_days": {
                "focus": "Major feature improvements",
                "features": [f.get('name') for f in major_projects[:3]]
            },
            "later_60_90_days": {
                "focus": "Fill-in improvements and polish",
                "features": [f.get('name') for f in fill_ins[:8]]
            },
            "backlog": {
                "features_count": max(0, len(prioritized) - 16),
                "total_rice_score": sum(score.score for _, score in prioritized)
            }
        }
    
    def create_prd_document(self, spec: FeatureSpecification) -> str:
        """Generate Product Requirements Document."""
        
        timestamp = datetime.now().isoformat()
        
        return f"""# Product Requirements Document: {spec.feature_name}

Generated: {timestamp}
PM Agent Version: {self.version}

## Executive Summary
**Problem**: {spec.problem_analysis.problem_statement}
**Solution**: {spec.solution_validation.core_capability}
**Impact**: {spec.problem_analysis.severity_score}/10 severity affecting {len(spec.problem_analysis.affected_users)} user groups
**Priority**: RICE Score {spec.rice_score.score:.1f}

## Problem Analysis
### Core Problem
- **Problem Statement**: {spec.problem_analysis.problem_statement}
- **Problem Severity**: {spec.problem_analysis.severity_score}/10
- **Affected Users**: {', '.join(spec.problem_analysis.affected_users)}
- **Frequency**: {spec.problem_analysis.frequency}
- **Current Workarounds**: {', '.join(spec.problem_analysis.current_workarounds)}

### Root Cause Analysis (5-Why)
{''.join(f'{i+1}. {why}' for i, why in enumerate(spec.problem_analysis.five_why_analysis))}

### Evidence
{''.join(f'- {evidence}' for evidence in spec.problem_analysis.evidence)}

## Solution Design
### Proposed Solution
- **Core Capability**: {spec.solution_validation.core_capability}
- **Key Differentiator**: {spec.solution_validation.key_differentiator}
- **Technical Approach**: {spec.solution_validation.technical_approach}
- **Why Now**: {spec.solution_validation.why_now}

### Alternatives Considered
{''.join(f"- **{alt.get('option', 'Unknown')}**: {alt.get('rejected', alt.get('selected', 'No reason'))}\\n" for alt in spec.solution_validation.alternatives_considered)}

## User Story
**As a** {spec.user_story.persona}
**I want to** {spec.user_story.action}
**So that I can** {spec.user_story.benefit}

### Acceptance Criteria
{''.join(f'- [ ] {criteria}' for criteria in spec.user_story.acceptance_criteria)}

### Edge Cases
{''.join(f'- [ ] {case}' for case in spec.user_story.edge_cases)}

## Requirements
### Functional Requirements
{''.join(f'- **{req.requirement_id}** ({req.priority}): {req.description}' for req in spec.requirements)}

### Success Metrics
#### Primary Metric
- **Metric**: {spec.success_metrics['primary_metric']['name']}
- **Baseline**: {spec.success_metrics['primary_metric']['baseline']}
- **Target**: {spec.success_metrics['primary_metric']['target']}
- **Measurement**: {spec.success_metrics['primary_metric']['measurement']}

#### Secondary Metrics
{''.join(f"- **{metric}**: {value}\\n" for metric, value in spec.success_metrics.get('secondary_metrics', {}).items())}

## Implementation Planning
### Effort Estimation
- **Engineering**: {spec.effort_estimate.get('engineering', 0)} days
- **Design**: {spec.effort_estimate.get('design', 0)} days  
- **QA**: {spec.effort_estimate.get('qa', 0)} days
- **Total**: {sum(spec.effort_estimate.values())} days

### RICE Prioritization
- **Reach**: {spec.rice_score.reach} users/quarter
- **Impact**: {spec.rice_score.impact:.1f}/3.0
- **Confidence**: {spec.rice_score.confidence:.0%}
- **Effort**: {spec.rice_score.effort} person-months
- **RICE Score**: {spec.rice_score.score:.1f}

## Risk Assessment
{''.join(f"### {risk['risk']}\\n- **Probability**: {risk['probability']}\\n- **Impact**: {risk['impact']}\\n- **Mitigation**: {risk['mitigation']}\\n\\n" for risk in spec.risks)}

## Dependencies
{''.join(f'- {dep}' for dep in spec.dependencies) if spec.dependencies else '- None identified'}

---
*This PRD was generated by autonomous Product Manager Agent v{self.version}*
"""


def create_product_manager_agent() -> ProductManagerAgent:
    """Factory function to create a Product Manager Agent."""
    return ProductManagerAgent()
