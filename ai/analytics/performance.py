"""Agent Performance Analytics and Optimization System.

This module tracks and analyzes agent spawn success rates, execution times,
user satisfaction, and other metrics to optimize Father's decision-making
and improve the overall agent system performance.

Cross-references:
    - Agent Spawner: ai/interface/agent_spawner.py for spawn metrics
    - Execution Monitor: ai/execution/monitor.py for execution metrics
    - Father Agent: ai/agents/Father.py for decision optimization
    - Memory System: ai/memory/README.md for analytics storage

Related:
    - Performance tracking across agent lifecycles
    - Success rate analysis by agent types and task types
    - User feedback integration for satisfaction metrics
    - Continuous improvement recommendations
"""
from __future__ import annotations
import json
import asyncio
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import sqlite3
from pathlib import Path

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Metrics for a single agent or batch execution."""
    metric_id: str
    spawn_request_id: str
    agent_type: str
    task_type: str
    spawn_time: datetime
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    status: str = "pending"
    
    # Timing metrics
    spawn_duration_seconds: Optional[float] = None
    execution_duration_seconds: Optional[float] = None
    total_duration_seconds: Optional[float] = None
    
    # Success metrics
    spawn_success: bool = True
    execution_success: bool = False
    completion_success: bool = False
    
    # Quality metrics
    steps_completed: int = 0
    steps_failed: int = 0
    retry_count: int = 0
    error_count: int = 0
    
    # Context metrics
    tools_used: List[str] = field(default_factory=list)
    memory_entries_created: int = 0
    user_feedback_score: Optional[float] = None  # 1-5 scale
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskTypeAnalysis:
    """Analysis results for a specific task type."""
    task_type: str
    total_requests: int
    success_rate: float
    avg_duration_minutes: float
    avg_agent_count: float
    most_effective_agent_types: List[Tuple[str, float]]  # (agent_type, success_rate)
    common_failure_reasons: List[str]
    user_satisfaction_avg: Optional[float]
    optimal_agent_configurations: List[Dict[str, Any]]


@dataclass
class AgentTypeAnalysis:
    """Analysis results for a specific agent type."""
    agent_type: str
    total_spawns: int
    success_rate: float
    avg_execution_time_minutes: float
    best_task_types: List[Tuple[str, float]]  # (task_type, success_rate)
    common_tools_used: List[str]
    typical_step_count: int
    improvement_suggestions: List[str]


class PerformanceAnalytics:
    """Tracks and analyzes agent performance for optimization."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path.home() / ".fresh" / "analytics.db")
        self.ensure_db_directory()
        self.init_database()
        
        # In-memory caches for fast access
        self.recent_metrics: deque = deque(maxlen=1000)
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        # Performance thresholds
        self.success_threshold = 0.8  # 80% success rate
        self.duration_threshold_minutes = 30  # 30 minute execution limit
        self.satisfaction_threshold = 3.5  # 3.5/5 user satisfaction
        
    def ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
    def init_database(self):
        """Initialize SQLite database for performance metrics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    metric_id TEXT PRIMARY KEY,
                    spawn_request_id TEXT,
                    agent_type TEXT,
                    task_type TEXT,
                    spawn_time TEXT,
                    start_time TEXT,
                    completion_time TEXT,
                    status TEXT,
                    spawn_duration_seconds REAL,
                    execution_duration_seconds REAL,
                    total_duration_seconds REAL,
                    spawn_success BOOLEAN,
                    execution_success BOOLEAN,
                    completion_success BOOLEAN,
                    steps_completed INTEGER,
                    steps_failed INTEGER,
                    retry_count INTEGER,
                    error_count INTEGER,
                    tools_used TEXT,
                    memory_entries_created INTEGER,
                    user_feedback_score REAL,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_type ON performance_metrics(task_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_type ON performance_metrics(agent_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_spawn_time ON performance_metrics(spawn_time)
            """)
            
    def record_spawn_metrics(
        self,
        spawn_request_id: str,
        agent_type: str,
        task_type: str,
        spawn_duration_seconds: float,
        spawn_success: bool,
        tools_assigned: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record metrics for agent spawning."""
        metric_id = f"spawn_{spawn_request_id}_{agent_type}_{int(datetime.now().timestamp())}"
        
        metrics = PerformanceMetrics(
            metric_id=metric_id,
            spawn_request_id=spawn_request_id,
            agent_type=agent_type,
            task_type=task_type,
            spawn_time=datetime.now(),
            spawn_duration_seconds=spawn_duration_seconds,
            spawn_success=spawn_success,
            tools_used=tools_assigned,
            metadata=metadata or {}
        )
        
        self._store_metrics(metrics)
        self.recent_metrics.append(metrics)
        
        # Store in memory system for persistence
        WriteMemory(
            content=f"Agent spawn metrics: {agent_type} for {task_type} - Success: {spawn_success} - Duration: {spawn_duration_seconds:.2f}s",
            tags=["analytics", "spawn", "metrics", agent_type.lower(), task_type]
        ).run()
        
        return metric_id
        
    def record_execution_metrics(
        self,
        metric_id: str,
        execution_duration_seconds: float,
        execution_success: bool,
        steps_completed: int,
        steps_failed: int,
        error_count: int,
        memory_entries_created: int = 0
    ):
        """Record metrics for agent execution."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE performance_metrics 
                SET execution_duration_seconds = ?,
                    execution_success = ?,
                    steps_completed = ?,
                    steps_failed = ?,
                    error_count = ?,
                    memory_entries_created = ?,
                    start_time = datetime('now'),
                    status = 'executing'
                WHERE metric_id = ?
            """, (execution_duration_seconds, execution_success, steps_completed, 
                  steps_failed, error_count, memory_entries_created, metric_id))
            
        # Update in-memory cache
        for metrics in self.recent_metrics:
            if metrics.metric_id == metric_id:
                metrics.execution_duration_seconds = execution_duration_seconds
                metrics.execution_success = execution_success
                metrics.steps_completed = steps_completed
                metrics.steps_failed = steps_failed
                metrics.error_count = error_count
                metrics.memory_entries_created = memory_entries_created
                metrics.start_time = datetime.now()
                metrics.status = "executing"
                break
                
    def record_completion_metrics(
        self,
        metric_id: str,
        completion_success: bool,
        total_duration_seconds: float,
        final_status: str = "completed"
    ):
        """Record metrics for agent completion."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE performance_metrics 
                SET completion_success = ?,
                    total_duration_seconds = ?,
                    completion_time = datetime('now'),
                    status = ?
                WHERE metric_id = ?
            """, (completion_success, total_duration_seconds, final_status, metric_id))
            
        # Update in-memory cache
        for metrics in self.recent_metrics:
            if metrics.metric_id == metric_id:
                metrics.completion_success = completion_success
                metrics.total_duration_seconds = total_duration_seconds
                metrics.completion_time = datetime.now()
                metrics.status = final_status
                break
                
        # Clear analysis cache to force refresh
        self.analysis_cache.clear()
        self.cache_expiry.clear()
        
    def record_user_feedback(self, spawn_request_id: str, satisfaction_score: float):
        """Record user satisfaction feedback (1-5 scale)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE performance_metrics 
                SET user_feedback_score = ?
                WHERE spawn_request_id = ?
            """, (satisfaction_score, spawn_request_id))
            
        WriteMemory(
            content=f"User feedback: {satisfaction_score}/5 for request {spawn_request_id}",
            tags=["analytics", "feedback", "satisfaction"]
        ).run()
        
    async def analyze_task_type_performance(self, task_type: str, days_back: int = 30) -> TaskTypeAnalysis:
        """Analyze performance for a specific task type."""
        cache_key = f"task_analysis_{task_type}_{days_back}"
        
        # Check cache
        if cache_key in self.analysis_cache:
            if datetime.now() < self.cache_expiry.get(cache_key, datetime.min):
                return TaskTypeAnalysis(**self.analysis_cache[cache_key])
                
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get all metrics for this task type
            cursor = conn.execute("""
                SELECT * FROM performance_metrics 
                WHERE task_type = ? AND spawn_time >= ?
                ORDER BY spawn_time DESC
            """, (task_type, cutoff_date.isoformat()))
            
            rows = cursor.fetchall()
            
        if not rows:
            return TaskTypeAnalysis(
                task_type=task_type,
                total_requests=0,
                success_rate=0.0,
                avg_duration_minutes=0.0,
                avg_agent_count=0.0,
                most_effective_agent_types=[],
                common_failure_reasons=[],
                user_satisfaction_avg=None,
                optimal_agent_configurations=[]
            )
            
        # Calculate metrics
        total_requests = len(set(row['spawn_request_id'] for row in rows))
        successful_requests = len([row for row in rows if row['completion_success']])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0.0
        
        # Duration analysis
        durations = [row['total_duration_seconds'] for row in rows 
                    if row['total_duration_seconds'] is not None]
        avg_duration_minutes = statistics.mean(durations) / 60 if durations else 0.0
        
        # Agent count analysis
        request_agent_counts = defaultdict(int)
        for row in rows:
            request_agent_counts[row['spawn_request_id']] += 1
        avg_agent_count = statistics.mean(request_agent_counts.values()) if request_agent_counts else 0.0
        
        # Agent effectiveness analysis
        agent_success = defaultdict(lambda: {'total': 0, 'success': 0})
        for row in rows:
            agent_success[row['agent_type']]['total'] += 1
            if row['completion_success']:
                agent_success[row['agent_type']]['success'] += 1
                
        most_effective = []
        for agent_type, stats in agent_success.items():
            if stats['total'] >= 3:  # Minimum sample size
                effectiveness = stats['success'] / stats['total']
                most_effective.append((agent_type, effectiveness))
        most_effective.sort(key=lambda x: x[1], reverse=True)
        
        # User satisfaction analysis
        satisfaction_scores = [row['user_feedback_score'] for row in rows 
                             if row['user_feedback_score'] is not None]
        user_satisfaction_avg = statistics.mean(satisfaction_scores) if satisfaction_scores else None
        
        # Failure analysis
        failures = [row for row in rows if not row['completion_success']]
        common_failure_reasons = self._analyze_failure_reasons(failures)
        
        # Optimal configurations (simplified)
        optimal_agent_configurations = self._determine_optimal_configurations(task_type, rows)
        
        analysis = TaskTypeAnalysis(
            task_type=task_type,
            total_requests=total_requests,
            success_rate=success_rate,
            avg_duration_minutes=avg_duration_minutes,
            avg_agent_count=avg_agent_count,
            most_effective_agent_types=most_effective[:5],
            common_failure_reasons=common_failure_reasons,
            user_satisfaction_avg=user_satisfaction_avg,
            optimal_agent_configurations=optimal_agent_configurations
        )
        
        # Cache results
        self.analysis_cache[cache_key] = analysis.__dict__
        self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
        
        return analysis
        
    async def analyze_agent_type_performance(self, agent_type: str, days_back: int = 30) -> AgentTypeAnalysis:
        """Analyze performance for a specific agent type."""
        cache_key = f"agent_analysis_{agent_type}_{days_back}"
        
        # Check cache
        if cache_key in self.analysis_cache:
            if datetime.now() < self.cache_expiry.get(cache_key, datetime.min):
                return AgentTypeAnalysis(**self.analysis_cache[cache_key])
                
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM performance_metrics 
                WHERE agent_type = ? AND spawn_time >= ?
                ORDER BY spawn_time DESC
            """, (agent_type, cutoff_date.isoformat()))
            
            rows = cursor.fetchall()
            
        if not rows:
            return AgentTypeAnalysis(
                agent_type=agent_type,
                total_spawns=0,
                success_rate=0.0,
                avg_execution_time_minutes=0.0,
                best_task_types=[],
                common_tools_used=[],
                typical_step_count=0,
                improvement_suggestions=[]
            )
            
        # Calculate metrics
        total_spawns = len(rows)
        successful_spawns = len([row for row in rows if row['completion_success']])
        success_rate = successful_spawns / total_spawns if total_spawns > 0 else 0.0
        
        # Execution time analysis
        execution_times = [row['execution_duration_seconds'] for row in rows 
                          if row['execution_duration_seconds'] is not None]
        avg_execution_time_minutes = statistics.mean(execution_times) / 60 if execution_times else 0.0
        
        # Task type effectiveness
        task_success = defaultdict(lambda: {'total': 0, 'success': 0})
        for row in rows:
            task_success[row['task_type']]['total'] += 1
            if row['completion_success']:
                task_success[row['task_type']]['success'] += 1
                
        best_task_types = []
        for task_type, stats in task_success.items():
            if stats['total'] >= 2:  # Minimum sample size
                effectiveness = stats['success'] / stats['total']
                best_task_types.append((task_type, effectiveness))
        best_task_types.sort(key=lambda x: x[1], reverse=True)
        
        # Tool usage analysis
        all_tools = []
        for row in rows:
            if row['tools_used']:
                try:
                    tools = json.loads(row['tools_used'])
                    all_tools.extend(tools)
                except (json.JSONDecodeError, TypeError):
                    pass
        common_tools_used = list(set(all_tools))  # Unique tools
        
        # Step count analysis
        step_counts = [row['steps_completed'] + row['steps_failed'] for row in rows 
                      if row['steps_completed'] is not None and row['steps_failed'] is not None]
        typical_step_count = int(statistics.mean(step_counts)) if step_counts else 0
        
        # Improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(agent_type, rows)
        
        analysis = AgentTypeAnalysis(
            agent_type=agent_type,
            total_spawns=total_spawns,
            success_rate=success_rate,
            avg_execution_time_minutes=avg_execution_time_minutes,
            best_task_types=best_task_types[:3],
            common_tools_used=common_tools_used,
            typical_step_count=typical_step_count,
            improvement_suggestions=improvement_suggestions
        )
        
        # Cache results
        self.analysis_cache[cache_key] = analysis.__dict__
        self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
        
        return analysis
        
    def get_optimization_recommendations(self) -> Dict[str, List[str]]:
        """Get optimization recommendations for Father's decision-making."""
        recommendations = {
            "agent_selection": [],
            "tool_assignment": [],
            "task_routing": [],
            "performance_improvements": []
        }
        
        # Analyze recent performance trends
        recent_cutoff = datetime.now() - timedelta(days=7)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get recent metrics
            cursor = conn.execute("""
                SELECT * FROM performance_metrics 
                WHERE spawn_time >= ?
                ORDER BY spawn_time DESC
            """, (recent_cutoff.isoformat(),))
            
            recent_metrics = cursor.fetchall()
            
        if not recent_metrics:
            return recommendations
            
        # Analyze underperforming combinations
        task_agent_performance = defaultdict(lambda: {'total': 0, 'success': 0})
        for metric in recent_metrics:
            key = f"{metric['task_type']}_{metric['agent_type']}"
            task_agent_performance[key]['total'] += 1
            if metric['completion_success']:
                task_agent_performance[key]['success'] += 1
                
        # Agent selection recommendations
        for key, stats in task_agent_performance.items():
            if stats['total'] >= 3:  # Minimum sample
                success_rate = stats['success'] / stats['total']
                task_type, agent_type = key.split('_', 1)
                
                if success_rate < self.success_threshold:
                    recommendations["agent_selection"].append(
                        f"Consider alternative to {agent_type} for {task_type} tasks (current success rate: {success_rate:.2%})"
                    )
                elif success_rate > 0.9:
                    recommendations["agent_selection"].append(
                        f"Prioritize {agent_type} for {task_type} tasks (high success rate: {success_rate:.2%})"
                    )
                    
        # Duration-based recommendations
        long_running = [m for m in recent_metrics 
                       if m['total_duration_seconds'] and m['total_duration_seconds'] > self.duration_threshold_minutes * 60]
        
        if long_running:
            task_duration = defaultdict(list)
            for metric in long_running:
                task_duration[metric['task_type']].append(metric['total_duration_seconds'])
                
            for task_type, durations in task_duration.items():
                avg_duration = statistics.mean(durations) / 60
                recommendations["performance_improvements"].append(
                    f"Optimize {task_type} tasks - averaging {avg_duration:.1f} minutes (threshold: {self.duration_threshold_minutes})"
                )
                
        # User satisfaction recommendations
        low_satisfaction = [m for m in recent_metrics 
                           if m['user_feedback_score'] and m['user_feedback_score'] < self.satisfaction_threshold]
        
        if low_satisfaction:
            task_satisfaction = defaultdict(list)
            for metric in low_satisfaction:
                task_satisfaction[metric['task_type']].append(metric['user_feedback_score'])
                
            for task_type, scores in task_satisfaction.items():
                avg_score = statistics.mean(scores)
                recommendations["performance_improvements"].append(
                    f"Improve user satisfaction for {task_type} tasks (current: {avg_score:.1f}/5)"
                )
                
        return recommendations
        
    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO performance_metrics (
                    metric_id, spawn_request_id, agent_type, task_type,
                    spawn_time, start_time, completion_time, status,
                    spawn_duration_seconds, execution_duration_seconds, total_duration_seconds,
                    spawn_success, execution_success, completion_success,
                    steps_completed, steps_failed, retry_count, error_count,
                    tools_used, memory_entries_created, user_feedback_score, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.metric_id, metrics.spawn_request_id, metrics.agent_type, metrics.task_type,
                metrics.spawn_time.isoformat(), 
                metrics.start_time.isoformat() if metrics.start_time else None,
                metrics.completion_time.isoformat() if metrics.completion_time else None,
                metrics.status,
                metrics.spawn_duration_seconds, metrics.execution_duration_seconds, 
                metrics.total_duration_seconds,
                metrics.spawn_success, metrics.execution_success, metrics.completion_success,
                metrics.steps_completed, metrics.steps_failed, metrics.retry_count, 
                metrics.error_count,
                json.dumps(metrics.tools_used), metrics.memory_entries_created, 
                metrics.user_feedback_score, json.dumps(metrics.metadata)
            ))
            
    def _analyze_failure_reasons(self, failures: List[sqlite3.Row]) -> List[str]:
        """Analyze common failure reasons from failed executions."""
        reasons = []
        
        if not failures:
            return reasons
            
        # High error count
        high_error_count = len([f for f in failures if f['error_count'] > 2])
        if high_error_count > len(failures) * 0.3:
            reasons.append("High error rates during execution")
            
        # Duration-based failures
        long_durations = [f for f in failures 
                         if f['total_duration_seconds'] and f['total_duration_seconds'] > self.duration_threshold_minutes * 60]
        if len(long_durations) > len(failures) * 0.4:
            reasons.append("Execution timeouts")
            
        # Step completion issues
        incomplete_steps = [f for f in failures if f['steps_failed'] > f['steps_completed']]
        if len(incomplete_steps) > len(failures) * 0.5:
            reasons.append("Step execution failures")
            
        if not reasons:
            reasons.append("Various execution issues")
            
        return reasons
        
    def _determine_optimal_configurations(self, task_type: str, metrics: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """Determine optimal agent configurations for a task type."""
        successful_metrics = [m for m in metrics if m['completion_success']]
        
        if not successful_metrics:
            return []
            
        # Group by agent combinations (simplified)
        config_performance = defaultdict(lambda: {'count': 0, 'avg_duration': 0, 'tools': set()})
        
        for metric in successful_metrics:
            config_key = metric['agent_type']
            config_performance[config_key]['count'] += 1
            
            if metric['total_duration_seconds']:
                current_avg = config_performance[config_key]['avg_duration']
                current_count = config_performance[config_key]['count']
                new_avg = (current_avg * (current_count - 1) + metric['total_duration_seconds']) / current_count
                config_performance[config_key]['avg_duration'] = new_avg
                
            if metric['tools_used']:
                try:
                    tools = json.loads(metric['tools_used'])
                    config_performance[config_key]['tools'].update(tools)
                except (json.JSONDecodeError, TypeError):
                    pass
                    
        # Format as configurations
        optimal_configs = []
        for agent_type, perf in config_performance.items():
            if perf['count'] >= 2:  # Minimum occurrences
                optimal_configs.append({
                    'agent_type': agent_type,
                    'success_count': perf['count'],
                    'avg_duration_minutes': perf['avg_duration'] / 60 if perf['avg_duration'] else 0,
                    'recommended_tools': list(perf['tools'])
                })
                
        # Sort by success count
        optimal_configs.sort(key=lambda x: x['success_count'], reverse=True)
        return optimal_configs[:3]
        
    def _generate_improvement_suggestions(self, agent_type: str, metrics: List[sqlite3.Row]) -> List[str]:
        """Generate improvement suggestions for an agent type."""
        suggestions = []
        
        if not metrics:
            return suggestions
            
        # Analyze failure patterns
        failures = [m for m in metrics if not m['completion_success']]
        failure_rate = len(failures) / len(metrics)
        
        if failure_rate > 0.3:
            suggestions.append("High failure rate - review error handling and step design")
            
        # Duration analysis
        durations = [m['execution_duration_seconds'] for m in metrics 
                    if m['execution_duration_seconds'] is not None]
        if durations:
            avg_duration = statistics.mean(durations)
            if avg_duration > self.duration_threshold_minutes * 60:
                suggestions.append("Long execution times - consider breaking down complex steps")
                
        # Step efficiency
        step_ratios = []
        for m in metrics:
            if m['steps_completed'] and m['steps_failed'] is not None:
                total_steps = m['steps_completed'] + m['steps_failed']
                if total_steps > 0:
                    success_ratio = m['steps_completed'] / total_steps
                    step_ratios.append(success_ratio)
                    
        if step_ratios and statistics.mean(step_ratios) < 0.8:
            suggestions.append("Low step success rate - improve individual step reliability")
            
        # Tool effectiveness
        tool_usage = defaultdict(int)
        for m in metrics:
            if m['tools_used']:
                try:
                    tools = json.loads(m['tools_used'])
                    for tool in tools:
                        tool_usage[tool] += 1
                except (json.JSONDecodeError, TypeError):
                    pass
                    
        if len(tool_usage) > 5:
            suggestions.append("Many tools used - consider focusing on core capabilities")
        elif len(tool_usage) < 2:
            suggestions.append("Limited tool usage - consider expanding available tools")
            
        if not suggestions:
            suggestions.append("Performance appears optimal - maintain current approach")
            
        return suggestions


# Global analytics instance
_analytics_instance: Optional[PerformanceAnalytics] = None

def get_performance_analytics() -> PerformanceAnalytics:
    """Get the global performance analytics instance."""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = PerformanceAnalytics()
    return _analytics_instance
