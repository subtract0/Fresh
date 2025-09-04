"""
Improvement Engine for Autonomous Loop
Generates and executes targeted improvements using the Magic Command system.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import logging

# Import will be done dynamically to avoid circular imports
# from ai.autonomous.loop import ImprovementOpportunity
from ai.cli.magic import MagicCommand
from ai.memory.intelligent_store import IntelligentMemoryStore


class ImprovementEngine:
    """
    Generates and executes targeted improvements.
    Integrates with Magic Command system for intelligent code improvements.
    """
    
    def __init__(self, 
                 working_directory: str,
                 memory_store: Optional[IntelligentMemoryStore] = None,
                 magic_command: Optional[MagicCommand] = None):
        """Initialize the improvement engine."""
        self.working_directory = Path(working_directory)
        self.memory_store = memory_store or IntelligentMemoryStore()
        self.magic_command = magic_command or MagicCommand(
            working_directory=str(self.working_directory),
            memory_store=self.memory_store
        )
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def plan_improvement(self, opportunity: Any) -> Optional[Dict[str, Any]]:
        """
        Plan an improvement for the given opportunity.
        
        Args:
            opportunity: ImprovementOpportunity to plan improvement for
            
        Returns:
            Dictionary containing improvement plan or None if no plan possible
        """
        try:
            # Analyze the opportunity
            improvement_type = self._determine_improvement_type(opportunity)
            
            if not improvement_type:
                self.logger.warning(f"Could not determine improvement type for: {opportunity.id}")
                return None
            
            # Generate improvement plan based on type
            plan = self._generate_improvement_plan(opportunity, improvement_type)
            
            if plan:
                self.logger.info(f"Generated improvement plan for: {opportunity.id}")
                return plan
            else:
                self.logger.warning(f"Could not generate plan for: {opportunity.id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error planning improvement for {opportunity.id}: {e}")
            return None
    
    def execute_improvement(self, improvement_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the improvement plan.
        
        Args:
            improvement_plan: Plan dictionary from plan_improvement()
            
        Returns:
            Dictionary containing execution results
        """
        try:
            opportunity = improvement_plan["opportunity"]
            improvement_type = improvement_plan["type"]
            
            self.logger.info(f"Executing {improvement_type} improvement for: {opportunity.id}")
            
            # Execute based on improvement type
            if improvement_type == "magic_fix":
                result = self._execute_magic_fix(improvement_plan)
            elif improvement_type == "magic_add":
                result = self._execute_magic_add(improvement_plan)
            elif improvement_type == "magic_test":
                result = self._execute_magic_test(improvement_plan)
            elif improvement_type == "magic_refactor":
                result = self._execute_magic_refactor(improvement_plan)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown improvement type: {improvement_type}"
                }
            
            # Record execution in memory
            self._record_execution(opportunity, improvement_plan, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing improvement: {e}")
            return {
                "success": False,
                "error": str(e),
                "critical_failure": False
            }
    
    def prioritize_fixes(self, opportunities: List[Any]) -> List[Any]:
        """
        Prioritize improvement opportunities by impact and safety.
        
        Args:
            opportunities: List of improvement opportunities
            
        Returns:
            Sorted list of opportunities by priority
        """
        # Score each opportunity
        scored_opportunities = []
        
        for opportunity in opportunities:
            # Calculate composite score
            impact_score = self._calculate_impact_score(opportunity)
            safety_score = opportunity.safety_score
            effort_score = self._calculate_effort_score(opportunity)
            
            # Weighted composite score
            composite_score = (
                impact_score * 0.4 +
                safety_score * 0.4 +
                effort_score * 0.2
            )
            
            scored_opportunities.append((composite_score, opportunity))
        
        # Sort by score descending
        scored_opportunities.sort(key=lambda x: x[0], reverse=True)
        
        return [opp for score, opp in scored_opportunities]
    
    def validate_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate changes before applying them.
        
        Args:
            changes: Dictionary describing changes to validate
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        try:
            # Check for syntax issues in code changes
            if "code_changes" in changes:
                syntax_validation = self._validate_syntax(changes["code_changes"])
                validation_result["warnings"].extend(syntax_validation.get("warnings", []))
                validation_result["errors"].extend(syntax_validation.get("errors", []))
            
            # Check for logical issues
            if "logic_changes" in changes:
                logic_validation = self._validate_logic(changes["logic_changes"])
                validation_result["warnings"].extend(logic_validation.get("warnings", []))
                validation_result["errors"].extend(logic_validation.get("errors", []))
            
            # Check impact on other parts of codebase
            impact_validation = self._validate_impact(changes)
            validation_result["warnings"].extend(impact_validation.get("warnings", []))
            validation_result["errors"].extend(impact_validation.get("errors", []))
            
            # Determine overall validity
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation failed: {e}")
        
        return validation_result
    
    def _determine_improvement_type(self, opportunity: Any) -> Optional[str]:
        """Determine the type of improvement needed."""
        opportunity_type = opportunity.type.lower()
        description = opportunity.description.lower()
        
        # Map opportunity types to improvement types
        if opportunity_type in ["bug", "security", "performance"]:
            return "magic_fix"
        elif opportunity_type == "test_coverage":
            return "magic_test"
        elif "refactor" in description or "restructure" in description:
            return "magic_refactor"
        elif opportunity_type in ["quality", "feature"]:
            # Could be add or fix depending on description
            if "add" in description or "implement" in description:
                return "magic_add"
            else:
                return "magic_fix"
        elif opportunity_type == "todo":
            # TODOs usually require adding missing functionality
            return "magic_add"
        else:
            # Default to fix for unknown types
            return "magic_fix"
    
    def _generate_improvement_plan(self, opportunity: Any, improvement_type: str) -> Dict[str, Any]:
        """Generate specific improvement plan."""
        base_plan = {
            "opportunity": opportunity,
            "type": improvement_type,
            "description": opportunity.description,
            "estimated_effort": opportunity.estimated_effort,
            "safety_score": opportunity.safety_score
        }
        
        # Add type-specific planning
        if improvement_type == "magic_fix":
            base_plan["magic_command"] = "fix"
            base_plan["command_description"] = self._generate_fix_description(opportunity)
        elif improvement_type == "magic_add":
            base_plan["magic_command"] = "add"
            base_plan["command_description"] = self._generate_add_description(opportunity)
        elif improvement_type == "magic_test":
            base_plan["magic_command"] = "test"
            base_plan["command_description"] = self._generate_test_description(opportunity)
        elif improvement_type == "magic_refactor":
            base_plan["magic_command"] = "refactor"
            base_plan["command_description"] = self._generate_refactor_description(opportunity)
        
        return base_plan
    
    def _execute_magic_fix(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute magic fix command."""
        try:
            description = plan["command_description"]
            result = self.magic_command.fix(description)
            
            return {
                "success": result.get("success", False),
                "description": result.get("description", ""),
                "files_changed": result.get("files_changed", []),
                "issues_found": result.get("issues_found", []),
                "execution_type": "magic_fix",
                "critical_failure": not result.get("success", False) and "critical" in str(result).lower()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_type": "magic_fix",
                "critical_failure": True
            }
    
    def _execute_magic_add(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute magic add command."""
        try:
            description = plan["command_description"]
            result = self.magic_command.add(description)
            
            return {
                "success": result.get("success", False),
                "description": result.get("description", ""),
                "files_changed": result.get("files_changed", []),
                "feature_added": result.get("feature_added", False),
                "execution_type": "magic_add",
                "critical_failure": False  # Adding features is usually not critical
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_type": "magic_add",
                "critical_failure": False
            }
    
    def _execute_magic_test(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute magic test command."""
        try:
            description = plan["command_description"]
            result = self.magic_command.test(description)
            
            return {
                "success": result.get("success", False),
                "description": result.get("description", ""),
                "files_changed": result.get("files_changed", []),
                "tests_added": result.get("tests_added", False),
                "execution_type": "magic_test",
                "critical_failure": False  # Test additions are not critical
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_type": "magic_test",
                "critical_failure": False
            }
    
    def _execute_magic_refactor(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute magic refactor command."""
        try:
            description = plan["command_description"]
            result = self.magic_command.refactor(description)
            
            return {
                "success": result.get("success", False),
                "description": result.get("description", ""),
                "files_changed": result.get("files_changed", []),
                "refactored": result.get("refactored", False),
                "execution_type": "magic_refactor",
                "critical_failure": not result.get("success", False) and len(result.get("files_changed", [])) > 10
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_type": "magic_refactor",
                "critical_failure": True  # Refactoring failures can be critical
            }
    
    def _generate_fix_description(self, opportunity: Any) -> str:
        """Generate description for fix command."""
        if opportunity.type == "security":
            return f"security issue: {opportunity.description}"
        elif opportunity.type == "bug":
            return f"bug: {opportunity.description}"
        elif opportunity.type == "performance":
            return f"performance issue: {opportunity.description}"
        else:
            return opportunity.description
    
    def _generate_add_description(self, opportunity: Any) -> str:
        """Generate description for add command."""
        if opportunity.type == "todo":
            # Extract what needs to be added from TODO
            todo_text = opportunity.details.get("todo_text", "")
            if todo_text:
                return f"implement TODO: {todo_text}"
            else:
                return f"implement missing functionality: {opportunity.description}"
        else:
            return f"add {opportunity.description}"
    
    def _generate_test_description(self, opportunity: Any) -> str:
        """Generate description for test command."""
        return f"comprehensive tests for {opportunity.description}"
    
    def _generate_refactor_description(self, opportunity: Any) -> str:
        """Generate description for refactor command."""
        return f"refactor {opportunity.description}"
    
    def _calculate_impact_score(self, opportunity: Any) -> float:
        """Calculate impact score for opportunity."""
        # Base impact on type and priority
        type_impact = {
            "security": 1.0,
            "bug": 0.8,
            "performance": 0.7,
            "test_coverage": 0.6,
            "quality": 0.5,
            "todo": 0.3
        }
        
        base_impact = type_impact.get(opportunity.type.lower(), 0.4)
        
        # Adjust for priority
        adjusted_impact = base_impact * opportunity.priority
        
        return min(1.0, adjusted_impact)
    
    def _calculate_effort_score(self, opportunity: Any) -> float:
        """Calculate effort score (higher = less effort)."""
        effort_scores = {
            "low": 1.0,
            "medium": 0.6,
            "high": 0.3
        }
        
        return effort_scores.get(opportunity.estimated_effort, 0.5)
    
    def _validate_syntax(self, code_changes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Validate syntax of code changes."""
        result = {"warnings": [], "errors": []}
        
        try:
            for change in code_changes:
                if "new_code" in change:
                    # Simple syntax validation
                    code = change["new_code"]
                    if not code.strip():
                        result["warnings"].append("Empty code change detected")
                    elif code.count("(") != code.count(")"):
                        result["errors"].append("Unmatched parentheses in code change")
                    elif code.count("{") != code.count("}"):
                        result["errors"].append("Unmatched braces in code change")
        except Exception as e:
            result["errors"].append(f"Syntax validation failed: {e}")
        
        return result
    
    def _validate_logic(self, logic_changes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Validate logical consistency of changes."""
        result = {"warnings": [], "errors": []}
        
        # This would implement more sophisticated logic validation
        # For now, just basic checks
        try:
            for change in logic_changes:
                if "removes_functionality" in change and change["removes_functionality"]:
                    result["warnings"].append("Change removes existing functionality")
        except Exception as e:
            result["errors"].append(f"Logic validation failed: {e}")
        
        return result
    
    def _validate_impact(self, changes: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate impact on rest of codebase."""
        result = {"warnings": [], "errors": []}
        
        try:
            files_changed = changes.get("files_changed", [])
            
            # Check for changes to critical files
            critical_files = ["__init__.py", "setup.py", "pyproject.toml"]
            
            for file_path in files_changed:
                filename = Path(file_path).name
                if filename in critical_files:
                    result["warnings"].append(f"Changing critical file: {filename}")
            
            # Check for large change scope
            if len(files_changed) > 5:
                result["warnings"].append(f"Large change scope: {len(files_changed)} files")
                
        except Exception as e:
            result["errors"].append(f"Impact validation failed: {e}")
        
        return result
    
    def _record_execution(self, opportunity: Any, plan: Dict[str, Any], result: Dict[str, Any]):
        """Record execution in memory for learning."""
        try:
            success_tag = "success" if result.get("success") else "failure"
            
            self.memory_store.write(
                content=f"Improvement execution: {opportunity.type} - {opportunity.description}",
                tags=["improvement_engine", "execution", success_tag, opportunity.type]
            )
        except:
            pass  # Don't fail if memory recording fails
