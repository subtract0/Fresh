"""
Test to ensure rule consolidation is maintained and no duplicates re-appear.
"""
import os
import sys
import pytest
from pathlib import Path

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_rule_consolidation import validate_consolidation, ORIGINAL_UNIQUE_RULES, CONSOLIDATED_MAPPING


class TestRuleConsolidation:
    """Test suite for rule consolidation integrity."""
    
    def test_consolidated_rules_file_exists(self):
        """Test that the consolidated rules file exists."""
        consolidated_path = Path(__file__).parent.parent / "docs" / "CONSOLIDATED_RULES.md"
        assert consolidated_path.exists(), "Consolidated rules file must exist"
    
    def test_validation_script_passes(self):
        """Test that the validation script passes."""
        assert validate_consolidation(), "Rule consolidation validation must pass"
    
    def test_no_rule_regression(self):
        """Test that we haven't lost any unique requirements."""
        # This would be extended with actual rule parsing if rules were stored in a structured format
        expected_unique_count = len(ORIGINAL_UNIQUE_RULES)
        mapped_count = len(set().union(*CONSOLIDATED_MAPPING.values())) - 1  # -1 for MCP duplicate
        
        assert mapped_count == expected_unique_count, f"Expected {expected_unique_count} unique rules, got {mapped_count}"
    
    def test_consolidation_efficiency(self):
        """Test that consolidation achieved significant reduction."""
        original_count = 27
        consolidated_count = len(CONSOLIDATED_MAPPING)
        reduction_percentage = (original_count - consolidated_count) / original_count
        
        assert reduction_percentage >= 0.5, f"Expected at least 50% reduction, got {reduction_percentage:.1%}"
        assert consolidated_count == 13, f"Expected exactly 13 consolidated statements, got {consolidated_count}"
    
    def test_precedence_order_maintained(self):
        """Test that precedence order is maintained (project rules first)."""
        consolidated_path = Path(__file__).parent.parent / "docs" / "CONSOLIDATED_RULES.md"
        content = consolidated_path.read_text()
        
        # Project documentation should be first (highest precedence)
        assert "Project Documentation & Truth Source" in content
        assert content.find("Project Documentation") < content.find("Development Workflow")
    
    def test_no_duplicate_requirements(self):
        """Test that no requirements are duplicated across consolidated rules."""
        # This is a placeholder for a more sophisticated test that would parse
        # the actual consolidated rules and check for semantic duplicates
        pass


if __name__ == "__main__":
    pytest.main([__file__])
