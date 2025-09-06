#!/usr/bin/env python3
"""
Phase 2: LLM-Driven Feature Implementation Runner
Transforms test skeletons into working implementations using OpenAI API
"""
import asyncio
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
import json
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai.orchestration.batch_runner import BatchImplementationOrchestrator
    from ai.monitor.cost_tracker import get_cost_tracker
    from ai.monitor.openai_tracker import OpenAIUsageTracker
    from ai.autonomous.safety import SafetyController
    DEPS_AVAILABLE = True
except ImportError as e:
    print(f"Execution system modules not available, running in compatibility mode")
    DEPS_AVAILABLE = False

import openai
from openai import OpenAI


class Phase2ImplementationRunner:
    """Phase 2: Transform test skeletons into working feature implementations."""
    
    def __init__(self, max_parallel_features: int = 5, max_cost: float = 100.0, model: str = "gpt-4"):
        self.max_parallel_features = max_parallel_features
        self.max_cost = max_cost
        self.model = model
        self.client = OpenAI()
        self.cost_tracker = get_cost_tracker() if DEPS_AVAILABLE else None
        self.safety = SafetyController('.') if DEPS_AVAILABLE else None
        self.implemented_features = 0
        self.failed_features = 0
        self.start_time = time.time()
        
    async def implement_feature_from_test(self, test_file_path: Path) -> bool:
        """Implement a feature based on its test skeleton."""
        try:
            # Read the test file
            with open(test_file_path, 'r') as f:
                test_content = f.read()
            
            # Extract feature name and requirements from test
            feature_name = test_file_path.stem.replace('test_', '')
            
            # Determine target implementation path
            if 'tests/api/' in str(test_file_path):
                impl_path = Path('ai/api') / f"{feature_name}.py"
            elif 'tests/cli/' in str(test_file_path):
                impl_path = Path('ai/cli') / f"{feature_name}.py"
            else:
                impl_path = Path('ai/features') / f"{feature_name}.py"
            
            # Skip if implementation already exists and is substantial
            if impl_path.exists():
                with open(impl_path, 'r') as f:
                    existing_content = f.read()
                if len(existing_content) > 500:  # Skip substantial implementations
                    print(f"⏭️  Skipping {feature_name} - implementation exists")
                    return True
            
            # Generate implementation using OpenAI
            implementation = await self.generate_implementation(feature_name, test_content, impl_path)
            
            if implementation:
                # Create directory if needed
                impl_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write implementation
                with open(impl_path, 'w') as f:
                    f.write(implementation)
                
                # Verify implementation by running test
                if await self.verify_implementation(test_file_path):
                    print(f"✅ {feature_name} - implemented successfully")
                    return True
                else:
                    print(f"⚠️  {feature_name} - implementation needs refinement")
                    return False
            else:
                print(f"❌ {feature_name} - implementation generation failed")
                return False
                
        except Exception as e:
            print(f"💥 Error implementing {feature_name}: {str(e)}")
            return False
    
    async def generate_implementation(self, feature_name: str, test_content: str, impl_path: Path) -> str:
        """Generate feature implementation using OpenAI."""
        try:
            # Analyze existing codebase for context
            context = await self.gather_implementation_context(feature_name, impl_path)
            
            prompt = f"""
Implement the {feature_name} feature based on the test requirements below.

TEST FILE CONTENT:
{test_content}

IMPLEMENTATION REQUIREMENTS:
1. Create a working implementation that passes the test cases
2. Follow Python best practices and typing hints
3. Use appropriate error handling and validation
4. Match the project's existing code patterns shown in context
5. Include comprehensive docstrings
6. Ensure the implementation is production-ready

CODEBASE CONTEXT:
{context}

TARGET FILE: {impl_path}

Generate only the implementation code - no markdown formatting or explanations.
The code should be complete and ready to save directly to the file.
"""

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a senior Python developer implementing features for the Fresh AI system. Generate clean, production-ready code."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.1
                )
            )
            
            # Track cost if available
            if self.cost_tracker:
                self.cost_tracker.record_usage(
                    service='openai',
                    operation='chat_completion',
                    tokens_input=len(prompt.split()) * 1.3,  # rough estimate
                    tokens_output=len(response.choices[0].message.content.split()) * 1.3,
                    cost=0.03  # rough estimate for gpt-4
                )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API Error for {feature_name}: {str(e)}")
            return None
    
    async def gather_implementation_context(self, feature_name: str, impl_path: Path) -> str:
        """Gather relevant context from existing codebase."""
        context_parts = []
        
        # Look for similar files in the target directory
        target_dir = impl_path.parent
        if target_dir.exists():
            similar_files = list(target_dir.glob("*.py"))[:3]  # Limit to 3 examples
            for file_path in similar_files:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if len(content) < 2000:  # Only include smaller files as context
                        context_parts.append(f"EXAMPLE FILE {file_path.name}:\n{content}\n")
                except:
                    continue
        
        # Look for related imports and patterns
        if 'api' in str(impl_path):
            context_parts.append("PATTERN: This is an API feature - use FastAPI patterns, proper HTTP responses, and validation")
        elif 'cli' in str(impl_path):
            context_parts.append("PATTERN: This is a CLI feature - use argparse, proper CLI patterns, and rich output")
        
        return "\n".join(context_parts[:5])  # Limit context size
    
    async def verify_implementation(self, test_file_path: Path) -> bool:
        """Verify implementation by running its test."""
        try:
            # Run the specific test file
            import subprocess
            result = subprocess.run(
                ["poetry", "run", "pytest", str(test_file_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check if tests passed
            return result.returncode == 0 and "FAILED" not in result.stdout
            
        except Exception as e:
            print(f"Test verification error: {str(e)}")
            return False
    
    async def run_phase2_implementation(self):
        """Run Phase 2: LLM-driven feature implementation."""
        print(f"""
🚀 PHASE 2: LLM-DRIVEN FEATURE IMPLEMENTATION
============================================================
📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Target: Transform 382 test skeletons into working features
💰 Budget: ${self.max_cost}
🔧 Model: {self.model}
⚡ Parallel features: {self.max_parallel_features}
============================================================
""")

        # Create safety checkpoint
        if self.safety:
            checkpoint_id = self.safety.create_checkpoint(
                "Before Phase 2: LLM-driven feature implementation"
            )
            print(f"🛡️ Safety checkpoint created: {checkpoint_id}")

        # Find all test skeleton files
        test_files = []
        test_dirs = [Path('tests/api'), Path('tests/cli')]
        
        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(list(test_dir.glob('test_*.py')))
        
        print(f"📋 Found {len(test_files)} test files to implement")
        
        # Process features in batches
        batch_size = self.max_parallel_features
        total_batches = (len(test_files) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(test_files))
            batch_files = test_files[start_idx:end_idx]
            
            print(f"\n📦 Processing Batch {batch_idx + 1}/{total_batches} ({len(batch_files)} features)")
            
            # Process batch concurrently
            tasks = [
                self.implement_feature_from_test(test_file)
                for test_file in batch_files
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update statistics
            for result in results:
                if isinstance(result, Exception):
                    self.failed_features += 1
                elif result:
                    self.implemented_features += 1
                else:
                    self.failed_features += 1
            
            # Progress update
            elapsed = time.time() - self.start_time
            progress = (batch_idx + 1) / total_batches * 100
            features_per_min = (self.implemented_features + self.failed_features) / (elapsed / 60) if elapsed > 0 else 0
            
            print(f"⚡ Progress: {progress:.1f}% | Implemented: {self.implemented_features} | Failed: {self.failed_features} | Rate: {features_per_min:.1f}/min")
            
            # Check budget limit
            if self.cost_tracker:
                current_cost = self.cost_tracker.get_usage_summary().get('total_cost', 0)
                if current_cost > self.max_cost:
                    print(f"💰 Budget limit reached: ${current_cost:.2f} > ${self.max_cost}")
                    break
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        # Final report
        await self.generate_phase2_report()
    
    async def generate_phase2_report(self):
        """Generate final Phase 2 execution report."""
        elapsed = time.time() - self.start_time
        success_rate = (self.implemented_features / (self.implemented_features + self.failed_features)) * 100 if (self.implemented_features + self.failed_features) > 0 else 0
        
        current_cost = 0
        if self.cost_tracker:
            current_cost = self.cost_tracker.get_usage_summary().get('total_cost', 0)
        
        report = {
            "phase": 2,
            "status": "completed",
            "execution_time_minutes": elapsed / 60,
            "features_implemented": self.implemented_features,
            "features_failed": self.failed_features,
            "success_rate_percent": success_rate,
            "total_cost_usd": current_cost,
            "cost_per_feature": current_cost / self.implemented_features if self.implemented_features > 0 else 0,
            "features_per_minute": (self.implemented_features + self.failed_features) / (elapsed / 60) if elapsed > 0 else 0,
            "model_used": self.model,
            "max_parallel": self.max_parallel_features
        }
        
        # Save report
        report_path = Path('ai/logs/phase2_implementation_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"""

🎉 PHASE 2 IMPLEMENTATION COMPLETE!
============================================================
⏱️  Execution Time: {elapsed/60:.1f} minutes
✅ Features Implemented: {self.implemented_features}
❌ Features Failed: {self.failed_features}
📊 Success Rate: {success_rate:.1f}%
💰 Total Cost: ${current_cost:.2f}
💵 Cost per Feature: ${current_cost/self.implemented_features if self.implemented_features > 0 else 0:.3f}
⚡ Implementation Rate: {(self.implemented_features + self.failed_features) / (elapsed / 60) if elapsed > 0 else 0:.1f} features/min

📋 Report saved: {report_path}
============================================================
""")


async def main():
    """Main entry point for Phase 2 implementation."""
    parser = argparse.ArgumentParser(description="Phase 2: LLM-driven feature implementation")
    parser.add_argument('--max-parallel-features', type=int, default=5, help='Max parallel feature implementations')
    parser.add_argument('--max-cost', type=float, default=100.0, help='Maximum budget in USD')
    parser.add_argument('--model', default='gpt-4o', help='OpenAI model to use')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize and run Phase 2
    runner = Phase2ImplementationRunner(
        max_parallel_features=args.max_parallel_features,
        max_cost=args.max_cost,
        model=args.model
    )
    
    try:
        await runner.run_phase2_implementation()
        print("🎯 Phase 2 completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Phase 2 stopped by user")
    except Exception as e:
        print(f"💥 Phase 2 error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
