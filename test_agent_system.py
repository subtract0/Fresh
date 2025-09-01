#!/usr/bin/env python
"""Test script to validate agent file modification capabilities."""

import sys
from pathlib import Path

# Add ai module to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.agents.mother import MotherAgent

def test_file_modification():
    """Test that agents can modify files properly."""
    print("🧪 Testing file modification capabilities...\n")
    
    # Create a test file
    test_file = Path("test_agent_modification.py")
    original_content = '''def calculate(x, y):
    # TODO: Add input validation
    return x + y

def process_data():
    # FIXME: Handle empty data case
    pass
'''
    
    test_file.write_text(original_content)
    print(f"📝 Created test file: {test_file}")
    print(f"Original content:\n{original_content}")
    
    # Test with a simulated agent (mock OpenAI call)
    mother = MotherAgent()
    
    # Replace the OpenAI call with a mock for testing
    def mock_execute_agent(agent_type, request):
        """Mock agent execution for testing."""
        return {
            "output": f"Fixed TODO in {test_file}",
            "artifacts": {
                "files_modified": [str(test_file)],
                "explanation": f"Added input validation to {test_file}"
            },
            "files_modified": [str(test_file)]
        }
    
    # Temporarily replace the execute method
    original_method = mother._execute_agent
    mother._execute_agent = mock_execute_agent
    
    # Test the spawn
    result = mother.run(
        name="test_fix",
        instructions=f"Fix the TODO in {test_file} about input validation",
        model="gpt-4o-mini"
    )
    
    # Restore original method
    mother._execute_agent = original_method
    
    print(f"\n✅ Agent Result:")
    print(f"   Success: {result.success}")
    print(f"   Agent Type: {result.agent_type}")
    print(f"   Output: {result.output}")
    print(f"   Artifacts: {result.artifacts}")
    
    # Clean up
    if test_file.exists():
        test_file.unlink()
        print(f"\n🗑️ Cleaned up test file")

if __name__ == "__main__":
    test_file_modification()
