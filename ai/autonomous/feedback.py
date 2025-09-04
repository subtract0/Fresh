"""
Feedback Loop for Autonomous Loop
Learns from improvement results to enhance future decisions.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from ai.memory.intelligent_store import IntelligentMemoryStore


@dataclass
class LearningPattern:
    """Represents a learned pattern from successful/failed improvements."""
    pattern_id: str
    pattern_type: str  # "success", "failure", "strategy"
    confidence: float  # 0.0 to 1.0
    description: str
    conditions: Dict[str, Any]  # Conditions when this pattern applies
    actions: Dict[str, Any]     # Actions to take when pattern matches
    outcomes: Dict[str, Any]    # Expected outcomes
    usage_count: int
    success_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "confidence": self.confidence,
            "description": self.description,
            "conditions": self.conditions,
            "actions": self.actions,
            "outcomes": self.outcomes,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }


class FeedbackLoop:
    """
    Learns from improvement results to enhance future decisions.
    Analyzes patterns in successful and failed improvements to improve strategy.
    """
    
    def __init__(self, memory_store: Optional[IntelligentMemoryStore] = None):
        """Initialize the feedback loop."""
        self.memory_store = memory_store or IntelligentMemoryStore()
        
        # Track patterns and learning
        self.learned_patterns: List[LearningPattern] = []
        self.execution_history: List[Dict[str, Any]] = []
        
        # Learning configuration
        self.config = {
            "min_confidence_threshold": 0.3,
            "pattern_match_threshold": 0.7,
            "max_patterns": 100,
            "learning_rate": 0.1
        }
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load existing patterns from memory
        self._load_patterns_from_memory()
    
    def analyze_results(self, execution_results: List[Dict[str, Any]]):
        """
        Analyze execution results to identify patterns.
        
        Args:
            execution_results: List of execution results from improvement engine
        """
        try:
            # Add to execution history
            for result in execution_results:
                result["timestamp"] = datetime.now().isoformat()
                self.execution_history.append(result)
            
            # Keep history manageable
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
            
            # Identify new patterns
            new_patterns = self._identify_patterns(execution_results)
            
            # Update existing patterns
            self._update_existing_patterns(execution_results)
            
            # Add new patterns
            for pattern in new_patterns:
                self._add_pattern(pattern)
            
            # Save patterns to memory
            self._save_patterns_to_memory()
            
            self.logger.info(f"Analyzed {len(execution_results)} results, found {len(new_patterns)} new patterns")
            
        except Exception as e:
            self.logger.error(f"Error analyzing results: {e}")
    
    def update_patterns(self):
        """Update pattern confidence and strategies based on recent performance."""
        try:
            # Get recent execution history
            cutoff = datetime.now() - timedelta(days=7)
            recent_executions = [
                ex for ex in self.execution_history 
                if datetime.fromisoformat(ex.get("timestamp", "1970-01-01")) > cutoff
            ]
            
            if not recent_executions:
                return
            
            # Update pattern success rates
            for pattern in self.learned_patterns:
                pattern_matches = self._find_pattern_matches(pattern, recent_executions)
                
                if pattern_matches:
                    successes = sum(1 for match in pattern_matches if match.get("success"))
                    pattern.success_rate = successes / len(pattern_matches)
                    pattern.usage_count += len(pattern_matches)
                    
                    # Adjust confidence based on recent performance
                    if pattern.success_rate > 0.8:
                        pattern.confidence = min(1.0, pattern.confidence + self.config["learning_rate"])
                    elif pattern.success_rate < 0.3:
                        pattern.confidence = max(0.1, pattern.confidence - self.config["learning_rate"])
            
            # Remove low-confidence patterns
            self.learned_patterns = [
                p for p in self.learned_patterns 
                if p.confidence >= self.config["min_confidence_threshold"]
            ]
            
            # Keep only top patterns
            self.learned_patterns.sort(key=lambda x: x.confidence * x.success_rate, reverse=True)
            self.learned_patterns = self.learned_patterns[:self.config["max_patterns"]]
            
            self.logger.info(f"Updated {len(self.learned_patterns)} patterns")
            
        except Exception as e:
            self.logger.error(f"Error updating patterns: {e}")
    
    def record_success(self, execution_result: Dict[str, Any]):
        """Record a successful improvement execution."""
        try:
            # Extract success factors
            success_factors = self._extract_success_factors(execution_result)
            
            # Create or update success pattern
            pattern = self._create_success_pattern(execution_result, success_factors)
            
            if pattern:
                self._add_pattern(pattern)
            
            # Store in memory
            self.memory_store.write(
                content=f"Successful improvement: {execution_result.get('execution_type', 'unknown')}",
                tags=["feedback_loop", "success", execution_result.get("execution_type", "unknown")]
            )
            
        except Exception as e:
            self.logger.error(f"Error recording success: {e}")
    
    def record_failure(self, execution_result: Dict[str, Any]):
        """Record a failed improvement execution."""
        try:
            # Extract failure factors
            failure_factors = self._extract_failure_factors(execution_result)
            
            # Create or update failure pattern
            pattern = self._create_failure_pattern(execution_result, failure_factors)
            
            if pattern:
                self._add_pattern(pattern)
            
            # Store in memory
            error_msg = execution_result.get("error", "Unknown failure")
            self.memory_store.write(
                content=f"Failed improvement: {execution_result.get('execution_type', 'unknown')} - {error_msg}",
                tags=["feedback_loop", "failure", execution_result.get("execution_type", "unknown")]
            )
            
        except Exception as e:
            self.logger.error(f"Error recording failure: {e}")
    
    def adjust_strategies(self) -> Dict[str, Any]:
        """
        Adjust improvement strategies based on learned patterns.
        
        Returns:
            Dictionary containing strategy adjustments
        """
        try:
            adjustments = {
                "priority_adjustments": {},
                "safety_adjustments": {},
                "effort_adjustments": {},
                "type_preferences": {}
            }
            
            # Analyze success patterns to identify what works
            success_patterns = [p for p in self.learned_patterns if p.pattern_type == "success"]
            
            for pattern in success_patterns:
                # Extract insights from successful patterns
                if "opportunity_type" in pattern.conditions:
                    opp_type = pattern.conditions["opportunity_type"]
                    current_weight = adjustments["type_preferences"].get(opp_type, 1.0)
                    adjustments["type_preferences"][opp_type] = min(1.5, current_weight + 0.1)
            
            # Analyze failure patterns to identify what to avoid
            failure_patterns = [p for p in self.learned_patterns if p.pattern_type == "failure"]
            
            for pattern in failure_patterns:
                if "opportunity_type" in pattern.conditions:
                    opp_type = pattern.conditions["opportunity_type"]
                    current_weight = adjustments["type_preferences"].get(opp_type, 1.0)
                    adjustments["type_preferences"][opp_type] = max(0.5, current_weight - 0.1)
            
            return adjustments
            
        except Exception as e:
            self.logger.error(f"Error adjusting strategies: {e}")
            return {}
    
    def get_recommendations(self, opportunity_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get recommendations based on learned patterns.
        
        Args:
            opportunity_context: Context about the improvement opportunity
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        try:
            # Find matching patterns
            matching_patterns = []
            
            for pattern in self.learned_patterns:
                if self._pattern_matches_context(pattern, opportunity_context):
                    matching_patterns.append(pattern)
            
            # Sort by confidence and success rate
            matching_patterns.sort(
                key=lambda x: x.confidence * x.success_rate, 
                reverse=True
            )
            
            # Generate recommendations from top patterns
            for pattern in matching_patterns[:3]:  # Top 3 patterns
                recommendation = {
                    "type": "pattern_based",
                    "confidence": pattern.confidence,
                    "description": pattern.description,
                    "recommended_actions": pattern.actions,
                    "expected_outcomes": pattern.outcomes,
                    "pattern_success_rate": pattern.success_rate
                }
                recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
        
        return recommendations
    
    def _identify_patterns(self, execution_results: List[Dict[str, Any]]) -> List[LearningPattern]:
        """Identify new patterns from execution results."""
        new_patterns = []
        
        try:
            # Group results by success/failure
            successes = [r for r in execution_results if r.get("success")]
            failures = [r for r in execution_results if not r.get("success")]
            
            # Identify success patterns
            success_patterns = self._find_common_patterns(successes, "success")
            new_patterns.extend(success_patterns)
            
            # Identify failure patterns
            failure_patterns = self._find_common_patterns(failures, "failure")
            new_patterns.extend(failure_patterns)
            
        except Exception as e:
            self.logger.error(f"Error identifying patterns: {e}")
        
        return new_patterns
    
    def _find_common_patterns(self, results: List[Dict[str, Any]], pattern_type: str) -> List[LearningPattern]:
        """Find common patterns in a set of results."""
        patterns = []
        
        if len(results) < 2:  # Need at least 2 results to find patterns
            return patterns
        
        try:
            # Group by execution type
            type_groups = {}
            for result in results:
                exec_type = result.get("execution_type", "unknown")
                if exec_type not in type_groups:
                    type_groups[exec_type] = []
                type_groups[exec_type].append(result)
            
            # Create patterns for common execution types
            for exec_type, group_results in type_groups.items():
                if len(group_results) >= 2:  # At least 2 instances
                    pattern = LearningPattern(
                        pattern_id=f"{pattern_type}_{exec_type}_{len(patterns)}",
                        pattern_type=pattern_type,
                        confidence=min(0.8, len(group_results) / 10.0),
                        description=f"{pattern_type.title()} pattern for {exec_type}",
                        conditions={"execution_type": exec_type},
                        actions=self._extract_common_actions(group_results),
                        outcomes=self._extract_common_outcomes(group_results),
                        usage_count=len(group_results),
                        success_rate=1.0 if pattern_type == "success" else 0.0
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            self.logger.error(f"Error finding common patterns: {e}")
        
        return patterns
    
    def _extract_success_factors(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract factors that contributed to success."""
        factors = {}
        
        try:
            if "opportunity" in result:
                opp = result["opportunity"]
                factors["opportunity_type"] = getattr(opp, "type", "unknown")
                factors["safety_score"] = getattr(opp, "safety_score", 0.5)
                factors["estimated_effort"] = getattr(opp, "estimated_effort", "medium")
            
            factors["execution_type"] = result.get("execution_type", "unknown")
            factors["files_changed_count"] = len(result.get("files_changed", []))
            
        except Exception as e:
            self.logger.error(f"Error extracting success factors: {e}")
        
        return factors
    
    def _extract_failure_factors(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract factors that contributed to failure."""
        factors = {}
        
        try:
            if "opportunity" in result:
                opp = result["opportunity"]
                factors["opportunity_type"] = getattr(opp, "type", "unknown")
                factors["safety_score"] = getattr(opp, "safety_score", 0.5)
                factors["estimated_effort"] = getattr(opp, "estimated_effort", "medium")
            
            factors["execution_type"] = result.get("execution_type", "unknown")
            factors["error_type"] = result.get("error", "unknown_error")
            factors["critical_failure"] = result.get("critical_failure", False)
            
        except Exception as e:
            self.logger.error(f"Error extracting failure factors: {e}")
        
        return factors
    
    def _create_success_pattern(self, result: Dict[str, Any], factors: Dict[str, Any]) -> Optional[LearningPattern]:
        """Create a success pattern from result and factors."""
        try:
            pattern = LearningPattern(
                pattern_id=f"success_{factors.get('execution_type', 'unknown')}_{int(datetime.now().timestamp())}",
                pattern_type="success",
                confidence=0.6,  # Initial confidence
                description=f"Success pattern for {factors.get('execution_type', 'unknown')}",
                conditions=factors,
                actions={"approach": result.get("execution_type", "unknown")},
                outcomes={"success": True, "files_changed": len(result.get("files_changed", []))},
                usage_count=1,
                success_rate=1.0
            )
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"Error creating success pattern: {e}")
            return None
    
    def _create_failure_pattern(self, result: Dict[str, Any], factors: Dict[str, Any]) -> Optional[LearningPattern]:
        """Create a failure pattern from result and factors."""
        try:
            pattern = LearningPattern(
                pattern_id=f"failure_{factors.get('execution_type', 'unknown')}_{int(datetime.now().timestamp())}",
                pattern_type="failure",
                confidence=0.6,  # Initial confidence
                description=f"Failure pattern for {factors.get('execution_type', 'unknown')}",
                conditions=factors,
                actions={"avoid": True, "alternative": "manual_review"},
                outcomes={"success": False, "error": result.get("error", "unknown")},
                usage_count=1,
                success_rate=0.0
            )
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"Error creating failure pattern: {e}")
            return None
    
    def _add_pattern(self, pattern: LearningPattern):
        """Add a new pattern or merge with existing similar pattern."""
        # Check for similar existing patterns
        similar_pattern = self._find_similar_pattern(pattern)
        
        if similar_pattern:
            # Merge patterns
            similar_pattern.usage_count += pattern.usage_count
            similar_pattern.confidence = (similar_pattern.confidence + pattern.confidence) / 2
        else:
            # Add new pattern
            self.learned_patterns.append(pattern)
    
    def _find_similar_pattern(self, pattern: LearningPattern) -> Optional[LearningPattern]:
        """Find similar existing pattern."""
        for existing in self.learned_patterns:
            if (existing.pattern_type == pattern.pattern_type and
                existing.conditions == pattern.conditions):
                return existing
        return None
    
    def _update_existing_patterns(self, execution_results: List[Dict[str, Any]]):
        """Update existing patterns based on new results."""
        for result in execution_results:
            # Find patterns that match this result
            for pattern in self.learned_patterns:
                if self._result_matches_pattern(result, pattern):
                    # Update pattern statistics
                    pattern.usage_count += 1
                    
                    if result.get("success"):
                        pattern.success_rate = (
                            (pattern.success_rate * (pattern.usage_count - 1) + 1) / 
                            pattern.usage_count
                        )
                    else:
                        pattern.success_rate = (
                            (pattern.success_rate * (pattern.usage_count - 1)) / 
                            pattern.usage_count
                        )
    
    def _result_matches_pattern(self, result: Dict[str, Any], pattern: LearningPattern) -> bool:
        """Check if a result matches a pattern's conditions."""
        try:
            for key, value in pattern.conditions.items():
                if key == "execution_type":
                    if result.get("execution_type") != value:
                        return False
                elif key == "opportunity_type":
                    if "opportunity" in result:
                        opp = result["opportunity"]
                        if getattr(opp, "type", "unknown") != value:
                            return False
            return True
        except:
            return False
    
    def _pattern_matches_context(self, pattern: LearningPattern, context: Dict[str, Any]) -> bool:
        """Check if a pattern matches the given context."""
        try:
            match_score = 0
            total_conditions = len(pattern.conditions)
            
            for key, value in pattern.conditions.items():
                if key in context and context[key] == value:
                    match_score += 1
            
            return (match_score / total_conditions) >= self.config["pattern_match_threshold"]
        except:
            return False
    
    def _find_pattern_matches(self, pattern: LearningPattern, executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find executions that match a pattern."""
        matches = []
        for execution in executions:
            if self._result_matches_pattern(execution, pattern):
                matches.append(execution)
        return matches
    
    def _extract_common_actions(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common actions from results."""
        # Simple implementation - extract most common execution type
        exec_types = [r.get("execution_type", "unknown") for r in results]
        most_common = max(set(exec_types), key=exec_types.count) if exec_types else "unknown"
        
        return {"approach": most_common}
    
    def _extract_common_outcomes(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common outcomes from results."""
        total = len(results)
        successes = sum(1 for r in results if r.get("success"))
        avg_files = sum(len(r.get("files_changed", [])) for r in results) / total if total > 0 else 0
        
        return {
            "success_rate": successes / total if total > 0 else 0,
            "avg_files_changed": avg_files
        }
    
    def _save_patterns_to_memory(self):
        """Save learned patterns to memory store."""
        try:
            patterns_data = [p.to_dict() for p in self.learned_patterns]
            
            self.memory_store.write(
                content=f"Learned patterns: {len(patterns_data)} patterns",
                tags=["feedback_loop", "patterns", "learning"]
            )
        except Exception as e:
            self.logger.error(f"Error saving patterns to memory: {e}")
    
    def _load_patterns_from_memory(self):
        """Load patterns from memory store."""
        try:
            # This would load previously saved patterns
            # For now, start with empty patterns
            self.learned_patterns = []
        except Exception as e:
            self.logger.error(f"Error loading patterns from memory: {e}")
            self.learned_patterns = []
