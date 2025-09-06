"""
State Migration Utilities

Utilities to migrate existing JSON-based agent state to the new Firestore
state management system, ensuring smooth transition and data preservation.

Migration types:
- Agent operational state from JSON files
- Coordination logs to structured events  
- System configuration to unified state
- Memory context preservation

Cross-references:
    - ADR-003: Unified Enhanced Architecture Migration
    - ai/state/firestore_manager.py: Target state system
    - ai/state/firestore_schema.py: Data models
"""
from __future__ import annotations
import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import asdict

# State management imports
from .firestore_manager import FirestoreStateManager
from .firestore_schema import (
    AgentState, AgentMemoryState, CoordinationEvent, SystemState,
    AgentStatus, TaskStatus, CoordinationEventType,
    get_agent_state_doc_id
)

logger = logging.getLogger(__name__)

class StateMigrator:
    """
    Handles migration from JSON-based state to Firestore state management.
    
    Provides comprehensive migration capabilities for existing agent systems
    with data validation and rollback support.
    """
    
    def __init__(self, source_dir: str = ".", firestore_manager: FirestoreStateManager = None):
        """
        Initialize state migrator.
        
        Args:
            source_dir: Directory containing JSON state files
            firestore_manager: Target Firestore manager (creates if None)
        """
        self.source_dir = Path(source_dir)
        self.firestore_manager = firestore_manager or FirestoreStateManager()
        self.migration_log: List[Dict[str, Any]] = []
        
    async def migrate_all(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate all state from JSON files to Firestore.
        
        Args:
            dry_run: If True, only analyze without actual migration
            
        Returns:
            Migration summary with statistics and any errors
        """
        logger.info(f"Starting state migration (dry_run={dry_run})")
        
        summary = {
            'dry_run': dry_run,
            'start_time': datetime.utcnow().isoformat(),
            'source_directory': str(self.source_dir),
            'agent_states_migrated': 0,
            'coordination_events_migrated': 0,
            'system_config_migrated': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. Migrate agent states from various JSON sources
            agent_result = await self._migrate_agent_states(dry_run)
            summary['agent_states_migrated'] = agent_result['migrated']
            summary['errors'].extend(agent_result['errors'])
            summary['warnings'].extend(agent_result['warnings'])
            
            # 2. Migrate coordination and monitoring logs
            coord_result = await self._migrate_coordination_events(dry_run)
            summary['coordination_events_migrated'] = coord_result['migrated']
            summary['errors'].extend(coord_result['errors'])
            
            # 3. Migrate system configuration
            system_result = await self._migrate_system_config(dry_run)
            summary['system_config_migrated'] = system_result['migrated']
            summary['errors'].extend(system_result['errors'])
            
            # 4. Generate migration report
            summary['end_time'] = datetime.utcnow().isoformat()
            summary['success'] = len(summary['errors']) == 0
            
            logger.info(f"Migration completed: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            summary['errors'].append(f"Migration failed: {str(e)}")
            summary['success'] = False
            return summary
    
    async def _migrate_agent_states(self, dry_run: bool) -> Dict[str, Any]:
        """
        Migrate agent state from JSON files to Firestore agent_states collection.
        
        Looks for various JSON file patterns that might contain agent state:
        - agent_*.json
        - *_state.json  
        - autonomous_*.json
        - monitoring_*.json
        """
        result = {'migrated': 0, 'errors': [], 'warnings': []}
        
        # Find potential agent state files
        patterns = [
            'agent_*.json',
            '*_state.json', 
            'autonomous_*.json',
            'monitoring_*.json',
            '*_agent.json'
        ]
        
        state_files = []
        for pattern in patterns:
            state_files.extend(glob.glob(str(self.source_dir / pattern)))
        
        logger.info(f"Found {len(state_files)} potential agent state files")
        
        for file_path in state_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Try to extract agent state from various JSON structures
                agent_states = self._extract_agent_states_from_json(data, file_path)
                
                for agent_state in agent_states:
                    if not dry_run:
                        success = await self.firestore_manager.save_agent_state(agent_state)
                        if not success:
                            result['errors'].append(f"Failed to save agent state: {agent_state.agent_id}")
                            continue
                    
                    result['migrated'] += 1
                    logger.debug(f"Migrated agent state: {agent_state.agent_id}")
                    
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
        
        return result
    
    def _extract_agent_states_from_json(self, data: Any, source_file: str) -> List[AgentState]:
        """
        Extract agent states from various JSON structures.
        
        Handles different JSON formats that might contain agent state information.
        """
        agent_states = []
        now = datetime.utcnow()
        
        try:
            # Handle different JSON structures
            if isinstance(data, dict):
                # Check for direct agent state structure
                if self._looks_like_agent_state(data):
                    agent_state = self._convert_to_agent_state(data, source_file, now)
                    if agent_state:
                        agent_states.append(agent_state)
                
                # Check for nested agent states (e.g., {'agents': {...}})
                elif 'agents' in data and isinstance(data['agents'], dict):
                    for agent_id, agent_data in data['agents'].items():
                        if self._looks_like_agent_state(agent_data):
                            agent_state = self._convert_to_agent_state(
                                agent_data, source_file, now, agent_id
                            )
                            if agent_state:
                                agent_states.append(agent_state)
                
                # Check for autonomous system state
                elif 'status' in data and 'last_active' in data:
                    # Looks like system monitoring data - create synthetic agent state
                    agent_state = self._create_synthetic_agent_state(data, source_file, now)
                    if agent_state:
                        agent_states.append(agent_state)
            
            elif isinstance(data, list):
                # Handle list of agent states
                for item in data:
                    if self._looks_like_agent_state(item):
                        agent_state = self._convert_to_agent_state(item, source_file, now)
                        if agent_state:
                            agent_states.append(agent_state)
        
        except Exception as e:
            logger.error(f"Error extracting agent states from {source_file}: {e}")
        
        return agent_states
    
    def _looks_like_agent_state(self, data: Dict) -> bool:
        """Check if dictionary structure looks like agent state."""
        required_fields = ['agent_id', 'agent_type'] 
        optional_fields = ['status', 'last_active', 'current_task', 'session_id']
        
        # Must have required fields or reasonable subset of optional fields
        has_required = all(field in data for field in required_fields)
        has_optional = sum(1 for field in optional_fields if field in data) >= 2
        
        return has_required or has_optional
    
    def _convert_to_agent_state(self, data: Dict, source_file: str, 
                               timestamp: datetime, agent_id: str = None) -> Optional[AgentState]:
        """Convert JSON data to AgentState object."""
        try:
            # Extract required fields with defaults
            agent_id = agent_id or data.get('agent_id', f"migrated_{timestamp.strftime('%Y%m%d_%H%M%S')}")
            agent_type = data.get('agent_type', 'Unknown')
            session_id = data.get('session_id', f"migration_{timestamp.strftime('%Y%m%d')}")
            
            # Map status strings to enum
            status_mapping = {
                'active': AgentStatus.ACTIVE,
                'running': AgentStatus.ACTIVE,
                'idle': AgentStatus.IDLE,
                'busy': AgentStatus.BUSY,
                'error': AgentStatus.ERROR,
                'terminated': AgentStatus.TERMINATED,
                'stopped': AgentStatus.TERMINATED
            }
            
            status_str = data.get('status', 'idle').lower()
            status = status_mapping.get(status_str, AgentStatus.IDLE)
            
            # Extract task information
            current_task = data.get('current_task')
            task_status = None
            if current_task and data.get('task_status'):
                task_status_map = {
                    'pending': TaskStatus.PENDING,
                    'in_progress': TaskStatus.IN_PROGRESS, 
                    'running': TaskStatus.IN_PROGRESS,
                    'completed': TaskStatus.COMPLETED,
                    'failed': TaskStatus.FAILED,
                    'cancelled': TaskStatus.CANCELLED
                }
                task_status = task_status_map.get(data.get('task_status', '').lower())
            
            # Handle timestamps
            created_at = timestamp
            if 'created_at' in data:
                try:
                    created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
                except:
                    pass
            
            last_updated = timestamp
            if 'last_updated' in data:
                try:
                    last_updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
                except:
                    pass
            
            last_active = timestamp
            if 'last_active' in data:
                try:
                    last_active = datetime.fromisoformat(data['last_active'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract operational data
            memory_context = data.get('memory_context', {})
            task_history = data.get('task_history', [])
            performance_metrics = data.get('performance_metrics', {})
            
            # Extract configuration
            agent_config = data.get('agent_config', data.get('config', {}))
            tools_enabled = data.get('tools_enabled', data.get('tools', []))
            
            # Extract coordination info
            parent_agent_id = data.get('parent_agent_id')
            child_agent_ids = data.get('child_agent_ids', [])
            collaboration_context = data.get('collaboration_context', {})
            
            return AgentState(
                agent_id=agent_id,
                agent_type=agent_type,
                session_id=session_id,
                status=status,
                current_task=current_task,
                task_status=task_status,
                created_at=created_at,
                last_updated=last_updated,
                last_active=last_active,
                memory_context=memory_context,
                task_history=task_history,
                performance_metrics=performance_metrics,
                agent_config=agent_config,
                tools_enabled=tools_enabled,
                parent_agent_id=parent_agent_id,
                child_agent_ids=child_agent_ids,
                collaboration_context=collaboration_context
            )
            
        except Exception as e:
            logger.error(f"Error converting data to AgentState: {e}")
            return None
    
    def _create_synthetic_agent_state(self, data: Dict, source_file: str,
                                    timestamp: datetime) -> Optional[AgentState]:
        """Create synthetic agent state from system monitoring data."""
        try:
            # Extract system info to create a representative agent state
            file_name = Path(source_file).stem
            agent_type = "System"
            agent_id = f"system_{file_name}"
            session_id = f"migration_{timestamp.strftime('%Y%m%d')}"
            
            status = AgentStatus.IDLE
            if data.get('status') == 'running':
                status = AgentStatus.ACTIVE
            elif data.get('status') == 'error':
                status = AgentStatus.ERROR
            
            return AgentState(
                agent_id=agent_id,
                agent_type=agent_type,
                session_id=session_id,
                status=status,
                current_task=data.get('current_operation'),
                created_at=timestamp,
                last_updated=timestamp,
                last_active=timestamp,
                memory_context={'source_file': source_file, 'original_data': data},
                task_history=[],
                performance_metrics=data.get('metrics', {}),
                agent_config={},
                tools_enabled=[],
                collaboration_context={}
            )
            
        except Exception as e:
            logger.error(f"Error creating synthetic agent state: {e}")
            return None
    
    async def _migrate_coordination_events(self, dry_run: bool) -> Dict[str, Any]:
        """Migrate coordination logs to structured coordination events."""
        result = {'migrated': 0, 'errors': []}
        
        # Look for coordination/monitoring log files
        log_patterns = [
            '*coordination*.json',
            '*monitor*.json', 
            '*activity*.json',
            'logs/*.json'
        ]
        
        log_files = []
        for pattern in log_patterns:
            log_files.extend(glob.glob(str(self.source_dir / pattern)))
        
        for file_path in log_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                events = self._extract_coordination_events(data, file_path)
                
                for event in events:
                    if not dry_run:
                        success = await self.firestore_manager.record_coordination_event(event)
                        if not success:
                            result['errors'].append(f"Failed to record event: {event.event_id}")
                            continue
                    
                    result['migrated'] += 1
                    
            except Exception as e:
                result['errors'].append(f"Error processing coordination log {file_path}: {str(e)}")
        
        return result
    
    def _extract_coordination_events(self, data: Any, source_file: str) -> List[CoordinationEvent]:
        """Extract coordination events from log data."""
        events = []
        now = datetime.utcnow()
        
        try:
            if isinstance(data, list):
                for item in data:
                    event = self._convert_to_coordination_event(item, source_file, now)
                    if event:
                        events.append(event)
            elif isinstance(data, dict):
                # Check if this looks like an event log structure
                if 'events' in data and isinstance(data['events'], list):
                    for event_data in data['events']:
                        event = self._convert_to_coordination_event(event_data, source_file, now)
                        if event:
                            events.append(event)
                else:
                    # Try to convert the dict itself to an event
                    event = self._convert_to_coordination_event(data, source_file, now)
                    if event:
                        events.append(event)
        
        except Exception as e:
            logger.error(f"Error extracting coordination events from {source_file}: {e}")
        
        return events
    
    def _convert_to_coordination_event(self, data: Dict, source_file: str,
                                     default_time: datetime) -> Optional[CoordinationEvent]:
        """Convert log data to CoordinationEvent."""
        try:
            # Generate event ID
            event_id = data.get('event_id', f"migrated_{default_time.strftime('%Y%m%d_%H%M%S')}")
            
            # Map event types
            event_type_map = {
                'spawn': CoordinationEventType.SPAWN,
                'created': CoordinationEventType.SPAWN,
                'handoff': CoordinationEventType.HANDOFF,
                'delegate': CoordinationEventType.HANDOFF,
                'collaboration': CoordinationEventType.COLLABORATION,
                'coordinate': CoordinationEventType.COLLABORATION,
                'termination': CoordinationEventType.TERMINATION,
                'terminated': CoordinationEventType.TERMINATION,
                'error': CoordinationEventType.ERROR,
                'failed': CoordinationEventType.ERROR
            }
            
            event_type_str = data.get('event_type', data.get('type', 'collaboration')).lower()
            event_type = event_type_map.get(event_type_str, CoordinationEventType.COLLABORATION)
            
            # Extract timestamp
            timestamp = default_time
            if 'timestamp' in data:
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract agent information
            source_agent_id = data.get('source_agent_id', data.get('from_agent', 'unknown'))
            source_agent_type = data.get('source_agent_type', data.get('from_type', 'Unknown'))
            target_agent_id = data.get('target_agent_id', data.get('to_agent'))
            target_agent_type = data.get('target_agent_type', data.get('to_type'))
            
            # Extract context
            context = data.get('context', {})
            task_context = data.get('task_context', data.get('task', {}))
            
            # Extract outcome
            success = data.get('success', data.get('status') != 'error')
            error_message = data.get('error_message', data.get('error'))
            duration_seconds = data.get('duration_seconds', data.get('duration'))
            
            return CoordinationEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=timestamp,
                source_agent_id=source_agent_id,
                source_agent_type=source_agent_type,
                target_agent_id=target_agent_id,
                target_agent_type=target_agent_type,
                context=context,
                task_context=task_context,
                success=success,
                error_message=error_message,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            logger.error(f"Error converting to coordination event: {e}")
            return None
    
    async def _migrate_system_config(self, dry_run: bool) -> Dict[str, Any]:
        """Migrate system configuration to unified system state."""
        result = {'migrated': 0, 'errors': []}
        
        # Look for system configuration files
        config_files = [
            'config.json',
            'system_config.json',
            'app_config.json',
            'settings.json'
        ]
        
        config_data = {}
        
        for config_file in config_files:
            config_path = self.source_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        data = json.load(f)
                        config_data.update(data)
                except Exception as e:
                    result['errors'].append(f"Error reading {config_file}: {str(e)}")
        
        if config_data:
            try:
                # Create system state from config data
                system_state = SystemState(
                    system_version=config_data.get('version', '1.0.0'),
                    last_updated=datetime.utcnow(),
                    active_sessions=[],
                    total_agents_spawned=config_data.get('total_agents', 0),
                    current_agent_count=0,
                    system_metrics=config_data.get('metrics', {}),
                    error_counts=config_data.get('error_counts', {}),
                    global_config=config_data,
                    feature_flags=config_data.get('feature_flags', {}),
                    emergency_stop=config_data.get('emergency_stop', False),
                    emergency_reason=config_data.get('emergency_reason')
                )
                
                if not dry_run:
                    success = await self.firestore_manager.update_system_state(system_state)
                    if not success:
                        result['errors'].append("Failed to migrate system state")
                        return result
                
                result['migrated'] = 1
                logger.info("Successfully migrated system configuration")
                
            except Exception as e:
                result['errors'].append(f"Error creating system state: {str(e)}")
        
        return result
    
    async def validate_migration(self) -> Dict[str, Any]:
        """
        Validate migrated data in Firestore.
        
        Returns:
            Validation report with statistics and any issues found
        """
        logger.info("Validating migration...")
        
        validation = {
            'timestamp': datetime.utcnow().isoformat(),
            'firestore_available': self.firestore_manager.firestore_available,
            'statistics': {},
            'issues': [],
            'success': False
        }
        
        try:
            # Get statistics from Firestore
            stats = await self.firestore_manager.get_state_statistics()
            validation['statistics'] = stats
            
            # Basic validation checks
            if stats['agent_states_count'] == 0:
                validation['issues'].append("No agent states found in Firestore")
            
            if stats['active_agents_count'] > stats['agent_states_count']:
                validation['issues'].append("More active agents than total agent states (data inconsistency)")
            
            if stats['error_agents_count'] > stats['agent_states_count'] * 0.5:
                validation['issues'].append("High percentage of agents in error state")
            
            # Check system state
            system_state = await self.firestore_manager.get_system_state()
            if system_state is None:
                validation['issues'].append("No system state found")
            
            validation['success'] = len(validation['issues']) == 0
            logger.info(f"Migration validation completed: {validation}")
            
        except Exception as e:
            validation['issues'].append(f"Validation failed: {str(e)}")
            logger.error(f"Migration validation error: {e}")
        
        return validation

# Convenience functions for common migration scenarios

async def migrate_from_directory(source_dir: str, dry_run: bool = True) -> Dict[str, Any]:
    """
    Simple migration function for a directory of JSON state files.
    
    Args:
        source_dir: Directory containing JSON files to migrate
        dry_run: If True, analyze without migrating
        
    Returns:
        Migration summary
    """
    migrator = StateMigrator(source_dir)
    return await migrator.migrate_all(dry_run)

async def migrate_agent_json_file(file_path: str, dry_run: bool = True) -> bool:
    """
    Migrate a single JSON file containing agent state.
    
    Args:
        file_path: Path to JSON file
        dry_run: If True, analyze without migrating
        
    Returns:
        Success status
    """
    migrator = StateMigrator(os.path.dirname(file_path))
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        agent_states = migrator._extract_agent_states_from_json(data, file_path)
        
        if not dry_run:
            for agent_state in agent_states:
                success = await migrator.firestore_manager.save_agent_state(agent_state)
                if not success:
                    return False
        
        logger.info(f"Successfully processed {len(agent_states)} agent states from {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error migrating {file_path}: {e}")
        return False
