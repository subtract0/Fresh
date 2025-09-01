"""Advanced Workflow Execution Engine - Core Runtime System.

This module implements a robust execution engine for the Advanced Agent Workflow
Orchestration System (AAWOS). It provides sophisticated workflow execution with
real-time monitoring, dependency management, error recovery, and intelligent
coordination of agents and external services.

Cross-references:
    - Workflow Types: ai/workflows/types.py for data structures  
    - Workflow Language: ai/workflows/language.py for WDL parsing
    - Agent System: ai/interface/agent_spawner.py for agent management
    - MCP Integration: ai/tools/enhanced_mcp.py for external services
    - Memory System: ai/memory/store.py for state persistence

Features:
    - Real-time workflow execution with dependency resolution
    - Parallel and conditional execution strategies
    - Advanced error recovery and retry mechanisms
    - Dynamic workflow adaptation based on results
    - Comprehensive monitoring and status reporting
    - Integration with agent spawning and MCP services
"""
from __future__ import annotations
import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable, Union
from collections import defaultdict, deque
from dataclasses import replace
import threading

from ai.workflows.types import (
    WorkflowDefinition, WorkflowExecution, WorkflowNode, NodeExecution,
    WorkflowStatus, NodeType, ExecutionStrategy, RetryStrategy,
    AgentSpawnNode, AgentExecuteNode, ConditionNode, ParallelNode, 
    LoopNode, MCPCallNode, HumanApprovalNode, WorkflowCondition
)
from ai.interface.agent_spawner import SpawnedAgent, get_agent_spawner
from ai.tools.enhanced_mcp import EnhancedMCPTool
from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

logger = logging.getLogger(__name__)


class WorkflowExecutionError(Exception):
    """Exception raised during workflow execution."""
    pass


class WorkflowTimeoutError(WorkflowExecutionError):
    """Exception raised when workflow execution times out."""
    pass


class NodeExecutionError(WorkflowExecutionError):
    """Exception raised when a specific node fails execution."""
    def __init__(self, message: str, node_id: str, retry_possible: bool = True):
        self.node_id = node_id
        self.retry_possible = retry_possible
        super().__init__(message)


class WorkflowExecutionEngine:
    """Advanced execution engine for agent workflows."""
    
    def __init__(self):
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.node_executors: Dict[NodeType, Callable] = {}
        self.max_parallel_executions = 10
        self._shutdown_event = asyncio.Event()
        
        # Performance tracking
        self.execution_metrics: Dict[str, Dict[str, Any]] = {}
        self.node_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Background task management
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Initialize node executors
        self._initialize_node_executors()
        
    def _initialize_node_executors(self):
        """Initialize the mapping of node types to execution methods."""
        self.node_executors = {
            NodeType.START: self._execute_start_node,
            NodeType.END: self._execute_end_node,
            NodeType.AGENT_SPAWN: self._execute_agent_spawn_node,
            NodeType.AGENT_EXECUTE: self._execute_agent_execute_node,
            NodeType.CONDITION: self._execute_condition_node,
            NodeType.PARALLEL: self._execute_parallel_node,
            NodeType.LOOP: self._execute_loop_node,
            NodeType.MCP_CALL: self._execute_mcp_call_node,
            NodeType.HUMAN_APPROVAL: self._execute_human_approval_node,
            NodeType.DATA_TRANSFORM: self._execute_data_transform_node,
            NodeType.DELAY: self._execute_delay_node
        }
        
    async def start_engine(self):
        """Start the workflow execution engine."""
        logger.info("Starting workflow execution engine")
        
        # Start background monitoring tasks
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Workflow execution engine started")
        
    async def stop_engine(self):
        """Stop the workflow execution engine."""
        logger.info("Stopping workflow execution engine")
        
        self._shutdown_event.set()
        
        # Cancel all active executions
        for execution in list(self.active_executions.values()):
            await self.cancel_execution(execution.execution_id)
            
        # Stop background tasks
        for task in [self._monitoring_task, self._cleanup_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        logger.info("Workflow execution engine stopped")
        
    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        initial_variables: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        trigger_source: str = "api"
    ) -> str:
        """Start execution of a workflow and return execution ID."""
        execution_id = str(uuid.uuid4())
        
        # Create workflow execution context
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow.workflow_id,
            workflow_definition=workflow,
            user_id=user_id,
            trigger_source=trigger_source
        )
        
        # Set initial variables
        if initial_variables:
            execution.variables.update(initial_variables)
            
        # Set default variables from workflow definition
        for var_name, var_def in workflow.default_variables.items():
            if var_name not in execution.variables:
                execution.variables[var_name] = var_def.value
                
        # Store execution
        self.active_executions[execution_id] = execution
        
        # Record in memory
        WriteMemory(
            content=f"Started workflow execution: {workflow.name} (ID: {execution_id})",
            tags=["workflow", "execution", "start", workflow.workflow_id]
        ).run()
        
        # Start async execution
        asyncio.create_task(self._execute_workflow_async(execution))
        
        logger.info(f"Started workflow execution: {execution_id}")
        return execution_id
        
    async def _execute_workflow_async(self, execution: WorkflowExecution):
        """Execute a workflow asynchronously."""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.add_log(f"Starting workflow execution: {execution.workflow_definition.name}")
            
            # Find start nodes
            start_nodes = [
                node for node in execution.workflow_definition.nodes.values()
                if node.node_type == NodeType.START
            ]
            
            if not start_nodes:
                raise WorkflowExecutionError("Workflow has no start nodes")
                
            # Initialize execution for start nodes
            for start_node in start_nodes:
                await self._schedule_node_execution(execution, start_node.node_id)
                
            # Main execution loop
            await self._execution_loop(execution)
            
            # Determine final status
            if execution.is_completed():
                execution.status = WorkflowStatus.COMPLETED
                execution.end_time = datetime.now()
                execution.add_log("Workflow completed successfully")
            elif execution.has_failed():
                execution.status = WorkflowStatus.FAILED
                execution.end_time = datetime.now()
                execution.add_log("Workflow failed", level="error")
            else:
                execution.status = WorkflowStatus.CANCELLED
                execution.end_time = datetime.now()
                execution.add_log("Workflow was cancelled")
                
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.add_log(f"Workflow execution failed: {str(e)}", level="error")
            logger.error(f"Workflow execution failed: {e}")
            
        finally:
            # Record completion in memory
            WriteMemory(
                content=f"Workflow execution completed: {execution.workflow_definition.name} - Status: {execution.status.value}",
                tags=["workflow", "execution", "complete", execution.workflow_id, execution.status.value]
            ).run()
            
            # Notify callbacks
            await self._notify_execution_callbacks(execution)
            
    async def _execution_loop(self, execution: WorkflowExecution):
        """Main execution loop for processing workflow nodes."""
        max_iterations = 10000  # Prevent infinite loops
        iteration = 0
        
        while (execution.current_nodes and 
               execution.status == WorkflowStatus.RUNNING and 
               iteration < max_iterations):
            
            iteration += 1
            
            # Process all ready nodes
            ready_nodes = await self._get_ready_nodes(execution)
            
            if not ready_nodes:
                # Check if we're waiting for async operations
                if execution.current_nodes:
                    await asyncio.sleep(0.1)  # Brief pause
                    continue
                else:
                    break
                    
            # Execute ready nodes (respecting parallelism limits)
            await self._execute_ready_nodes(execution, ready_nodes)
            
            # Brief pause to prevent CPU spinning
            await asyncio.sleep(0.01)
            
        if iteration >= max_iterations:
            raise WorkflowExecutionError("Workflow execution exceeded maximum iterations")
            
    async def _get_ready_nodes(self, execution: WorkflowExecution) -> List[str]:
        """Get list of nodes that are ready for execution."""
        ready_nodes = []
        
        for node_id in execution.current_nodes:
            node = execution.workflow_definition.nodes.get(node_id)
            if not node:
                continue
                
            # Check if node is already being executed
            node_exec = execution.node_executions.get(node_id)
            if node_exec and node_exec.status == WorkflowStatus.RUNNING:
                continue
                
            # Check dependencies
            if await self._are_dependencies_satisfied(execution, node):
                ready_nodes.append(node_id)
                
        return ready_nodes
        
    async def _are_dependencies_satisfied(self, execution: WorkflowExecution, node: WorkflowNode) -> bool:
        """Check if all dependencies for a node are satisfied."""
        # Check explicit dependencies
        for dep_id in node.depends_on:
            if dep_id not in execution.completed_nodes:
                return False
                
        # Check incoming edges with conditions
        for edge in execution.workflow_definition.edges:
            if edge.to_node == node.node_id:
                # Source node must be completed
                if edge.from_node not in execution.completed_nodes:
                    return False
                    
                # Check edge condition if present
                if edge.condition:
                    if not edge.condition.evaluate(execution.variables):
                        return False
                        
        return True
        
    async def _execute_ready_nodes(self, execution: WorkflowExecution, ready_nodes: List[str]):
        """Execute all ready nodes, respecting parallelism limits."""
        # Limit parallel execution
        max_parallel = min(len(ready_nodes), self.max_parallel_executions)
        
        # Create execution tasks
        tasks = []
        for node_id in ready_nodes[:max_parallel]:
            task = asyncio.create_task(self._execute_node(execution, node_id))
            tasks.append(task)
            
        if tasks:
            # Wait for at least one task to complete
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # Cancel remaining pending tasks if needed (for immediate failure handling)
            for task in pending:
                if not task.done():
                    task.cancel()
                    
    async def _execute_node(self, execution: WorkflowExecution, node_id: str):
        """Execute a single workflow node."""
        node = execution.workflow_definition.nodes.get(node_id)
        if not node:
            execution.add_log(f"Node not found: {node_id}", level="error")
            return
            
        # Create node execution context
        node_execution = NodeExecution(
            execution_id=str(uuid.uuid4()),
            node_id=node_id,
            status=WorkflowStatus.RUNNING
        )
        execution.node_executions[node_id] = node_execution
        
        execution.add_log(f"Starting execution of node: {node_id} ({node.node_type.value})")
        
        try:
            # Apply input mapping
            await self._apply_input_mapping(execution, node)
            
            # Get executor for node type
            executor = self.node_executors.get(node.node_type)
            if not executor:
                raise NodeExecutionError(f"No executor found for node type: {node.node_type}", node_id)
                
            # Execute node with timeout
            start_time = time.time()
            
            if node.timeout:
                result = await asyncio.wait_for(
                    executor(execution, node),
                    timeout=node.timeout.total_seconds()
                )
            else:
                result = await executor(execution, node)
                
            execution_time = time.time() - start_time
            
            # Apply output mapping
            await self._apply_output_mapping(execution, node, result)
            
            # Mark node as completed
            execution.mark_node_completed(node_id, result)
            
            # Record performance
            self.node_performance[node.node_type.value].append(execution_time)
            
            # Schedule next nodes
            await self._schedule_next_nodes(execution, node_id)
            
        except asyncio.TimeoutError:
            error_msg = f"Node {node_id} timed out"
            execution.mark_node_failed(node_id, error_msg)
            await self._handle_node_failure(execution, node, error_msg)
            
        except NodeExecutionError as e:
            execution.mark_node_failed(node_id, str(e))
            await self._handle_node_failure(execution, node, str(e))
            
        except Exception as e:
            error_msg = f"Unexpected error in node {node_id}: {str(e)}"
            execution.mark_node_failed(node_id, error_msg)
            await self._handle_node_failure(execution, node, error_msg)
            logger.error(f"Node execution error: {e}")
            
    async def _apply_input_mapping(self, execution: WorkflowExecution, node: WorkflowNode):
        """Apply input variable mapping to node parameters."""
        for param_name, var_name in node.input_mapping.items():
            if var_name in execution.variables:
                node.parameters[param_name] = execution.variables[var_name]
                
    async def _apply_output_mapping(self, execution: WorkflowExecution, node: WorkflowNode, result: Any):
        """Apply output variable mapping from node results."""
        if not isinstance(result, dict):
            return
            
        for result_key, var_name in node.output_mapping.items():
            if result_key in result:
                execution.set_variable(var_name, result[result_key], source=node.node_id)
                
    async def _schedule_next_nodes(self, execution: WorkflowExecution, completed_node_id: str):
        """Schedule execution of nodes that depend on the completed node."""
        # Find outgoing edges
        for edge in execution.workflow_definition.edges:
            if edge.from_node == completed_node_id:
                next_node_id = edge.to_node
                
                # Check if condition is satisfied
                if edge.condition and not edge.condition.evaluate(execution.variables):
                    execution.add_log(f"Edge condition not satisfied: {edge.edge_id}")
                    continue
                    
                # Schedule next node
                await self._schedule_node_execution(execution, next_node_id)
                
    async def _schedule_node_execution(self, execution: WorkflowExecution, node_id: str):
        """Schedule a node for execution."""
        if node_id not in execution.current_nodes and node_id not in execution.completed_nodes:
            execution.current_nodes.add(node_id)
            execution.add_log(f"Scheduled node for execution: {node_id}")
            
    async def _handle_node_failure(self, execution: WorkflowExecution, node: WorkflowNode, error_msg: str):
        """Handle failure of a node execution."""
        if node.skip_on_failure:
            execution.add_log(f"Skipping failed node {node.node_id} as configured")
            # Schedule next nodes as if it completed
            await self._schedule_next_nodes(execution, node.node_id)
        elif node.retry_config and node.retry_config.strategy != RetryStrategy.NONE:
            # Attempt retry
            await self._retry_node_execution(execution, node, error_msg)
        else:
            # Mark workflow as failed if critical node fails
            execution.add_log(f"Critical node {node.node_id} failed, stopping workflow", level="error")
            execution.status = WorkflowStatus.FAILED
            
    async def _retry_node_execution(self, execution: WorkflowExecution, node: WorkflowNode, error_msg: str):
        """Attempt to retry a failed node execution."""
        node_exec = execution.node_executions.get(node.node_id)
        if not node_exec or not node.retry_config:
            return
            
        retry_config = node.retry_config
        
        if node_exec.attempt_count >= retry_config.max_attempts:
            execution.add_log(f"Max retry attempts reached for node {node.node_id}", level="error")
            return
            
        # Calculate delay
        delay = self._calculate_retry_delay(retry_config, node_exec.attempt_count)
        
        execution.add_log(f"Retrying node {node.node_id} in {delay.total_seconds()}s (attempt {node_exec.attempt_count + 1})")
        
        # Schedule retry
        async def retry_after_delay():
            await asyncio.sleep(delay.total_seconds())
            node_exec.attempt_count += 1
            node_exec.status = WorkflowStatus.PENDING
            await self._schedule_node_execution(execution, node.node_id)
            
        asyncio.create_task(retry_after_delay())
        
    def _calculate_retry_delay(self, retry_config, attempt_count: int) -> timedelta:
        """Calculate delay before retry attempt."""
        if retry_config.strategy == RetryStrategy.IMMEDIATE:
            return timedelta(seconds=0)
        elif retry_config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = retry_config.initial_delay * (attempt_count + 1)
        elif retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = retry_config.initial_delay * (retry_config.backoff_multiplier ** attempt_count)
        else:
            delay = retry_config.initial_delay
            
        # Cap at maximum delay
        return min(delay, retry_config.max_delay)
        
    # Node Executors
    async def _execute_start_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a START node."""
        execution.add_log(f"Workflow started: {execution.workflow_definition.name}")
        return {"status": "started", "timestamp": datetime.now().isoformat()}
        
    async def _execute_end_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute an END node."""
        execution.add_log(f"Reached end node: {node.name}")
        return {"status": "ended", "timestamp": datetime.now().isoformat()}
        
    async def _execute_agent_spawn_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute an AGENT_SPAWN node."""
        if not isinstance(node, AgentSpawnNode):
            raise NodeExecutionError(f"Invalid node type for agent spawn: {type(node)}", node.node_id)
            
        execution.add_log(f"Spawning agent: {node.agent_type}")
        
        # Get agent spawner
        try:
            from ai.interface.agent_spawner import get_agent_spawner
            spawner = get_agent_spawner()
        except ImportError:
            raise NodeExecutionError("Agent spawner not available", node.node_id)
            
        # Create spawn request (simplified)
        agent_spec = {
            "type": node.agent_type,
            "role": node.agent_role,
            "instructions": node.agent_instructions,
            "tools": node.tools
        }
        
        # For now, create a mock spawned agent
        agent_id = f"agent_{node.node_id}_{int(time.time())}"
        spawned_agent = SpawnedAgent(
            agent_id=agent_id,
            agent_type=node.agent_type,
            role=node.agent_role,
            instructions=node.agent_instructions,
            tools=node.tools,
            status="spawned",
            parent_task=execution.execution_id
        )
        
        execution.spawned_agents[agent_id] = spawned_agent
        execution.set_variable(f"agent_{node.node_id}", agent_id)
        
        return {
            "agent_id": agent_id,
            "agent_type": node.agent_type,
            "status": "spawned"
        }
        
    async def _execute_agent_execute_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute an AGENT_EXECUTE node."""
        if not isinstance(node, AgentExecuteNode):
            raise NodeExecutionError(f"Invalid node type for agent execute: {type(node)}", node.node_id)
            
        # Get agent to execute
        agent_id = node.agent_id or execution.get_variable(f"agent_{node.node_id}")
        if not agent_id:
            raise NodeExecutionError("No agent specified for execution", node.node_id)
            
        agent = execution.spawned_agents.get(agent_id)
        if not agent:
            raise NodeExecutionError(f"Agent not found: {agent_id}", node.node_id)
            
        execution.add_log(f"Executing task with agent {agent_id}: {node.task_description}")
        
        # Simulate agent execution (in real implementation, this would execute the agent)
        await asyncio.sleep(1)  # Simulate processing time
        
        result = {
            "agent_id": agent_id,
            "task": node.task_description,
            "outcome": f"Task completed: {node.task_description}",
            "status": "completed",
            "execution_time": 1.0
        }
        
        return result
        
    async def _execute_condition_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a CONDITION node."""
        if not isinstance(node, ConditionNode):
            raise NodeExecutionError(f"Invalid node type for condition: {type(node)}", node.node_id)
            
        # Evaluate conditions
        condition_result = node.evaluate_conditions(execution.variables)
        
        execution.add_log(f"Condition evaluation: {condition_result}")
        
        # Schedule appropriate path
        if condition_result:
            for next_node in node.true_path:
                await self._schedule_node_execution(execution, next_node)
        else:
            for next_node in node.false_path:
                await self._schedule_node_execution(execution, next_node)
                
        return {
            "condition_result": condition_result,
            "conditions_evaluated": len(node.conditions)
        }
        
    async def _execute_parallel_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a PARALLEL node."""
        if not isinstance(node, ParallelNode):
            raise NodeExecutionError(f"Invalid node type for parallel: {type(node)}", node.node_id)
            
        execution.add_log(f"Starting parallel execution of {len(node.branches)} branches")
        
        # Schedule all branches for parallel execution
        for branch in node.branches:
            for branch_node in branch:
                await self._schedule_node_execution(execution, branch_node)
                
        return {
            "branches_started": len(node.branches),
            "join_strategy": node.join_strategy
        }
        
    async def _execute_loop_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a LOOP node."""
        if not isinstance(node, LoopNode):
            raise NodeExecutionError(f"Invalid node type for loop: {type(node)}", node.node_id)
            
        execution.add_log(f"Starting {node.loop_type} loop")
        
        iteration_count = 0
        
        if node.loop_type == "while":
            while (iteration_count < node.max_iterations and 
                   (not node.condition or node.condition.evaluate(execution.variables))):
                
                execution.set_variable(node.iteration_variable, iteration_count)
                
                # Execute loop body
                for body_node in node.loop_body:
                    await self._schedule_node_execution(execution, body_node)
                    
                # Wait for body completion (simplified)
                await asyncio.sleep(0.1)
                iteration_count += 1
                
        elif node.loop_type == "for":
            start = node.start_value or 0
            end = node.end_value or 10
            step = node.step
            
            for i in range(start, end, step):
                if iteration_count >= node.max_iterations:
                    break
                    
                execution.set_variable(node.iteration_variable, i)
                
                # Execute loop body
                for body_node in node.loop_body:
                    await self._schedule_node_execution(execution, body_node)
                    
                await asyncio.sleep(0.1)
                iteration_count += 1
                
        elif node.loop_type == "foreach":
            if node.iterable_variable:
                iterable = execution.get_variable(node.iterable_variable, [])
                if isinstance(iterable, list):
                    for item in iterable:
                        if iteration_count >= node.max_iterations:
                            break
                            
                        execution.set_variable(node.iteration_variable, item)
                        
                        # Execute loop body
                        for body_node in node.loop_body:
                            await self._schedule_node_execution(execution, body_node)
                            
                        await asyncio.sleep(0.1)
                        iteration_count += 1
                        
        return {
            "loop_type": node.loop_type,
            "iterations_completed": iteration_count
        }
        
    async def _execute_mcp_call_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute an MCP_CALL node."""
        if not isinstance(node, MCPCallNode):
            raise NodeExecutionError(f"Invalid node type for MCP call: {type(node)}", node.node_id)
            
        execution.add_log(f"Calling MCP service: {node.capability_category}")
        
        try:
            # Use enhanced MCP tool
            mcp_tool = EnhancedMCPTool()
            await mcp_tool.initialize()
            
            # Execute MCP request based on capability
            if node.capability_category == "research":
                result = await mcp_tool.research_query(
                    query=node.service_parameters.get("query", ""),
                    max_results=node.service_parameters.get("max_results", 10)
                )
            elif node.capability_category == "documentation":
                result = await mcp_tool.generate_documentation(
                    topic=node.service_parameters.get("topic", ""),
                    format_type=node.service_parameters.get("format", "markdown")
                )
            elif node.capability_category == "analysis":
                result = await mcp_tool.analyze_document(
                    document_path=node.service_parameters.get("document_path", "")
                )
            else:
                # Generic capability execution
                result = await mcp_tool._execute_capability_request(
                    capability=node.capability_category,
                    task_description=node.service_parameters.get("task_description", ""),
                    parameters=node.service_parameters
                )
                
            return {
                "mcp_result": result.result if hasattr(result, 'result') else result,
                "success": result.success if hasattr(result, 'success') else True,
                "server_used": result.server_used if hasattr(result, 'server_used') else None,
                "cached": result.cached if hasattr(result, 'cached') else False
            }
            
        except Exception as e:
            raise NodeExecutionError(f"MCP call failed: {str(e)}", node.node_id)
            
    async def _execute_human_approval_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a HUMAN_APPROVAL node."""
        if not isinstance(node, HumanApprovalNode):
            raise NodeExecutionError(f"Invalid node type for human approval: {type(node)}", node.node_id)
            
        execution.add_log(f"Requesting human approval: {node.approval_message}")
        
        # Store approval request in memory for human review
        WriteMemory(
            content=f"Human approval required - Workflow: {execution.workflow_definition.name}, Node: {node.node_id}, Message: {node.approval_message}",
            tags=["workflow", "approval", "human", execution.execution_id, node.node_id]
        ).run()
        
        # For now, simulate automatic approval after a delay
        await asyncio.sleep(2)
        
        # In a real implementation, this would wait for actual human input
        approval_result = "approve"  # Default action for demo
        
        return {
            "approval_result": approval_result,
            "approved": approval_result == "approve",
            "message": node.approval_message
        }
        
    async def _execute_data_transform_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a DATA_TRANSFORM node."""
        execution.add_log(f"Data transformation: {node.name}")
        
        # Basic data transformation logic
        transform_result = {
            "transformed": True,
            "input_variables": list(execution.variables.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        return transform_result
        
    async def _execute_delay_node(self, execution: WorkflowExecution, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a DELAY node."""
        delay_seconds = node.parameters.get("delay_seconds", 1)
        execution.add_log(f"Delaying execution for {delay_seconds} seconds")
        
        await asyncio.sleep(delay_seconds)
        
        return {"delayed_seconds": delay_seconds}
        
    # Monitoring and Management
    async def _monitoring_loop(self):
        """Background monitoring loop for active executions."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                for execution in list(self.active_executions.values()):
                    await self._monitor_execution(execution)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
    async def _monitor_execution(self, execution: WorkflowExecution):
        """Monitor a single workflow execution."""
        # Check for timeouts
        if execution.workflow_definition.timeout:
            elapsed = datetime.now() - execution.start_time
            if elapsed > execution.workflow_definition.timeout:
                execution.add_log("Workflow timed out", level="error")
                execution.status = WorkflowStatus.FAILED
                
        # Update progress
        progress = execution.calculate_progress()
        
        # Log progress periodically
        if hasattr(execution, '_last_progress_log'):
            if progress - execution._last_progress_log >= 10:  # Log every 10% progress
                execution.add_log(f"Workflow progress: {progress:.1f}%")
                execution._last_progress_log = progress
        else:
            execution._last_progress_log = 0
            
    async def _cleanup_loop(self):
        """Background cleanup loop for completed executions."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                
                cutoff_time = datetime.now() - timedelta(hours=1)
                
                # Remove old completed executions
                completed_executions = [
                    exec_id for exec_id, execution in self.active_executions.items()
                    if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]
                    and execution.end_time and execution.end_time < cutoff_time
                ]
                
                for exec_id in completed_executions:
                    del self.active_executions[exec_id]
                    logger.debug(f"Cleaned up completed execution: {exec_id}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                
    async def _notify_execution_callbacks(self, execution: WorkflowExecution):
        """Notify registered callbacks about execution completion."""
        callbacks = self.execution_callbacks.get(execution.execution_id, [])
        for callback in callbacks:
            try:
                await callback(execution)
            except Exception as e:
                logger.error(f"Error in execution callback: {e}")
                
    # Public API Methods
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution."""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return None
            
        return {
            "execution_id": execution_id,
            "workflow_id": execution.workflow_id,
            "workflow_name": execution.workflow_definition.name,
            "status": execution.status.value,
            "progress": execution.calculate_progress(),
            "start_time": execution.start_time.isoformat(),
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "current_nodes": list(execution.current_nodes),
            "completed_nodes": list(execution.completed_nodes),
            "failed_nodes": list(execution.failed_nodes),
            "variables": dict(execution.variables),
            "log_entries": len(execution.execution_log)
        }
        
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return False
            
        execution.status = WorkflowStatus.CANCELLED
        execution.end_time = datetime.now()
        execution.add_log("Execution cancelled by user request")
        
        logger.info(f"Cancelled workflow execution: {execution_id}")
        return True
        
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause a running workflow execution."""
        execution = self.active_executions.get(execution_id)
        if not execution or execution.status != WorkflowStatus.RUNNING:
            return False
            
        execution.status = WorkflowStatus.PAUSED
        execution.add_log("Execution paused by user request")
        
        logger.info(f"Paused workflow execution: {execution_id}")
        return True
        
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused workflow execution."""
        execution = self.active_executions.get(execution_id)
        if not execution or execution.status != WorkflowStatus.PAUSED:
            return False
            
        execution.status = WorkflowStatus.RUNNING
        execution.add_log("Execution resumed by user request")
        
        # Restart execution loop
        asyncio.create_task(self._execute_workflow_async(execution))
        
        logger.info(f"Resumed workflow execution: {execution_id}")
        return True
        
    def register_execution_callback(self, execution_id: str, callback: Callable):
        """Register a callback for workflow execution completion."""
        self.execution_callbacks[execution_id].append(callback)
        
    def get_execution_log(self, execution_id: str, limit: int = 100) -> List[str]:
        """Get the execution log for a workflow."""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return []
            
        return execution.execution_log[-limit:]
        
    def get_engine_metrics(self) -> Dict[str, Any]:
        """Get execution engine performance metrics."""
        return {
            "active_executions": len(self.active_executions),
            "total_executions_processed": len(self.execution_metrics),
            "node_performance": {
                node_type: {
                    "count": len(times),
                    "avg_time": sum(times) / len(times) if times else 0,
                    "max_time": max(times) if times else 0
                }
                for node_type, times in self.node_performance.items()
            }
        }


# Global engine instance
_engine: Optional[WorkflowExecutionEngine] = None

def get_workflow_engine() -> WorkflowExecutionEngine:
    """Get the global workflow execution engine instance."""
    global _engine
    if _engine is None:
        _engine = WorkflowExecutionEngine()
    return _engine
