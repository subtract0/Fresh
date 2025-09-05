#!/usr/bin/env python3
"""
Autonomous OpenAI Implementation Worker
Production-ready implementation with GPT-5 → GPT-4o fallback
"""
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')

load_env()

class AutonomousImplementationWorker:
    """Production autonomous implementation worker with fallback models"""
    
    def __init__(self, budget_limit: float = 10.0):
        self.budget_limit = budget_limit
        self.total_cost = 0.0
        self.implementations = []
        self.setup_openai()
    
    def setup_openai(self):
        """Setup OpenAI with proper error handling"""
        try:
            from openai import OpenAI
            
            # Set API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI client configured successfully")
            
        except ImportError:
            print("❌ OpenAI package not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "--break-system-packages"])
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            print("✅ OpenAI package installed and configured")
    
    def get_implementation_prompt(self, file_path: str, current_code: str, feature_description: str) -> str:
        """Create a comprehensive implementation prompt"""
        return f"""You are an expert Python developer implementing features in the Fresh AI Agent System.

TASK: Implement the feature in {file_path}
DESCRIPTION: {feature_description}

CURRENT STUB CODE:
```python
{current_code}
```

REQUIREMENTS:
1. Replace ALL TODO comments with working implementations
2. Maintain existing FastAPI/Click patterns and signatures
3. Add comprehensive error handling with try/except blocks
4. Keep all existing imports and class/function names
5. Add proper docstrings for new functions
6. Make the code production-ready and functional
7. Follow the existing project patterns visible in the code
8. For API endpoints: return proper JSON responses
9. For CLI commands: add proper Click decorators and help text
10. Add input validation where appropriate

RESPONSE FORMAT:
Return ONLY the complete, functional Python code. No explanations, no markdown formatting, just the working code that can be directly written to the file.

The implementation should be professional, robust, and ready for production use."""

    def implement_with_model(self, model: str, prompt: str, max_tokens: int = 2500) -> Optional[str]:
        """Attempt implementation with a specific model"""
        try:
            print(f"🤖 Trying model: {model}")
            
            # Prepare API call parameters based on model type
            api_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an expert Python developer. Return only working Python code, no explanations."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Model-specific parameter requirements
            if model.startswith("o3") or model.startswith("o1"):
                # o3 reasoning models - use for planning
                api_params["max_completion_tokens"] = max_tokens
                api_params["messages"] = [
                    {"role": "developer", "content": "You are an expert Python developer. Return only working Python code, no explanations."},
                    {"role": "user", "content": prompt}
                ]
            elif model.startswith("gpt-5"):
                # GPT-5 models - use for coding
                api_params["max_completion_tokens"] = max_tokens
                # GPT-5 supports temperature and reasoning_effort
                api_params["temperature"] = 0.1
                api_params["reasoning_effort"] = "medium"  # balanced speed vs quality
            else:
                api_params["max_tokens"] = max_tokens
                api_params["temperature"] = 0.1
                api_params["timeout"] = 30
            
            # Use the new OpenAI v1.x API format
            response = self.client.chat.completions.create(**api_params)
            content = response.choices[0].message.content
            
            # Clean up markdown formatting if present
            if content.startswith('```python\n'):
                content = content[10:]  # Remove ```python\n
            if content.endswith('\n```'):
                content = content[:-4]  # Remove \n```
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            
            # Track costs using actual usage if available
            if hasattr(response, 'usage') and response.usage:
                # More accurate cost estimation using actual tokens
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                
                # Rough cost estimation (varies by model)
                cost_per_1k_prompt = 0.01   # Approximate for GPT-4
                cost_per_1k_completion = 0.03
                estimated_cost = (prompt_tokens / 1000 * cost_per_1k_prompt) + \
                                (completion_tokens / 1000 * cost_per_1k_completion)
            else:
                # Fallback rough estimate
                estimated_cost = (len(prompt) + len(content)) / 1000 * 0.002
            
            self.total_cost += estimated_cost
            
            return content.strip()
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Model {model} failed: {error_msg}")
            
            # Model-specific debugging
            if model.startswith("o3") or model.startswith("o1"):
                print(f"   🔍 o3 reasoning model debug: {error_msg}")
            elif model.startswith("gpt-5"):
                print(f"   🔍 GPT-5 coding model debug: {error_msg}")
            
            if hasattr(e, 'response'):
                print(f"   🔍 Response status: {getattr(e.response, 'status_code', 'N/A')}")
            
            return None
    
    def implement_feature(self, file_path: str, feature_description: str) -> bool:
        """Implement a single feature with model fallback"""
        print(f"\n📝 Implementing: {file_path}")
        print(f"💡 Feature: {feature_description}")
        
        # Check budget
        if self.total_cost >= self.budget_limit:
            print(f"💰 Budget limit reached (${self.total_cost:.2f})")
            return False
        
        # Read current stub
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        with open(full_path, 'r') as f:
            current_code = f.read()
        
        # Create prompt
        prompt = self.get_implementation_prompt(file_path, current_code, feature_description)
        
        # Try models: o3 for planning, gpt-5 for coding, fallbacks
        models_to_try = [
            "o3",           # Planning and high-level reasoning
            "gpt-5",        # Code generation (flagship)
            "gpt-5-mini",   # Code generation (cost-efficient) 
            "gpt-4o",       # Fallback
            "gpt-4-turbo"   # Last resort
        ]
        
        implementation = None
        successful_model = None
        
        for model in models_to_try:
            implementation = self.implement_with_model(model, prompt)
            if implementation:
                successful_model = model
                print(f"✅ Success with {model}")
                break
            time.sleep(1)  # Rate limiting between attempts
        
        if not implementation:
            print(f"❌ All models failed for {file_path}")
            return False
        
        # Validate implementation (basic checks)
        if len(implementation) < 100 or "TODO" in implementation:
            print(f"⚠️  Implementation seems incomplete for {file_path}")
            return False
        
        # Backup original
        backup_path = full_path.with_suffix(full_path.suffix + '.backup')
        with open(backup_path, 'w') as f:
            f.write(current_code)
        
        # Write new implementation
        try:
            with open(full_path, 'w') as f:
                f.write(implementation)
            
            print(f"✅ Successfully implemented {file_path} using {successful_model}")
            print(f"💰 Running cost: ${self.total_cost:.2f}")
            
            # Store implementation info
            self.implementations.append({
                "file_path": file_path,
                "description": feature_description,
                "model_used": successful_model,
                "timestamp": datetime.now().isoformat(),
                "estimated_cost": self.total_cost
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to write implementation to {file_path}: {e}")
            return False
    
    def run_batch(self, features: List[Dict]) -> Dict:
        """Run a batch of feature implementations"""
        print(f"\n🚀 Starting batch implementation of {len(features)} features")
        print(f"💰 Budget limit: ${self.budget_limit}")
        print("=" * 60)
        
        start_time = time.time()
        successes = 0
        failures = 0
        
        for i, feature in enumerate(features, 1):
            print(f"\n[{i}/{len(features)}]", end=" ")
            
            success = self.implement_feature(
                feature["file_path"], 
                feature["description"]
            )
            
            if success:
                successes += 1
            else:
                failures += 1
            
            # Rate limiting
            time.sleep(2)
            
            # Budget check
            if self.total_cost >= self.budget_limit:
                print(f"\n💰 Budget limit reached, stopping batch")
                break
        
        duration = time.time() - start_time
        
        # Generate report
        report = {
            "batch_summary": {
                "total_features": len(features),
                "successful": successes,
                "failed": failures,
                "success_rate": successes / len(features) if features else 0,
                "total_cost": self.total_cost,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            },
            "implementations": self.implementations
        }
        
        print(f"\n🎯 BATCH COMPLETE!")
        print(f"✅ Successful: {successes}")
        print(f"❌ Failed: {failures}")
        print(f"💰 Total cost: ${self.total_cost:.2f}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        
        # Save report
        report_path = Path("logs/implementation_report.json")
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Report saved: {report_path}")
        
        return report

def main():
    """Main execution function"""
    print("🚀 Fresh AI Autonomous Implementation Worker")
    print("🤖 o3 (planning) → GPT-5 (coding) → GPT-5-mini → GPT-4o fallback")
    print("=" * 60)
    
    # 40 Feature batch for autonomous implementation  
    test_features = [
        {"file_path": "ai/api/endpoints/create_activity_panel.py", "description": "Activity panel creation with monitoring dashboard"},
        {"file_path": "ai/api/endpoints/track_embedding.py", "description": "Embedding usage tracking and analytics"},
        {"file_path": "ai/api/endpoints/appgenesisagent.py", "description": "Application genesis agent for project initialization"},
        {"file_path": "ai/api/endpoints/quick_cost_summary.py", "description": "Quick cost summary and budget overview"},
        {"file_path": "ai/api/endpoints/openaiusagetracker.py", "description": "OpenAI API usage tracking and monitoring"},
        {"file_path": "ai/api/endpoints/memorysync.py", "description": "Memory synchronization between stores"},
        {"file_path": "ai/api/endpoints/get_discovery_summary.py", "description": "Discovery summary and analytics reporting"},
        {"file_path": "ai/api/endpoints/trackedembeddings.py", "description": "Tracked embeddings with usage analytics"},
        {"file_path": "ai/api/endpoints/execute.py", "description": "General execution endpoint for commands"},
        {"file_path": "ai/api/endpoints/forecast_monthly_cost.py", "description": "Monthly cost forecasting and budgeting"},
        {"file_path": "ai/api/endpoints/track_write.py", "description": "Write operation tracking and monitoring"},
        {"file_path": "ai/api/endpoints/clear_activity.py", "description": "Activity clearing and reset functionality"},
        {"file_path": "ai/api/endpoints/set_memory_store.py", "description": "Memory store configuration and setup"},
        {"file_path": "ai/api/endpoints/get_active_agents.py", "description": "Active agent listing and status"},
        {"file_path": "ai/api/endpoints/initialize_agent_memory_system.py", "description": "Agent memory system initialization"},
        {"file_path": "ai/api/endpoints/restorememorystore.py", "description": "Memory store backup and restoration"},
        {"file_path": "ai/api/endpoints/get_by_id.py", "description": "Get entity by ID with error handling"},
        {"file_path": "ai/api/endpoints/trackedquerysnapshot.py", "description": "Query snapshot tracking for analytics"},
        {"file_path": "ai/api/endpoints/estimate_and_track_from_messages.py", "description": "Message-based cost estimation and tracking"},
        {"file_path": "ai/api/endpoints/inmemorymemorystore.py", "description": "In-memory store implementation"},
        {"file_path": "ai/api/endpoints/sync_with_firestore.py", "description": "Firestore synchronization operations"},
        {"file_path": "ai/api/endpoints/check_budget_status.py", "description": "Budget status checking and alerts"},
        {"file_path": "ai/api/endpoints/analyze_usage_patterns.py", "description": "Usage pattern analysis and insights"},
        {"file_path": "ai/api/endpoints/refreshcontroller.py", "description": "Refresh controller for UI updates"},
        {"file_path": "ai/api/endpoints/consolidate_memories.py", "description": "Memory consolidation and optimization"},
        {"file_path": "ai/api/endpoints/count_messages_tokens.py", "description": "Token counting for messages"},
        {"file_path": "ai/api/endpoints/crosssessionanalytics.py", "description": "Cross-session analytics and tracking"},
        {"file_path": "ai/api/endpoints/create.py", "description": "Generic creation endpoint"},
        {"file_path": "ai/api/endpoints/limit.py", "description": "Rate limiting and quota management"},
        {"file_path": "ai/api/endpoints/show_integration_examples.py", "description": "Integration examples and documentation"},
        {"file_path": "ai/api/endpoints/get_related_memories.py", "description": "Related memory retrieval and linking"},
        {"file_path": "ai/api/endpoints/ensure_memory_system_ready.py", "description": "Memory system readiness validation"},
        {"file_path": "ai/api/endpoints/trackedquery.py", "description": "Query tracking and performance monitoring"},
        {"file_path": "ai/api/endpoints/get_development_status.py", "description": "Development status and progress tracking"},
        {"file_path": "ai/api/endpoints/memoryintegrationconfig.py", "description": "Memory integration configuration"},
        {"file_path": "ai/api/endpoints/get_agent.py", "description": "Agent retrieval and information"},
        {"file_path": "ai/api/endpoints/demonstrate_analytics.py", "description": "Analytics demonstration and examples"},
        {"file_path": "ai/api/endpoints/enhancedmemoryitem.py", "description": "Enhanced memory item with metadata"},
        {"file_path": "ai/api/endpoints/get_production_analytics.py", "description": "Production analytics and monitoring"},
        {"file_path": "ai/api/endpoints/track_completion.py", "description": "Completion tracking and metrics"}
    ]
    
    # Create worker with $5 budget for 40-feature batch (estimated $1.20)
    worker = AutonomousImplementationWorker(budget_limit=5.0)
    
    # Run the batch
    report = worker.run_batch(test_features)
    
    # Check if we should continue
    if report["batch_summary"]["success_rate"] >= 0.8:
        print(f"\n🎉 SUCCESS! Ready for full-scale implementation")
        print(f"✨ All systems working. Ready to implement all 587 features!")
    else:
        print(f"\n⚠️  Some issues encountered. Review and adjust before full-scale.")
    
    return report["batch_summary"]["success_rate"] >= 0.5

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
