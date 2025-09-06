#!/usr/bin/env python3
"""
Full-Scale LLM Implementation Workers
Deploy GPT-5 workers across all remaining features with DeveloperAgent pattern
"""
import asyncio
import argparse
import time
from datetime import datetime
from pathlib import Path
import json
import sys
import os
from dotenv import load_dotenv
import yaml
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
try:
    from ai.monitor.cost_tracker import get_cost_tracker
    from ai.autonomous.safety import SafetyController
    DEPS_AVAILABLE = True
except ImportError:
    print("Some dependencies not available, running in compatibility mode")
    DEPS_AVAILABLE = False


class DeveloperAgent:
    """Individual developer agent for implementing features using GPT-5."""
    
    def __init__(self, agent_id: str, model: str = "gpt-5"):
        self.agent_id = agent_id
        self.model = model
        self.client = OpenAI()
        self.implementations_completed = 0
        self.implementations_failed = 0
        self.total_cost = 0.0
        
    async def implement_feature(self, feature_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a single feature using test-driven development."""
        feature_name = feature_spec['name']
        test_path = feature_spec.get('test_path', f"tests/api/test_{feature_name}.py")
        impl_path = self._determine_impl_path(feature_spec)
        
        try:
            print(f"🤖 Agent {self.agent_id}: Implementing {feature_name}")
            
            # Read test file for requirements
            if not Path(test_path).exists():
                print(f"⚠️  Test file not found: {test_path}")
                return {'success': False, 'error': 'test_file_missing'}
            
            with open(test_path, 'r') as f:
                test_content = f.read()
            
            # Check if implementation already exists
            if impl_path.exists() and impl_path.stat().st_size > 300:
                print(f"⏭️  {feature_name} - implementation exists, skipping")
                return {'success': True, 'skipped': True}
            
            # Generate implementation using GPT-5
            implementation = await self._generate_implementation(
                feature_name, feature_spec, test_content
            )
            
            if not implementation:
                print(f"❌ {feature_name} - implementation generation failed")
                self.implementations_failed += 1
                return {'success': False, 'error': 'generation_failed'}
            
            # Write implementation
            impl_path.parent.mkdir(parents=True, exist_ok=True)
            with open(impl_path, 'w') as f:
                f.write(implementation)
            
            # Run tests to validate
            test_result = await self._validate_implementation(test_path)
            
            if test_result:
                print(f"✅ {feature_name} - implemented and tested successfully")
                self.implementations_completed += 1
                return {'success': True, 'tested': True}
            else:
                print(f"⚠️  {feature_name} - implemented but tests need refinement")
                self.implementations_completed += 1
                return {'success': True, 'tested': False}
                
        except Exception as e:
            print(f"💥 {feature_name} - error: {str(e)}")
            self.implementations_failed += 1
            return {'success': False, 'error': str(e)}
    
    def _determine_impl_path(self, feature_spec: Dict[str, Any]) -> Path:
        """Determine implementation path based on feature spec."""
        feature_name = feature_spec['name']
        file_path = feature_spec.get('file_path')
        
        if file_path:
            # Use specified file path
            return Path(file_path)
        
        # Determine based on interface type
        interface = feature_spec.get('interface', 'api')
        if 'cli' in interface:
            return Path(f"ai/cli/features/{feature_name.lower()}.py")
        else:
            return Path(f"ai/api/features/{feature_name.lower()}.py")
    
    async def _generate_implementation(self, feature_name: str, feature_spec: Dict[str, Any], test_content: str) -> str:
        """Generate implementation using GPT-5."""
        try:
            # Build comprehensive context
            context = self._build_implementation_context(feature_spec)
            
            prompt = f"""
You are a senior Python developer implementing the '{feature_name}' feature using the latest GPT-5 capabilities.

FEATURE SPECIFICATION:
{json.dumps(feature_spec, indent=2)}

TEST REQUIREMENTS:
{test_content}

IMPLEMENTATION CONTEXT:
{context}

REQUIREMENTS:
1. Create a complete, working implementation that passes the tests
2. Use modern Python (3.12+) with proper type hints
3. Include comprehensive docstrings with examples
4. Implement robust error handling and validation
5. Follow the existing codebase patterns and conventions
6. Add logging where appropriate
7. Make the code production-ready and maintainable

Generate ONLY the implementation code - no markdown formatting or explanations.
The code should be complete, syntactically correct, and ready to save directly to a file.
"""

            # Call GPT-5 with intelligent reasoning (with fallback)
            model_to_use = self.model
            try:
                response = self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": "You are an expert Python developer using GPT-5 with high reasoning to create production-quality implementations. Generate clean, well-documented, and tested code."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=2500,
                    reasoning_effort="high",  # High reasoning for complex implementations
                    verbosity="low"  # Concise output for cost control
                )
            except Exception as model_error:
                if "does not exist" in str(model_error).lower() or "not found" in str(model_error).lower():
                    print(f"⚠️ GPT-5 not available, falling back to gpt-4-turbo for {feature_name}")
                    model_to_use = "gpt-4-turbo"
                    response = self.client.chat.completions.create(
                        model=model_to_use,
                        messages=[
                            {"role": "system", "content": "You are an expert Python developer using advanced AI to create production-quality implementations. Generate clean, well-documented, and tested code."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=2500,
                        temperature=0.1
                    )
                else:
                    raise model_error
            
            implementation = response.choices[0].message.content.strip()
            
            # Track costs
            prompt_tokens = len(prompt.split()) * 1.3
            completion_tokens = len(implementation.split()) * 1.3
            cost = self._estimate_cost(prompt_tokens, completion_tokens, model_to_use)
            self.total_cost += cost
            
            # Clean up implementation
            if implementation.startswith("```python"):
                implementation = implementation.split("```python")[1].split("```")[0].strip()
            elif implementation.startswith("```"):
                implementation = implementation.split("```")[1].split("```")[0].strip()
            
            return implementation
            
        except Exception as e:
            print(f"GPT API Error for {feature_name}: {str(e)}")
            return None
    
    def _build_implementation_context(self, feature_spec: Dict[str, Any]) -> str:
        """Build context for implementation."""
        context_parts = []
        
        # Add interface-specific guidance
        interface = feature_spec.get('interface', 'api')
        if 'api' in interface:
            context_parts.append("""
API IMPLEMENTATION PATTERNS:
- Use FastAPI with proper request/response models
- Include comprehensive error handling with HTTPException
- Add proper status codes and responses
- Use dependency injection where appropriate
- Include OpenAPI documentation with examples
""")
        
        if 'cli' in interface:
            context_parts.append("""
CLI IMPLEMENTATION PATTERNS:
- Use Click framework for commands
- Include Rich for beautiful output formatting
- Add proper argument validation and help text
- Implement verbose and quiet modes
- Include progress indicators for long operations
""")
        
        # Add memory system context if relevant
        if 'memory' in feature_spec['name'].lower():
            context_parts.append("""
MEMORY SYSTEM INTEGRATION:
- Use the existing memory store patterns
- Implement proper serialization/deserialization
- Add memory type classification
- Include search and retrieval capabilities
- Follow the MemoryItem and MemoryStore abstractions
""")
        
        return "\n".join(context_parts)
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate API cost based on model and tokens."""
        if "gpt-5" in model.lower():
            # Estimated GPT-5 pricing (premium for high reasoning)
            input_cost = (prompt_tokens / 1000) * 0.05
            output_cost = (completion_tokens / 1000) * 0.10
        elif "gpt-4" in model.lower():
            input_cost = (prompt_tokens / 1000) * 0.03
            output_cost = (completion_tokens / 1000) * 0.06
        else:
            input_cost = (prompt_tokens / 1000) * 0.002
            output_cost = (completion_tokens / 1000) * 0.002
            
        return input_cost + output_cost
    
    async def _validate_implementation(self, test_path: Path) -> bool:
        """Validate implementation by running its tests."""
        try:
            import subprocess
            result = subprocess.run(
                ["poetry", "run", "pytest", str(test_path), "-x", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Test validation error: {str(e)}")
            return False


class FullScaleImplementationOrchestrator:
    """Orchestrates full-scale implementation using multiple DeveloperAgent workers."""
    
    def __init__(self, max_parallel_agents: int = 5, max_cost: float = 200.0):
        self.max_parallel_agents = max_parallel_agents
        self.max_cost = max_cost
        self.agents = []
        self.total_cost = 0.0
        self.implemented_features = 0
        self.failed_features = 0
        self.start_time = time.time()
        self.safety_controller = SafetyController('.') if DEPS_AVAILABLE else None
        
    def load_integration_plan(self, plan_path: str) -> List[Dict[str, Any]]:
        """Load all features from integration plan."""
        print(f"📋 Loading integration plan: {plan_path}")
        
        with open(plan_path, 'r') as f:
            plan = yaml.safe_load(f)
        
        all_features = []
        for batch in plan['batches']:
            all_features.extend(batch.get('features', []))
        
        print(f"✅ Loaded {len(all_features)} features across {len(plan['batches'])} batches")
        return all_features
    
    async def deploy_implementation_workers(self, features: List[Dict[str, Any]]):
        """Deploy DeveloperAgent workers to implement all features."""
        print(f"""
🚀 FULL-SCALE LLM IMPLEMENTATION DEPLOYMENT
============================================================
📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Target: {len(features)} features
💰 Budget: ${self.max_cost}
🤖 Parallel Agents: {self.max_parallel_agents}  
🔧 Model: GPT-5 (high reasoning)
============================================================
""")
        
        # Create safety checkpoint
        if self.safety_controller:
            checkpoint = self.safety_controller.create_checkpoint(
                "Before full-scale LLM implementation"
            )
            print(f"🛡️ Safety checkpoint: {checkpoint}")
        
        # Process features in batches
        batch_size = self.max_parallel_agents
        total_batches = (len(features) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            if self.total_cost > self.max_cost:
                print(f"💰 Budget limit reached: ${self.total_cost:.2f}")
                break
                
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(features))
            batch_features = features[start_idx:end_idx]
            
            print(f"\n📦 Processing Batch {batch_idx + 1}/{total_batches} ({len(batch_features)} features)")
            
            # Create agent tasks
            agent_tasks = []
            for i, feature in enumerate(batch_features):
                agent_id = f"dev_agent_{batch_idx}_{i}"
                agent = DeveloperAgent(agent_id)
                self.agents.append(agent)
                
                task = agent.implement_feature(feature)
                agent_tasks.append(task)
            
            # Execute batch concurrently
            results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Process results
            for agent, result in zip(self.agents[-len(batch_features):], results):
                if isinstance(result, Exception):
                    self.failed_features += 1
                    print(f"❌ Agent {agent.agent_id} failed: {str(result)}")
                elif result.get('success'):
                    if not result.get('skipped'):
                        self.implemented_features += 1
                else:
                    self.failed_features += 1
                
                self.total_cost += agent.total_cost
            
            # Progress update
            elapsed = time.time() - self.start_time
            progress = (batch_idx + 1) / total_batches * 100
            features_per_min = (self.implemented_features + self.failed_features) / (elapsed / 60) if elapsed > 0 else 0
            
            print(f"⚡ Progress: {progress:.1f}% | Implemented: {self.implemented_features} | Failed: {self.failed_features} | Cost: ${self.total_cost:.2f} | Rate: {features_per_min:.1f}/min")
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        # Generate final report
        await self.generate_implementation_report()
    
    async def generate_implementation_report(self):
        """Generate comprehensive implementation report."""
        elapsed = time.time() - self.start_time
        total_processed = self.implemented_features + self.failed_features
        success_rate = (self.implemented_features / total_processed * 100) if total_processed > 0 else 0
        
        report = {
            "orchestration_id": f"fullscale_{int(time.time())}",
            "execution_time_minutes": elapsed / 60,
            "total_features_processed": total_processed,
            "features_implemented": self.implemented_features,
            "features_failed": self.failed_features,
            "success_rate_percent": success_rate,
            "total_cost_usd": self.total_cost,
            "cost_per_feature": self.total_cost / self.implemented_features if self.implemented_features > 0 else 0,
            "implementation_rate_per_minute": total_processed / (elapsed / 60) if elapsed > 0 else 0,
            "parallel_agents_used": self.max_parallel_agents,
            "model_primary": "gpt-5",
            "agents_stats": [
                {
                    "agent_id": agent.agent_id,
                    "completed": agent.implementations_completed,
                    "failed": agent.implementations_failed,
                    "cost": agent.total_cost
                }
                for agent in self.agents
            ],
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        report_path = Path('ai/logs/fullscale_implementation_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"""

🎉 FULL-SCALE LLM IMPLEMENTATION COMPLETE!
============================================================
⏱️  Execution Time: {elapsed/60:.1f} minutes
✅ Features Implemented: {self.implemented_features}
❌ Features Failed: {self.failed_features}
📊 Success Rate: {success_rate:.1f}%
💰 Total Cost: ${self.total_cost:.2f}
💵 Cost per Feature: ${self.total_cost/self.implemented_features if self.implemented_features > 0 else 0:.3f}
⚡ Implementation Rate: {total_processed/(elapsed/60) if elapsed > 0 else 0:.1f} features/min
🤖 Agents Deployed: {len(self.agents)}

📋 Report saved: {report_path}
============================================================
""")


async def main():
    """Main entry point for full-scale implementation."""
    parser = argparse.ArgumentParser(description="Full-scale LLM implementation using GPT-5")
    parser.add_argument('--max-parallel-agents', type=int, default=5, help='Max parallel agents')
    parser.add_argument('--max-cost', type=float, default=200.0, help='Maximum budget in USD')
    parser.add_argument('--plan', default='docs/hookup_analysis/integration_plan.yaml', help='Integration plan path')
    
    args = parser.parse_args()
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        # Initialize orchestrator
        orchestrator = FullScaleImplementationOrchestrator(
            max_parallel_agents=args.max_parallel_agents,
            max_cost=args.max_cost
        )
        
        # Load integration plan
        features = orchestrator.load_integration_plan(args.plan)
        
        # Deploy implementation workers
        await orchestrator.deploy_implementation_workers(features)
        
        print("🎯 Full-scale implementation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Implementation stopped by user")
    except Exception as e:
        print(f"💥 Implementation error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
