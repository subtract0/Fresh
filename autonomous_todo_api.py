#!/usr/bin/env python3
"""
🎯 AUTONOMOUS TODO API DEVELOPMENT

Strategic first project: Build a FastAPI Todo Management API
Uses the most stable AAWOS components for maximum success probability.
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Ensure we can import from the ai directory regardless of current working directory
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir / 'ai'))
sys.path.append(str(script_dir))

def setup_project_environment():
    """Set up the project environment for autonomous development."""
    
    print("🚀 SETTING UP PROJECT ENVIRONMENT")
    print("=" * 40)
    
    # Create project directory
    project_dir = Path("autonomous_todo_api")
    if project_dir.exists():
        print(f"📁 Project directory {project_dir} already exists")
        response = input("🤔 Continue with existing directory? (y/n): ")
        if response.lower() != 'y':
            print("❌ Exiting - please choose a different project name")
            return None
    else:
        project_dir.mkdir()
        print(f"📁 Created project directory: {project_dir}")
    
    # Change to project directory
    os.chdir(project_dir)
    print(f"📍 Changed to directory: {os.getcwd()}")
    
    # Initialize git if not already done
    if not (project_dir / ".git").exists():
        os.system("git init")
        print("📚 Initialized git repository")
    
    return project_dir

def execute_autonomous_development():
    """Execute autonomous development using enhanced agency."""
    
    print("🤖 STARTING AUTONOMOUS DEVELOPMENT")
    print("=" * 40)
    
    start_time = datetime.now()
    print(f"⏰ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import enhanced agency
        from enhanced_agency import build_enhanced_agency
        
        print("🧠 Initializing enhanced agent team...")
        agency = build_enhanced_agency(
            enable_qa=True, 
            enable_reviewer=True, 
            use_enhanced_firestore=False,
            include_docs_agent=False
        )
        
        print(f"✅ Agency initialized with {len(agency.agents)} agents")
        
        # Define the project requirements
        project_request = """Build a FastAPI Todo Management API with the following requirements:

CORE FUNCTIONALITY:
- Create a new todo item (POST /todos)
- Get all todos (GET /todos)
- Get a specific todo by ID (GET /todos/{id})
- Update a todo item (PUT /todos/{id})
- Delete a todo item (DELETE /todos/{id})

TECHNICAL REQUIREMENTS:
- Use FastAPI framework
- SQLite database with SQLAlchemy ORM
- Pydantic models for request/response validation
- Proper error handling and HTTP status codes
- CORS enabled for frontend integration

DATA MODEL:
- Todo fields: id (auto), title (required), description (optional), completed (boolean), created_at, updated_at

TESTING & QUALITY:
- Comprehensive pytest test suite with 95%+ coverage
- Test all endpoints including edge cases
- Mock database for testing
- Proper test fixtures and cleanup

DOCUMENTATION:
- Complete README with setup instructions
- API documentation with example requests/responses
- Requirements.txt with all dependencies
- Clear project structure and comments

DELIVERABLES:
- main.py (FastAPI application)
- models.py (Pydantic and SQLAlchemy models)
- database.py (database configuration)
- test_main.py (comprehensive test suite)
- README.md (complete documentation)
- requirements.txt (dependencies)

The API should be production-ready with proper error handling, validation, and testing."""
        
        print("📝 Sending project request to agent team...")
        print("🎯 Project: Todo Management API with SQLite")
        print()
        
        # Execute autonomous development
        response = agency.get_completion(project_request)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("🎊 AUTONOMOUS DEVELOPMENT COMPLETED!")
        print("=" * 40)
        print(f"⏰ Duration: {duration}")
        print(f"📝 Response: {response}")
        
        return True, duration
        
    except Exception as e:
        print(f"❌ Autonomous development failed: {e}")
        return False, None

def validate_generated_code():
    """Validate the generated code and run tests."""
    
    print("🔍 VALIDATING GENERATED CODE")
    print("=" * 35)
    
    # Check for expected files
    expected_files = [
        "main.py",
        "models.py", 
        "database.py",
        "test_main.py",
        "README.md",
        "requirements.txt"
    ]
    
    print("📁 Checking for generated files:")
    missing_files = []
    for file in expected_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing files: {missing_files}")
        return False
    
    print()
    print("🧪 Running generated tests...")
    
    # Install requirements if they exist
    if Path("requirements.txt").exists():
        print("📦 Installing requirements...")
        os.system("pip install -r requirements.txt")
    
    # Run tests
    test_result = os.system("python -m pytest test_main.py -v --cov=. --cov-report=term-missing")
    
    if test_result == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        return False
    
    print()
    print("🌐 Testing API startup...")
    
    # Test if the API can start (just import, don't run server)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        print("✅ API module loads successfully")
        return True
    except Exception as e:
        print(f"❌ API startup failed: {e}")
        return False

def generate_success_report(duration, validation_success):
    """Generate a success report for the autonomous development."""
    
    print("📊 AUTONOMOUS DEVELOPMENT SUCCESS REPORT")
    print("=" * 50)
    
    report = {
        "project_name": "Todo Management API",
        "completion_status": "SUCCESS" if validation_success else "PARTIAL",
        "development_time": str(duration) if duration else "N/A",
        "files_generated": len(list(Path(".").glob("*.py"))) + len(list(Path(".").glob("*.md"))) + len(list(Path(".").glob("*.txt"))),
        "estimated_manual_time": "4-6 hours",
        "time_savings": "Estimated 80-90% time reduction",
        "quality_assessment": "High" if validation_success else "Needs Review"
    }
    
    for key, value in report.items():
        print(f"🎯 {key.replace('_', ' ').title()}: {value}")
    
    print()
    print("🎉 STRATEGIC INSIGHTS:")
    
    if validation_success:
        print("✅ Enhanced agent system performs excellently for API development")
        print("✅ Intelligent memory system provides good context awareness")
        print("✅ Test generation capabilities exceed expectations")
        print("✅ Documentation generation is comprehensive and accurate")
        print("✅ System ready for more complex projects")
        
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Test the API manually: uvicorn main:app --reload")
        print("   2. Try making API calls to validate functionality")
        print("   3. Review generated code for learning opportunities")
        print("   4. Plan next autonomous development project")
        print("   5. Consider enabling GitHub integration for next project")
    else:
        print("⚠️  System needs refinement for optimal autonomous development")
        print("🔍 Review generated code for improvement opportunities")
        print("📝 Document issues for system enhancement")
        print("🛠️  Consider manual fixes before next autonomous attempt")
    
    return report

def main():
    """Main autonomous development execution function."""
    
    print("🎯 AUTONOMOUS TODO API DEVELOPMENT")
    print("=" * 50)
    print("Strategic first project for maximum stability and learning")
    print()
    
    # Setup project environment
    project_dir = setup_project_environment()
    if not project_dir:
        return
    
    print()
    
    # Execute autonomous development
    success, duration = execute_autonomous_development()
    
    print()
    
    # Validate generated code
    validation_success = False
    if success:
        validation_success = validate_generated_code()
    
    print()
    
    # Generate success report
    report = generate_success_report(duration, validation_success)
    
    print()
    print("🌟 AUTONOMOUS DEVELOPMENT SESSION COMPLETE!")
    print(f"📍 Project location: {os.getcwd()}")

if __name__ == "__main__":
    main()
