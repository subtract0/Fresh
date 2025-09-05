#!/usr/bin/env python3
"""
Update Integration Spec Snapshot
Enhanced validation and metadata enrichment for integration_plan.yaml
"""
import yaml
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai.api.write_memory import WriteMemory
    from ai.memory.store import get_memory_store
    MEMORY_AVAILABLE = True
except ImportError:
    print("Memory system not available, storing to file instead")
    MEMORY_AVAILABLE = False


class IntegrationSpecValidator:
    """Validates and enhances integration specification with metadata."""
    
    def __init__(self, plan_path: str):
        self.plan_path = Path(plan_path)
        self.enhanced_plan = None
        self.checksum = None
        
    def load_and_validate(self) -> Dict[str, Any]:
        """Load and validate the YAML integration plan."""
        print(f"📋 Loading integration plan: {self.plan_path}")
        
        try:
            with open(self.plan_path, 'r') as f:
                plan = yaml.safe_load(f)
            
            # Basic validation
            required_fields = ['version', 'batches', 'summary']
            missing_fields = [field for field in required_fields if field not in plan]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            print(f"✅ YAML validation passed")
            print(f"📊 Plan summary: {plan['summary']['total_features']} features in {len(plan['batches'])} batches")
            
            return plan
            
        except Exception as e:
            print(f"❌ YAML validation failed: {str(e)}")
            raise
    
    def enhance_with_metadata(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Add runtime estimates and dependency analysis."""
        print("🔧 Enhancing plan with metadata...")
        
        enhanced_plan = plan.copy()
        
        # Add enhanced metadata to summary
        enhanced_plan['metadata'] = {
            'enhanced_at': datetime.now().isoformat(),
            'validation_status': 'validated',
            'total_estimated_cost': 0.0,
            'risk_assessment': 'low',
            'dependency_graph': {},
            'runtime_estimates': {}
        }
        
        total_estimated_time = 0.0
        total_estimated_cost = 0.0
        
        # Process each batch
        for batch_idx, batch in enumerate(enhanced_plan['batches']):
            batch_id = batch['batch_id']
            batch_features = len(batch.get('features', []))
            
            # Estimate runtime (based on Phase 2 results: ~4.7 features/minute)
            estimated_minutes = batch_features / 4.7
            batch_cost = batch_features * 0.019  # From Phase 2: $0.019 per feature
            
            # Add batch metadata
            batch['metadata'] = {
                'estimated_runtime_minutes': round(estimated_minutes, 2),
                'estimated_cost_usd': round(batch_cost, 3),
                'feature_count': batch_features,
                'complexity_score': self._calculate_complexity(batch['features']),
                'dependencies': self._identify_dependencies(batch['features']),
                'risk_factors': self._assess_risks(batch['features'])
            }
            
            total_estimated_time += estimated_minutes
            total_estimated_cost += batch_cost
            
            print(f"  📦 Batch {batch_id}: {batch_features} features, ~{estimated_minutes:.1f}min, ${batch_cost:.2f}")
        
        # Update summary with enhanced data
        enhanced_plan['metadata']['total_estimated_time_minutes'] = round(total_estimated_time, 2)
        enhanced_plan['metadata']['total_estimated_cost'] = round(total_estimated_cost, 2)
        enhanced_plan['metadata']['runtime_estimates'] = {
            'sequential_hours': round(total_estimated_time / 60, 2),
            'parallel_hours': round(total_estimated_time / 60 / 3, 2),  # 3 batches parallel
            'cost_per_feature': 0.019
        }
        
        print(f"💰 Total estimated cost: ${total_estimated_cost:.2f}")
        print(f"⏱️ Estimated time: {total_estimated_time/60:.1f}h sequential, {total_estimated_time/60/3:.1f}h parallel")
        
        self.enhanced_plan = enhanced_plan
        return enhanced_plan
    
    def _calculate_complexity(self, features: List[Dict]) -> str:
        """Calculate complexity score based on feature characteristics."""
        api_features = sum(1 for f in features if f.get('interface') in ['both', 'api'])
        cli_features = sum(1 for f in features if f.get('interface') in ['both', 'cli'])
        
        complexity_score = (api_features * 1.2) + (cli_features * 0.8)
        
        if complexity_score > 30:
            return 'high'
        elif complexity_score > 15:
            return 'medium'
        else:
            return 'low'
    
    def _identify_dependencies(self, features: List[Dict]) -> List[str]:
        """Identify potential dependencies between features."""
        dependencies = []
        
        # Look for common patterns
        file_groups = {}
        for feature in features:
            file_path = feature.get('file_path', '')
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append(feature['name'])
        
        # Features in the same file have dependencies
        for file_path, feature_names in file_groups.items():
            if len(feature_names) > 1:
                dependencies.append(f"File dependency: {file_path} ({len(feature_names)} features)")
        
        return dependencies
    
    def _assess_risks(self, features: List[Dict]) -> List[str]:
        """Assess potential risks for the batch."""
        risks = []
        
        # Check for high-priority features
        high_priority = [f for f in features if f.get('priority_score', 0) > 80]
        if high_priority:
            risks.append(f"High-priority features: {len(high_priority)}")
        
        # Check for API vs CLI balance
        api_count = sum(1 for f in features if 'api' in f.get('interface', ''))
        cli_count = sum(1 for f in features if 'cli' in f.get('interface', ''))
        
        if abs(api_count - cli_count) > 10:
            risks.append("Unbalanced API/CLI distribution")
        
        return risks if risks else ['low-risk']
    
    def generate_checksum(self) -> str:
        """Generate checksum for the enhanced plan."""
        if not self.enhanced_plan:
            raise ValueError("Plan must be enhanced before generating checksum")
        
        # Create deterministic string for checksum
        plan_str = json.dumps(self.enhanced_plan, sort_keys=True, separators=(',', ':'))
        checksum = hashlib.sha256(plan_str.encode()).hexdigest()[:16]
        
        self.checksum = checksum
        print(f"🔐 Generated checksum: {checksum}")
        return checksum
    
    def store_in_memory(self) -> bool:
        """Store the enhanced plan and checksum in memory system."""
        if not MEMORY_AVAILABLE:
            print("⚠️ Memory system not available, storing to file")
            return self._store_to_file()
        
        try:
            # Store the enhanced plan
            memory_data = {
                'type': 'integration_plan_snapshot',
                'checksum': self.checksum,
                'plan': self.enhanced_plan,
                'stored_at': datetime.now().isoformat(),
                'status': 'immutable_contract'
            }
            
            # Use our implemented WriteMemory
            write_memory = WriteMemory()
            success = write_memory.store_memory(
                key=f"integration_plan_{self.checksum}",
                content=memory_data,
                memory_type='system'
            )
            
            if success:
                print(f"✅ Integration plan stored in memory with checksum: {self.checksum}")
                return True
            else:
                print("⚠️ Memory storage failed, falling back to file")
                return self._store_to_file()
                
        except Exception as e:
            print(f"⚠️ Memory storage error: {str(e)}, falling back to file")
            return self._store_to_file()
    
    def _store_to_file(self) -> bool:
        """Fallback: store to file system."""
        try:
            snapshot_dir = Path('ai/logs/integration_snapshots')
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            snapshot_file = snapshot_dir / f"snapshot_{self.checksum}.json"
            
            with open(snapshot_file, 'w') as f:
                json.dump({
                    'checksum': self.checksum,
                    'plan': self.enhanced_plan,
                    'stored_at': datetime.now().isoformat()
                }, f, indent=2)
            
            print(f"✅ Integration plan snapshot saved: {snapshot_file}")
            return True
            
        except Exception as e:
            print(f"❌ File storage failed: {str(e)}")
            return False


def main():
    """Main function to update integration specification."""
    print(f"""
🔧 INTEGRATION SPEC SNAPSHOT UPDATE
============================================================
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Task: Validate and enhance integration_plan.yaml
🔐 Goal: Create immutable contract with metadata
============================================================
""")
    
    plan_path = "docs/hookup_analysis/integration_plan.yaml"
    
    try:
        # Initialize validator
        validator = IntegrationSpecValidator(plan_path)
        
        # Load and validate YAML
        plan = validator.load_and_validate()
        
        # Enhance with metadata
        enhanced_plan = validator.enhance_with_metadata(plan)
        
        # Generate checksum
        checksum = validator.generate_checksum()
        
        # Store in memory system
        success = validator.store_in_memory()
        
        if success:
            print(f"""
✅ INTEGRATION SPEC SNAPSHOT COMPLETE!
============================================================
🔐 Checksum: {checksum}
📋 Features: {enhanced_plan['summary']['total_features']}
📦 Batches: {len(enhanced_plan['batches'])}
💰 Estimated Cost: ${enhanced_plan['metadata']['total_estimated_cost']:.2f}
⏱️ Estimated Time: {enhanced_plan['metadata']['runtime_estimates']['parallel_hours']:.1f}h
🛡️ Status: Immutable contract established
============================================================
""")
        else:
            print("❌ Failed to store integration snapshot")
            return 1
            
    except Exception as e:
        print(f"💥 Error updating integration spec: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
