#!/usr/bin/env python3
"""
Cost Monitoring Setup Script

Sets up the cost monitoring system for the Fresh AI project with:
- Initial configuration
- Sample budget alerts
- Example usage tracking
- Dashboard demo

Usage:
    python scripts/setup_cost_monitoring.py
    python scripts/setup_cost_monitoring.py --demo
    python scripts/setup_cost_monitoring.py --dashboard
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType
from ai.monitor.cost_dashboard import CostDashboard, quick_cost_summary
from ai.monitor.cost_optimizer import get_cost_optimizer, quick_optimization_report
from ai.monitor.firestore_tracker import wrap_firestore_client
from ai.monitor.openai_tracker import wrap_openai_client


def setup_cost_monitoring():
    """Set up the cost monitoring system."""
    print("🚀 Setting up Fresh AI Cost Monitoring System")
    print("=" * 50)
    
    # Initialize cost tracker
    cost_tracker = get_cost_tracker()
    print(f"✅ Cost tracker initialized")
    print(f"   Data directory: {cost_tracker.data_dir}")
    print(f"   Existing records: {len(cost_tracker.usage_records)}")
    
    # Set up default budget alerts
    print("\n💸 Setting up budget alerts...")
    
    # Add a total monthly budget alert
    if not any(alert.service is None for alert in cost_tracker.budget_alerts):
        total_alert = cost_tracker.add_budget_alert(
            monthly_limit_usd=100.0,
            threshold_percentage=0.8,
            service=None
        )
        print(f"   ✅ Total budget alert: $100/month (80% threshold)")
    
    # Add service-specific alerts
    if not any(alert.service == ServiceType.OPENAI for alert in cost_tracker.budget_alerts):
        openai_alert = cost_tracker.add_budget_alert(
            monthly_limit_usd=50.0,
            threshold_percentage=0.8,
            service=ServiceType.OPENAI
        )
        print(f"   ✅ OpenAI budget alert: $50/month (80% threshold)")
        
    if not any(alert.service == ServiceType.FIRESTORE for alert in cost_tracker.budget_alerts):
        firestore_alert = cost_tracker.add_budget_alert(
            monthly_limit_usd=25.0,
            threshold_percentage=0.9,
            service=ServiceType.FIRESTORE
        )
        print(f"   ✅ Firestore budget alert: $25/month (90% threshold)")
    
    # Display current pricing
    print("\n💰 Current pricing configuration:")
    for service_type, pricing in cost_tracker.pricing.items():
        print(f"   {service_type.value}:")
        for operation, price in list(pricing.pricing_per_unit.items())[:3]:
            print(f"     {operation}: ${price}")
        if len(pricing.pricing_per_unit) > 3:
            print(f"     ... and {len(pricing.pricing_per_unit) - 3} more")
    
    print(f"\n✅ Cost monitoring setup complete!")
    return cost_tracker


def run_demo():
    """Run a demo with sample data."""
    print("\n🎬 Running cost monitoring demo...")
    
    cost_tracker = get_cost_tracker()
    
    # Generate some sample usage data
    sample_data = [
        (ServiceType.OPENAI, OperationType.COMPLETION, 1500, "gpt-3.5-turbo"),
        (ServiceType.OPENAI, OperationType.COMPLETION, 800, "gpt-4"),
        (ServiceType.FIRESTORE, OperationType.READ, 100, None),
        (ServiceType.FIRESTORE, OperationType.WRITE, 50, None),
        (ServiceType.OPENAI, OperationType.EMBEDDING, 2000, "text-embedding-ada-002"),
    ]
    
    print("   Adding sample usage records...")
    for service, operation, quantity, model in sample_data:
        record = cost_tracker.record_usage(
            service=service,
            operation=operation,
            quantity=quantity,
            model=model,
            metadata={"demo": True, "source": "setup_script"}
        )
        print(f"   📊 {service.value} {operation.value}: {quantity} units, ${record.estimated_cost_usd:.4f}")
    
    # Show usage summary
    print("\n📈 Usage Summary (last 7 days):")
    summary = cost_tracker.get_usage_summary(days=7)
    print(f"   Total cost: ${summary['total_cost_usd']:.4f}")
    print(f"   Total operations: {summary['total_operations']}")
    
    for service, data in summary['service_breakdown'].items():
        percentage = (data['cost'] / max(summary['total_cost_usd'], 0.0001)) * 100
        print(f"   {service}: ${data['cost']:.4f} ({percentage:.1f}%)")
    
    # Show optimization suggestions
    optimizer = get_cost_optimizer()
    recommendations = optimizer.generate_recommendations(days=7)
    
    if recommendations:
        print(f"\n💡 Optimization recommendations ({len(recommendations)} found):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec.title}")
            print(f"      Potential savings: ${rec.potential_savings_usd:.2f}")
            print(f"      Effort: {rec.effort_level}")


def show_integration_examples():
    """Show integration examples."""
    print("\n🔧 Integration Examples")
    print("=" * 30)
    
    print("\n1. Firestore Integration:")
    print("""
# Original Firestore usage
from google.cloud import firestore
db = firestore.Client()

# With cost tracking
from ai.monitor.firestore_tracker import wrap_firestore_client
db = wrap_firestore_client(firestore.Client())

# Use normally - all operations are automatically tracked!
doc_ref = db.collection('users').document('user123')
doc_ref.set({'name': 'John', 'email': 'john@example.com'})
""")
    
    print("\n2. OpenAI Integration:")
    print("""
# Original OpenAI usage
import openai
client = openai.OpenAI(api_key="your-key")

# With cost tracking
from ai.monitor.openai_tracker import wrap_openai_client
client = wrap_openai_client(openai.OpenAI(api_key="your-key"))

# Use normally - all operations are automatically tracked!
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
""")
    
    print("\n3. Manual Tracking:")
    print("""
from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType

tracker = get_cost_tracker()
tracker.record_usage(
    service=ServiceType.OPENAI,
    operation=OperationType.COMPLETION,
    quantity=1500,  # tokens
    model="gpt-3.5-turbo"
)
""")
    
    print("\n4. Dashboard Usage:")
    print("""
# Quick summary
python -m ai.monitor.cost_dashboard quick

# Full dashboard
python -m ai.monitor.cost_dashboard

# Or programmatically
from ai.monitor.cost_dashboard import quick_cost_summary
quick_cost_summary()
""")


async def run_dashboard():
    """Run the cost monitoring dashboard."""
    dashboard = CostDashboard()
    await dashboard.run_dashboard()


def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up Fresh AI cost monitoring")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--dashboard", action="store_true", help="Launch dashboard")
    parser.add_argument("--quick", action="store_true", help="Show quick summary")
    parser.add_argument("--examples", action="store_true", help="Show integration examples")
    
    args = parser.parse_args()
    
    # Always run basic setup
    cost_tracker = setup_cost_monitoring()
    
    if args.examples:
        show_integration_examples()
        
    if args.demo:
        run_demo()
        
    if args.quick:
        print("\n" + "=" * 50)
        quick_cost_summary()
        
    if args.dashboard:
        print("\n🚀 Launching cost monitoring dashboard...")
        print("Press Ctrl+C to exit")
        try:
            asyncio.run(run_dashboard())
        except KeyboardInterrupt:
            print("\n👋 Dashboard closed")
            
    if not any([args.demo, args.dashboard, args.quick, args.examples]):
        print(f"\n📚 Next steps:")
        print(f"   1. Integrate cost tracking in your code (see --examples)")
        print(f"   2. Run a demo: python {__file__} --demo")
        print(f"   3. Launch dashboard: python {__file__} --dashboard") 
        print(f"   4. Quick summary: python {__file__} --quick")
        
        print(f"\n🔧 Configuration:")
        print(f"   - Budget alerts: {len(cost_tracker.budget_alerts)} configured")
        print(f"   - Data directory: {cost_tracker.data_dir}")
        print(f"   - Usage records: {len(cost_tracker.usage_records)}")


if __name__ == "__main__":
    main()
