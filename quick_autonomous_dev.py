#!/usr/bin/env python3
"""
⚡ QUICK START AUTONOMOUS DEVELOPMENT

One-command autonomous development execution.
"""

import sys
import os

sys.path.append('ai')

def quick_autonomous_dev(project_request):
    """Execute autonomous development with one function call."""
    
    from enhanced_agency import build_enhanced_agency
    from datetime import datetime
    
    print(f"🚀 Quick Autonomous Development: {project_request}")
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Build enhanced agency
    agency = build_enhanced_agency()
    print("✅ AI agents ready!")
    
    # Execute autonomous development
    response = agency.get_completion(project_request)
    
    print("🎉 Autonomous development complete!")
    return response

if __name__ == "__main__":
    # Example usage
    project = "Build a FastAPI for user management with authentication"
    result = quick_autonomous_dev(project)
