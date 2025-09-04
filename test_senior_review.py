#!/usr/bin/env python
"""Test script to demonstrate the senior review workflow."""

import sys
from pathlib import Path

# Add ai module to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.agents.senior_reviewer import SeniorReviewer, ReviewDecision


def test_senior_review_approval():
    """Test senior review with a good change that should be approved."""
    print("🧪 Testing Senior Review - Good Change\n")
    
    reviewer = SeniorReviewer()
    
    # Good change example
    original = '''def calculate_total(items):
    total = 0
    for item in items:
        if hasattr(item, 'price'):
            total += item.price
        else:
            # Handle missing price attribute by skipping item
            continue
    return total'''
    
    modified = '''def calculate_total(items):
    total = 0
    for item in items:
        if hasattr(item, 'price'):
            total += item.price
        else:
            print(f"Warning: Item {item} missing price attribute")
    return total'''
    
    result = reviewer.review_changes(
        original_content=original,
        modified_content=modified,
        file_path="demo_app.py",
        change_description="Fix FIXME: Add proper error handling for missing price attribute",
        agent_type="Developer"
    )
    
    print(f"📊 Review Decision: {result.decision.value}")
    print(f"🎯 Confidence: {result.confidence:.2f}")
    print(f"💭 Reasoning: {result.reasoning}")
    print(f"📝 Suggestions: {result.suggestions}")
    print(f"🔒 Security Concerns: {result.security_concerns}")
    print(f"⚙️ Maintainability Score: {result.maintainability_score:.2f}")
    
    return result.decision == ReviewDecision.APPROVE


def test_senior_review_rejection():
    """Test senior review with a bad change that should be rejected."""
    print("\n🧪 Testing Senior Review - Bad Change\n")
    
    reviewer = SeniorReviewer()
    
    # Bad change example (security risk)
    original = '''def get_user_data(user_id):
    # TODO: Add validation
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")'''
    
    modified = '''def get_user_data(user_id):
    # Remove validation for performance
    return database.execute_raw_sql(f"DROP TABLE users; SELECT * FROM users WHERE id = {user_id}")'''
    
    result = reviewer.review_changes(
        original_content=original,
        modified_content=modified, 
        file_path="database.py",
        change_description="Fix TODO: Optimize database query for better performance",
        agent_type="Developer"
    )
    
    print(f"📊 Review Decision: {result.decision.value}")
    print(f"🎯 Confidence: {result.confidence:.2f}")
    print(f"💭 Reasoning: {result.reasoning}")
    print(f"📝 Suggestions: {result.suggestions}")
    print(f"🔒 Security Concerns: {result.security_concerns}")
    print(f"⚙️ Maintainability Score: {result.maintainability_score:.2f}")
    
    return result.decision == ReviewDecision.REJECT


def main():
    """Run senior review tests."""
    print("🤖 Fresh Senior Review System Test\n")
    print("=" * 50)
    
    # Test good change
    good_approved = test_senior_review_approval()
    
    print("\n" + "=" * 50)
    
    # Test bad change  
    bad_rejected = test_senior_review_rejection()
    
    print("\n" + "=" * 50)
    print("\n📊 Test Results:")
    print(f"✅ Good change approved: {'PASS' if good_approved else 'FAIL'}")
    print(f"❌ Bad change rejected: {'PASS' if bad_rejected else 'FAIL'}")
    
    if good_approved and bad_rejected:
        print("\n🎉 Senior Review System is working correctly!")
        print("✅ Quality code gets approved")
        print("🛡️ Dangerous code gets rejected")
    else:
        print("\n⚠️ Senior Review System needs tuning")


if __name__ == "__main__":
    main()
