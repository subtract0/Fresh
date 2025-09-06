#!/usr/bin/env python3
"""
🧠 Enhanced Father Learning System
Persistent memory for strategic planning improvements

This module enables Enhanced Father to:
- Store outcomes from each orchestration
- Learn from MotherAgent performance patterns  
- Improve strategic planning over time
- Track which optimizations work best

Agent Hook Points:
- store_orchestration_outcome(): Save results from each run
- retrieve_learning_patterns(): Get historical insights
- analyze_performance_trends(): Identify improvement opportunities
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..memory.intelligent_store import IntelligentMemoryStore


class EnhancedFatherLearning:
    """
    Learning system for Enhanced Father to improve strategic planning.
    
    This class provides persistent memory and learning capabilities
    for the Enhanced Father orchestrator, enabling it to get smarter
    with each execution cycle.
    """
    
    def __init__(self, memory_store: Optional[IntelligentMemoryStore] = None):
        """
        Initialize the learning system.
        
        Args:
            memory_store: Optional memory store instance. Creates default if not provided.
        """
        self.memory_store = memory_store or IntelligentMemoryStore()
        self.learning_file = Path("logs/enhanced_father_learning.json")
        self.learning_file.parent.mkdir(exist_ok=True)
        self._load_historical_learning()
    
    def _load_historical_learning(self) -> None:
        """Load historical learning data from persistent storage."""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r') as f:
                    self.historical_data = json.load(f)
            except json.JSONDecodeError:
                self.historical_data = {"orchestrations": [], "patterns": {}}
        else:
            self.historical_data = {"orchestrations": [], "patterns": {}}
    
    def store_orchestration_outcome(self, outcome: Dict[str, Any]) -> None:
        """
        Store the outcome of an orchestration for learning.
        
        Args:
            outcome: Dictionary containing orchestration results, metrics, and insights
        
        Agent Usage:
            learning.store_orchestration_outcome({
                "timestamp": datetime.now().isoformat(),
                "tasks": task_list,
                "results": execution_results,
                "cost": total_cost,
                "duration": duration_minutes,
                "success_rate": success_rate
            })
        """
        # Add timestamp if not present
        if "timestamp" not in outcome:
            outcome["timestamp"] = datetime.now().isoformat()
        
        # Store in memory
        self.memory_store.store(
            content=json.dumps(outcome),
            metadata={
                "type": "orchestration_outcome",
                "timestamp": outcome["timestamp"],
                "success_rate": outcome.get("success_rate", 0)
            }
        )
        
        # Store in persistent file
        self.historical_data["orchestrations"].append(outcome)
        self._save_learning()
        
        # Extract and store patterns
        self._extract_patterns(outcome)
    
    def retrieve_learning_patterns(self) -> Dict[str, Any]:
        """
        Retrieve learned patterns for strategic planning.
        
        Returns:
            Dictionary of learned patterns and insights
            
        Agent Usage:
            patterns = learning.retrieve_learning_patterns()
            # Use patterns to inform next orchestration strategy
        """
        return {
            "successful_strategies": self._get_successful_strategies(),
            "common_failures": self._get_common_failures(),
            "optimal_parameters": self._get_optimal_parameters(),
            "performance_trends": self._get_performance_trends()
        }
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze performance trends over time.
        
        Returns:
            Dictionary with performance analysis and recommendations
            
        Agent Usage:
            trends = learning.analyze_performance_trends()
            # Adjust strategy based on trends
        """
        if not self.historical_data["orchestrations"]:
            return {"status": "no_data", "message": "No historical data available yet"}
        
        orchestrations = self.historical_data["orchestrations"]
        
        # Calculate trends
        success_rates = [o.get("success_rate", 0) for o in orchestrations]
        costs = [o.get("cost", 0) for o in orchestrations]
        durations = [o.get("duration", 0) for o in orchestrations]
        
        return {
            "total_orchestrations": len(orchestrations),
            "average_success_rate": sum(success_rates) / len(success_rates) if success_rates else 0,
            "success_rate_trend": "improving" if len(success_rates) > 1 and success_rates[-1] > success_rates[0] else "stable",
            "average_cost": sum(costs) / len(costs) if costs else 0,
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "recommendations": self._generate_recommendations(success_rates, costs, durations)
        }
    
    def _extract_patterns(self, outcome: Dict[str, Any]) -> None:
        """Extract patterns from orchestration outcome."""
        success_rate = outcome.get("success_rate", 0)
        
        # Track high-performing task types
        if success_rate > 0.7:
            for task in outcome.get("tasks", []):
                task_type = task.get("type", "unknown")
                if task_type not in self.historical_data["patterns"]:
                    self.historical_data["patterns"][task_type] = {"success_count": 0, "total_count": 0}
                self.historical_data["patterns"][task_type]["success_count"] += 1
                self.historical_data["patterns"][task_type]["total_count"] += 1
    
    def _get_successful_strategies(self) -> List[Dict[str, Any]]:
        """Get list of successful strategies from history."""
        successful = [
            o for o in self.historical_data["orchestrations"]
            if o.get("success_rate", 0) > 0.7
        ]
        return successful[-5:]  # Return last 5 successful orchestrations
    
    def _get_common_failures(self) -> List[str]:
        """Identify common failure patterns."""
        failures = []
        for orchestration in self.historical_data["orchestrations"]:
            for result in orchestration.get("results", {}).get("job_details", []):
                if result.get("status") == "failed":
                    failures.append(result.get("error_message", "Unknown error"))
        
        # Count frequency
        from collections import Counter
        failure_counts = Counter(failures)
        return [f"{msg} ({count} times)" for msg, count in failure_counts.most_common(5)]
    
    def _get_optimal_parameters(self) -> Dict[str, Any]:
        """Determine optimal parameters based on historical performance."""
        if not self.historical_data["orchestrations"]:
            return {"max_workers": 20, "budget_limit": 2.0}
        
        # Find parameters from most successful orchestration
        best = max(
            self.historical_data["orchestrations"],
            key=lambda x: x.get("success_rate", 0),
            default={}
        )
        
        return {
            "max_workers": best.get("max_workers", 20),
            "budget_limit": best.get("budget_limit", 2.0),
            "retry_strategy": best.get("retry_strategy", "exponential_backoff")
        }
    
    def _get_performance_trends(self) -> Dict[str, str]:
        """Analyze performance trends."""
        if len(self.historical_data["orchestrations"]) < 2:
            return {"status": "insufficient_data"}
        
        recent = self.historical_data["orchestrations"][-5:]
        older = self.historical_data["orchestrations"][:-5]
        
        recent_success = sum(o.get("success_rate", 0) for o in recent) / len(recent)
        older_success = sum(o.get("success_rate", 0) for o in older) / len(older) if older else 0
        
        return {
            "trend": "improving" if recent_success > older_success else "declining",
            "recent_average": f"{recent_success:.1%}",
            "historical_average": f"{older_success:.1%}"
        }
    
    def _generate_recommendations(self, success_rates: List[float], costs: List[float], durations: List[float]) -> List[str]:
        """Generate recommendations based on performance data."""
        recommendations = []
        
        if success_rates and success_rates[-1] < 0.5:
            recommendations.append("Consider revising task selection strategy - recent success rate is low")
        
        if costs and costs[-1] > 2.0:
            recommendations.append("Cost exceeding budget - optimize model selection or reduce task complexity")
        
        if durations and durations[-1] > 60:
            recommendations.append("Execution taking too long - increase parallelization or simplify tasks")
        
        if not recommendations:
            recommendations.append("Performance is optimal - continue current strategy")
        
        return recommendations
    
    def _save_learning(self) -> None:
        """Save learning data to persistent storage."""
        with open(self.learning_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)
    
    def get_learning_summary(self) -> str:
        """
        Get a human-readable summary of learning insights.
        
        Returns:
            String summary of key learnings
            
        Agent Usage:
            print(learning.get_learning_summary())
        """
        trends = self.analyze_performance_trends()
        patterns = self.retrieve_learning_patterns()
        
        summary = f"""
Enhanced Father Learning Summary
================================
Total Orchestrations: {trends.get('total_orchestrations', 0)}
Average Success Rate: {trends.get('average_success_rate', 0):.1%}
Success Trend: {trends.get('success_rate_trend', 'unknown')}
Average Cost: ${trends.get('average_cost', 0):.2f}
Average Duration: {trends.get('average_duration', 0):.1f} minutes

Key Insights:
- {', '.join(trends.get('recommendations', ['No recommendations yet']))}

Common Failures:
{chr(10).join(f'- {f}' for f in patterns.get('common_failures', ['None identified'])[:3])}

Optimal Parameters:
- Max Workers: {patterns.get('optimal_parameters', {}).get('max_workers', 20)}
- Budget Limit: ${patterns.get('optimal_parameters', {}).get('budget_limit', 2.0):.2f}
"""
        return summary


# Agent-friendly interface
def create_learning_system() -> EnhancedFatherLearning:
    """
    Create a learning system instance for Enhanced Father.
    
    Returns:
        Configured EnhancedFatherLearning instance
        
    Agent Usage:
        from ai.memory.enhanced_father_learning import create_learning_system
        learning = create_learning_system()
        learning.store_orchestration_outcome(results)
    """
    return EnhancedFatherLearning()
