"""
Firestore State Manager

Implements state persistence and retrieval for the Fresh AI agent system,
replacing fragile JSON file-based state management with robust Firestore.

Key features:
- Agent lifecycle state management
- Cross-session memory persistence
- Multi-agent coordination tracking
- System-wide state monitoring
- Automatic fallback to in-memory state

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/state/firestore_schema.py: Data models and schema
    - ai/memory/firestore_store.py: Memory persistence
"""
from __future__ import annotations
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from contextlib import asynccontextmanager

# Schema imports
from .firestore_schema import (
    AgentState, AgentMemoryState, CoordinationEvent, SystemState,
    AgentStatus, TaskStatus, CoordinationEventType,
    get_agent_state_doc_id, get_agent_memory_doc_id, get_coordination_event_doc_id
)

# Configure logging
logger = logging.getLogger(__name__)

class FirestoreStateManager:
    """
    Manages agent state persistence using Firestore.
    
    Provides high-level interface for agent state operations with
    automatic fallback to in-memory state when Firestore is unavailable.
    """
    
    def __init__(self, project_id: str = None, fallback_to_memory: bool = True):
        """
        Initialize Firestore state manager.
        
        Args:
            project_id: Firebase project ID (from env if None)
            fallback_to_memory: Whether to fall back to in-memory state
        """
        self.project_id = project_id or os.getenv('FIREBASE_PROJECT_ID')
        self.fallback_to_memory = fallback_to_memory
        self.firestore_available = False
        self.db = None
        
        # In-memory fallback state
        self._memory_agent_states: Dict[str, Dict] = {}
        self._memory_coordination: List[Dict] = []
        self._memory_system_state: Optional[Dict] = None
        
        # Initialize Firestore connection
        self._initialize_firestore()
    
    def _initialize_firestore(self) -> bool:
        """Initialize Firestore connection with graceful fallback."""
        try:
            # Try to initialize Firestore
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Initialize Firebase app if not already initialized
            if not firebase_admin._apps:
                # Try to use service account credentials
                if os.getenv('FIREBASE_CLIENT_EMAIL') and os.getenv('FIREBASE_PRIVATE_KEY'):
                    cred_dict = {
                        "type": "service_account",
                        "project_id": self.project_id,
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                else:
                    # Try default credentials (for deployed environments)
                    firebase_admin.initialize_app()
            
            # Get Firestore client
            self.db = firestore.client()
            self.firestore_available = True
            logger.info("Firestore state manager initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Firestore initialization failed, using in-memory fallback: {e}")
            self.firestore_available = False
            return False
    
    # Agent State Management
    
    async def save_agent_state(self, agent_state: AgentState) -> bool:
        """
        Save agent state to Firestore or memory fallback.
        
        Args:
            agent_state: Agent state to save
            
        Returns:
            bool: Success status
        """
        doc_id = get_agent_state_doc_id(
            agent_state.agent_type,
            agent_state.agent_id, 
            agent_state.session_id
        )
        
        if self.firestore_available:
            try:
                doc_ref = self.db.collection('agent_states').document(doc_id)
                doc_ref.set(agent_state.to_dict())
                logger.debug(f"Saved agent state to Firestore: {doc_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to save agent state to Firestore: {e}")
                if not self.fallback_to_memory:
                    return False
        
        # Fallback to memory
        self._memory_agent_states[doc_id] = agent_state.to_dict()
        logger.debug(f"Saved agent state to memory: {doc_id}")
        return True
    
    async def load_agent_state(self, agent_type: str, agent_id: str, session_id: str) -> Optional[AgentState]:
        """
        Load agent state from Firestore or memory fallback.
        
        Args:
            agent_type: Type of agent (Father, Architect, etc.)
            agent_id: Unique agent identifier
            session_id: Session identifier
            
        Returns:
            AgentState if found, None otherwise
        """
        doc_id = get_agent_state_doc_id(agent_type, agent_id, session_id)
        
        if self.firestore_available:
            try:
                doc_ref = self.db.collection('agent_states').document(doc_id)
                doc = doc_ref.get()
                if doc.exists:
                    return AgentState.from_dict(doc.to_dict())
            except Exception as e:
                logger.error(f"Failed to load agent state from Firestore: {e}")
        
        # Fallback to memory
        if doc_id in self._memory_agent_states:
            return AgentState.from_dict(self._memory_agent_states[doc_id])
        
        return None
    
    async def get_active_agents(self, session_id: str = None) -> List[AgentState]:
        """
        Get all active agents, optionally filtered by session.
        
        Args:
            session_id: Optional session filter
            
        Returns:
            List of active agent states
        """
        if self.firestore_available:
            try:
                query = self.db.collection('agent_states').where('status', '==', AgentStatus.ACTIVE.value)
                if session_id:
                    query = query.where('session_id', '==', session_id)
                
                docs = query.stream()
                return [AgentState.from_dict(doc.to_dict()) for doc in docs]
            except Exception as e:
                logger.error(f"Failed to query active agents from Firestore: {e}")
        
        # Fallback to memory
        active_agents = []
        for state_dict in self._memory_agent_states.values():
            if state_dict['status'] == AgentStatus.ACTIVE.value:
                if session_id is None or state_dict.get('session_id') == session_id:
                    active_agents.append(AgentState.from_dict(state_dict))
        
        return active_agents
    
    async def update_agent_status(self, agent_type: str, agent_id: str, session_id: str, 
                                  status: AgentStatus, task: str = None) -> bool:
        """
        Update agent status and current task.
        
        Args:
            agent_type: Type of agent
            agent_id: Agent identifier
            session_id: Session identifier  
            status: New agent status
            task: Current task description
            
        Returns:
            bool: Success status
        """
        doc_id = get_agent_state_doc_id(agent_type, agent_id, session_id)
        update_data = {
            'status': status.value,
            'last_updated': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat()
        }
        
        if task:
            update_data['current_task'] = task
            update_data['task_status'] = TaskStatus.IN_PROGRESS.value
        
        if self.firestore_available:
            try:
                doc_ref = self.db.collection('agent_states').document(doc_id)
                doc_ref.update(update_data)
                logger.debug(f"Updated agent status in Firestore: {doc_id} -> {status.value}")
                return True
            except Exception as e:
                logger.error(f"Failed to update agent status in Firestore: {e}")
                if not self.fallback_to_memory:
                    return False
        
        # Fallback to memory
        if doc_id in self._memory_agent_states:
            self._memory_agent_states[doc_id].update(update_data)
            logger.debug(f"Updated agent status in memory: {doc_id} -> {status.value}")
            return True
        
        return False
    
    # Coordination Event Management
    
    async def record_coordination_event(self, event: CoordinationEvent) -> bool:
        """
        Record a coordination event between agents.
        
        Args:
            event: Coordination event to record
            
        Returns:
            bool: Success status
        """
        doc_id = get_coordination_event_doc_id(event.timestamp)
        
        if self.firestore_available:
            try:
                doc_ref = self.db.collection('coordination').document(doc_id)
                doc_ref.set(event.to_dict())
                logger.debug(f"Recorded coordination event in Firestore: {event.event_type.value}")
                return True
            except Exception as e:
                logger.error(f"Failed to record coordination event in Firestore: {e}")
                if not self.fallback_to_memory:
                    return False
        
        # Fallback to memory
        self._memory_coordination.append(event.to_dict())
        # Keep only last 1000 events in memory
        if len(self._memory_coordination) > 1000:
            self._memory_coordination = self._memory_coordination[-1000:]
        
        logger.debug(f"Recorded coordination event in memory: {event.event_type.value}")
        return True
    
    async def get_recent_coordination_events(self, hours: int = 24, 
                                           event_type: CoordinationEventType = None) -> List[CoordinationEvent]:
        """
        Get recent coordination events.
        
        Args:
            hours: Number of hours to look back
            event_type: Optional event type filter
            
        Returns:
            List of coordination events
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if self.firestore_available:
            try:
                query = self.db.collection('coordination').where(
                    'timestamp', '>=', cutoff_time.isoformat()
                )
                if event_type:
                    query = query.where('event_type', '==', event_type.value)
                
                query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(100)
                docs = query.stream()
                return [CoordinationEvent.from_dict(doc.to_dict()) for doc in docs]
            except Exception as e:
                logger.error(f"Failed to query coordination events from Firestore: {e}")
        
        # Fallback to memory
        events = []
        for event_dict in self._memory_coordination:
            event_time = datetime.fromisoformat(event_dict['timestamp'])
            if event_time >= cutoff_time:
                if event_type is None or event_dict['event_type'] == event_type.value:
                    events.append(CoordinationEvent.from_dict(event_dict))
        
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:100]
    
    # System State Management
    
    async def get_system_state(self) -> Optional[SystemState]:
        """
        Get current system state.
        
        Returns:
            SystemState if available, None otherwise
        """
        if self.firestore_available:
            try:
                doc_ref = self.db.collection('system_state').document('global_config')
                doc = doc_ref.get()
                if doc.exists:
                    return SystemState.from_dict(doc.to_dict())
            except Exception as e:
                logger.error(f"Failed to load system state from Firestore: {e}")
        
        # Fallback to memory
        if self._memory_system_state:
            return SystemState.from_dict(self._memory_system_state)
        
        return None
    
    async def update_system_state(self, system_state: SystemState) -> bool:
        """
        Update system state.
        
        Args:
            system_state: System state to save
            
        Returns:
            bool: Success status
        """
        if self.firestore_available:
            try:
                doc_ref = self.db.collection('system_state').document('global_config')
                doc_ref.set(system_state.to_dict())
                logger.debug("Updated system state in Firestore")
                return True
            except Exception as e:
                logger.error(f"Failed to update system state in Firestore: {e}")
                if not self.fallback_to_memory:
                    return False
        
        # Fallback to memory
        self._memory_system_state = system_state.to_dict()
        logger.debug("Updated system state in memory")
        return True
    
    # Utility and Maintenance Methods
    
    async def cleanup_old_states(self, days: int = 30) -> int:
        """
        Clean up old agent states and coordination events.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of documents cleaned up
        """
        if not self.firestore_available:
            return 0
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            cleanup_count = 0
            
            # Clean up old agent states
            query = self.db.collection('agent_states').where(
                'last_updated', '<', cutoff_time.isoformat()
            ).where('status', 'in', [AgentStatus.TERMINATED.value, AgentStatus.ERROR.value])
            
            docs = query.limit(100).stream()  # Process in batches
            batch = self.db.batch()
            
            for doc in docs:
                batch.delete(doc.reference)
                cleanup_count += 1
            
            batch.commit()
            logger.info(f"Cleaned up {cleanup_count} old agent states")
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old states: {e}")
            return 0
    
    async def get_state_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about current state storage.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'firestore_available': self.firestore_available,
            'agent_states_count': 0,
            'coordination_events_count': 0,
            'active_agents_count': 0,
            'error_agents_count': 0
        }
        
        if self.firestore_available:
            try:
                # Count agent states
                agent_states = self.db.collection('agent_states').stream()
                agent_count = 0
                active_count = 0
                error_count = 0
                
                for doc in agent_states:
                    agent_count += 1
                    data = doc.to_dict()
                    if data.get('status') == AgentStatus.ACTIVE.value:
                        active_count += 1
                    elif data.get('status') == AgentStatus.ERROR.value:
                        error_count += 1
                
                stats['agent_states_count'] = agent_count
                stats['active_agents_count'] = active_count  
                stats['error_agents_count'] = error_count
                
                # Count coordination events (last 24 hours)
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                coord_query = self.db.collection('coordination').where(
                    'timestamp', '>=', cutoff_time.isoformat()
                )
                coordination_docs = coord_query.stream()
                stats['coordination_events_count'] = len(list(coordination_docs))
                
            except Exception as e:
                logger.error(f"Failed to get Firestore statistics: {e}")
        else:
            # Memory fallback statistics
            stats['agent_states_count'] = len(self._memory_agent_states)
            stats['coordination_events_count'] = len(self._memory_coordination)
            stats['active_agents_count'] = len([
                s for s in self._memory_agent_states.values() 
                if s.get('status') == AgentStatus.ACTIVE.value
            ])
        
        return stats

# Global instance for easy access
_global_state_manager: Optional[FirestoreStateManager] = None

def get_state_manager(project_id: str = None) -> FirestoreStateManager:
    """
    Get global state manager instance with lazy initialization.
    
    Args:
        project_id: Firebase project ID (optional)
        
    Returns:
        FirestoreStateManager instance
    """
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = FirestoreStateManager(project_id)
    return _global_state_manager

# Context manager for state transactions
@asynccontextmanager
async def state_transaction():
    """
    Context manager for grouping state operations.
    
    Note: This is a placeholder for future transaction support.
    Firestore transactions require more complex implementation.
    """
    # For now, just provide the state manager
    state_manager = get_state_manager()
    try:
        yield state_manager
    finally:
        pass  # Future: commit or rollback transaction
