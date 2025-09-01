"""Advanced Agent Workflow Orchestration System (AAWOS) - Main Module.

This module provides the main entry point for the Advanced Agent Workflow
Orchestration System, bringing together all components for comprehensive
workflow management and execution.

Cross-references:
    - Workflow Types: ai/workflows/types.py for core data structures
    - Workflow Language: ai/workflows/language.py for WDL
    - Workflow Engine: ai/workflows/engine.py for execution
    - Workflow Templates: ai/workflows/templates.py for common patterns
    - Enhanced MCP: ai/tools/enhanced_mcp.py for external services
    - Agent System: ai/interface/agent_spawner.py for agent coordination

Features:
    - Complete workflow lifecycle management
    - Template-based workflow creation
    - Real-time execution monitoring
    - Advanced error recovery and adaptation
    - Integration with agent spawning and MCP services
    - Comprehensive testing and validation
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Union

# Core Types
from ai.workflows.types import (
    WorkflowDefinition, WorkflowExecution, WorkflowTemplate,
    WorkflowNode, WorkflowEdge, WorkflowCondition, WorkflowVariable,
    WorkflowStatus, NodeType, ExecutionStrategy, RetryStrategy,
    AgentSpawnNode, AgentExecuteNode, ConditionNode, ParallelNode,
    LoopNode, MCPCallNode, HumanApprovalNode
)

# Language Support
from ai.workflows.language import (
    WorkflowBuilder, WDLParser, WDLExporter, WorkflowSyntaxError,
    create_workflow, parse_workflow, load_workflow, save_workflow
)

# Execution Engine
from ai.workflows.engine import (
    WorkflowExecutionEngine, WorkflowExecutionError, NodeExecutionError,
    get_workflow_engine
)

# Template Library
from ai.workflows.templates import (
    TemplateLibrary, get_template_library,
    list_workflow_templates, get_workflow_template,
    create_workflow_from_template, get_template_categories
)

__version__ = "1.0.0"
__author__ = "Fresh Agent System"

# Main API Classes
__all__ = [
    # Core Types
    "WorkflowDefinition", "WorkflowExecution", "WorkflowTemplate",
    "WorkflowNode", "WorkflowEdge", "WorkflowCondition", "WorkflowVariable",
    "WorkflowStatus", "NodeType", "ExecutionStrategy", "RetryStrategy",
    "AgentSpawnNode", "AgentExecuteNode", "ConditionNode", "ParallelNode",
    "LoopNode", "MCPCallNode", "HumanApprovalNode",
    
    # Language Support
    "WorkflowBuilder", "WDLParser", "WDLExporter", "WorkflowSyntaxError",
    "create_workflow", "parse_workflow", "load_workflow", "save_workflow",
    
    # Execution Engine
    "WorkflowExecutionEngine", "WorkflowExecutionError", "NodeExecutionError",
    "get_workflow_engine",
    
    # Template Library
    "TemplateLibrary", "get_template_library",
    "list_workflow_templates", "get_workflow_template", 
    "create_workflow_from_template", "get_template_categories",
    
    # Main API
    "WorkflowOrchestrator"
]


class WorkflowOrchestrator:
    """Main orchestrator for the Advanced Agent Workflow System.
    
    This class provides a high-level interface for creating, managing,
    and executing workflows with full integration of all AAWOS components.
    """
    
    def __init__(self):
        self.engine = get_workflow_engine()
        self.template_library = get_template_library()
        self.parser = WDLParser()
        self.exporter = WDLExporter()
        
    async def initialize(self):
        """Initialize the workflow orchestration system."""
        await self.engine.start_engine()
        
    async def shutdown(self):
        """Shutdown the workflow orchestration system."""
        await self.engine.stop_engine()
        
    # Workflow Creation
    def create_workflow_builder(self, name: str, description: str = "") -> WorkflowBuilder:
        """Create a new workflow builder."""
        return create_workflow(name, description)
        
    def load_workflow_from_file(self, file_path: str) -> WorkflowDefinition:
        """Load a workflow from a file."""
        return load_workflow(file_path)
        
    def parse_workflow_from_string(self, content: str, format: str = "yaml") -> WorkflowDefinition:
        """Parse a workflow from string content."""
        return parse_workflow(content, format)
        
    def save_workflow_to_file(self, workflow: WorkflowDefinition, file_path: str):
        """Save a workflow to a file."""
        save_workflow(workflow, file_path)
        
    # Template Management
    def list_templates(self, category: Optional[str] = None) -> List[WorkflowTemplate]:
        """List available workflow templates."""
        return list_workflow_templates(category)
        
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by ID."""
        return get_workflow_template(template_id)
        
    def create_from_template(
        self, 
        template_id: str, 
        parameters: Dict[str, Any],
        name_override: Optional[str] = None
    ) -> WorkflowDefinition:
        """Create a workflow from a template."""
        return create_workflow_from_template(template_id, parameters, name_override)
        
    def get_template_categories(self) -> List[str]:
        """Get all available template categories."""
        return get_template_categories()
        
    # Workflow Execution
    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        initial_variables: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        trigger_source: str = "orchestrator"
    ) -> str:
        """Execute a workflow and return execution ID."""
        return await self.engine.execute_workflow(
            workflow, initial_variables, user_id, trigger_source
        )
        
    async def execute_template(
        self,
        template_id: str,
        parameters: Dict[str, Any],
        initial_variables: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Execute a workflow from a template."""
        workflow = self.create_from_template(template_id, parameters)
        return await self.execute_workflow(workflow, initial_variables, user_id)
        
    # Execution Management
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution."""
        return self.engine.get_execution_status(execution_id)
        
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        return await self.engine.cancel_execution(execution_id)
        
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause a running workflow execution."""
        return await self.engine.pause_execution(execution_id)
        
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused workflow execution."""
        return await self.engine.resume_execution(execution_id)
        
    def get_execution_log(self, execution_id: str, limit: int = 100) -> List[str]:
        """Get the execution log for a workflow."""
        return self.engine.get_execution_log(execution_id, limit)
        
    # System Information
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        engine_metrics = self.engine.get_engine_metrics()
        template_metrics = {
            "total_templates": len(self.template_library.templates),
            "template_categories": len(self.template_library.get_template_categories()),
            "templates_by_category": {
                category: len(self.template_library.list_templates(category))
                for category in self.template_library.get_template_categories()
            }
        }
        
        return {
            "engine": engine_metrics,
            "templates": template_metrics,
            "version": __version__
        }
        
    # Validation and Testing
    def validate_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """Validate a workflow definition."""
        return workflow.validate()
        
    def test_workflow_syntax(self, workflow_content: str, format: str = "yaml") -> Dict[str, Any]:
        """Test workflow syntax and return validation results."""
        try:
            workflow = self.parse_workflow_from_string(workflow_content, format)
            errors = self.validate_workflow(workflow)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.name,
                "node_count": len(workflow.nodes),
                "edge_count": len(workflow.edges)
            }
        except WorkflowSyntaxError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "workflow_id": None,
                "workflow_name": None,
                "node_count": 0,
                "edge_count": 0
            }
            
    # Workflow Export
    def export_workflow_to_yaml(self, workflow: WorkflowDefinition) -> str:
        """Export workflow to YAML format."""
        return self.exporter.export_to_yaml(workflow)
        
    def export_workflow_to_json(self, workflow: WorkflowDefinition, indent: int = 2) -> str:
        """Export workflow to JSON format."""
        return self.exporter.export_to_json(workflow, indent)


# Convenience functions for quick access
async def create_orchestrator() -> WorkflowOrchestrator:
    """Create and initialize a workflow orchestrator."""
    orchestrator = WorkflowOrchestrator()
    await orchestrator.initialize()
    return orchestrator

def quick_workflow(name: str, description: str = "") -> WorkflowBuilder:
    """Create a workflow builder quickly."""
    return create_workflow(name, description)

async def execute_simple_workflow(
    workflow_definition: Union[WorkflowDefinition, str, Dict[str, Any]],
    variables: Optional[Dict[str, Any]] = None
) -> str:
    """Execute a simple workflow with minimal setup."""
    orchestrator = await create_orchestrator()
    
    if isinstance(workflow_definition, str):
        workflow = orchestrator.parse_workflow_from_string(workflow_definition)
    elif isinstance(workflow_definition, dict):
        import json
        workflow = orchestrator.parse_workflow_from_string(json.dumps(workflow_definition), "json")
    else:
        workflow = workflow_definition
        
    return await orchestrator.execute_workflow(workflow, variables)
