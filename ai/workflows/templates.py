"""Workflow Template Library - Common Patterns and Templates.

This module provides a comprehensive library of common workflow templates for 
typical scenarios in software development, research projects, documentation 
generation, system analysis, and other common agent tasks. Templates provide
reusable workflow patterns that can be instantiated with specific parameters.

Cross-references:
    - Workflow Types: ai/workflows/types.py for data structures
    - Workflow Language: ai/workflows/language.py for WDL building  
    - Workflow Engine: ai/workflows/engine.py for execution
    - Agent System: ai/interface/agent_spawner.py for agent coordination
    - MCP Integration: ai/tools/enhanced_mcp.py for external services

Features:
    - Pre-built templates for common workflows
    - Parameter-driven template instantiation
    - Best practice workflow patterns
    - Extensible template system
    - Template validation and testing
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Union
from datetime import timedelta
import uuid

from ai.workflows.types import (
    WorkflowTemplate, WorkflowDefinition, WorkflowCondition, 
    ConditionOperator, RetryConfig, RetryStrategy
)
from ai.workflows.language import WorkflowBuilder, create_workflow


class TemplateLibrary:
    """Central repository for workflow templates."""
    
    def __init__(self):
        self.templates: Dict[str, WorkflowTemplate] = {}
        self._initialize_builtin_templates()
        
    def _initialize_builtin_templates(self):
        """Initialize the library with built-in templates."""
        # Software Development Templates
        self.register_template(self._create_software_development_template())
        self.register_template(self._create_code_review_template())
        self.register_template(self._create_bug_fix_template())
        self.register_template(self._create_feature_development_template())
        
        # Research Templates
        self.register_template(self._create_research_analysis_template())
        self.register_template(self._create_competitive_analysis_template())
        self.register_template(self._create_literature_review_template())
        
        # Documentation Templates
        self.register_template(self._create_api_documentation_template())
        self.register_template(self._create_user_manual_template())
        self.register_template(self._create_technical_specification_template())
        
        # System Analysis Templates
        self.register_template(self._create_system_audit_template())
        self.register_template(self._create_performance_analysis_template())
        self.register_template(self._create_security_assessment_template())
        
        # General Purpose Templates
        self.register_template(self._create_data_processing_pipeline_template())
        self.register_template(self._create_approval_workflow_template())
        self.register_template(self._create_parallel_processing_template())
        
    def register_template(self, template: WorkflowTemplate):
        """Register a new template in the library."""
        self.templates[template.template_id] = template
        
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)
        
    def list_templates(self, category: Optional[str] = None) -> List[WorkflowTemplate]:
        """List all templates, optionally filtered by category."""
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())
        
    def get_template_categories(self) -> List[str]:
        """Get all template categories."""
        return list(set(t.category for t in self.templates.values()))
        
    def instantiate_template(
        self, 
        template_id: str, 
        parameters: Dict[str, Any],
        name_override: Optional[str] = None
    ) -> WorkflowDefinition:
        """Instantiate a template with given parameters."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
            
        # Validate parameters
        for param_name, param_def in template.parameters.items():
            if param_def.get("required", False) and param_name not in parameters:
                raise ValueError(f"Required parameter missing: {param_name}")
                
        # Use template-specific instantiation method
        instantiation_method = getattr(self, f"_instantiate_{template_id}", None)
        if instantiation_method:
            workflow = instantiation_method(parameters)
        else:
            workflow = template.instantiate(parameters)
            
        if name_override:
            workflow.name = name_override
            
        return workflow
        
    # Software Development Templates
    def _create_software_development_template(self) -> WorkflowTemplate:
        """Create a comprehensive software development workflow template."""
        return WorkflowTemplate(
            template_id="software_development",
            name="Software Development Workflow",
            description="Complete software development workflow with planning, implementation, testing, and deployment",
            category="development",
            parameters={
                "project_name": {"type": "string", "required": True, "description": "Name of the project"},
                "requirements": {"type": "string", "required": True, "description": "Project requirements"},
                "target_language": {"type": "string", "default": "python", "description": "Programming language"},
                "include_tests": {"type": "boolean", "default": True, "description": "Include automated testing"},
                "include_docs": {"type": "boolean", "default": True, "description": "Include documentation"},
                "deployment_target": {"type": "string", "default": "local", "description": "Deployment target"}
            },
            author="Fresh Agent System",
            examples=[{
                "name": "Web API Development",
                "parameters": {
                    "project_name": "User Management API",
                    "requirements": "REST API for user authentication and profile management",
                    "target_language": "python",
                    "include_tests": True,
                    "include_docs": True,
                    "deployment_target": "docker"
                }
            }]
        )
        
    def _instantiate_software_development(self, params: Dict[str, Any]) -> WorkflowDefinition:
        """Instantiate software development workflow."""
        builder = create_workflow(
            name=f"Software Development: {params['project_name']}",
            description="Complete software development lifecycle workflow"
        )
        
        # Set workflow variables
        builder.set_variable("project_name", params["project_name"])
        builder.set_variable("requirements", params["requirements"])
        builder.set_variable("target_language", params.get("target_language", "python"))
        builder.set_variable("include_tests", params.get("include_tests", True))
        builder.set_variable("include_docs", params.get("include_docs", True))
        
        # Start node
        builder.add_start("start")
        
        # Planning phase
        builder.spawn_agent(
            "architect",
            role="Software Architect", 
            instructions=f"Create technical specification for: {params['requirements']}",
            tools=["WriteMemory", "ReadMemoryContext", "GenerateNextSteps"],
            node_id="spawn_architect"
        )
        
        builder.execute_agent(
            task_description="Create detailed technical specification and architecture design",
            expected_outcome="Technical specification document with architecture decisions",
            node_id="planning_phase"
        )
        
        # Implementation phase
        builder.spawn_agent(
            "developer",
            role="Software Developer",
            instructions=f"Implement {params['project_name']} using {params.get('target_language', 'python')}",
            tools=["WriteMemory", "ReadMemoryContext", "CallMCPTool"],
            node_id="spawn_developer"
        )
        
        builder.execute_agent(
            task_description="Implement core functionality based on technical specification",
            expected_outcome="Working code implementation",
            node_id="implementation_phase"
        )
        
        # Conditional testing phase
        if params.get("include_tests", True):
            builder.spawn_agent(
                "qa_engineer", 
                role="QA Engineer",
                instructions="Create comprehensive test suite and validate functionality",
                tools=["WriteMemory", "ReadMemoryContext", "DoDCheck"],
                node_id="spawn_qa"
            )
            
            builder.execute_agent(
                task_description="Create and execute test suite",
                expected_outcome="Test results and coverage report",
                node_id="testing_phase"
            )
            
        # Conditional documentation phase
        if params.get("include_docs", True):
            builder.spawn_agent(
                "technical_writer",
                role="Technical Writer", 
                instructions="Create comprehensive documentation for the project",
                tools=["WriteMemory", "ReadMemoryContext", "GenerateReleaseNotes"],
                node_id="spawn_writer"
            )
            
            builder.execute_agent(
                task_description="Generate user documentation and API references",
                expected_outcome="Complete project documentation",
                node_id="documentation_phase"
            )
            
        # Deployment preparation
        builder.execute_agent(
            task_description="Prepare deployment artifacts and configuration",
            expected_outcome="Deployment-ready package",
            node_id="deployment_prep"
        )
        
        # Human approval for deployment
        builder.add_human_approval(
            approval_message=f"Ready to deploy {params['project_name']}. Please review and approve.",
            node_id="deployment_approval"
        )
        
        # End node
        builder.add_end("end")
        
        # Connect the workflow
        builder.connect("start", "spawn_architect")
        builder.connect("spawn_architect", "planning_phase")
        builder.connect("planning_phase", "spawn_developer")
        builder.connect("spawn_developer", "implementation_phase")
        
        if params.get("include_tests", True):
            builder.connect("implementation_phase", "spawn_qa")
            builder.connect("spawn_qa", "testing_phase")
            next_node = "testing_phase"
        else:
            next_node = "implementation_phase"
            
        if params.get("include_docs", True):
            builder.connect(next_node, "spawn_writer")
            builder.connect("spawn_writer", "documentation_phase")
            builder.connect("documentation_phase", "deployment_prep")
        else:
            builder.connect(next_node, "deployment_prep")
            
        builder.connect("deployment_prep", "deployment_approval")
        builder.connect("deployment_approval", "end")
        
        return builder.build()
        
    def _create_code_review_template(self) -> WorkflowTemplate:
        """Create code review workflow template."""
        return WorkflowTemplate(
            template_id="code_review",
            name="Code Review Workflow", 
            description="Automated code review process with multiple reviewers",
            category="development",
            parameters={
                "repository_url": {"type": "string", "required": True, "description": "Git repository URL"},
                "pull_request_id": {"type": "string", "required": True, "description": "Pull request ID"},
                "review_criteria": {"type": "array", "default": ["code_quality", "security", "performance"], "description": "Review criteria"},
                "required_approvals": {"type": "number", "default": 2, "description": "Number of required approvals"}
            }
        )
        
    def _create_bug_fix_template(self) -> WorkflowTemplate:
        """Create bug fix workflow template.""" 
        return WorkflowTemplate(
            template_id="bug_fix",
            name="Bug Fix Workflow",
            description="Systematic approach to bug investigation and resolution", 
            category="development",
            parameters={
                "bug_description": {"type": "string", "required": True, "description": "Description of the bug"},
                "severity": {"type": "string", "default": "medium", "description": "Bug severity (low, medium, high, critical)"},
                "affected_components": {"type": "array", "default": [], "description": "List of affected system components"},
                "include_root_cause": {"type": "boolean", "default": True, "description": "Include root cause analysis"}
            }
        )
        
    def _create_feature_development_template(self) -> WorkflowTemplate:
        """Create feature development workflow template."""
        return WorkflowTemplate(
            template_id="feature_development",
            name="Feature Development Workflow",
            description="End-to-end feature development with design, implementation, and validation",
            category="development", 
            parameters={
                "feature_name": {"type": "string", "required": True, "description": "Name of the feature"},
                "feature_requirements": {"type": "string", "required": True, "description": "Detailed feature requirements"},
                "user_stories": {"type": "array", "default": [], "description": "User stories for the feature"},
                "design_required": {"type": "boolean", "default": True, "description": "Whether design phase is required"}
            }
        )
        
    # Research Templates
    def _create_research_analysis_template(self) -> WorkflowTemplate:
        """Create research analysis workflow template."""
        return WorkflowTemplate(
            template_id="research_analysis", 
            name="Research Analysis Workflow",
            description="Comprehensive research analysis with data collection and synthesis",
            category="research",
            parameters={
                "research_topic": {"type": "string", "required": True, "description": "Main research topic"},
                "research_questions": {"type": "array", "required": True, "description": "List of research questions"},
                "data_sources": {"type": "array", "default": ["web", "academic", "reports"], "description": "Data sources to use"},
                "analysis_depth": {"type": "string", "default": "comprehensive", "description": "Analysis depth (basic, standard, comprehensive)"}
            }
        )
        
    def _create_competitive_analysis_template(self) -> WorkflowTemplate:
        """Create competitive analysis workflow template."""
        return WorkflowTemplate(
            template_id="competitive_analysis",
            name="Competitive Analysis Workflow", 
            description="Systematic competitive analysis and benchmarking",
            category="research",
            parameters={
                "company_name": {"type": "string", "required": True, "description": "Your company name"},
                "competitors": {"type": "array", "required": True, "description": "List of competitors to analyze"},
                "analysis_dimensions": {"type": "array", "default": ["features", "pricing", "market_share"], "description": "Analysis dimensions"},
                "market_segment": {"type": "string", "default": "", "description": "Target market segment"}
            }
        )
        
    def _create_literature_review_template(self) -> WorkflowTemplate:
        """Create literature review workflow template."""
        return WorkflowTemplate(
            template_id="literature_review",
            name="Literature Review Workflow",
            description="Systematic literature review and synthesis", 
            category="research",
            parameters={
                "research_domain": {"type": "string", "required": True, "description": "Research domain or field"},
                "keywords": {"type": "array", "required": True, "description": "Search keywords"},
                "time_range": {"type": "string", "default": "5_years", "description": "Time range for literature (1_year, 5_years, 10_years, all)"},
                "min_papers": {"type": "number", "default": 20, "description": "Minimum number of papers to review"}
            }
        )
        
    # Documentation Templates
    def _create_api_documentation_template(self) -> WorkflowTemplate:
        """Create API documentation workflow template."""
        return WorkflowTemplate(
            template_id="api_documentation",
            name="API Documentation Workflow",
            description="Comprehensive API documentation generation",
            category="documentation", 
            parameters={
                "api_name": {"type": "string", "required": True, "description": "API name"},
                "api_version": {"type": "string", "default": "1.0", "description": "API version"},
                "endpoints_file": {"type": "string", "required": True, "description": "File containing endpoint definitions"},
                "include_examples": {"type": "boolean", "default": True, "description": "Include usage examples"},
                "output_format": {"type": "string", "default": "openapi", "description": "Output format (openapi, markdown, html)"}
            }
        )
        
    def _create_user_manual_template(self) -> WorkflowTemplate:
        """Create user manual workflow template."""
        return WorkflowTemplate(
            template_id="user_manual",
            name="User Manual Workflow",
            description="Comprehensive user manual and guide creation",
            category="documentation",
            parameters={
                "product_name": {"type": "string", "required": True, "description": "Product name"},
                "target_audience": {"type": "string", "default": "general", "description": "Target audience (general, technical, business)"},
                "manual_sections": {"type": "array", "default": ["getting_started", "features", "troubleshooting"], "description": "Manual sections"},
                "include_screenshots": {"type": "boolean", "default": True, "description": "Include screenshots and visuals"}
            }
        )
        
    def _create_technical_specification_template(self) -> WorkflowTemplate:
        """Create technical specification workflow template."""
        return WorkflowTemplate(
            template_id="technical_specification",
            name="Technical Specification Workflow", 
            description="Detailed technical specification document creation",
            category="documentation",
            parameters={
                "project_name": {"type": "string", "required": True, "description": "Project name"},
                "requirements": {"type": "string", "required": True, "description": "High-level requirements"},
                "architecture_type": {"type": "string", "default": "microservices", "description": "Architecture type"},
                "include_diagrams": {"type": "boolean", "default": True, "description": "Include architectural diagrams"}
            }
        )
        
    # System Analysis Templates
    def _create_system_audit_template(self) -> WorkflowTemplate:
        """Create system audit workflow template."""
        return WorkflowTemplate(
            template_id="system_audit",
            name="System Audit Workflow",
            description="Comprehensive system audit and assessment",
            category="analysis",
            parameters={
                "system_name": {"type": "string", "required": True, "description": "System name"},
                "audit_scope": {"type": "array", "default": ["security", "performance", "compliance"], "description": "Audit scope areas"},
                "compliance_standards": {"type": "array", "default": [], "description": "Compliance standards to check"},
                "generate_report": {"type": "boolean", "default": True, "description": "Generate audit report"}
            }
        )
        
    def _create_performance_analysis_template(self) -> WorkflowTemplate:
        """Create performance analysis workflow template."""
        return WorkflowTemplate(
            template_id="performance_analysis",
            name="Performance Analysis Workflow",
            description="System performance analysis and optimization recommendations",
            category="analysis",
            parameters={
                "system_type": {"type": "string", "required": True, "description": "Type of system (web_app, database, api, etc.)"},
                "metrics_to_analyze": {"type": "array", "default": ["response_time", "throughput", "resource_usage"], "description": "Performance metrics"},
                "baseline_period": {"type": "string", "default": "30_days", "description": "Baseline period for comparison"},
                "optimization_focus": {"type": "string", "default": "balanced", "description": "Optimization focus (speed, efficiency, scalability)"}
            }
        )
        
    def _create_security_assessment_template(self) -> WorkflowTemplate:
        """Create security assessment workflow template."""
        return WorkflowTemplate(
            template_id="security_assessment",
            name="Security Assessment Workflow",
            description="Comprehensive security assessment and vulnerability analysis",
            category="analysis", 
            parameters={
                "target_system": {"type": "string", "required": True, "description": "Target system for assessment"},
                "assessment_type": {"type": "string", "default": "comprehensive", "description": "Assessment type (basic, standard, comprehensive)"},
                "security_frameworks": {"type": "array", "default": ["OWASP", "NIST"], "description": "Security frameworks to apply"},
                "include_penetration_testing": {"type": "boolean", "default": False, "description": "Include penetration testing"}
            }
        )
        
    # General Purpose Templates
    def _create_data_processing_pipeline_template(self) -> WorkflowTemplate:
        """Create data processing pipeline workflow template."""
        return WorkflowTemplate(
            template_id="data_processing_pipeline",
            name="Data Processing Pipeline Workflow",
            description="Automated data processing and transformation pipeline",
            category="data",
            parameters={
                "data_source": {"type": "string", "required": True, "description": "Data source location or type"},
                "processing_steps": {"type": "array", "required": True, "description": "List of processing steps"},
                "output_format": {"type": "string", "default": "json", "description": "Output data format"},
                "validation_rules": {"type": "array", "default": [], "description": "Data validation rules"},
                "error_handling": {"type": "string", "default": "skip", "description": "Error handling strategy (skip, retry, fail)"}
            }
        )
        
    def _create_approval_workflow_template(self) -> WorkflowTemplate:
        """Create approval workflow template."""
        return WorkflowTemplate(
            template_id="approval_workflow",
            name="Multi-Stage Approval Workflow",
            description="Multi-stage approval process with conditional routing",
            category="process",
            parameters={
                "approval_item": {"type": "string", "required": True, "description": "Item requiring approval"},
                "approval_stages": {"type": "array", "default": ["manager", "director", "executive"], "description": "Approval stages"},
                "approval_criteria": {"type": "object", "default": {}, "description": "Criteria for each stage"},
                "timeout_hours": {"type": "number", "default": 24, "description": "Timeout for each approval stage"}
            }
        )
        
    def _create_parallel_processing_template(self) -> WorkflowTemplate:
        """Create parallel processing workflow template."""
        return WorkflowTemplate(
            template_id="parallel_processing",
            name="Parallel Processing Workflow", 
            description="Parallel processing of multiple tasks with aggregation",
            category="process",
            parameters={
                "tasks": {"type": "array", "required": True, "description": "List of tasks to process"},
                "max_parallel": {"type": "number", "default": 5, "description": "Maximum parallel executions"},
                "aggregation_method": {"type": "string", "default": "collect", "description": "Result aggregation method"},
                "failure_tolerance": {"type": "string", "default": "partial", "description": "Failure tolerance (none, partial, full)"}
            }
        )
        
    # Template instantiation methods for complex templates
    def _instantiate_research_analysis(self, params: Dict[str, Any]) -> WorkflowDefinition:
        """Instantiate research analysis workflow."""
        builder = create_workflow(
            name=f"Research Analysis: {params['research_topic']}",
            description="Comprehensive research analysis workflow"
        )
        
        # Set variables
        builder.set_variable("research_topic", params["research_topic"])
        builder.set_variable("research_questions", params["research_questions"])
        builder.set_variable("data_sources", params.get("data_sources", ["web", "academic"]))
        
        # Start
        builder.add_start("start")
        
        # Research planning
        builder.spawn_agent(
            "research_coordinator",
            role="Research Coordinator",
            instructions=f"Plan comprehensive research strategy for: {params['research_topic']}",
            tools=["WriteMemory", "ReadMemoryContext", "CallMCPTool"],
            node_id="spawn_coordinator"
        )
        
        builder.execute_agent(
            task_description="Create detailed research plan and methodology",
            expected_outcome="Research plan with data collection strategy",
            node_id="research_planning"
        )
        
        # Parallel data collection
        data_sources = params.get("data_sources", ["web", "academic", "reports"])
        branches = []
        
        for i, source in enumerate(data_sources):
            # Create data collection branch
            collector_id = f"spawn_collector_{i}"
            collection_id = f"data_collection_{i}"
            
            builder.spawn_agent(
                "data_collector",
                role=f"Data Collector - {source.title()}",
                instructions=f"Collect data from {source} sources for research topic",
                tools=["WriteMemory", "ReadMemoryContext", "CallMCPTool"],
                node_id=collector_id
            )
            
            builder.execute_agent(
                task_description=f"Collect and curate data from {source} sources",
                expected_outcome=f"Curated data from {source}",
                node_id=collection_id
            )
            
            builder.connect(collector_id, collection_id)
            branches.append([collector_id, collection_id])
            
        # Add parallel node for data collection
        builder.add_parallel(
            branches=branches,
            join_strategy="wait_all",
            node_id="parallel_collection"
        )
        
        # Data synthesis
        builder.spawn_agent(
            "research_analyst",
            role="Research Analyst", 
            instructions="Synthesize collected data and answer research questions",
            tools=["WriteMemory", "ReadMemoryContext", "GenerateReleaseNotes"],
            node_id="spawn_analyst"
        )
        
        builder.execute_agent(
            task_description="Analyze collected data and synthesize findings",
            expected_outcome="Research findings and analysis report",
            node_id="data_synthesis"
        )
        
        # Quality review
        builder.add_human_approval(
            approval_message="Research analysis complete. Please review findings and approve.",
            node_id="quality_review"
        )
        
        # End
        builder.add_end("end")
        
        # Connect workflow
        builder.connect("start", "spawn_coordinator")
        builder.connect("spawn_coordinator", "research_planning")
        builder.connect("research_planning", "parallel_collection")
        
        # Connect parallel branches to coordinator
        for i, source in enumerate(data_sources):
            builder.connect("research_planning", f"spawn_collector_{i}")
            
        builder.connect("parallel_collection", "spawn_analyst")
        builder.connect("spawn_analyst", "data_synthesis")
        builder.connect("data_synthesis", "quality_review")
        builder.connect("quality_review", "end")
        
        return builder.build()
        
    def _instantiate_api_documentation(self, params: Dict[str, Any]) -> WorkflowDefinition:
        """Instantiate API documentation workflow."""
        builder = create_workflow(
            name=f"API Documentation: {params['api_name']}",
            description="Comprehensive API documentation generation workflow"
        )
        
        # Set variables
        builder.set_variable("api_name", params["api_name"])
        builder.set_variable("api_version", params.get("api_version", "1.0"))
        builder.set_variable("endpoints_file", params["endpoints_file"])
        
        # Start
        builder.add_start("start")
        
        # Parse API specification
        builder.call_mcp(
            capability_category="analysis",
            service_parameters={
                "document_path": params["endpoints_file"],
                "analysis_type": "api_specification"
            },
            node_id="parse_api_spec"
        )
        
        # Generate documentation sections in parallel
        doc_sections = ["overview", "authentication", "endpoints", "examples", "errors"]
        branches = []
        
        for section in doc_sections:
            writer_id = f"spawn_writer_{section}"
            write_id = f"write_{section}"
            
            builder.spawn_agent(
                "technical_writer",
                role=f"Technical Writer - {section.title()}",
                instructions=f"Write {section} section for API documentation",
                tools=["WriteMemory", "ReadMemoryContext", "GenerateReleaseNotes"],
                node_id=writer_id
            )
            
            builder.execute_agent(
                task_description=f"Generate {section} documentation section",
                expected_outcome=f"Complete {section} documentation",
                node_id=write_id
            )
            
            builder.connect(writer_id, write_id)
            branches.append([writer_id, write_id])
            
        # Parallel documentation generation
        builder.add_parallel(
            branches=branches,
            join_strategy="wait_all",
            node_id="parallel_documentation"
        )
        
        # Compile final documentation
        builder.spawn_agent(
            "doc_compiler",
            role="Documentation Compiler",
            instructions="Compile all sections into final API documentation",
            tools=["WriteMemory", "ReadMemoryContext", "CallMCPTool"],
            node_id="spawn_compiler"
        )
        
        builder.execute_agent(
            task_description="Compile and format final API documentation",
            expected_outcome="Complete API documentation package",
            node_id="compile_docs"
        )
        
        # Quality review
        builder.add_human_approval(
            approval_message="API documentation complete. Please review and approve.",
            node_id="doc_review"
        )
        
        # End
        builder.add_end("end")
        
        # Connect workflow
        builder.connect("start", "parse_api_spec")
        builder.connect("parse_api_spec", "parallel_documentation")
        
        # Connect sections to parallel node
        for section in doc_sections:
            builder.connect("parse_api_spec", f"spawn_writer_{section}")
            
        builder.connect("parallel_documentation", "spawn_compiler")
        builder.connect("spawn_compiler", "compile_docs")
        builder.connect("compile_docs", "doc_review")
        builder.connect("doc_review", "end")
        
        return builder.build()


# Global template library instance
_template_library: Optional[TemplateLibrary] = None

def get_template_library() -> TemplateLibrary:
    """Get the global template library instance."""
    global _template_library
    if _template_library is None:
        _template_library = TemplateLibrary()
    return _template_library

# Convenience functions
def list_workflow_templates(category: Optional[str] = None) -> List[WorkflowTemplate]:
    """List available workflow templates."""
    library = get_template_library()
    return library.list_templates(category)

def get_workflow_template(template_id: str) -> Optional[WorkflowTemplate]:
    """Get a workflow template by ID."""
    library = get_template_library()
    return library.get_template(template_id)

def create_workflow_from_template(
    template_id: str,
    parameters: Dict[str, Any],
    name_override: Optional[str] = None
) -> WorkflowDefinition:
    """Create a workflow from a template."""
    library = get_template_library()
    return library.instantiate_template(template_id, parameters, name_override)

def get_template_categories() -> List[str]:
    """Get all available template categories."""
    library = get_template_library()
    return library.get_template_categories()
