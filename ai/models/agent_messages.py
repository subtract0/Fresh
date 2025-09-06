"""
Pydantic Models for Agent Communication Schema Validation

Implements formal schema validation for all agent communication,
ensuring type safety and data integrity across the system.

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - Gemini Analysis: Communication Protocol Formalization
    - ai/agents/: Agent implementations
    - ai/state/: State management
"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from enum import Enum
import json

class MessageType(str, Enum):
    """Types of messages between agents."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    SPAWN_REQUEST = "spawn_request"
    SPAWN_RESPONSE = "spawn_response"
    HANDOFF = "handoff"
    COLLABORATION = "collaboration"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    MEMORY_QUERY = "memory_query"
    MEMORY_RESPONSE = "memory_response"


class Priority(str, Enum):
    """Message priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentMessage(BaseModel):
    """Base message structure for agent communication."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "message_id": "msg_123456",
                "message_type": "task_assignment",
                "sender": "Father",
                "recipient": "Developer",
                "timestamp": "2025-01-04T12:00:00Z",
                "priority": "high",
                "payload": {"task": "Implement authentication"}
            }
        }
    )
    
    message_id: str = Field(..., description="Unique message identifier")
    message_type: MessageType = Field(..., description="Type of message")
    sender: str = Field(..., description="Agent sending the message")
    recipient: str = Field(..., description="Agent receiving the message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp")
    priority: Priority = Field(default=Priority.MEDIUM, description="Message priority")
    session_id: Optional[str] = Field(None, description="Session identifier for tracking")
    correlation_id: Optional[str] = Field(None, description="ID linking related messages")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message-specific data")
    
    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v):
        """Ensure message ID is not empty."""
        if not v or not v.strip():
            raise ValueError("message_id cannot be empty")
        return v
    
    @field_validator('sender', 'recipient')
    @classmethod
    def validate_agent_names(cls, v):
        """Validate agent names."""
        valid_agents = ["Father", "Architect", "Developer", "QA", "Mother", "System"]
        if v not in valid_agents:
            raise ValueError(f"Invalid agent name: {v}. Must be one of {valid_agents}")
        return v


class TaskAssignment(BaseModel):
    """Schema for task assignment messages."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task (bug_fix, feature, refactor, etc.)")
    description: str = Field(..., description="Detailed task description")
    file_path: Optional[str] = Field(None, description="File to modify")
    line_number: Optional[int] = Field(None, ge=1, description="Line number in file")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    requirements: List[str] = Field(default_factory=list, description="Task requirements")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Ensure description is meaningful."""
        if len(v) < 10:
            raise ValueError("Task description must be at least 10 characters")
        return v


class TaskResult(BaseModel):
    """Schema for task result messages."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether task succeeded")
    result_type: str = Field(..., description="Type of result (code, tests, docs, etc.)")
    output: Optional[str] = Field(None, description="Task output/solution")
    files_modified: List[str] = Field(default_factory=list, description="Files modified")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Task duration")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    
    @field_validator('output')
    @classmethod
    def validate_output(cls, v):
        """Output validation - can be None for successful tasks."""
        # Allow None output, but if provided, it should not be empty string
        if v is not None and v == "":
            raise ValueError("Output cannot be empty string")
        return v


class SpawnRequest(BaseModel):
    """Schema for agent spawn requests."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    agent_type: str = Field(..., description="Type of agent to spawn")
    agent_name: str = Field(..., description="Name for the new agent")
    instructions: str = Field(..., description="Instructions for the agent")
    model: str = Field(default="gpt-4", description="LLM model to use")
    tools: List[str] = Field(default_factory=list, description="Tools to equip agent with")
    memory_context: Dict[str, Any] = Field(default_factory=dict, description="Initial memory context")
    parent_task_id: Optional[str] = Field(None, description="Parent task if spawned for specific task")
    
    @field_validator('agent_type')
    @classmethod
    def validate_agent_type(cls, v):
        """Validate agent type."""
        valid_types = ["Father", "Architect", "Developer", "QA"]
        if v not in valid_types:
            raise ValueError(f"Invalid agent type: {v}. Must be one of {valid_types}")
        return v


class SpawnResponse(BaseModel):
    """Schema for agent spawn responses."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    success: bool = Field(..., description="Whether spawn succeeded")
    agent_id: Optional[str] = Field(None, description="ID of spawned agent")
    agent_type: Optional[str] = Field(None, description="Type of spawned agent")
    session_id: Optional[str] = Field(None, description="Session ID for the agent")
    error: Optional[str] = Field(None, description="Error if spawn failed")
    spawn_duration_seconds: Optional[float] = Field(None, ge=0, description="Time to spawn")
    
    @field_validator('agent_id')
    @classmethod
    def validate_spawn_response(cls, v):
        """Validate agent_id is non-empty when provided."""
        if v is not None and len(v) < 5:
            raise ValueError("agent_id must be at least 5 characters")
        return v


class HandoffMessage(BaseModel):
    """Schema for task handoff between agents."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    task_id: str = Field(..., description="Task being handed off")
    from_agent: str = Field(..., description="Agent handing off the task")
    to_agent: str = Field(..., description="Agent receiving the task")
    reason: str = Field(..., description="Reason for handoff")
    current_progress: Dict[str, Any] = Field(default_factory=dict, description="Current task progress")
    remaining_work: List[str] = Field(default_factory=list, description="Work remaining")
    context: Dict[str, Any] = Field(default_factory=dict, description="Handoff context")


class CollaborationRequest(BaseModel):
    """Schema for collaboration requests between agents."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    collaboration_id: str = Field(..., description="Unique collaboration identifier")
    initiator: str = Field(..., description="Agent initiating collaboration")
    collaborators: List[str] = Field(..., min_length=1, description="Agents to collaborate with")
    objective: str = Field(..., description="Collaboration objective")
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="Tasks to collaborate on")
    deadline: Optional[datetime] = Field(None, description="Collaboration deadline")
    coordination_strategy: str = Field(default="parallel", description="How to coordinate (parallel, sequential)")


class StatusUpdate(BaseModel):
    """Schema for agent status updates."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    agent_id: str = Field(..., description="Agent identifier")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Current status (idle, active, busy, error)")
    current_task: Optional[str] = Field(None, description="Current task if active")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100, description="Task progress")
    memory_usage_mb: Optional[float] = Field(None, ge=0, description="Memory usage in MB")
    active_tools: List[str] = Field(default_factory=list, description="Currently active tools")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")


class ErrorReport(BaseModel):
    """Schema for error reports."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    error_id: str = Field(..., description="Unique error identifier")
    error_type: str = Field(..., description="Type of error")
    severity: str = Field(..., description="Error severity (critical, high, medium, low)")
    message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    recovery_attempted: bool = Field(default=False, description="Whether recovery was attempted")
    recovery_successful: Optional[bool] = Field(None, description="Whether recovery succeeded")
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Validate severity level."""
        valid_severities = ["critical", "high", "medium", "low"]
        if v.lower() not in valid_severities:
            raise ValueError(f"Invalid severity: {v}. Must be one of {valid_severities}")
        return v.lower()


class MemoryQuery(BaseModel):
    """Schema for memory system queries."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    query_id: str = Field(..., description="Unique query identifier")
    query_type: str = Field(..., description="Type of query (search, retrieve, analyze)")
    query: str = Field(..., description="Query string")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Query filters")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum results to return")
    include_metadata: bool = Field(default=True, description="Include metadata in results")


class MemoryResponse(BaseModel):
    """Schema for memory system responses."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    query_id: str = Field(..., description="Query identifier")
    success: bool = Field(..., description="Whether query succeeded")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Query results")
    total_matches: int = Field(default=0, ge=0, description="Total matches found")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    error: Optional[str] = Field(None, description="Error if query failed")


# Message factory for easy creation
class MessageFactory:
    """Factory for creating validated messages."""
    
    @staticmethod
    def create_task_assignment(
        sender: str,
        recipient: str,
        task_id: str,
        task_type: str,
        description: str,
        **kwargs
    ) -> AgentMessage:
        """Create a validated task assignment message."""
        task = TaskAssignment(
            task_id=task_id,
            task_type=task_type,
            description=description,
            **kwargs
        )
        
        return AgentMessage(
            message_id=f"msg_{task_id}_{datetime.now(timezone.utc).timestamp()}",
            message_type=MessageType.TASK_ASSIGNMENT,
            sender=sender,
            recipient=recipient,
            priority=Priority.HIGH if "critical" in description.lower() else Priority.MEDIUM,
            payload=task.model_dump()
        )
    
    @staticmethod
    def create_task_result(
        sender: str,
        recipient: str,
        task_id: str,
        success: bool,
        result_type: str,
        **kwargs
    ) -> AgentMessage:
        """Create a validated task result message."""
        result = TaskResult(
            task_id=task_id,
            success=success,
            result_type=result_type,
            **kwargs
        )
        
        return AgentMessage(
            message_id=f"result_{task_id}_{datetime.now(timezone.utc).timestamp()}",
            message_type=MessageType.TASK_RESULT,
            sender=sender,
            recipient=recipient,
            priority=Priority.CRITICAL if not success else Priority.MEDIUM,
            payload=result.model_dump()
        )
    
    @staticmethod
    def create_error_report(
        sender: str,
        error_type: str,
        severity: str,
        message: str,
        **kwargs
    ) -> AgentMessage:
        """Create a validated error report message."""
        error = ErrorReport(
            error_id=f"err_{datetime.now(timezone.utc).timestamp()}",
            error_type=error_type,
            severity=severity,
            message=message,
            **kwargs
        )
        
        return AgentMessage(
            message_id=f"error_{error.error_id}",
            message_type=MessageType.ERROR_REPORT,
            sender=sender,
            recipient="System",  # Errors typically go to system
            priority=Priority.CRITICAL if severity == "critical" else Priority.HIGH,
            payload=error.model_dump()
        )
