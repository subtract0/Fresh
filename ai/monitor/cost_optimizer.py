"""
Cost Optimization Utilities

Advanced cost optimization tools for analyzing usage patterns,
identifying waste, and providing actionable recommendations.

Features:
- Usage pattern analysis
- Cost anomaly detection
- Model optimization suggestions
- Batch operation recommendations
- Rate limiting guidance
- Cost forecasting
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass

from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType, UsageRecord

logger = logging.getLogger(__name__)


@dataclass
class OptimizationRecommendation:
    """Single optimization recommendation."""
    title: str
    description: str
    potential_savings_usd: float
    effort_level: str  # "Low", "Medium", "High"
    category: str  # "Model", "Batching", "Caching", "Rate Limiting"
    implementation_notes: str
    priority: int  # 1-10, higher is more important


@dataclass
class UsagePattern:
    """Detected usage pattern."""
    pattern_type: str
    frequency: int
    cost_impact: float
    description: str
    recommendations: List[str]


class CostOptimizer:
    """Advanced cost optimization analyzer."""
    
    def __init__(self):
        self.cost_tracker = get_cost_tracker()
        
    def analyze_usage_patterns(self, days: int = 30) -> List[UsagePattern]:
        """Analyze usage patterns to identify optimization opportunities."""
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        recent_records = [
            r for r in self.cost_tracker.usage_records 
            if r.timestamp >= cutoff_date
        ]
        
        patterns = []
        
        # Pattern 1: High-cost model usage
        patterns.extend(self._detect_high_cost_model_patterns(recent_records))
        
        # Pattern 2: Inefficient batching
        patterns.extend(self._detect_batching_opportunities(recent_records))
        
        # Pattern 3: Repeated similar operations
        patterns.extend(self._detect_repetitive_operations(recent_records))
        
        # Pattern 4: Peak usage times
        patterns.extend(self._detect_usage_spikes(recent_records))
        
        # Pattern 5: Firestore read/write patterns
        patterns.extend(self._detect_firestore_inefficiencies(recent_records))
        
        return patterns
        
    def _detect_high_cost_model_patterns(self, records: List[UsageRecord]) -> List[UsagePattern]:
        """Detect patterns with high-cost models that could be optimized."""
        patterns = []
        
        # Group by model
        model_usage = defaultdict(lambda: {"count": 0, "cost": 0.0, "tokens": 0})
        
        for record in records:
            if record.service == ServiceType.OPENAI and record.model:
                model_usage[record.model]["count"] += 1
                model_usage[record.model]["cost"] += record.estimated_cost_usd
                model_usage[record.model]["tokens"] += record.quantity
                
        # Identify expensive model usage
        for model, usage in model_usage.items():
            if "gpt-4" in model and usage["cost"] > 1.0:  # >$1 in period
                # Calculate potential savings with GPT-3.5
                gpt35_cost = (usage["tokens"] / 1000.0) * 0.001  # GPT-3.5 pricing
                potential_savings = usage["cost"] - gpt35_cost
                
                if potential_savings > 0.1:  # Worth optimizing
                    patterns.append(UsagePattern(
                        pattern_type="high_cost_model",
                        frequency=usage["count"],
                        cost_impact=usage["cost"],
                        description=f"{model} usage: {usage['count']} calls, ${usage['cost']:.2f}",
                        recommendations=[
                            f"Consider GPT-3.5-turbo for simpler tasks (potential savings: ${potential_savings:.2f})",
                            "Evaluate if GPT-4 complexity is required for all use cases",
                            "Implement model selection logic based on task complexity"
                        ]
                    ))
        
        return patterns
        
    def _detect_batching_opportunities(self, records: List[UsageRecord]) -> List[UsagePattern]:
        """Detect opportunities for batching operations."""
        patterns = []
        
        # Group Firestore operations by collection and time windows
        firestore_ops = [r for r in records if r.service == ServiceType.FIRESTORE]
        
        # Group by 5-minute windows
        time_groups = defaultdict(lambda: defaultdict(int))
        
        for record in firestore_ops:
            time_key = record.timestamp.replace(minute=record.timestamp.minute // 5 * 5, second=0, microsecond=0)
            collection = record.metadata.get("collection", "unknown")
            time_groups[time_key][f"{collection}_{record.operation.value}"] += 1
            
        # Find high-frequency operations that could be batched
        for time_key, ops in time_groups.items():
            for op_key, count in ops.items():
                if count >= 10:  # 10+ operations in 5 minutes
                    collection, operation = op_key.rsplit("_", 1)
                    
                    patterns.append(UsagePattern(
                        pattern_type="batching_opportunity",
                        frequency=count,
                        cost_impact=count * 0.00000108,  # Firestore operation cost
                        description=f"High-frequency {operation} operations on {collection}: {count} in 5 minutes",
                        recommendations=[
                            f"Batch {operation} operations to reduce API calls",
                            "Implement operation queuing with periodic flushes",
                            "Consider using Firestore batch writes for multiple operations"
                        ]
                    ))
        
        return patterns
        
    def _detect_repetitive_operations(self, records: List[UsageRecord]) -> List[UsagePattern]:
        """Detect repetitive operations that could benefit from caching."""
        patterns = []
        
        # Look for repeated OpenAI calls with similar content
        openai_records = [r for r in records if r.service == ServiceType.OPENAI]
        
        # Simple content similarity detection (could be enhanced)
        content_patterns = defaultdict(int)
        
        for record in openai_records:
            # Create a simple fingerprint of the operation
            fingerprint = f"{record.model}_{record.operation.value}_{record.quantity//100*100}"  # Round to nearest 100 tokens
            content_patterns[fingerprint] += 1
            
        # Identify highly repetitive patterns
        for pattern, count in content_patterns.items():
            if count >= 5:  # 5+ similar operations
                model, operation, token_range = pattern.split("_")
                
                patterns.append(UsagePattern(
                    pattern_type="repetitive_operations",
                    frequency=count,
                    cost_impact=count * 0.002,  # Estimated cost
                    description=f"Repetitive {model} {operation} calls (~{token_range} tokens): {count} times",
                    recommendations=[
                        "Implement response caching for similar requests",
                        "Consider using embeddings for semantic similarity matching",
                        "Add request deduplication logic"
                    ]
                ))
        
        return patterns
        
    def _detect_usage_spikes(self, records: List[UsageRecord]) -> List[UsagePattern]:
        """Detect usage spikes that might indicate inefficient patterns."""
        patterns = []
        
        # Group by hour
        hourly_costs = defaultdict(float)
        hourly_counts = defaultdict(int)
        
        for record in records:
            hour_key = record.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_costs[hour_key] += record.estimated_cost_usd
            hourly_counts[hour_key] += 1
            
        if not hourly_costs:
            return patterns
            
        # Calculate average and find spikes
        avg_cost = sum(hourly_costs.values()) / len(hourly_costs)
        avg_count = sum(hourly_counts.values()) / len(hourly_counts)
        
        spike_threshold = avg_cost * 3  # 3x average is a spike
        
        for hour, cost in hourly_costs.items():
            if cost > spike_threshold:
                count = hourly_counts[hour]
                
                patterns.append(UsagePattern(
                    pattern_type="usage_spike",
                    frequency=count,
                    cost_impact=cost,
                    description=f"Usage spike at {hour.strftime('%Y-%m-%d %H:%M')}: ${cost:.2f} ({count} operations)",
                    recommendations=[
                        "Investigate what caused the usage spike",
                        "Consider implementing rate limiting",
                        "Add monitoring alerts for unusual usage patterns"
                    ]
                ))
        
        return patterns
        
    def _detect_firestore_inefficiencies(self, records: List[UsageRecord]) -> List[UsagePattern]:
        """Detect inefficient Firestore usage patterns."""
        patterns = []
        
        firestore_records = [r for r in records if r.service == ServiceType.FIRESTORE]
        
        # Analyze read/write ratios by collection
        collection_stats = defaultdict(lambda: {"reads": 0, "writes": 0, "deletes": 0})
        
        for record in firestore_records:
            collection = record.metadata.get("collection", "unknown")
            collection_stats[collection][record.operation.value + "s"] += record.quantity
            
        # Identify collections with high read-to-write ratios (caching opportunity)
        for collection, stats in collection_stats.items():
            total_reads = stats["reads"]
            total_writes = stats["writes"]
            
            if total_reads > 0 and total_writes > 0:
                read_write_ratio = total_reads / total_writes
                
                if read_write_ratio > 10:  # 10:1 read/write ratio
                    cost_impact = total_reads * 0.00000036  # Read cost
                    
                    patterns.append(UsagePattern(
                        pattern_type="high_read_ratio",
                        frequency=total_reads,
                        cost_impact=cost_impact,
                        description=f"Collection '{collection}': {total_reads} reads vs {total_writes} writes (ratio: {read_write_ratio:.1f}:1)",
                        recommendations=[
                            "Implement local caching for frequently read data",
                            "Consider using Firestore offline persistence",
                            "Evaluate if all reads are necessary"
                        ]
                    ))
        
        return patterns
        
    def generate_recommendations(self, days: int = 30) -> List[OptimizationRecommendation]:
        """Generate comprehensive optimization recommendations."""
        
        patterns = self.analyze_usage_patterns(days)
        usage_summary = self.cost_tracker.get_usage_summary(days)
        recommendations = []
        
        # Convert patterns to recommendations
        for pattern in patterns:
            if pattern.pattern_type == "high_cost_model":
                recommendations.append(OptimizationRecommendation(
                    title="Optimize Model Selection",
                    description=pattern.description,
                    potential_savings_usd=pattern.cost_impact * 0.7,  # Estimated 70% savings
                    effort_level="Medium",
                    category="Model",
                    implementation_notes="Implement task complexity analysis to choose appropriate models",
                    priority=8
                ))
                
            elif pattern.pattern_type == "batching_opportunity":
                recommendations.append(OptimizationRecommendation(
                    title="Implement Operation Batching",
                    description=pattern.description,
                    potential_savings_usd=pattern.cost_impact * 0.3,  # 30% savings from batching
                    effort_level="Medium",
                    category="Batching",
                    implementation_notes="Use Firestore batch operations and implement operation queuing",
                    priority=6
                ))
                
            elif pattern.pattern_type == "repetitive_operations":
                recommendations.append(OptimizationRecommendation(
                    title="Add Response Caching",
                    description=pattern.description,
                    potential_savings_usd=pattern.cost_impact * 0.8,  # 80% savings from caching
                    effort_level="Low",
                    category="Caching", 
                    implementation_notes="Implement in-memory or Redis caching for repeated operations",
                    priority=9
                ))
                
            elif pattern.pattern_type == "high_read_ratio":
                recommendations.append(OptimizationRecommendation(
                    title="Implement Data Caching",
                    description=pattern.description,
                    potential_savings_usd=pattern.cost_impact * 0.5,  # 50% reduction in reads
                    effort_level="Low",
                    category="Caching",
                    implementation_notes="Add local caching layer for frequently accessed data",
                    priority=7
                ))
                
            elif pattern.pattern_type == "usage_spike":
                recommendations.append(OptimizationRecommendation(
                    title="Add Rate Limiting and Monitoring",
                    description=pattern.description,
                    potential_savings_usd=pattern.cost_impact * 0.2,  # 20% reduction from controlled usage
                    effort_level="Medium",
                    category="Rate Limiting",
                    implementation_notes="Implement rate limiting and usage monitoring alerts",
                    priority=5
                ))
        
        # Add general recommendations based on overall usage
        total_cost = usage_summary["total_cost_usd"]
        
        if total_cost > 50.0:  # High usage overall
            recommendations.append(OptimizationRecommendation(
                title="Implement Comprehensive Cost Monitoring",
                description=f"Total cost in {days} days: ${total_cost:.2f}",
                potential_savings_usd=total_cost * 0.15,  # 15% potential reduction
                effort_level="Low",
                category="Monitoring",
                implementation_notes="Set up budget alerts, usage dashboards, and regular cost reviews",
                priority=10
            ))
        
        # Sort by priority (highest first)
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        
        return recommendations
        
    def forecast_monthly_cost(self, days_history: int = 7) -> Dict[str, Any]:
        """Forecast monthly costs based on recent usage trends."""
        
        recent_usage = self.cost_tracker.get_usage_summary(days_history)
        daily_average = recent_usage["total_cost_usd"] / days_history
        
        # Simple linear projection
        monthly_forecast = daily_average * 30
        
        # Calculate trend
        half_period = days_history // 2
        first_half = self.cost_tracker.get_usage_summary(half_period)["total_cost_usd"]
        second_half_days = days_history - half_period
        second_half = recent_usage["total_cost_usd"] - first_half
        
        if half_period > 0:
            first_half_daily = first_half / half_period
            second_half_daily = second_half / second_half_days
            trend = (second_half_daily - first_half_daily) / first_half_daily if first_half_daily > 0 else 0
        else:
            trend = 0
            
        # Adjust forecast based on trend
        trend_adjusted_forecast = monthly_forecast * (1 + trend)
        
        # Service breakdown forecast
        service_forecasts = {}
        for service, data in recent_usage["service_breakdown"].items():
            daily_service_cost = data["cost"] / days_history
            service_forecasts[service] = daily_service_cost * 30
            
        return {
            "daily_average": daily_average,
            "monthly_forecast_linear": monthly_forecast,
            "monthly_forecast_trend_adjusted": trend_adjusted_forecast,
            "trend_percentage": trend * 100,
            "service_forecasts": service_forecasts,
            "confidence_level": "medium" if days_history >= 7 else "low",
            "based_on_days": days_history
        }
        
    def get_cost_breakdown_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed cost breakdown analysis."""
        
        usage = self.cost_tracker.get_usage_summary(days)
        
        # Analyze service costs
        service_analysis = {}
        for service, data in usage["service_breakdown"].items():
            percentage = (data["cost"] / max(usage["total_cost_usd"], 0.0001)) * 100
            
            service_analysis[service] = {
                "cost": data["cost"],
                "percentage": percentage,
                "operations": data["operations"],
                "avg_cost_per_operation": data["cost"] / max(data["operations"], 1),
                "optimization_priority": self._get_service_optimization_priority(service, data, percentage)
            }
            
        # Top expensive operations
        top_operations = usage["top_expensive_operations"][:10]
        
        return {
            "total_cost": usage["total_cost_usd"],
            "total_operations": usage["total_operations"],
            "service_analysis": service_analysis,
            "top_expensive_operations": top_operations,
            "cost_per_operation": usage["average_cost_per_operation"],
            "analysis_period_days": days
        }
        
    def _get_service_optimization_priority(self, service: str, data: Dict, percentage: float) -> str:
        """Determine optimization priority for a service."""
        
        if percentage > 50:
            return "High - Major cost contributor"
        elif percentage > 20:
            return "Medium - Significant cost contributor" 
        elif data["operations"] > 1000:
            return "Medium - High volume usage"
        else:
            return "Low - Minor cost contributor"


def get_cost_optimizer() -> CostOptimizer:
    """Get cost optimizer instance."""
    return CostOptimizer()


def quick_optimization_report(days: int = 7) -> Dict[str, Any]:
    """Generate a quick optimization report."""
    optimizer = CostOptimizer()
    
    recommendations = optimizer.generate_recommendations(days)
    patterns = optimizer.analyze_usage_patterns(days)
    forecast = optimizer.forecast_monthly_cost(days)
    
    return {
        "analysis_period_days": days,
        "total_recommendations": len(recommendations),
        "high_priority_recommendations": len([r for r in recommendations if r.priority >= 8]),
        "potential_monthly_savings": sum(r.potential_savings_usd for r in recommendations) * (30 / days),
        "patterns_detected": len(patterns),
        "monthly_cost_forecast": forecast["monthly_forecast_trend_adjusted"],
        "top_recommendations": [
            {
                "title": r.title,
                "savings": r.potential_savings_usd,
                "effort": r.effort_level,
                "category": r.category
            }
            for r in recommendations[:5]
        ]
    }
