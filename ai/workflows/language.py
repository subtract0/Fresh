"""Workflow Definition Language (WDL) - Parser and Builder System.

This module provides a comprehensive Workflow Definition Language that allows users
to define complex agent workflows as code. It supports conditions, loops, parallel
branches, error handling, dynamic agent spawning, and advanced workflow patterns.

Cross-references:
    - Workflow Types: ai/workflows/types.py for core data structures
    - Workflow Engine: ai/workflows/engine.py for execution logic
    - Agent Integration: ai/interface/agent_spawner.py for agent management
    - MCP Integration: ai/tools/enhanced_mcp.py for external service calls

Features:
    - Human-readable YAML/JSON workflow definitions
    - Programmatic workflow builder API
    - Template parameter substitution
    - Workflow validation and optimization
    - Import/export functionality
    - Visual workflow representation
"""
from __future__ import annotations
import yaml
import json
import re
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from dataclasses import asdict
from datetime import timedelta

from ai.workflows.types import (
    WorkflowDefinition, WorkflowNode, WorkflowEdge, WorkflowCondition, WorkflowVariable,
    AgentSpawnNode, AgentExecuteNode, ConditionNode, ParallelNode, LoopNode, 
    MCPCallNode, HumanApprovalNode, RetryConfig,
    NodeType, WorkflowStatus, ConditionOperator, RetryStrategy
)


class WorkflowSyntaxError(Exception):
    """Exception raised for syntax errors in workflow definitions."""
    def __init__(self, message: str, line: Optional[int] = None, context: Optional[str] = None):
        self.message = message
        self.line = line
        self.context = context
        super().__init__(self._format_message())
        
    def _format_message(self) -> str:
        msg = f"Workflow syntax error: {self.message}"
        if self.line:
            msg += f" (line {self.line})"
        if self.context:
            msg += f" in {self.context}"
        return msg


class WorkflowBuilder:
    """Builder class for creating workflow definitions programmatically."""
    
    def __init__(self, name: str, description: str = ""):
        self.workflow = WorkflowDefinition(
            workflow_id="",  # Will be set when building
            name=name,
            description=description
        )
        self._node_counter = 0
        
    def add_start(self, node_id: Optional[str] = None, **kwargs) -> 'WorkflowBuilder':
        """Add a start node to the workflow."""
        if node_id is None:
            node_id = self._next_node_id("start")
            
        node = WorkflowNode(
            node_id=node_id,
            node_type=NodeType.START,
            name="Start",
            description="Workflow start point",
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def add_end(self, node_id: Optional[str] = None, **kwargs) -> 'WorkflowBuilder':
        """Add an end node to the workflow."""
        if node_id is None:
            node_id = self._next_node_id("end")
            
        node = WorkflowNode(
            node_id=node_id,
            node_type=NodeType.END,
            name="End",
            description="Workflow end point",
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def spawn_agent(
        self,
        agent_type: str,
        role: str = "",
        instructions: str = "",
        tools: Optional[List[str]] = None,
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add an agent spawn node."""
        if node_id is None:
            node_id = self._next_node_id("spawn_agent")
            
        node = AgentSpawnNode(
            node_id=node_id,
            name=f"Spawn {agent_type}",
            description=f"Spawn agent of type {agent_type}",
            agent_type=agent_type,
            agent_role=role or agent_type,
            agent_instructions=instructions,
            tools=tools or [],
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def execute_agent(
        self,
        task_description: str,
        agent_id: Optional[str] = None,
        expected_outcome: str = "",
        evaluation_criteria: Optional[List[str]] = None,
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add an agent execution node."""
        if node_id is None:
            node_id = self._next_node_id("execute")
            
        node = AgentExecuteNode(
            node_id=node_id,
            name="Execute Task",
            description=task_description,
            agent_id=agent_id,
            task_description=task_description,
            expected_outcome=expected_outcome,
            evaluation_criteria=evaluation_criteria or [],
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def add_condition(
        self,
        conditions: List[WorkflowCondition],
        logic_operator: str = "AND",
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add a conditional branch node."""
        if node_id is None:
            node_id = self._next_node_id("condition")
            
        node = ConditionNode(
            node_id=node_id,
            name="Conditional Branch",
            description=f"Conditional execution with {logic_operator} logic",
            conditions=conditions,
            logic_operator=logic_operator,
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def add_parallel(
        self,
        branches: List[List[str]],
        join_strategy: str = "wait_all",
        max_concurrency: Optional[int] = None,
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add a parallel execution node."""
        if node_id is None:
            node_id = self._next_node_id("parallel")
            
        node = ParallelNode(
            node_id=node_id,
            name="Parallel Execution",
            description=f"Execute {len(branches)} branches in parallel",
            branches=branches,
            join_strategy=join_strategy,
            max_concurrency=max_concurrency,
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def add_loop(
        self,
        loop_type: str = "while",
        condition: Optional[WorkflowCondition] = None,
        loop_body: Optional[List[str]] = None,
        max_iterations: int = 100,
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add a loop node."""
        if node_id is None:
            node_id = self._next_node_id("loop")
            
        node = LoopNode(
            node_id=node_id,
            name=f"{loop_type.title()} Loop",
            description=f"Loop execution ({loop_type})",
            loop_type=loop_type,
            condition=condition,
            loop_body=loop_body or [],
            max_iterations=max_iterations,
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def call_mcp(
        self,
        capability_category: str,
        service_parameters: Optional[Dict[str, Any]] = None,
        server_selection: str = "auto",
        cache_results: bool = True,
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add an MCP service call node."""
        if node_id is None:
            node_id = self._next_node_id("mcp_call")
            
        node = MCPCallNode(
            node_id=node_id,
            name=f"MCP Call - {capability_category}",
            description=f"Call MCP service for {capability_category}",
            capability_category=capability_category,
            service_parameters=service_parameters or {},
            server_selection=server_selection,
            cache_results=cache_results,
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def add_human_approval(
        self,
        approval_message: str,
        approval_options: Optional[List[str]] = None,
        timeout_hours: int = 24,
        default_action: str = "reject",
        node_id: Optional[str] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add a human approval node."""
        if node_id is None:
            node_id = self._next_node_id("approval")
            
        node = HumanApprovalNode(
            node_id=node_id,
            name="Human Approval Required",
            description=approval_message,
            approval_message=approval_message,
            approval_options=approval_options or ["approve", "reject"],
            timeout=timedelta(hours=timeout_hours),
            default_action=default_action,
            **kwargs
        )
        self.workflow.add_node(node)
        return self
        
    def connect(
        self,
        from_node: str,
        to_node: str,
        condition: Optional[WorkflowCondition] = None
    ) -> 'WorkflowBuilder':
        """Connect two nodes with an edge."""
        self.workflow.connect(from_node, to_node, condition)
        return self
        
    def set_variable(self, name: str, value: Any, var_type: str = "string", description: str = "") -> 'WorkflowBuilder':
        """Set a default workflow variable."""
        variable = WorkflowVariable(
            name=name,
            value=value,
            type=var_type,
            description=description
        )
        self.workflow.default_variables[name] = variable
        return self
        
    def build(self, workflow_id: Optional[str] = None) -> WorkflowDefinition:
        """Build and validate the workflow definition."""
        import uuid
        
        if workflow_id:
            self.workflow.workflow_id = workflow_id
        else:
            self.workflow.workflow_id = str(uuid.uuid4())
            \n        # Validate the workflow
        errors = self.workflow.validate()
        if errors:
            raise WorkflowSyntaxError(f"Workflow validation failed: {'; '.join(errors)}")
            
        return self.workflow
        
    def _next_node_id(self, prefix: str) -> str:
        """Generate the next node ID with given prefix."""
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"


class WDLParser:
    """Parser for Workflow Definition Language (WDL) files."""
    
    def __init__(self):
        self.variables = {}  # For template parameter substitution
        
    def parse_file(self, file_path: Union[str, Path]) -> WorkflowDefinition:
        """Parse a WDL file and return a workflow definition."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")
            
        content = file_path.read_text(encoding='utf-8')
        
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            return self.parse_yaml(content)
        elif file_path.suffix.lower() == '.json':
            return self.parse_json(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
    def parse_yaml(self, yaml_content: str) -> WorkflowDefinition:
        """Parse YAML workflow definition."""
        try:
            data = yaml.safe_load(yaml_content)
            return self._parse_workflow_dict(data)
        except yaml.YAMLError as e:
            raise WorkflowSyntaxError(f"Invalid YAML: {str(e)}")
            
    def parse_json(self, json_content: str) -> WorkflowDefinition:
        """Parse JSON workflow definition."""
        try:
            data = json.loads(json_content)
            return self._parse_workflow_dict(data)
        except json.JSONDecodeError as e:
            raise WorkflowSyntaxError(f"Invalid JSON: {str(e)}")
            
    def _parse_workflow_dict(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """Parse workflow definition from dictionary."""
        if not isinstance(data, dict):
            raise WorkflowSyntaxError("Workflow definition must be a dictionary/object")
            
        # Required fields
        workflow_id = data.get('workflow_id', '')
        name = data.get('name', '')
        if not name:
            raise WorkflowSyntaxError("Workflow must have a 'name' field")
            
        description = data.get('description', '')
        
        # Create workflow definition
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            version=data.get('version', '1.0.0'),
            author=data.get('author', ''),
            tags=data.get('tags', [])
        )
        
        # Parse variables
        if 'variables' in data:
            for var_name, var_def in data['variables'].items():
                if isinstance(var_def, dict):
                    variable = WorkflowVariable(
                        name=var_name,
                        value=var_def.get('value'),
                        type=var_def.get('type', 'string'),
                        description=var_def.get('description', ''),
                        is_sensitive=var_def.get('sensitive', False)
                    )
                else:
                    variable = WorkflowVariable(
                        name=var_name,
                        value=var_def,
                        type=self._infer_type(var_def)
                    )
                workflow.default_variables[var_name] = variable
                
        # Parse nodes
        if 'nodes' in data:
            for node_data in data['nodes']:
                node = self._parse_node(node_data)
                workflow.add_node(node)
                
        # Parse edges/connections
        if 'edges' in data:
            for edge_data in data['edges']:
                edge = self._parse_edge(edge_data)
                workflow.add_edge(edge)
        elif 'connections' in data:
            # Alternative syntax
            for conn in data['connections']:
                from_node = conn.get('from')
                to_node = conn.get('to')
                condition = self._parse_condition(conn.get('condition')) if 'condition' in conn else None
                workflow.connect(from_node, to_node, condition)
                
        return workflow
        
    def _parse_node(self, node_data: Dict[str, Any]) -> WorkflowNode:
        """Parse a single node definition."""
        node_id = node_data.get('id', '')
        node_type = node_data.get('type', '')
        name = node_data.get('name', node_id)
        
        if not node_id:
            raise WorkflowSyntaxError("Node must have an 'id' field")
        if not node_type:
            raise WorkflowSyntaxError(f"Node '{node_id}' must have a 'type' field")
            
        # Parse common node properties
        description = node_data.get('description', '')
        timeout_seconds = node_data.get('timeout_seconds')
        timeout = timedelta(seconds=timeout_seconds) if timeout_seconds else None
        retry_config = self._parse_retry_config(node_data.get('retry')) if 'retry' in node_data else None
        skip_on_failure = node_data.get('skip_on_failure', False)
        parameters = node_data.get('parameters', {})
        input_mapping = node_data.get('input_mapping', {})
        output_mapping = node_data.get('output_mapping', {})
        depends_on = node_data.get('depends_on', [])
        tags = node_data.get('tags', [])
        metadata = node_data.get('metadata', {})
        
        # Create node based on type
        if node_type == 'start':
            return WorkflowNode(
                node_id=node_id,
                node_type=NodeType.START,
                name=name,
                description=description,
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'end':
            return WorkflowNode(
                node_id=node_id,
                node_type=NodeType.END,
                name=name,
                description=description,
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'spawn_agent':
            return AgentSpawnNode(
                node_id=node_id,
                name=name,
                description=description,
                agent_type=parameters.get('agent_type', ''),
                agent_role=parameters.get('role', ''),
                agent_instructions=parameters.get('instructions', ''),
                tools=parameters.get('tools', []),
                spawn_strategy=parameters.get('spawn_strategy', 'immediate'),
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'execute_agent':
            return AgentExecuteNode(
                node_id=node_id,
                name=name,
                description=description,
                agent_id=parameters.get('agent_id'),
                task_description=parameters.get('task_description', ''),
                expected_outcome=parameters.get('expected_outcome', ''),
                evaluation_criteria=parameters.get('evaluation_criteria', []),
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'condition':
            conditions = []
            if 'conditions' in parameters:
                for cond_data in parameters['conditions']:
                    conditions.append(self._parse_condition(cond_data))
                    
            return ConditionNode(
                node_id=node_id,
                name=name,
                description=description,
                conditions=conditions,
                logic_operator=parameters.get('logic_operator', 'AND'),
                true_path=parameters.get('true_path', []),
                false_path=parameters.get('false_path', []),
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'parallel':
            return ParallelNode(
                node_id=node_id,
                name=name,
                description=description,
                branches=parameters.get('branches', []),
                join_strategy=parameters.get('join_strategy', 'wait_all'),
                max_concurrency=parameters.get('max_concurrency'),
                branch_timeout=timedelta(seconds=parameters['branch_timeout_seconds']) if 'branch_timeout_seconds' in parameters else None,
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'loop':
            condition = None
            if 'condition' in parameters:
                condition = self._parse_condition(parameters['condition'])
                
            return LoopNode(
                node_id=node_id,
                name=name,
                description=description,
                loop_type=parameters.get('loop_type', 'while'),
                condition=condition,
                iteration_variable=parameters.get('iteration_variable', 'loop_index'),
                max_iterations=parameters.get('max_iterations', 100),
                loop_body=parameters.get('loop_body', []),
                start_value=parameters.get('start_value'),
                end_value=parameters.get('end_value'),
                step=parameters.get('step', 1),
                iterable_variable=parameters.get('iterable_variable'),
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'mcp_call':
            return MCPCallNode(
                node_id=node_id,
                name=name,
                description=description,
                server_selection=parameters.get('server_selection', 'auto'),
                capability_category=parameters.get('capability_category', ''),
                service_parameters=parameters.get('service_parameters', {}),
                fallback_servers=parameters.get('fallback_servers', []),
                cache_results=parameters.get('cache_results', True),
                timeout=timeout,
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        elif node_type == 'human_approval':
            approval_timeout = None
            if 'timeout_hours' in parameters:
                approval_timeout = timedelta(hours=parameters['timeout_hours'])
            elif 'timeout_minutes' in parameters:
                approval_timeout = timedelta(minutes=parameters['timeout_minutes'])
                
            return HumanApprovalNode(
                node_id=node_id,
                name=name,
                description=description,
                approval_message=parameters.get('approval_message', ''),
                approval_options=parameters.get('approval_options', ['approve', 'reject']),
                timeout=approval_timeout,
                default_action=parameters.get('default_action', 'reject'),
                notification_channels=parameters.get('notification_channels', []),
                retry_config=retry_config,
                skip_on_failure=skip_on_failure,
                parameters=parameters,
                input_mapping=input_mapping,
                output_mapping=output_mapping,
                depends_on=depends_on,
                tags=tags,
                metadata=metadata
            )
        else:
            raise WorkflowSyntaxError(f"Unknown node type: {node_type}")
            
    def _parse_condition(self, cond_data: Dict[str, Any]) -> WorkflowCondition:
        """Parse a workflow condition."""
        if isinstance(cond_data, str):
            # Simple string condition like "status == 'completed'"
            return self._parse_string_condition(cond_data)
            
        variable_name = cond_data.get('variable', cond_data.get('var', ''))
        operator_str = cond_data.get('operator', cond_data.get('op', ''))
        expected_value = cond_data.get('value', cond_data.get('expected', ''))
        description = cond_data.get('description', '')
        
        if not variable_name:
            raise WorkflowSyntaxError("Condition must specify a 'variable' field")
        if not operator_str:
            raise WorkflowSyntaxError("Condition must specify an 'operator' field")
            
        # Map operator string to enum
        operator_map = {
            '==': ConditionOperator.EQUALS,
            '!=': ConditionOperator.NOT_EQUALS,
            '>': ConditionOperator.GREATER_THAN,
            '<': ConditionOperator.LESS_THAN,
            '>=': ConditionOperator.GREATER_EQUAL,
            '<=': ConditionOperator.LESS_EQUAL,
            'contains': ConditionOperator.CONTAINS,
            'not_contains': ConditionOperator.NOT_CONTAINS,
            'regex': ConditionOperator.REGEX_MATCH,
            'exists': ConditionOperator.EXISTS,
            'not_exists': ConditionOperator.NOT_EXISTS
        }
        
        operator = operator_map.get(operator_str)
        if operator is None:
            raise WorkflowSyntaxError(f"Unknown condition operator: {operator_str}")
            
        return WorkflowCondition(
            variable_name=variable_name,
            operator=operator,
            expected_value=expected_value,
            description=description
        )
        
    def _parse_string_condition(self, condition_str: str) -> WorkflowCondition:
        """Parse a string-based condition like 'status == completed'."""
        # Simple regex-based parsing
        pattern = r'(\w+)\s*(==|!=|>=|<=|>|<|contains|not_contains|exists|not_exists)\s*(.+)?'
        match = re.match(pattern, condition_str.strip())
        
        if not match:
            raise WorkflowSyntaxError(f"Invalid condition syntax: {condition_str}")
            
        variable_name = match.group(1)
        operator_str = match.group(2)
        value_str = match.group(3)
        
        # Parse value
        expected_value = None
        if value_str:
            value_str = value_str.strip().strip('"').strip("'")
            # Try to parse as number or boolean
            if value_str.lower() in ['true', 'false']:
                expected_value = value_str.lower() == 'true'
            elif value_str.replace('.', '').replace('-', '').isdigit():
                expected_value = float(value_str) if '.' in value_str else int(value_str)
            else:
                expected_value = value_str
                
        return self._parse_condition({
            'variable': variable_name,
            'operator': operator_str,
            'value': expected_value
        })
        
    def _parse_edge(self, edge_data: Dict[str, Any]) -> WorkflowEdge:
        """Parse an edge definition."""
        edge_id = edge_data.get('id', '')
        from_node = edge_data.get('from', '')
        to_node = edge_data.get('to', '')
        
        if not from_node:
            raise WorkflowSyntaxError("Edge must specify 'from' node")
        if not to_node:
            raise WorkflowSyntaxError("Edge must specify 'to' node")
            
        if not edge_id:
            edge_id = f"{from_node}->{to_node}"
            
        condition = None
        if 'condition' in edge_data:
            condition = self._parse_condition(edge_data['condition'])
            
        return WorkflowEdge(
            edge_id=edge_id,
            from_node=from_node,
            to_node=to_node,
            condition=condition,
            weight=edge_data.get('weight', 1),
            metadata=edge_data.get('metadata', {})
        )
        
    def _parse_retry_config(self, retry_data: Dict[str, Any]) -> RetryConfig:
        """Parse retry configuration."""
        strategy_str = retry_data.get('strategy', 'none')
        strategy_map = {
            'none': RetryStrategy.NONE,
            'immediate': RetryStrategy.IMMEDIATE,
            'exponential_backoff': RetryStrategy.EXPONENTIAL_BACKOFF,
            'linear_backoff': RetryStrategy.LINEAR_BACKOFF,
            'custom': RetryStrategy.CUSTOM
        }
        
        strategy = strategy_map.get(strategy_str, RetryStrategy.NONE)
        
        return RetryConfig(
            strategy=strategy,
            max_attempts=retry_data.get('max_attempts', 3),
            initial_delay=timedelta(seconds=retry_data.get('initial_delay_seconds', 1)),
            max_delay=timedelta(seconds=retry_data.get('max_delay_seconds', 300)),
            backoff_multiplier=retry_data.get('backoff_multiplier', 2.0),
            retry_on_errors=retry_data.get('retry_on_errors', [])
        )
        
    def _infer_type(self, value: Any) -> str:
        """Infer the type of a value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"


class WDLExporter:
    """Exporter for converting workflow definitions to WDL format."""
    
    def export_to_yaml(self, workflow: WorkflowDefinition) -> str:
        """Export workflow definition to YAML format."""
        data = self._workflow_to_dict(workflow)
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
        
    def export_to_json(self, workflow: WorkflowDefinition, indent: int = 2) -> str:
        """Export workflow definition to JSON format."""
        data = self._workflow_to_dict(workflow)
        return json.dumps(data, indent=indent, default=self._json_serializer)
        
    def save_to_file(self, workflow: WorkflowDefinition, file_path: Union[str, Path]):
        """Save workflow definition to a file."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            content = self.export_to_yaml(workflow)
        elif file_path.suffix.lower() == '.json':
            content = self.export_to_json(workflow)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
        file_path.write_text(content, encoding='utf-8')
        
    def _workflow_to_dict(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Convert workflow definition to dictionary representation."""
        data = {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'description': workflow.description,
            'version': workflow.version,
            'author': workflow.author,
            'tags': workflow.tags
        }
        
        # Add variables
        if workflow.default_variables:
            data['variables'] = {}
            for var_name, var in workflow.default_variables.items():
                data['variables'][var_name] = {
                    'value': var.value,
                    'type': var.type,
                    'description': var.description,
                    'sensitive': var.is_sensitive
                }
                
        # Add nodes
        data['nodes'] = []
        for node in workflow.nodes.values():
            node_dict = self._node_to_dict(node)
            data['nodes'].append(node_dict)
            
        # Add connections
        data['connections'] = []
        for edge in workflow.edges:
            conn_dict = {
                'from': edge.from_node,
                'to': edge.to_node
            }
            if edge.condition:
                conn_dict['condition'] = self._condition_to_dict(edge.condition)
            if edge.weight != 1:
                conn_dict['weight'] = edge.weight
            if edge.metadata:
                conn_dict['metadata'] = edge.metadata
            data['connections'].append(conn_dict)
            
        return data
        
    def _node_to_dict(self, node: WorkflowNode) -> Dict[str, Any]:
        """Convert a node to dictionary representation."""
        node_dict = {
            'id': node.node_id,
            'type': node.node_type.value,
            'name': node.name,
            'description': node.description
        }
        
        if node.timeout:
            node_dict['timeout_seconds'] = int(node.timeout.total_seconds())
            
        if node.retry_config:
            node_dict['retry'] = self._retry_config_to_dict(node.retry_config)
            
        if node.skip_on_failure:
            node_dict['skip_on_failure'] = True
            
        if node.parameters:
            node_dict['parameters'] = node.parameters.copy()
            
        # Add type-specific parameters
        if isinstance(node, AgentSpawnNode):
            node_dict['parameters'].update({
                'agent_type': node.agent_type,
                'role': node.agent_role,
                'instructions': node.agent_instructions,
                'tools': node.tools,
                'spawn_strategy': node.spawn_strategy
            })
        elif isinstance(node, AgentExecuteNode):
            node_dict['parameters'].update({
                'agent_id': node.agent_id,
                'task_description': node.task_description,
                'expected_outcome': node.expected_outcome,
                'evaluation_criteria': node.evaluation_criteria
            })
        elif isinstance(node, ConditionNode):
            node_dict['parameters'].update({
                'conditions': [self._condition_to_dict(c) for c in node.conditions],
                'logic_operator': node.logic_operator,
                'true_path': node.true_path,
                'false_path': node.false_path
            })
        elif isinstance(node, ParallelNode):
            node_dict['parameters'].update({
                'branches': node.branches,
                'join_strategy': node.join_strategy,
                'max_concurrency': node.max_concurrency
            })
            if node.branch_timeout:
                node_dict['parameters']['branch_timeout_seconds'] = int(node.branch_timeout.total_seconds())
        elif isinstance(node, LoopNode):
            params = {
                'loop_type': node.loop_type,
                'iteration_variable': node.iteration_variable,
                'max_iterations': node.max_iterations,
                'loop_body': node.loop_body
            }
            if node.condition:
                params['condition'] = self._condition_to_dict(node.condition)
            if node.start_value is not None:
                params['start_value'] = node.start_value
            if node.end_value is not None:
                params['end_value'] = node.end_value
            if node.step != 1:
                params['step'] = node.step
            if node.iterable_variable:
                params['iterable_variable'] = node.iterable_variable
            node_dict['parameters'].update(params)
        elif isinstance(node, MCPCallNode):
            node_dict['parameters'].update({
                'server_selection': node.server_selection,
                'capability_category': node.capability_category,
                'service_parameters': node.service_parameters,
                'fallback_servers': node.fallback_servers,
                'cache_results': node.cache_results
            })
        elif isinstance(node, HumanApprovalNode):
            params = {
                'approval_message': node.approval_message,
                'approval_options': node.approval_options,
                'default_action': node.default_action,
                'notification_channels': node.notification_channels
            }
            if node.timeout:
                params['timeout_hours'] = node.timeout.total_seconds() / 3600
            node_dict['parameters'].update(params)
            
        if node.input_mapping:
            node_dict['input_mapping'] = node.input_mapping
        if node.output_mapping:
            node_dict['output_mapping'] = node.output_mapping
        if node.depends_on:
            node_dict['depends_on'] = node.depends_on
        if node.tags:
            node_dict['tags'] = node.tags
        if node.metadata:
            node_dict['metadata'] = node.metadata
            
        return node_dict
        
    def _condition_to_dict(self, condition: WorkflowCondition) -> Dict[str, Any]:
        """Convert a condition to dictionary representation."""
        return {
            'variable': condition.variable_name,
            'operator': condition.operator.value,
            'value': condition.expected_value,
            'description': condition.description
        }
        
    def _retry_config_to_dict(self, retry_config: RetryConfig) -> Dict[str, Any]:
        """Convert retry config to dictionary representation."""
        return {
            'strategy': retry_config.strategy.value,
            'max_attempts': retry_config.max_attempts,
            'initial_delay_seconds': int(retry_config.initial_delay.total_seconds()),
            'max_delay_seconds': int(retry_config.max_delay.total_seconds()),
            'backoff_multiplier': retry_config.backoff_multiplier,
            'retry_on_errors': retry_config.retry_on_errors
        }
        
    def _json_serializer(self, obj):
        """Custom JSON serializer for complex objects."""
        if isinstance(obj, timedelta):
            return int(obj.total_seconds())
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# Convenience functions for creating workflows
def create_workflow(name: str, description: str = "") -> WorkflowBuilder:
    """Create a new workflow builder."""
    return WorkflowBuilder(name, description)
    
def parse_workflow(content: str, format: str = "yaml") -> WorkflowDefinition:
    """Parse workflow definition from string content."""
    parser = WDLParser()
    if format.lower() == "yaml":
        return parser.parse_yaml(content)
    elif format.lower() == "json":
        return parser.parse_json(content)
    else:
        raise ValueError(f"Unsupported format: {format}")
        
def load_workflow(file_path: Union[str, Path]) -> WorkflowDefinition:
    """Load workflow definition from file."""
    parser = WDLParser()
    return parser.parse_file(file_path)
    
def save_workflow(workflow: WorkflowDefinition, file_path: Union[str, Path]):
    """Save workflow definition to file."""
    exporter = WDLExporter()
    exporter.save_to_file(workflow, file_path)
