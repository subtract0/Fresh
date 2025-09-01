# Cost Monitoring System

Comprehensive cost monitoring and optimization for Firebase Firestore, OpenAI API, and Google APIs in the Fresh AI system.

## Overview

The cost monitoring system provides:

- **Real-time Usage Tracking**: Automatic tracking of API calls, tokens, and operations
- **Cost Estimation**: Real-time cost calculation based on current pricing
- **Budget Management**: Configurable budget alerts and limits
- **Optimization Recommendations**: AI-powered suggestions for cost reduction
- **Interactive Dashboard**: Rich terminal UI for monitoring and management
- **Integration-Ready**: Drop-in wrappers for existing API clients

## Quick Start

### 1. Setup Cost Monitoring

```bash
# Basic setup with default budget alerts
python scripts/setup_cost_monitoring.py

# Run with demo data to see it in action
python scripts/setup_cost_monitoring.py --demo

# Launch the interactive dashboard
python scripts/setup_cost_monitoring.py --dashboard
```

### 2. Integrate with Your Code

#### Firestore Integration

```python
# Before (original Firestore usage)
from google.cloud import firestore
db = firestore.Client()

# After (with cost tracking)
from ai.monitor.firestore_tracker import wrap_firestore_client
db = wrap_firestore_client(firestore.Client())

# Use exactly as before - all operations are automatically tracked
doc_ref = db.collection('users').document('user123')
doc_ref.set({'name': 'John', 'email': 'john@example.com'})
```

#### OpenAI Integration

```python
# Before (original OpenAI usage)
import openai
client = openai.OpenAI(api_key="your-key")

# After (with cost tracking)
from ai.monitor.openai_tracker import wrap_openai_client
client = wrap_openai_client(openai.OpenAI(api_key="your-key"))

# Use exactly as before - all operations are automatically tracked
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### Manual Tracking

```python
from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType

tracker = get_cost_tracker()

# Track OpenAI usage
tracker.record_usage(
    service=ServiceType.OPENAI,
    operation=OperationType.COMPLETION,
    quantity=1500,  # tokens
    model="gpt-3.5-turbo"
)

# Track Firestore usage
tracker.record_usage(
    service=ServiceType.FIRESTORE,
    operation=OperationType.READ,
    quantity=10,  # document reads
    metadata={"collection": "users"}
)
```

### 3. Monitor Usage

#### Quick Summary

```bash
# Show quick cost summary
python scripts/setup_cost_monitoring.py --quick
```

#### Interactive Dashboard

```bash
# Launch full dashboard
python scripts/setup_cost_monitoring.py --dashboard
```

#### Programmatic Access

```python
from ai.monitor.cost_tracker import get_cost_tracker

tracker = get_cost_tracker()

# Get usage summary
summary = tracker.get_usage_summary(days=30)
print(f"Monthly cost: ${summary['total_cost_usd']:.2f}")

# Get monthly breakdown
monthly = tracker.get_monthly_usage(2024, 12)
print(f"This month: ${monthly['total_cost_usd']:.2f}")
```

## Core Components

### 1. Cost Tracker (`ai.monitor.cost_tracker`)

The central component that tracks all usage and costs.

**Key Features:**
- Records usage events with timestamps and metadata
- Calculates costs based on current pricing
- Manages budget alerts
- Provides usage analytics
- Persists data locally in JSON format

**Usage:**
```python
from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType

tracker = get_cost_tracker()

# Record usage
record = tracker.record_usage(
    service=ServiceType.OPENAI,
    operation=OperationType.COMPLETION,
    quantity=1000,
    model="gpt-3.5-turbo",
    metadata={"user_id": "123", "feature": "chat"}
)

# Get usage summary
summary = tracker.get_usage_summary(days=7)
```

### 2. Service Wrappers

#### Firestore Tracker (`ai.monitor.firestore_tracker`)

Transparent wrapper around Firestore operations:

```python
from ai.monitor.firestore_tracker import wrap_firestore_client
from google.cloud import firestore

# Wrap your existing client
db = wrap_firestore_client(firestore.Client())

# All operations are automatically tracked
docs = db.collection('users').get()  # Tracks document reads
db.collection('users').add({'name': 'Alice'})  # Tracks document write

# Batch operations are also tracked
with db.batch() as batch:
    batch.set(doc_ref1, data1)  # Will track all operations in batch
    batch.update(doc_ref2, data2)
    batch.commit()  # Tracks the batch operation
```

#### OpenAI Tracker (`ai.monitor.openai_tracker`)

Comprehensive OpenAI API tracking:

```python
from ai.monitor.openai_tracker import wrap_openai_client
import openai

# Wrap your existing client
client = wrap_openai_client(openai.OpenAI(api_key="your-key"))

# All operations are automatically tracked
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
# Automatically tracks input/output tokens and calculates cost

# Streaming is also supported
stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)
# Tracks input tokens immediately, output tokens as they arrive

# Embeddings
embeddings = client.embeddings.create(
    model="text-embedding-ada-002",
    input=["Hello", "World"]
)
# Tracks token usage and cost
```

### 3. Cost Dashboard (`ai.monitor.cost_dashboard`)

Interactive terminal dashboard built with Rich:

```python
from ai.monitor.cost_dashboard import CostDashboard, quick_cost_summary

# Quick summary
quick_cost_summary()

# Full dashboard
dashboard = CostDashboard()
await dashboard.run_dashboard()
```

**Dashboard Features:**
- Real-time usage and cost display
- Service breakdown with percentages
- Budget status with alerts
- Recent activity log
- Optimization recommendations
- Export capabilities

### 4. Cost Optimizer (`ai.monitor.cost_optimizer`)

AI-powered cost optimization and recommendations:

```python
from ai.monitor.cost_optimizer import get_cost_optimizer

optimizer = get_cost_optimizer()

# Analyze usage patterns
patterns = optimizer.analyze_usage_patterns(days=30)

# Get recommendations
recommendations = optimizer.generate_recommendations(days=30)
for rec in recommendations:
    print(f"{rec.title}: ${rec.potential_savings_usd:.2f} savings")

# Forecast costs
forecast = optimizer.forecast_monthly_cost(days_history=7)
print(f"Projected monthly cost: ${forecast['monthly_forecast_trend_adjusted']:.2f}")
```

## Budget Management

### Setting Up Budget Alerts

```python
from ai.monitor.cost_tracker import get_cost_tracker, ServiceType

tracker = get_cost_tracker()

# Total budget alert (all services)
tracker.add_budget_alert(
    monthly_limit_usd=100.0,
    threshold_percentage=0.8,  # Alert at 80%
    service=None  # All services
)

# Service-specific alerts
tracker.add_budget_alert(
    monthly_limit_usd=50.0,
    threshold_percentage=0.9,  # Alert at 90%
    service=ServiceType.OPENAI
)

tracker.add_budget_alert(
    monthly_limit_usd=25.0,
    threshold_percentage=0.8,
    service=ServiceType.FIRESTORE
)
```

### Budget Alert Configuration

Budget alerts can be configured with:
- **Monthly Limit**: Dollar amount threshold
- **Threshold Percentage**: When to trigger (0.8 = 80% of budget)
- **Service**: Specific service or None for total budget
- **Telegram Notifications**: Automatic alerts via bot (configure `COST_ALERT_CHAT_ID`)

### Environment Variables

```bash
# Optional: Telegram chat ID for budget alerts
export COST_ALERT_CHAT_ID="your-telegram-chat-id"

# Firestore configuration (if using Firestore)
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_CLIENT_EMAIL="your-service-account-email"
export FIREBASE_PRIVATE_KEY="your-private-key"
```

## Cost Optimization

### Automatic Recommendations

The system analyzes your usage patterns and provides recommendations:

1. **Model Optimization**: Suggests cheaper models for appropriate tasks
2. **Batching Opportunities**: Identifies operations that could be batched
3. **Caching Suggestions**: Finds repetitive operations that benefit from caching
4. **Usage Spike Detection**: Identifies unusual usage patterns
5. **Read/Write Ratio Analysis**: Firestore-specific optimizations

### Example Recommendations

```python
optimizer = get_cost_optimizer()
recommendations = optimizer.generate_recommendations(days=30)

for rec in recommendations:
    print(f"""
    {rec.title}
    Description: {rec.description}
    Potential Savings: ${rec.potential_savings_usd:.2f}
    Effort Level: {rec.effort_level}
    Category: {rec.category}
    Priority: {rec.priority}/10
    """)
```

### Cost Forecasting

```python
forecast = optimizer.forecast_monthly_cost(days_history=14)

print(f"Daily Average: ${forecast['daily_average']:.2f}")
print(f"Monthly Forecast: ${forecast['monthly_forecast_trend_adjusted']:.2f}")
print(f"Trend: {forecast['trend_percentage']:.1f}%")
print(f"Confidence: {forecast['confidence_level']}")
```

## Advanced Usage

### Custom Pricing

Update pricing for services:

```python
tracker = get_cost_tracker()

# Update OpenAI pricing
openai_pricing = tracker.pricing[ServiceType.OPENAI]
openai_pricing.pricing_per_unit["gpt-4"] = 0.03  # Update price
```

### Export and Reporting

```python
# Export detailed report
tracker.export_usage_report("cost_report_2024_12.json", days=30)

# Get detailed analytics
analytics = tracker.get_production_analytics()  # If using Firestore store
```

### Integration with Monitoring

The cost monitoring is integrated with the existing monitoring system:

```python
from ai.monitor.status import get_status

status = get_status()
cost_info = status["cost_summary"]

# Contains:
# - Daily/weekly/monthly summaries
# - Budget alert counts
# - Total records tracked
```

## Pricing Information

Current pricing (as of 2024 - update regularly):

### OpenAI API
- **GPT-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **GPT-4 Turbo**: $0.01 per 1K input tokens, $0.03 per 1K output tokens  
- **GPT-3.5 Turbo**: $0.001 per 1K input tokens, $0.002 per 1K output tokens
- **Embeddings (ada-002)**: $0.0001 per 1K tokens

### Firestore
- **Document Reads**: $0.36 per 1M operations
- **Document Writes**: $1.08 per 1M operations  
- **Document Deletes**: $1.08 per 1M operations

### Google APIs
- **Generic API Request**: $0.001 per request (configurable)

## File Structure

```
ai/monitor/
├── cost_tracker.py          # Core cost tracking system
├── firestore_tracker.py     # Firestore operation wrapper
├── openai_tracker.py        # OpenAI API wrapper  
├── cost_dashboard.py        # Interactive dashboard
├── cost_optimizer.py        # Optimization recommendations
└── status.py                # Integration with monitoring

scripts/
└── setup_cost_monitoring.py # Setup and demo script

docs/
└── COST_MONITORING.md       # This documentation

data/cost_monitoring/         # Data directory (auto-created)
├── usage_records.json       # Usage history (last 90 days)
└── budget_alerts.json       # Budget alert configuration
```

## Best Practices

### 1. Regular Monitoring
- Set up budget alerts for all services you use
- Review monthly reports to identify trends
- Run optimization analysis quarterly

### 2. Integration Strategy
- Wrap API clients at the application initialization level
- Use metadata fields to track features/users for detailed analysis
- Implement gradual rollout to validate tracking accuracy

### 3. Optimization Implementation
- Start with high-priority, low-effort recommendations
- Test model downgrades on non-critical features first
- Implement caching for frequently repeated operations

### 4. Budget Management
- Set conservative initial budgets (can be increased)
- Use multiple alert thresholds (75%, 90%, 100%)
- Configure Telegram notifications for immediate alerts

## Troubleshooting

### Common Issues

**1. No usage data appearing:**
- Ensure you're using wrapped clients (`wrap_firestore_client`, `wrap_openai_client`)
- Check that the data directory is writable: `data/cost_monitoring/`
- Verify manual tracking calls have correct parameters

**2. Budget alerts not triggering:**
- Check that alerts are enabled: `alert.is_enabled = True`
- Verify threshold calculations are correct
- Ensure Telegram bot configuration if using notifications

**3. Dashboard not updating:**
- Check that usage is being recorded: `len(tracker.usage_records)`
- Verify date ranges in queries match your usage timeframe
- Ensure Rich library is installed: `pip install rich`

**4. Cost calculations seem wrong:**
- Verify pricing data is up to date in `cost_tracker.py`
- Check that model names match exactly (case-sensitive)
- Review usage records for correct quantities

### Debug Commands

```python
from ai.monitor.cost_tracker import get_cost_tracker

tracker = get_cost_tracker()

# Check data
print(f"Records: {len(tracker.usage_records)}")
print(f"Budget alerts: {len(tracker.budget_alerts)}")
print(f"Data directory: {tracker.data_dir}")

# Recent usage
recent = tracker.usage_records[-10:]
for record in recent:
    print(f"{record.timestamp}: {record.service.value} {record.operation.value} - ${record.estimated_cost_usd:.4f}")
```

## Contributing

The cost monitoring system is designed to be extensible:

### Adding New Services

1. Add service to `ServiceType` enum
2. Add operations to `OperationType` enum  
3. Add pricing data to `CostTracker._initialize_default_pricing()`
4. Create service wrapper (follow `firestore_tracker.py` pattern)

### Enhancing Optimization

1. Add new pattern detection in `CostOptimizer._detect_*_patterns()`
2. Update recommendation generation logic
3. Add new recommendation categories

### Dashboard Extensions

1. Add new panels to `CostDashboard`
2. Extend layout structure
3. Add new interactive features

## License

This cost monitoring system is part of the Fresh AI project and follows the same license terms.
