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
            
            # Reasoning models (o3, o3-mini) have different parameter requirements
            if model.startswith("o3") or model.startswith("o1"):
                api_params["max_completion_tokens"] = max_tokens
                # Reasoning models use default temperature, no custom temperature
                # Use developer messages instead of system messages for reasoning models
                api_params["messages"] = [
                    {"role": "developer", "content": "You are an expert Python developer. Return only working Python code, no explanations."},
                    {"role": "user", "content": prompt}
                ]
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
            
            # For reasoning models, provide more detailed debugging
            if model.startswith("o3") or model.startswith("o1"):
                print(f"   🔍 Reasoning model debug: Full error details for troubleshooting")
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
        
        # Try models in order: o3 → o3-mini → GPT-4o (state-of-art per MCP reference)
        models_to_try = [
            "o3",           # Latest OpenAI reasoning model
            "o3-mini",      # Reasoning model (cost-efficient)
            "gpt-4o",       # Fallback to GPT-4o
            "gpt-4-turbo-preview",  # Final fallback
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
    print("🤖 o3 → o3-mini → GPT-4o fallback chain (state-of-art per MCP 688cf28d)")
    print("=" * 60)
    
    # Test features (testing o3 reasoning models with real TODO stub)
    test_features = [
        {
            "file_path": "ai/api/endpoints/basetool.py",
            "description": "Base tool API endpoint with core functionality and error handling"
        }
    ]
    
    # Create worker with $10 budget for testing
    worker = AutonomousImplementationWorker(budget_limit=10.0)
    
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
