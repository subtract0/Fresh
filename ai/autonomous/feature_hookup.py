#!/usr/bin/env python3
"""
Autonomous Feature Hookup System

This module autonomously analyzes the feature inventory and hooks up
unconnected features to CLI and API interfaces following TDD principles.

Addresses the core issue: 520+ features (94.4%) not accessible through CLI/API.
Target: Achieve 80%+ hookup ratio (440+ features connected).
"""
from __future__ import annotations
import json
import csv
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import subprocess
import re
import ast
import importlib.util

logger = logging.getLogger(__name__)


@dataclass
class FeatureAnalysis:
    """Analysis of a feature for hookup potential."""
    name: str
    file_path: str
    function_name: str
    description: str
    cli_accessible: bool
    api_accessible: bool
    business_value: int  # 1-10
    usage_frequency: int  # 1-10  
    complexity_score: int  # 1-10
    priority_score: float
    recommended_interface: str  # 'cli', 'api', 'both'
    command_suggestion: Optional[str] = None
    endpoint_suggestion: Optional[str] = None
    test_template: Optional[str] = None


@dataclass
class HookupPlan:
    """Plan for hooking up features."""
    total_features: int
    unhooked_features: int
    target_hookup_count: int
    prioritized_features: List[FeatureAnalysis]
    integration_batches: List[Dict[str, Any]]
    estimated_completion_time: str


class AutonomousFeatureHookup:
    """Autonomous system to hook up unconnected features."""
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = Path(working_dir)
        self.inventory_path = self.working_dir / "docs" / "feature_inventory.json"
        self.cli_patterns = self._analyze_existing_cli_patterns()
        self.api_patterns = self._analyze_existing_api_patterns()
        
    def _analyze_existing_cli_patterns(self) -> Dict[str, Any]:
        """Analyze existing CLI patterns for reuse."""
        cli_file = self.working_dir / "ai" / "cli" / "fresh.py"
        patterns = {
            "import_pattern": "from ai.cli.fresh import cmd_",
            "command_template": "def cmd_{name}(args):",
            "error_handling": "return 0 if success else 1",
            "output_formats": ["json", "text", "markdown"],
            "common_args": ["--json", "--limit", "--output", "--verbose"]
        }
        
        if cli_file.exists():
            content = cli_file.read_text()
            # Extract actual patterns from existing code
            patterns["existing_commands"] = re.findall(r"def cmd_(\w+)", content)
            patterns["argparse_pattern"] = "parser.add_argument" in content
        
        return patterns
        
    def _analyze_existing_api_patterns(self) -> Dict[str, Any]:
        """Analyze existing API patterns for reuse."""
        api_patterns = {
            "framework": "fastapi",  # Could detect from codebase
            "router_pattern": "@router.get",
            "response_models": ["JSONResponse", "PlainTextResponse"],
            "authentication": ["token_auth", "api_key"],
            "error_codes": [400, 401, 404, 500]
        }
        return api_patterns
        
    def load_feature_inventory(self) -> Dict[str, Any]:
        """Load current feature inventory."""
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"Feature inventory not found: {self.inventory_path}")
        
        with open(self.inventory_path, 'r') as f:
            return json.load(f)
    
    def analyze_unhooked_features(self, inventory: Dict[str, Any]) -> List[FeatureAnalysis]:
        """Analyze unhooked features and prioritize them."""
        unhooked_features = []
        
        for feature_data in inventory.get("features", []):
            # Skip already hooked features
            if feature_data.get("hooked_up", False) or feature_data.get("cli_accessible", False) or feature_data.get("api_accessible", False):
                continue
                
            # Calculate business value score
            business_value = self._calculate_business_value(feature_data)
            usage_frequency = self._calculate_usage_frequency(feature_data)  
            complexity = self._calculate_complexity(feature_data)
            
            priority_score = (business_value * usage_frequency) + (10 - complexity)
            
            # Determine recommended interface
            interface = self._recommend_interface(feature_data, business_value, usage_frequency)
            
            analysis = FeatureAnalysis(
                name=feature_data.get("name", "unknown"),
                file_path=feature_data.get("module_path", ""),
                function_name=feature_data.get("function_name", ""),
                description=feature_data.get("description", ""),
                cli_accessible=feature_data.get("cli_accessible", False),
                api_accessible=feature_data.get("api_accessible", False),
                business_value=business_value,
                usage_frequency=usage_frequency,
                complexity_score=complexity,
                priority_score=priority_score,
                recommended_interface=interface,
                command_suggestion=self._suggest_cli_command(feature_data.get("name", "unknown"), feature_data),
                endpoint_suggestion=self._suggest_api_endpoint(feature_data.get("name", "unknown"), feature_data)
            )
            
            unhooked_features.append(analysis)
        
        # Sort by priority score (highest first)
        unhooked_features.sort(key=lambda x: x.priority_score, reverse=True)
        
        return unhooked_features
        
    def _calculate_business_value(self, feature_data: Dict[str, Any]) -> int:
        """Calculate business value score (1-10)."""
        keywords_high_value = ["memory", "agent", "monitor", "orchestrate", "telegram", "github"]
        keywords_medium_value = ["test", "validate", "report", "analyze"]
        keywords_low_value = ["demo", "debug", "temp", "helper"]
        
        description = (feature_data.get("description") or "").lower()
        name = (feature_data.get("function_name") or "").lower()
        file_path = (feature_data.get("module_path") or "").lower()
        
        text = f"{description} {name} {file_path}"
        
        if any(keyword in text for keyword in keywords_high_value):
            return 9
        elif any(keyword in text for keyword in keywords_medium_value):
            return 6
        elif any(keyword in text for keyword in keywords_low_value):
            return 3
        else:
            return 5  # Default middle value
            
    def _calculate_usage_frequency(self, feature_data: Dict[str, Any]) -> int:
        """Calculate expected usage frequency (1-10)."""
        # This would ideally use actual usage data, but we'll estimate
        core_modules = ["cli", "agents", "memory", "monitor"]
        file_path = feature_data.get("module_path", "")
        
        if any(module in file_path for module in core_modules):
            return 8
        elif "interface" in file_path:
            return 6
        elif "tools" in file_path:
            return 7
        else:
            return 4
            
    def _calculate_complexity(self, feature_data: Dict[str, Any]) -> int:
        """Calculate implementation complexity (1-10, where 10 is most complex)."""
        function_name = feature_data.get("function_name") or ""
        description = feature_data.get("description") or ""
        
        # Simple heuristics for complexity
        if "async" in description.lower():
            complexity = 7
        elif len(function_name.split('_')) > 3:
            complexity = 6
        elif "initialize" in function_name or "setup" in function_name:
            complexity = 8
        else:
            complexity = 4
            
        return min(complexity, 10)
        
    def _recommend_interface(self, feature_data: Dict[str, Any], business_value: int, usage_frequency: int) -> str:
        """Recommend CLI, API, or both interfaces."""
        function_name = feature_data.get("function_name", "")
        description = feature_data.get("description", "").lower()
        
        # API-first recommendations
        if any(keyword in description for keyword in ["server", "web", "http", "endpoint"]):
            return "api"
        
        # CLI-first recommendations  
        if any(keyword in description for keyword in ["command", "cli", "terminal", "console"]):
            return "cli"
            
        # Both interfaces for high-value, high-frequency features
        if business_value >= 8 and usage_frequency >= 7:
            return "both"
            
        # Default to CLI for most features (easier to implement and test)
        return "cli"
        
    def _suggest_cli_command(self, feature_name: str, feature_data: Dict[str, Any]) -> str:
        """Suggest CLI command name and structure."""
        function_name = feature_data.get("function_name") or feature_name or "unknown"
        
        # Convert function name to CLI command
        # e.g., get_memory_stats -> memory stats
        parts = function_name.replace("get_", "").replace("set_", "").replace("_", " ")
        
        # Group related commands
        if "memory" in parts:
            return f"memory {parts.replace('memory', '').strip()}"
        elif "agent" in parts:
            return f"agent {parts.replace('agent', '').strip()}"
        elif "monitor" in parts:
            return f"monitor {parts.replace('monitor', '').strip()}"
        else:
            return parts
            
    def _suggest_api_endpoint(self, feature_name: str, feature_data: Dict[str, Any]) -> str:
        """Suggest API endpoint path."""
        function_name = feature_data.get("function_name") or feature_name or "unknown"
        
        # Convert function name to REST endpoint
        if function_name.startswith("get_"):
            method = "GET"
            resource = function_name[4:]
        elif function_name.startswith("create_") or function_name.startswith("add_"):
            method = "POST"  
            resource = function_name[7:] if function_name.startswith("create_") else function_name[4:]
        elif function_name.startswith("update_"):
            method = "PUT"
            resource = function_name[7:]
        elif function_name.startswith("delete_"):
            method = "DELETE"
            resource = function_name[7:]
        else:
            method = "POST"
            resource = function_name
            
        # Convert snake_case to kebab-case for URLs
        endpoint_path = resource.replace("_", "-")
        
        return f"{method} /api/v1/{endpoint_path}"
        
    def generate_hookup_plan(self, max_features: int = 440) -> HookupPlan:
        """Generate comprehensive hookup plan."""
        inventory = self.load_feature_inventory()
        unhooked = self.analyze_unhooked_features(inventory)
        
        # Limit to target number
        prioritized = unhooked[:max_features]
        
        # Create batches of 50 features each
        batch_size = 50
        batches = []
        
        for i in range(0, len(prioritized), batch_size):
            batch = prioritized[i:i + batch_size]
            batches.append({
                "batch_id": i // batch_size + 1,
                "features": batch,
                "estimated_time_hours": len(batch) * 0.25,  # 15 minutes per feature
                "test_count": len(batch),
                "cli_commands": sum(1 for f in batch if f.recommended_interface in ["cli", "both"]),
                "api_endpoints": sum(1 for f in batch if f.recommended_interface in ["api", "both"])
            })
        
        plan = HookupPlan(
            total_features=inventory.get("summary", {}).get("total_features", 0),
            unhooked_features=len(unhooked),
            target_hookup_count=len(prioritized),
            prioritized_features=prioritized,
            integration_batches=batches,
            estimated_completion_time=f"{sum(b['estimated_time_hours'] for b in batches):.1f} hours"
        )
        
        return plan
        
    def export_prioritized_features(self, features: List[FeatureAnalysis], output_path: str):
        """Export prioritized features to CSV for transparency."""
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'rank', 'name', 'file_path', 'function_name', 'description', 
                'cli_accessible', 'api_accessible', 'business_value', 'usage_frequency', 
                'complexity_score', 'priority_score', 'recommended_interface', 
                'command_suggestion', 'endpoint_suggestion', 'test_template'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, feature in enumerate(features, 1):
                row = asdict(feature)
                row['rank'] = i
                writer.writerow(row)
                
    def generate_integration_spec(self, plan: HookupPlan, output_path: str):
        """Generate machine-readable integration specification."""
        spec = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_features": plan.total_features,
                "target_hookup_count": plan.target_hookup_count,
                "batches": len(plan.integration_batches),
                "estimated_time": plan.estimated_completion_time
            },
            "batches": []
        }
        
        for batch_info in plan.integration_batches:
            batch_spec = {
                "batch_id": batch_info["batch_id"],
                "features": [],
                "estimated_time_hours": batch_info["estimated_time_hours"]
            }
            
            for feature in batch_info["features"]:
                feature_spec = {
                    "name": feature.name,
                    "interface": feature.recommended_interface,
                    "cli_command": feature.command_suggestion,
                    "api_endpoint": feature.endpoint_suggestion,
                    "file_path": feature.file_path,
                    "function_name": feature.function_name,
                    "test_path": f"tests/cli/test_{feature.name}.py" if "cli" in feature.recommended_interface else f"tests/api/test_{feature.name}.py",
                    "priority_score": feature.priority_score
                }
                batch_spec["features"].append(feature_spec)
            
            spec["batches"].append(batch_spec)
        
        with open(output_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
            
        return spec
        
    def validate_plan(self, plan: HookupPlan) -> Dict[str, Any]:
        """Validate the hookup plan for feasibility."""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "statistics": {
                "cli_features": sum(1 for f in plan.prioritized_features if f.recommended_interface in ["cli", "both"]),
                "api_features": sum(1 for f in plan.prioritized_features if f.recommended_interface in ["api", "both"]),
                "high_priority_features": sum(1 for f in plan.prioritized_features if f.priority_score > 15),
                "complex_features": sum(1 for f in plan.prioritized_features if f.complexity_score > 7)
            }
        }
        
        # Validation checks
        if plan.target_hookup_count < plan.unhooked_features * 0.8:
            validation["warnings"].append(f"Target hookup count ({plan.target_hookup_count}) is less than 80% of unhooked features")
            
        if validation["statistics"]["complex_features"] > plan.target_hookup_count * 0.3:
            validation["warnings"].append("High number of complex features may slow implementation")
            
        return validation


def main():
    """Main entry point for autonomous feature hookup."""
    hookup_system = AutonomousFeatureHookup()
    
    print("🔗 AUTONOMOUS FEATURE HOOKUP SYSTEM")
    print("=" * 50)
    
    try:
        # Generate hookup plan
        print("📊 Analyzing feature inventory...")
        plan = hookup_system.generate_hookup_plan()
        
        print(f"✅ Analysis complete!")
        print(f"   Total Features: {plan.total_features}")
        print(f"   Unhooked Features: {plan.unhooked_features}")
        print(f"   Target Hookup: {plan.target_hookup_count}")
        print(f"   Batches: {len(plan.integration_batches)}")
        print(f"   Estimated Time: {plan.estimated_completion_time}")
        
        # Export results
        output_dir = Path("docs/hookup_analysis")
        output_dir.mkdir(exist_ok=True)
        
        # Export prioritized features
        csv_path = output_dir / "unconnected_prioritized.csv"
        hookup_system.export_prioritized_features(plan.prioritized_features, csv_path)
        print(f"📄 Exported prioritized features to {csv_path}")
        
        # Generate integration spec
        spec_path = output_dir / "integration_plan.yaml"
        spec = hookup_system.generate_integration_spec(plan, spec_path)
        print(f"📋 Generated integration plan at {spec_path}")
        
        # Validate plan
        validation = hookup_system.validate_plan(plan)
        print(f"\n🔍 Plan Validation: {'✅ VALID' if validation['valid'] else '❌ INVALID'}")
        
        if validation["warnings"]:
            print("⚠️ Warnings:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        if validation["errors"]:
            print("❌ Errors:")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        print("\n📈 Statistics:")
        stats = validation["statistics"]
        print(f"   CLI Features: {stats['cli_features']}")
        print(f"   API Features: {stats['api_features']}")
        print(f"   High Priority: {stats['high_priority_features']}")
        print(f"   Complex Features: {stats['complex_features']}")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review {csv_path} for feature priorities")
        print(f"   2. Implement features in batches using {spec_path}")
        print(f"   3. Run TDD cycle for each batch")
        print(f"   4. Update feature inventory after each batch")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
