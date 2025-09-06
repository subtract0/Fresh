#!/usr/bin/env python3
"""
Phase 2: Simplified LLM-Driven Feature Implementation
Creates working implementations for the most critical features first
"""
import asyncio
import time
from datetime import datetime
from pathlib import Path
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI


class SimplePhase2Runner:
    """Simplified Phase 2 implementation focusing on critical features."""
    
    def __init__(self, max_cost: float = 50.0):
        self.max_cost = max_cost
        self.model = "gpt-5"
        self.client = OpenAI()
        self.implemented_features = 0
        self.failed_features = 0
        self.total_cost = 0.0
        self.start_time = time.time()
        
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate OpenAI API cost."""
        # GPT-4 pricing (approximate)
        input_cost = (prompt_tokens / 1000) * 0.03
        output_cost = (completion_tokens / 1000) * 0.06
        return input_cost + output_cost
    
    async def implement_feature(self, feature_name: str, test_content: str, impl_path: Path) -> bool:
        """Implement a single feature."""
        try:
            print(f"🔨 Implementing {feature_name}...")
            
            # Check budget
            if self.total_cost > self.max_cost:
                print(f"💰 Budget exceeded: ${self.total_cost:.2f} > ${self.max_cost}")
                return False
            
            # Skip if implementation exists
            if impl_path.exists() and impl_path.stat().st_size > 200:
                print(f"⏭️  {feature_name} - already implemented")
                return True
            
            # Generate context-aware prompt
            context = self.get_implementation_context(feature_name, impl_path)
            
            prompt = f"""
Implement the Python feature '{feature_name}' based on the test requirements.

TEST FILE:
{test_content}

REQUIREMENTS:
1. Create a complete, working implementation
2. Use proper Python typing and docstrings
3. Follow the existing code patterns shown in context
4. Handle errors appropriately
5. Make tests pass

CODEBASE CONTEXT:
{context}

Generate ONLY the implementation code - no markdown, explanations, or comments outside the code.
The code should be production-ready and complete.
"""

            # Call OpenAI API with intelligent model fallback
            model_to_use = self.model
            try:
                response = self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": "You are a senior Python developer using the latest AI capabilities. Generate clean, production-ready code for the Fresh AI system."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=1500,
                    reasoning_effort="high",  # High reasoning for feature implementation
                    verbosity="low"  # Concise output
                )
            except Exception as model_error:
                if "does not exist" in str(model_error).lower() or "not found" in str(model_error).lower():
                    print(f"⚠️ GPT-5 not available, falling back to gpt-4-turbo")
                    model_to_use = "gpt-4-turbo"
                    response = self.client.chat.completions.create(
                        model=model_to_use,
                        messages=[
                            {"role": "system", "content": "You are a senior Python developer using advanced AI capabilities. Generate clean, production-ready code for the Fresh AI system."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.1
                    )
                else:
                    raise model_error
            
            implementation = response.choices[0].message.content.strip()
            
            # Estimate and track cost
            prompt_tokens = len(prompt.split()) * 1.3  # rough estimate
            completion_tokens = len(implementation.split()) * 1.3
            cost = self.estimate_cost(prompt_tokens, completion_tokens)
            self.total_cost += cost
            
            # Clean up the implementation (remove markdown if present)
            if implementation.startswith("```python"):
                implementation = implementation.split("```python")[1].split("```")[0].strip()
            elif implementation.startswith("```"):
                implementation = implementation.split("```")[1].split("```")[0].strip()
            
            # Write implementation
            impl_path.parent.mkdir(parents=True, exist_ok=True)
            with open(impl_path, 'w') as f:
                f.write(implementation)
            
            print(f"✅ {feature_name} - implemented (cost: ${cost:.3f})")
            return True
            
        except Exception as e:
            print(f"❌ {feature_name} - error: {str(e)}")
            return False
    
    def get_implementation_context(self, feature_name: str, impl_path: Path) -> str:
        """Get context for implementation."""
        context_parts = []
        
        # Add basic patterns based on path
        if 'api' in str(impl_path):
            context_parts.append("This is an API feature. Use classes, proper typing, and return appropriate data structures.")
        elif 'cli' in str(impl_path):
            context_parts.append("This is a CLI feature. Use functions, argparse patterns, and Rich for output.")
        
        # Look for existing example in same directory
        target_dir = impl_path.parent
        if target_dir.exists():
            for example_file in list(target_dir.glob("*.py"))[:2]:  # Max 2 examples
                try:
                    with open(example_file, 'r') as f:
                        content = f.read()
                    if 50 < len(content) < 1000:  # Good size example
                        context_parts.append(f"EXAMPLE ({example_file.name}):\n{content[:800]}")
                        break
                except:
                    continue
        
        return "\n\n".join(context_parts)
    
    async def run_priority_features(self):
        """Implement high-priority features first."""
        print(f"""
🚀 SIMPLIFIED PHASE 2: PRIORITY FEATURE IMPLEMENTATION
============================================================
📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 Budget: ${self.max_cost}
🔧 Model: GPT-5 (high reasoning)
🎯 Strategy: Implement critical features first
============================================================
""")

        # Define priority features (most important for system functionality)
        priority_features = [
            # Core memory system
            ('tests/api/test_MemoryStore.py', 'ai/memory/store.py'),
            ('tests/api/test_InMemoryMemoryStore.py', 'ai/memory/in_memory_store.py'),
            ('tests/api/test_MemoryItem.py', 'ai/memory/item.py'),
            
            # Essential API features
            ('tests/api/test_WriteMemory.py', 'ai/api/write_memory.py'),
            ('tests/api/test_ReadMemoryContext.py', 'ai/api/read_memory_context.py'),
            ('tests/api/test_AgentConfig.py', 'ai/api/agent_config.py'),
            
            # Core CLI features
            ('tests/cli/test_cmd_scan.py', 'ai/cli/cmd_scan.py'),
            ('tests/cli/test_cmd_run.py', 'ai/cli/cmd_run.py'),
            ('tests/cli/test_cmd_monitor.py', 'ai/cli/cmd_monitor.py'),
            
            # Cost tracking
            ('tests/api/test_CostTracker.py', 'ai/monitor/cost_tracker_impl.py'),
            ('tests/api/test_OpenAIUsageTracker.py', 'ai/monitor/openai_usage_tracker.py'),
            
            # Agent management
            ('tests/api/test_Agent.py', 'ai/agents/base_agent.py'),
            ('tests/api/test_AgentExecution.py', 'ai/execution/agent_execution.py'),
        ]
        
        print(f"📋 Implementing {len(priority_features)} priority features")
        
        for test_path_str, impl_path_str in priority_features:
            if self.total_cost > self.max_cost:
                print(f"💰 Budget limit reached: ${self.total_cost:.2f}")
                break
                
            test_path = Path(test_path_str)
            impl_path = Path(impl_path_str)
            
            if not test_path.exists():
                print(f"⚠️  Test file not found: {test_path}")
                continue
            
            # Read test content
            with open(test_path, 'r') as f:
                test_content = f.read()
            
            # Implement feature
            feature_name = impl_path.stem
            success = await self.implement_feature(feature_name, test_content, impl_path)
            
            if success:
                self.implemented_features += 1
            else:
                self.failed_features += 1
            
            # Small delay to avoid rate limits
            await asyncio.sleep(2)
        
        # Final report
        await self.generate_report()
    
    async def generate_report(self):
        """Generate final implementation report."""
        elapsed = time.time() - self.start_time
        success_rate = (self.implemented_features / (self.implemented_features + self.failed_features)) * 100 if (self.implemented_features + self.failed_features) > 0 else 0
        
        report = {
            "phase": "2-simplified",
            "status": "completed",
            "execution_time_minutes": elapsed / 60,
            "features_implemented": self.implemented_features,
            "features_failed": self.failed_features,
            "success_rate_percent": success_rate,
            "total_cost_usd": self.total_cost,
            "cost_per_feature": self.total_cost / self.implemented_features if self.implemented_features > 0 else 0,
            "model_used": self.model
        }
        
        # Save report
        report_path = Path('ai/logs/phase2_simple_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"""

🎉 PHASE 2 SIMPLIFIED IMPLEMENTATION COMPLETE!
============================================================
⏱️  Execution Time: {elapsed/60:.1f} minutes
✅ Features Implemented: {self.implemented_features}
❌ Features Failed: {self.failed_features}
📊 Success Rate: {success_rate:.1f}%
💰 Total Cost: ${self.total_cost:.2f}
💵 Cost per Feature: ${self.total_cost/self.implemented_features if self.implemented_features > 0 else 0:.3f}

📋 Report saved: {report_path}
============================================================

🎯 NEXT STEPS:
1. Run tests to verify implementations: poetry run pytest tests/ -x
2. Check created implementations in ai/ directories
3. Run full batch implementation if needed
4. Deploy working features
============================================================
""")


async def main():
    """Main entry point."""
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("💡 Please set your OpenAI API key: export OPENAI_API_KEY=your-key-here")
        sys.exit(1)
    
    # Run simplified Phase 2
    runner = SimplePhase2Runner(max_cost=50.0)
    
    try:
        await runner.run_priority_features()
        print("🎯 Phase 2 simplified implementation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Phase 2 stopped by user")
    except Exception as e:
        print(f"💥 Phase 2 error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
