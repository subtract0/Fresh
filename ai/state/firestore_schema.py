"""
Firestore State Management Schema

Defines the collection structure and data models for agent state persistence
in Firestore, replacing fragile JSON file-based state management.

Collections:
- agent_states: Agent lifecycle and operational state
- agent_memory: Agent memory and learning data
- coordination: Multi-agent coordination state
- system_state: Global system state and configuration

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/memory/firestore_store.py: Firestore memory implementation
    - ai/agents/: Agent implementations
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json

class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    TERMINATED = "terminated"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CoordinationEventType(Enum):
    """Types of coordination events between agents"""
    SPAWN = "spawn"
    HANDOFF = "handoff"
    COLLABORATION = "collaboration"
    TERMINATION = "termination"
    ERROR = "error"

@dataclass
class AgentState:
    """
    Agent operational state stored in Firestore.
    
    Collection: agent_states
    Document ID: {agent_type}_{agent_id}_{session_id}
    """
    # Identity (required fields first)
    agent_id: str
    agent_type: str  # Father, Architect, Developer, QA
    session_id: str
    
    # State (required fields)
    status: AgentStatus
    
    # Lifecycle (required fields)
    created_at: datetime
    last_updated: datetime
    last_active: datetime
    
    # Operational data (required fields)
    memory_context: Dict[str, Any]  # Current working context
    task_history: List[Dict[str, Any]]  # Recent task history
    performance_metrics: Dict[str, float]  # Success rate, avg time, etc.
    
    # Configuration (required fields)
    agent_config: Dict[str, Any]  # Agent-specific configuration
    tools_enabled: List[str]  # Available tools for this agent
    
    # Optional fields with defaults
    current_task: Optional[str] = None
    task_status: Optional[TaskStatus] = None
    parent_agent_id: Optional[str] = None  # Spawning agent
    child_agent_ids: Optional[List[str]] = None  # Spawned agents
    collaboration_context: Optional[Dict[str, Any]] = None  # Multi-agent context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage"""
        result = asdict(self)
        # Convert enums to strings
        result['status'] = self.status.value
        if self.task_status:
            result['task_status'] = self.task_status.value
        # Convert datetime to timestamp
        result['created_at'] = self.created_at.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        result['last_active'] = self.last_active.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentState:
        """Create from dictionary retrieved from Firestore"""
        data = data.copy()
        # Convert strings back to enums
        data['status'] = AgentStatus(data['status'])
        if data.get('task_status'):
            data['task_status'] = TaskStatus(data['task_status'])
        # Convert timestamps back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        data['last_active'] = datetime.fromisoformat(data['last_active'])
        # Handle optional fields - set to None if not present (dataclass defaults will handle)
        if 'child_agent_ids' not in data:
            data['child_agent_ids'] = None
        if 'collaboration_context' not in data:
            data['collaboration_context'] = None
        return cls(**data)

@dataclass
class AgentMemoryState:
    """
    Agent memory state for learning and context.
    
    Collection: agent_memory
    Document ID: {agent_type}_{agent_id}
    """
    # Identity
    agent_id: str
    agent_type: str
    
    # Memory metadata
    memory_count: int
    last_memory_sync: datetime
    learning_context: Dict[str, Any]
    
    # Learning state
    learned_patterns: List[Dict[str, Any]]  # Recognized patterns
    decision_history: List[Dict[str, Any]]  # Past decisions and outcomes
    performance_insights: Dict[str, Any]  # Learning insights
    
    # Memory analytics
    memory_types_count: Dict[str, int]  # Count by memory type
    importance_distribution: Dict[str, int]  # Importance score distribution
    recent_activity: List[Dict[str, Any]]  # Recent memory operations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage"""
        result = asdict(self)
        result['last_memory_sync'] = self.last_memory_sync.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentMemoryState:
        """Create from dictionary retrieved from Firestore"""
        data = data.copy()
        data['last_memory_sync'] = datetime.fromisoformat(data['last_memory_sync'])
        return cls(**data)

@dataclass
class CoordinationEvent:
    """
    Multi-agent coordination event.
    
    Collection: coordination
    Document ID: auto-generated with timestamp
    """
    # Event metadata (required fields first)
    event_id: str
    event_type: CoordinationEventType
    timestamp: datetime
    
    # Agent information (required fields)
    source_agent_id: str
    source_agent_type: str
    
    # Event context (required fields)
    context: Dict[str, Any]  # Event-specific data
    task_context: Dict[str, Any]  # Task being coordinated
    
    # Outcome tracking (required fields)
    success: bool
    
    # Optional fields with defaults
    target_agent_id: Optional[str] = None
    target_agent_type: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CoordinationEvent:
        """Create from dictionary retrieved from Firestore"""
        data = data.copy()
        data['event_type'] = CoordinationEventType(data['event_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class SystemState:
    """
    Global system state and configuration.
    
    Collection: system_state  
    Document ID: global_config
    """
    # System metadata
    system_version: str
    last_updated: datetime
    
    # Agent orchestration state
    active_sessions: List[str]
    total_agents_spawned: int
    current_agent_count: int
    
    # Performance metrics
    system_metrics: Dict[str, Any]  # Global performance data
    error_counts: Dict[str, int]  # Error tracking by type
    
    # Configuration
    global_config: Dict[str, Any]  # System-wide settings
    feature_flags: Dict[str, bool]  # Feature enablement
    
    # Emergency state
    emergency_stop: bool = False
    emergency_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage"""
        result = asdict(self)
        result['last_updated'] = self.last_updated.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SystemState:
        """Create from dictionary retrieved from Firestore"""
        data = data.copy()
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

# Collection and index configuration for optimal performance
FIRESTORE_SCHEMA_CONFIG = {
    "collections": {
        "agent_states": {
            "indexes": [
                # Compound indexes for common queries
                ["agent_type", "status", "last_active"],
                ["session_id", "status"],
                ["parent_agent_id", "created_at"],
                ["status", "last_active"]
            ],
            "ttl_field": None,  # Keep indefinitely for learning
            "security_rules": "authenticated_users_only"
        },
        "agent_memory": {
            "indexes": [
                ["agent_type", "last_memory_sync"],
                ["memory_count", "last_memory_sync"]
            ],
            "ttl_field": None,  # Keep indefinitely for learning
            "security_rules": "authenticated_users_only"
        },
        "coordination": {
            "indexes": [
                # Time-based queries for monitoring
                ["timestamp", "event_type"],
                ["source_agent_id", "timestamp"],
                ["event_type", "success", "timestamp"],
                # Agent relationship queries
                ["source_agent_type", "target_agent_type", "timestamp"]
            ],
            "ttl_field": "timestamp",  # Auto-delete old events (90 days)
            "security_rules": "authenticated_users_only"
        },
        "system_state": {
            "indexes": [],  # Single document, no indexes needed
            "ttl_field": None,
            "security_rules": "admin_only"
        }
    }
}

def get_collection_path(collection_name: str, project_id: str = None) -> str:
    """Get full Firestore collection path"""
    if project_id:
        return f"projects/{project_id}/databases/(default)/documents/{collection_name}"
    return collection_name

def get_agent_state_doc_id(agent_type: str, agent_id: str, session_id: str) -> str:
    """Generate consistent document ID for agent states"""
    return f"{agent_type}_{agent_id}_{session_id}"

def get_agent_memory_doc_id(agent_type: str, agent_id: str) -> str:
    """Generate consistent document ID for agent memory"""
    return f"{agent_type}_{agent_id}"

def get_coordination_event_doc_id(timestamp: datetime = None) -> str:
    """Generate coordination event document ID with timestamp"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    return f"event_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond}"
