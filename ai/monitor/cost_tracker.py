"""
Cost Monitoring System for Fresh AI

Comprehensive cost tracking and monitoring for:
- Firebase Firestore operations (reads, writes, deletes)
- OpenAI API usage (tokens, requests, models)
- Google API usage (various services)

Features:
- Real-time usage tracking
- Cost estimation based on current pricing
- Budget management and alerts
- Usage analytics and optimization recommendations
- Integration with existing monitoring system
"""
from __future__ import annotations
import os
import json
import time
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Supported services for cost tracking."""
    FIRESTORE = "firestore"
    OPENAI = "openai"
    GOOGLE_API = "google_api"


class OperationType(Enum):
    """Types of operations being tracked."""
    # Firestore operations
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    
    # OpenAI operations
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    
    # Generic API operations
    REQUEST = "request"


@dataclass
class UsageRecord:
    """Individual usage record for cost tracking."""
    service: ServiceType
    operation: OperationType
    timestamp: datetime
    quantity: int  # reads, writes, tokens, requests
    model: Optional[str] = None  # For OpenAI models
    metadata: Dict[str, Any] = field(default_factory=dict)
    estimated_cost_usd: float = 0.0


@dataclass
class ServicePricing:
    """Pricing information for a service."""
    service: ServiceType
    pricing_per_unit: Dict[str, float]  # operation -> price per unit
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BudgetAlert:
    """Budget alert configuration."""
    service: Optional[ServiceType]  # None for total budget
    threshold_percentage: float  # 0.0 to 1.0
    monthly_limit_usd: float
    is_enabled: bool = True
    last_triggered: Optional[datetime] = None


class CostTracker:
    """Main cost tracking and monitoring system."""
    
    def __init__(self, data_dir: str = "data/cost_monitoring"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.usage_records: List[UsageRecord] = []
        self.budget_alerts: List[BudgetAlert] = []
        self.pricing: Dict[ServiceType, ServicePricing] = {}
        
        self._load_data()
        self._initialize_default_pricing()
        
        # Usage caches for performance
        self._daily_cache: Dict[str, Dict[str, float]] = {}
        self._monthly_cache: Dict[str, Dict[str, float]] = {}
        self._last_cache_update = datetime.now(timezone.utc)
        
    def _load_data(self):
        """Load existing usage records and configuration."""
        try:
            # Load usage records
            usage_file = self.data_dir / "usage_records.json"
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    for record_data in data:
                        record = UsageRecord(
                            service=ServiceType(record_data["service"]),
                            operation=OperationType(record_data["operation"]),
                            timestamp=datetime.fromisoformat(record_data["timestamp"]),
                            quantity=record_data["quantity"],
                            model=record_data.get("model"),
                            metadata=record_data.get("metadata", {}),
                            estimated_cost_usd=record_data.get("estimated_cost_usd", 0.0)
                        )
                        self.usage_records.append(record)
                        
            # Load budget alerts
            alerts_file = self.data_dir / "budget_alerts.json"
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    data = json.load(f)
                    for alert_data in data:
                        alert = BudgetAlert(
                            service=ServiceType(alert_data["service"]) if alert_data.get("service") else None,
                            threshold_percentage=alert_data["threshold_percentage"],
                            monthly_limit_usd=alert_data["monthly_limit_usd"],
                            is_enabled=alert_data.get("is_enabled", True),
                            last_triggered=datetime.fromisoformat(alert_data["last_triggered"]) if alert_data.get("last_triggered") else None
                        )
                        self.budget_alerts.append(alert)
                        
            logger.info(f"📊 Loaded {len(self.usage_records)} usage records, {len(self.budget_alerts)} budget alerts")
            
        except Exception as e:
            logger.error(f"Failed to load cost monitoring data: {e}")
            
    def _save_data(self):
        """Save usage records and configuration."""
        try:
            # Save usage records (keep only last 90 days to manage size)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            recent_records = [r for r in self.usage_records if r.timestamp >= cutoff_date]
            
            usage_file = self.data_dir / "usage_records.json"
            with open(usage_file, 'w') as f:
                records_data = []
                for record in recent_records:
                    records_data.append({
                        "service": record.service.value,
                        "operation": record.operation.value,
                        "timestamp": record.timestamp.isoformat(),
                        "quantity": record.quantity,
                        "model": record.model,
                        "metadata": record.metadata,
                        "estimated_cost_usd": record.estimated_cost_usd
                    })
                json.dump(records_data, f, indent=2)
                
            # Save budget alerts
            alerts_file = self.data_dir / "budget_alerts.json"
            with open(alerts_file, 'w') as f:
                alerts_data = []
                for alert in self.budget_alerts:
                    alerts_data.append({
                        "service": alert.service.value if alert.service else None,
                        "threshold_percentage": alert.threshold_percentage,
                        "monthly_limit_usd": alert.monthly_limit_usd,
                        "is_enabled": alert.is_enabled,
                        "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None
                    })
                json.dump(alerts_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save cost monitoring data: {e}")
            
    def _initialize_default_pricing(self):
        """Initialize default pricing for supported services."""
        # Current pricing as of 2024 (update regularly!)
        
        # OpenAI pricing (per 1K tokens)
        openai_pricing = ServicePricing(
            service=ServiceType.OPENAI,
            pricing_per_unit={
                # GPT-4 models
                "gpt-4": 0.03,  # input per 1K tokens
                "gpt-4-output": 0.06,  # output per 1K tokens
                "gpt-4-turbo": 0.01,
                "gpt-4-turbo-output": 0.03,
                
                # GPT-3.5 models
                "gpt-3.5-turbo": 0.001,
                "gpt-3.5-turbo-output": 0.002,
                
                # Embeddings
                "text-embedding-3-small": 0.00002,
                "text-embedding-3-large": 0.00013,
                "text-embedding-ada-002": 0.0001,
            }
        )
        
        # Firestore pricing
        firestore_pricing = ServicePricing(
            service=ServiceType.FIRESTORE,
            pricing_per_unit={
                "read": 0.00000036,  # per document read
                "write": 0.00000108,  # per document write
                "delete": 0.00000108,  # per document delete
            }
        )
        
        # Google API pricing (generic - adjust per service)
        google_api_pricing = ServicePricing(
            service=ServiceType.GOOGLE_API,
            pricing_per_unit={
                "request": 0.001,  # Generic API request cost
            }
        )
        
        self.pricing[ServiceType.OPENAI] = openai_pricing
        self.pricing[ServiceType.FIRESTORE] = firestore_pricing
        self.pricing[ServiceType.GOOGLE_API] = google_api_pricing
        
    def record_usage(
        self,
        service: ServiceType,
        operation: OperationType,
        quantity: int,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UsageRecord:
        """Record a usage event and calculate estimated cost."""
        
        # Calculate estimated cost
        cost = self._calculate_cost(service, operation, quantity, model)
        
        # Create usage record
        record = UsageRecord(
            service=service,
            operation=operation,
            timestamp=datetime.now(timezone.utc),
            quantity=quantity,
            model=model,
            metadata=metadata or {},
            estimated_cost_usd=cost
        )
        
        self.usage_records.append(record)
        
        # Clear cache to force recalculation
        self._clear_cache()
        
        # Check budget alerts (only in async context)
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._check_budget_alerts())
        except RuntimeError:
            # No event loop running, skip async budget check
            pass
        
        # Periodic save (every 100 records or 10 minutes)
        if len(self.usage_records) % 100 == 0:
            self._save_data()
            
        return record
        
    def _calculate_cost(
        self,
        service: ServiceType,
        operation: OperationType,
        quantity: int,
        model: Optional[str] = None
    ) -> float:
        """Calculate estimated cost for an operation."""
        
        if service not in self.pricing:
            return 0.0
            
        pricing = self.pricing[service]
        
        if service == ServiceType.OPENAI and model:
            # For OpenAI, use model-specific pricing
            if model in pricing.pricing_per_unit:
                return (quantity / 1000.0) * pricing.pricing_per_unit[model]
            else:
                # Default to GPT-3.5 pricing if model unknown
                return (quantity / 1000.0) * pricing.pricing_per_unit.get("gpt-3.5-turbo", 0.001)
                
        elif operation.value in pricing.pricing_per_unit:
            return quantity * pricing.pricing_per_unit[operation.value]
            
        return 0.0
        
    def get_usage_summary(
        self,
        service: Optional[ServiceType] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage summary for specified period."""
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Filter records
        filtered_records = [
            r for r in self.usage_records 
            if r.timestamp >= cutoff_date and (service is None or r.service == service)
        ]
        
        # Aggregate data
        total_cost = sum(r.estimated_cost_usd for r in filtered_records)
        total_operations = len(filtered_records)
        
        # Break down by service and operation
        service_breakdown = {}
        operation_breakdown = {}
        
        for record in filtered_records:
            # Service breakdown
            service_key = record.service.value
            if service_key not in service_breakdown:
                service_breakdown[service_key] = {
                    "operations": 0,
                    "cost": 0.0,
                    "quantity": 0
                }
            service_breakdown[service_key]["operations"] += 1
            service_breakdown[service_key]["cost"] += record.estimated_cost_usd
            service_breakdown[service_key]["quantity"] += record.quantity
            
            # Operation breakdown
            op_key = f"{record.service.value}_{record.operation.value}"
            if op_key not in operation_breakdown:
                operation_breakdown[op_key] = {
                    "operations": 0,
                    "cost": 0.0,
                    "quantity": 0
                }
            operation_breakdown[op_key]["operations"] += 1
            operation_breakdown[op_key]["cost"] += record.estimated_cost_usd
            operation_breakdown[op_key]["quantity"] += record.quantity
        
        return {
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_operations": total_operations,
            "average_cost_per_operation": round(total_cost / max(total_operations, 1), 6),
            "service_breakdown": service_breakdown,
            "operation_breakdown": operation_breakdown,
            "top_expensive_operations": sorted(
                operation_breakdown.items(),
                key=lambda x: x[1]["cost"],
                reverse=True
            )[:10]
        }
        
    def get_monthly_usage(self, year: int, month: int) -> Dict[str, Any]:
        """Get detailed usage for a specific month."""
        
        # Filter records for the month
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
        monthly_records = [
            r for r in self.usage_records
            if start_date <= r.timestamp < end_date
        ]
        
        # Daily breakdown
        daily_usage = {}
        for record in monthly_records:
            day = record.timestamp.day
            if day not in daily_usage:
                daily_usage[day] = {"cost": 0.0, "operations": 0}
            daily_usage[day]["cost"] += record.estimated_cost_usd
            daily_usage[day]["operations"] += 1
            
        total_cost = sum(r.estimated_cost_usd for r in monthly_records)
        
        return {
            "year": year,
            "month": month,
            "total_cost_usd": round(total_cost, 4),
            "total_operations": len(monthly_records),
            "daily_breakdown": daily_usage,
            "records_count": len(monthly_records)
        }
        
    def add_budget_alert(
        self,
        monthly_limit_usd: float,
        threshold_percentage: float = 0.8,
        service: Optional[ServiceType] = None
    ) -> BudgetAlert:
        """Add a budget alert."""
        
        alert = BudgetAlert(
            service=service,
            threshold_percentage=threshold_percentage,
            monthly_limit_usd=monthly_limit_usd
        )
        
        self.budget_alerts.append(alert)
        self._save_data()
        
        return alert
        
    async def _check_budget_alerts(self):
        """Check if any budget alerts should be triggered."""
        
        current_month = datetime.now(timezone.utc)
        monthly_usage = self.get_monthly_usage(current_month.year, current_month.month)
        
        for alert in self.budget_alerts:
            if not alert.is_enabled:
                continue
                
            # Calculate current usage for this alert
            if alert.service:
                # Service-specific alert
                service_usage = 0.0
                for record in self.usage_records:
                    if (record.service == alert.service and 
                        record.timestamp.year == current_month.year and 
                        record.timestamp.month == current_month.month):
                        service_usage += record.estimated_cost_usd
                current_usage = service_usage
            else:
                # Total budget alert
                current_usage = monthly_usage["total_cost_usd"]
                
            # Check if threshold exceeded
            threshold_amount = alert.monthly_limit_usd * alert.threshold_percentage
            
            if current_usage >= threshold_amount:
                # Check if we already triggered this alert recently (within 24h)
                if (alert.last_triggered and 
                    datetime.now(timezone.utc) - alert.last_triggered < timedelta(hours=24)):
                    continue
                    
                # Trigger alert
                await self._trigger_budget_alert(alert, current_usage, monthly_usage["total_cost_usd"])
                alert.last_triggered = datetime.now(timezone.utc)
                
    async def _trigger_budget_alert(self, alert: BudgetAlert, current_usage: float, total_usage: float):
        """Trigger a budget alert notification."""
        
        service_name = alert.service.value if alert.service else "Total"
        percentage = (current_usage / alert.monthly_limit_usd) * 100
        
        message = f"🚨 BUDGET ALERT: {service_name} usage\n\n"
        message += f"💰 Current usage: ${current_usage:.2f}\n"
        message += f"📊 Budget limit: ${alert.monthly_limit_usd:.2f}\n"
        message += f"📈 Usage: {percentage:.1f}% of budget\n"
        message += f"🗓 Total monthly usage: ${total_usage:.2f}\n\n"
        message += f"⚠️ Threshold: {alert.threshold_percentage * 100:.0f}%"
        
        logger.warning(f"Budget alert triggered: {service_name} - ${current_usage:.2f}")
        
        # Send notification via Telegram if available
        try:
            from ai.interface.telegram_bot import get_bot_instance
            
            bot = get_bot_instance()
            if bot:
                # Send to admin users or configured channels
                admin_chat_id = os.getenv("COST_ALERT_CHAT_ID")
                if admin_chat_id:
                    await bot.send_message(chat_id=admin_chat_id, text=message)
                    
        except Exception as e:
            logger.error(f"Failed to send budget alert notification: {e}")
            
    def _clear_cache(self):
        """Clear usage caches."""
        self._daily_cache.clear()
        self._monthly_cache.clear()
        self._last_cache_update = datetime.now(timezone.utc)
        
    def get_optimization_suggestions(self) -> List[str]:
        """Get cost optimization suggestions based on usage patterns."""
        
        suggestions = []
        
        # Get recent usage
        recent_usage = self.get_usage_summary(days=7)
        
        # Check for expensive operations
        expensive_ops = recent_usage["top_expensive_operations"][:5]
        
        for op_name, op_data in expensive_ops:
            if "openai" in op_name and op_data["cost"] > 1.0:  # > $1/week
                if "gpt-4" in op_name:
                    suggestions.append(
                        f"Consider using GPT-3.5-turbo instead of GPT-4 for {op_name} "
                        f"(current weekly cost: ${op_data['cost']:.2f})"
                    )
                    
            elif "firestore" in op_name and op_data["operations"] > 1000:  # > 1000 ops/week
                suggestions.append(
                    f"High Firestore {op_name} usage ({op_data['operations']} operations/week). "
                    f"Consider caching or batch operations."
                )
                
        # Check for patterns
        if recent_usage["total_cost_usd"] > 10.0:  # > $10/week
            suggestions.append(
                f"Weekly costs are ${recent_usage['total_cost_usd']:.2f}. "
                f"Consider implementing cost controls or optimization."
            )
            
        return suggestions
        
    def export_usage_report(self, filepath: str, days: int = 30):
        """Export detailed usage report to JSON file."""
        
        summary = self.get_usage_summary(days=days)
        
        # Add additional details
        report = {
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "period_days": days,
            "summary": summary,
            "budget_alerts": [
                {
                    "service": alert.service.value if alert.service else "total",
                    "limit": alert.monthly_limit_usd,
                    "threshold": alert.threshold_percentage,
                    "enabled": alert.is_enabled
                }
                for alert in self.budget_alerts
            ],
            "pricing_info": {
                service.value: {
                    "pricing_per_unit": pricing.pricing_per_unit,
                    "last_updated": pricing.last_updated.isoformat()
                }
                for service, pricing in self.pricing.items()
            },
            "optimization_suggestions": self.get_optimization_suggestions()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📊 Cost report exported to {filepath}")


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
