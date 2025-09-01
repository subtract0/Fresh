"""Advanced Agent Workflow Orchestration System - Core Types and Models.

This module defines the foundational data types, models, and enums for the
Advanced Agent Workflow Orchestration System (AAWOS). It provides a comprehensive
framework for defining, executing, and monitoring complex multi-agent workflows.

Cross-references:
    - Workflow Engine: ai/workflows/engine.py for execution logic
    - Workflow Language: ai/workflows/language.py for WDL parsing
    - Agent Integration: ai/interface/agent_spawner.py for agent lifecycle
    - Memory System: ai/memory/README.md for workflow state persistence

Related:
    - Complex multi-step agent coordination
    - Conditional workflow execution with branching logic
    - Parallel execution with dependency management
    - Error recovery and alternative path execution
    - Dynamic workflow adaptation based on results
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ai.interface.agent_spawner import SpawnedAgent
from ai.integration.mcp_discovery import MCPDiscoverySystem


class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class NodeType(Enum):
    """Types of nodes in a workflow graph."""
    START = "start"
    END = "end"
    AGENT_SPAWN = "agent_spawn"
    AGENT_EXECUTE = "agent_execute"
    CONDITION = "condition"
    PARALLEL = "parallel"
    JOIN = "join"
    LOOP = "loop"
    MCP_CALL = "mcp_call"
    DELAY = "delay"
    WEBHOOK = "webhook"
    HUMAN_APPROVAL = "human_approval"
    DATA_TRANSFORM = "data_transform"


class ExecutionStrategy(Enum):
    """Strategies for executing workflow nodes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ADAPTIVE = "adaptive"


class RetryStrategy(Enum):
    """Retry strategies for failed workflow nodes."""
    NONE = "none"
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CUSTOM = "custom"


class ConditionOperator(Enum):
    """Operators for workflow conditions."""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX_MATCH = "regex_match"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


@dataclass
class WorkflowVariable:
    """Variable definition for workflow context."""
    name: str
    value: Any
    type: str  # "string", "number", "boolean", "object", "array"
    description: str = ""
    is_sensitive: bool = False
    source: Optional[str] = None  # Node ID that produced this variable


@dataclass
class WorkflowCondition:
    """Condition definition for conditional workflow execution."""
    variable_name: str
    operator: ConditionOperator
    expected_value: Any
    description: str = ""
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition against the workflow context."""
        actual_value = context.get(self.variable_name)
        
        if actual_value is None and self.operator not in [ConditionOperator.EXISTS, ConditionOperator.NOT_EXISTS]:
            return False
            
        try:
            if self.operator == ConditionOperator.EQUALS:
                return actual_value == self.expected_value
            elif self.operator == ConditionOperator.NOT_EQUALS:
                return actual_value != self.expected_value
            elif self.operator == ConditionOperator.GREATER_THAN:
                return float(actual_value) > float(self.expected_value)
            elif self.operator == ConditionOperator.LESS_THAN:
                return float(actual_value) < float(self.expected_value)
            elif self.operator == ConditionOperator.GREATER_EQUAL:
                return float(actual_value) >= float(self.expected_value)
            elif self.operator == ConditionOperator.LESS_EQUAL:
                return float(actual_value) <= float(self.expected_value)
            elif self.operator == ConditionOperator.CONTAINS:
                return str(self.expected_value) in str(actual_value)
            elif self.operator == ConditionOperator.NOT_CONTAINS:
                return str(self.expected_value) not in str(actual_value)
            elif self.operator == ConditionOperator.EXISTS:
                return actual_value is not None
            elif self.operator == ConditionOperator.NOT_EXISTS:
                return actual_value is None
            elif self.operator == ConditionOperator.REGEX_MATCH:
                import re
                return bool(re.match(str(self.expected_value), str(actual_value)))
                
        except (ValueError, TypeError):
            return False
            
        return False


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    strategy: RetryStrategy
    max_attempts: int = 3
    initial_delay: timedelta = field(default_factory=lambda: timedelta(seconds=1))
    max_delay: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    backoff_multiplier: float = 2.0
    retry_on_errors: List[str] = field(default_factory=list)  # Error types to retry on
    custom_handler: Optional[Callable] = None


@dataclass
class WorkflowEdge:
    """Edge connecting two workflow nodes."""
    edge_id: str
    from_node: str
    to_node: str
    condition: Optional[WorkflowCondition] = None
    weight: int = 1  # For prioritization in parallel branches
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowNode:
    """Base workflow node definition."""
    node_id: str
    node_type: NodeType
    name: str
    description: str = ""
    
    # Execution configuration
    timeout: Optional[timedelta] = None
    retry_config: Optional[RetryConfig] = None
    skip_on_failure: bool = False
    
    # Node-specific parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Input/output mapping
    input_mapping: Dict[str, str] = field(default_factory=dict)  # parameter -> variable
    output_mapping: Dict[str, str] = field(default_factory=dict)  # result_key -> variable
    
    # Dependencies and scheduling
    depends_on: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSpawnNode(WorkflowNode):
    """Node for spawning new agents during workflow execution."""
    agent_type: str = ""
    agent_role: str = ""
    agent_instructions: str = ""
    tools: List[str] = field(default_factory=list)
    spawn_strategy: str = "immediate"  # immediate, lazy, on_demand
    
    def __post_init__(self):
        self.node_type = NodeType.AGENT_SPAWN


@dataclass
class AgentExecuteNode(WorkflowNode):
    """Node for executing tasks with spawned agents."""
    agent_id: Optional[str] = None  # If None, uses agent from context
    task_description: str = ""
    expected_outcome: str = ""
    evaluation_criteria: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.node_type = NodeType.AGENT_EXECUTE


@dataclass
class ConditionNode(WorkflowNode):
    """Node for conditional workflow branching."""
    conditions: List[WorkflowCondition] = field(default_factory=list)
    logic_operator: str = "AND"  # AND, OR, XOR
    true_path: List[str] = field(default_factory=list)  # Node IDs for true branch
    false_path: List[str] = field(default_factory=list)  # Node IDs for false branch
    
    def __post_init__(self):
        self.node_type = NodeType.CONDITION
        
    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions based on logic operator."""
        if not self.conditions:
            return True
            
        results = [condition.evaluate(context) for condition in self.conditions]
        
        if self.logic_operator == "AND":
            return all(results)
        elif self.logic_operator == "OR":
            return any(results)
        elif self.logic_operator == "XOR":
            return sum(results) == 1
            
        return False


@dataclass
class ParallelNode(WorkflowNode):
    """Node for parallel execution of multiple branches."""
    branches: List[List[str]] = field(default_factory=list)  # Lists of node IDs
    join_strategy: str = "wait_all"  # wait_all, wait_any, wait_first, no_wait
    max_concurrency: Optional[int] = None
    branch_timeout: Optional[timedelta] = None
    
    def __post_init__(self):
        self.node_type = NodeType.PARALLEL


@dataclass
class LoopNode(WorkflowNode):
    """Node for loop execution with various loop types."""
    loop_type: str = "while"  # while, for, foreach
    condition: Optional[WorkflowCondition] = None
    iteration_variable: str = "loop_index"
    max_iterations: int = 100
    loop_body: List[str] = field(default_factory=list)  # Node IDs in loop body
    
    # For 'for' loops
    start_value: Optional[int] = None
    end_value: Optional[int] = None
    step: int = 1
    
    # For 'foreach' loops  
    iterable_variable: Optional[str] = None
    
    def __post_init__(self):
        self.node_type = NodeType.LOOP


@dataclass
class MCPCallNode(WorkflowNode):
    """Node for calling MCP (Model Context Protocol) services."""
    server_selection: str = "auto"  # auto, specific, best_performance
    capability_category: str = ""
    service_parameters: Dict[str, Any] = field(default_factory=dict)
    fallback_servers: List[str] = field(default_factory=list)
    cache_results: bool = True
    
    def __post_init__(self):
        self.node_type = NodeType.MCP_CALL


@dataclass
class HumanApprovalNode(WorkflowNode):
    """Node for human approval/intervention in workflow."""
    approval_message: str = ""
    approval_options: List[str] = field(default_factory=lambda: ["approve", "reject"])
    timeout: Optional[timedelta] = field(default_factory=lambda: timedelta(hours=24))
    default_action: str = "reject"
    notification_channels: List[str] = field(default_factory=list)  # email, telegram, etc.
    
    def __post_init__(self):
        self.node_type = NodeType.HUMAN_APPROVAL


@dataclass
class NodeExecution:
    """Runtime execution state for a workflow node."""
    execution_id: str
    node_id: str
    status: WorkflowStatus
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    attempt_count: int = 0
    max_attempts: int = 1
    
    # Execution results
    result: Any = None
    error: Optional[str] = None
    output_variables: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime context
    agent_id: Optional[str] = None
    execution_logs: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete definition of a workflow."""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0.0"
    
    # Workflow structure
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    edges: List[WorkflowEdge] = field(default_factory=list)
    
    # Workflow configuration
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    default_variables: Dict[str, WorkflowVariable] = field(default_factory=dict)
    
    # Execution settings
    timeout: Optional[timedelta] = None
    max_parallel_nodes: int = 10
    retry_policy: Optional[RetryConfig] = None
    
    # Metadata
    author: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_node(self, node: WorkflowNode) -> 'WorkflowDefinition':
        """Add a node to the workflow."""
        self.nodes[node.node_id] = node
        self.updated_at = datetime.now()
        return self
        
    def add_edge(self, edge: WorkflowEdge) -> 'WorkflowDefinition':
        """Add an edge to the workflow."""
        self.edges.append(edge)
        self.updated_at = datetime.now()
        return self
        
    def connect(self, from_node: str, to_node: str, condition: Optional[WorkflowCondition] = None) -> 'WorkflowDefinition':
        """Convenience method to connect two nodes."""
        edge_id = f"{from_node}->{to_node}"
        edge = WorkflowEdge(
            edge_id=edge_id,
            from_node=from_node,
            to_node=to_node,
            condition=condition
        )
        return self.add_edge(edge)
        
    def validate(self) -> List[str]:
        """Validate the workflow definition and return any errors."""
        errors = []
        
        # Check for start and end nodes
        start_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.START]
        end_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.END]
        
        if not start_nodes:
            errors.append("Workflow must have at least one START node")
        if not end_nodes:
            errors.append("Workflow must have at least one END node")
            
        # Check edge references
        node_ids = set(self.nodes.keys())
        for edge in self.edges:
            if edge.from_node not in node_ids:
                errors.append(f"Edge references unknown from_node: {edge.from_node}")
            if edge.to_node not in node_ids:
                errors.append(f"Edge references unknown to_node: {edge.to_node}")
                
        # Check for cycles (basic detection)
        # TODO: Implement more sophisticated cycle detection
        
        # Check dependencies
        for node in self.nodes.values():
            for dep in node.depends_on:
                if dep not in node_ids:
                    errors.append(f"Node {node.node_id} depends on unknown node: {dep}")
                    
        return errors


@dataclass
class WorkflowExecution:
    """Runtime execution state of a workflow."""
    execution_id: str
    workflow_id: str
    workflow_definition: WorkflowDefinition
    
    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    current_nodes: Set[str] = field(default_factory=set)
    
    # Runtime context
    variables: Dict[str, Any] = field(default_factory=dict)
    node_executions: Dict[str, NodeExecution] = field(default_factory=dict)
    spawned_agents: Dict[str, SpawnedAgent] = field(default_factory=dict)
    
    # Execution tracking
    completed_nodes: Set[str] = field(default_factory=set)
    failed_nodes: Set[str] = field(default_factory=set)
    execution_log: List[str] = field(default_factory=list)
    
    # User context
    user_id: Optional[str] = None
    trigger_source: str = "manual"  # manual, api, schedule, webhook
    
    def add_log(self, message: str, level: str = "info"):
        """Add an entry to the execution log."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        self.execution_log.append(log_entry)
        
    def set_variable(self, name: str, value: Any, source: Optional[str] = None):
        """Set a workflow variable."""
        self.variables[name] = value
        self.add_log(f"Set variable '{name}' = {repr(value)[:100]}")
        
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a workflow variable."""
        return self.variables.get(name, default)
        
    def mark_node_completed(self, node_id: str, result: Any = None):
        """Mark a node as completed."""
        self.completed_nodes.add(node_id)
        self.current_nodes.discard(node_id)
        
        if node_id in self.node_executions:
            self.node_executions[node_id].status = WorkflowStatus.COMPLETED
            self.node_executions[node_id].end_time = datetime.now()
            self.node_executions[node_id].result = result
            
        self.add_log(f"Node '{node_id}' completed")
        
    def mark_node_failed(self, node_id: str, error: str):
        """Mark a node as failed."""
        self.failed_nodes.add(node_id)
        self.current_nodes.discard(node_id)
        
        if node_id in self.node_executions:
            self.node_executions[node_id].status = WorkflowStatus.FAILED
            self.node_executions[node_id].end_time = datetime.now()
            self.node_executions[node_id].error = error
            
        self.add_log(f"Node '{node_id}' failed: {error}", level="error")
        
    def calculate_progress(self) -> float:
        """Calculate workflow execution progress as percentage."""
        total_nodes = len(self.workflow_definition.nodes)
        if total_nodes == 0:
            return 100.0
            
        completed_count = len(self.completed_nodes)
        return (completed_count / total_nodes) * 100.0
        
    def is_completed(self) -> bool:
        """Check if workflow execution is completed."""
        end_nodes = [n for n in self.workflow_definition.nodes.values() 
                    if n.node_type == NodeType.END]
        return any(node.node_id in self.completed_nodes for node in end_nodes)
        
    def has_failed(self) -> bool:
        """Check if workflow execution has failed."""
        return bool(self.failed_nodes) and not self.current_nodes


@dataclass
class WorkflowTemplate:
    """Template for creating workflow definitions."""
    template_id: str
    name: str
    description: str
    category: str  # development, research, analysis, documentation, etc.
    
    # Template parameters
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # name -> {type, default, description}
    
    # Template definition (can contain parameter placeholders)
    template_definition: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    author: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def instantiate(self, parameters: Dict[str, Any]) -> WorkflowDefinition:
        """Create a workflow definition from this template with given parameters."""
        # This would involve parameter substitution in the template definition
        # Implementation would parse the template and replace placeholders
        # For now, return a basic workflow
        workflow_id = str(uuid.uuid4())
        return WorkflowDefinition(
            workflow_id=workflow_id,
            name=f"{self.name} - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"Instantiated from template: {self.name}",
            metadata={"template_id": self.template_id, "parameters": parameters}
        )
