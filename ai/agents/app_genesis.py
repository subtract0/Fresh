"""App Genesis Agent - Autonomous Application Development System.

This agent can create entire applications from scratch through intelligent Q&A
with the user, then continuously develop and improve them autonomously.

Key Capabilities:
- Intelligent Q&A to understand app requirements
- Full-stack application generation
- Continuous autonomous development
- Architecture and feature planning
- Code generation and testing
"""
from __future__ import annotations
import asyncio
import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from openai import OpenAI
from ai.agents.mother import MotherAgent, AgentResult
from ai.agents.senior_reviewer import SeniorReviewer
from ai.integration.github_pr import GitHubPRIntegration


class AppType(Enum):
    """Types of applications the agent can create."""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_app"
    CHATBOT = "chatbot"
    SAAS_PLATFORM = "saas_platform"


class DevelopmentPhase(Enum):
    """Phases of application development."""
    DISCOVERY = "discovery"
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    ENHANCEMENT = "enhancement"


@dataclass
class AppRequirement:
    """Individual application requirement."""
    id: str
    category: str  # UI, functionality, business_logic, integration, etc.
    description: str
    priority: int  # 1-10
    complexity: int  # 1-10
    dependencies: List[str] = field(default_factory=list)
    
    
@dataclass
class AppSpec:
    """Complete application specification."""
    name: str
    description: str
    app_type: AppType
    target_audience: str
    core_features: List[str]
    requirements: List[AppRequirement]
    tech_stack: Dict[str, str]
    architecture: Dict[str, Any]
    business_model: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass 
class DevelopmentTask:
    """Individual development task for agents."""
    id: str
    title: str
    description: str
    phase: DevelopmentPhase
    agent_type: str  # Developer, QA, DevOps, etc.
    priority: int
    estimated_hours: int
    dependencies: List[str] = field(default_factory=list)
    files_to_modify: List[str] = field(default_factory=list)
    completion_criteria: List[str] = field(default_factory=list)


class AppGenesisAgent:
    """Agent that creates and develops entire applications autonomously."""
    
    def __init__(self, workspace_path: str = "./app_workspace"):
        """Initialize the App Genesis Agent.
        
        Args:
            workspace_path: Directory where applications will be created
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        
        self.client = OpenAI()  # Using GPT-5 for superior reasoning
        self.mother_agent = MotherAgent()
        self.senior_reviewer = SeniorReviewer()
        self.github = GitHubPRIntegration()
        
        # Conversation state
        self.current_app: Optional[AppSpec] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.development_tasks: List[DevelopmentTask] = []
        
    async def start_app_creation(self, initial_idea: str) -> str:
        """Start the app creation process with an initial idea.
        
        Args:
            initial_idea: User's initial app idea
            
        Returns:
            First question from the agent
        """
        print(f"🚀 Starting app creation for: {initial_idea}")
        
        # Store initial idea
        self.conversation_history = [
            {"role": "user", "content": initial_idea}
        ]
        
        # Generate intelligent first question
        system_prompt = """You are an expert app development consultant. Your job is to understand 
        what kind of application the user wants to build through intelligent questions.

        Key principles:
        - Ask focused, high-impact questions that clarify the most important aspects
        - Keep total questions under 10 to get to development quickly
        - Focus on: target audience, core functionality, business model, key features
        - Avoid technical details - focus on user needs and business logic
        - Be conversational and insightful, not robotic
        
        The user just described their app idea. Ask ONE focused question that will help you understand 
        the most critical aspect of their vision."""
        
        try:
            # Use GPT-4o for app creation
            response = self.client.chat.completions.create(
                model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": initial_idea}
                    ],
                    temperature=0.7,
                    max_completion_tokens=200
                )
            
            first_question = response.choices[0].message.content
            
            self.conversation_history.append({
                "role": "assistant", 
                "content": first_question
            })
            
            return first_question
            
        except Exception as e:
            return f"I'd love to help you build this app! To start, could you tell me more about who your target users are and what their main problem is that your app solves?"
    
    async def continue_conversation(self, user_response: str) -> Tuple[str, bool]:
        """Continue the Q&A conversation.
        
        Args:
            user_response: User's answer to the previous question
            
        Returns:
            Tuple of (next_question_or_summary, is_ready_to_build)
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_response
        })
        
        # Check if we have enough info to start building
        if len(self.conversation_history) >= 8:  # After 4 Q&A cycles, evaluate readiness
            is_ready = await self._assess_readiness_to_build()
            if is_ready:
                app_spec = await self._generate_app_specification()
                self.current_app = app_spec
                summary = await self._create_development_summary()
                return summary, True
        
        # Generate next question
        next_question = await self._generate_next_question()
        
        self.conversation_history.append({
            "role": "assistant",
            "content": next_question
        })
        
        return next_question, False
    
    async def _assess_readiness_to_build(self) -> bool:
        """Assess if we have enough information to start building."""
        assessment_prompt = """Review this conversation about an app idea. Do we have enough information 
        to start building the application? 
        
        We need clarity on:
        - Core functionality and features
        - Target audience
        - Basic business model/monetization (if applicable)
        - Key user workflows
        
        Conversation:
        """ + "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])
        
        assessment_prompt += "\n\nRespond with just 'YES' if ready to build, or 'NO' if we need more information."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": assessment_prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            return response.choices[0].message.content.strip().upper() == "YES"
        except Exception:
            return len(self.conversation_history) >= 12  # Fallback after 6 Q&A cycles
    
    async def _generate_next_question(self) -> str:
        """Generate the next intelligent question."""
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history
        ])
        
        next_question_prompt = f"""Based on this conversation about an app, what's the most important 
        thing you still need to understand to create a great application?
        
        Conversation so far:
        {conversation_text}
        
        Ask ONE focused question that gets to the heart of what's missing. 
        Focus on functionality, user experience, or business logic - not technical implementation.
        Keep it conversational and insightful."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": next_question_prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception:
            return "Could you tell me more about how users will interact with your app and what their main workflow will be?"
    
    async def _generate_app_specification(self) -> AppSpec:
        """Generate comprehensive app specification from conversation."""
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history
        ])
        
        spec_prompt = f"""Based on this conversation, create a detailed app specification.

        Conversation:
        {conversation_text}

        Generate a JSON specification with these fields:
        {{
            "name": "app name",
            "description": "detailed description",
            "app_type": "web_app|mobile_app|api_service|desktop_app|chatbot|saas_platform",
            "target_audience": "description of target users",
            "core_features": ["feature1", "feature2", "feature3"],
            "business_model": "how it makes money",
            "tech_stack": {{
                "frontend": "technology choice",
                "backend": "technology choice", 
                "database": "database choice",
                "deployment": "deployment platform"
            }},
            "architecture": {{
                "pattern": "architecture pattern",
                "components": ["component1", "component2"]
            }}
        }}
        
        Choose appropriate modern technologies and architecture patterns."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": spec_prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            spec_data = json.loads(response.choices[0].message.content.strip())
            
            return AppSpec(
                name=spec_data.get("name", "Unnamed App"),
                description=spec_data.get("description", ""),
                app_type=AppType(spec_data.get("app_type", "web_app")),
                target_audience=spec_data.get("target_audience", ""),
                core_features=spec_data.get("core_features", []),
                tech_stack=spec_data.get("tech_stack", {}),
                architecture=spec_data.get("architecture", {}),
                business_model=spec_data.get("business_model"),
                requirements=[]  # Will be populated during planning
            )
            
        except Exception as e:
            print(f"Error generating spec: {e}")
            # Fallback basic spec
            return AppSpec(
                name="Generated App",
                description="Application based on user requirements",
                app_type=AppType.WEB_APP,
                target_audience="General users",
                core_features=["User interface", "Core functionality"],
                tech_stack={"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"},
                architecture={"pattern": "MVC", "components": ["Frontend", "API", "Database"]},
                requirements=[]
            )
    
    async def _create_development_summary(self) -> str:
        """Create a summary of what will be built."""
        if not self.current_app:
            return "Error: No app specification available"
        
        app = self.current_app
        
        summary = f"""
🎉 **Ready to Build: {app.name}**

**What we're building:**
{app.description}

**Target Users:** {app.target_audience}

**Core Features:**
{chr(10).join(f"• {feature}" for feature in app.core_features)}

**Tech Stack:**
{chr(10).join(f"• {component}: {tech}" for component, tech in app.tech_stack.items())}

**Architecture:** {app.architecture.get('pattern', 'Modern web architecture')}

**Business Model:** {app.business_model or 'Not specified'}

**Next Steps:**
I'll now create a development plan and start building your application autonomously. 
I'll create pull requests as I develop each component, and you can review the progress.

Would you like me to start development immediately?
"""
        return summary.strip()
    
    async def start_autonomous_development(self) -> str:
        """Begin autonomous development of the specified app."""
        if not self.current_app:
            return "❌ No app specification available. Please complete the Q&A process first."
        
        app = self.current_app
        app_dir = self.workspace_path / app.name.lower().replace(" ", "_")
        app_dir.mkdir(exist_ok=True)
        
        print(f"🏗️ Starting autonomous development of {app.name}")
        
        # 1. Create project structure
        await self._create_project_structure(app_dir, app)
        
        # 2. Generate development tasks
        tasks = await self._generate_development_tasks(app)
        self.development_tasks = tasks
        
        # 3. Start executing tasks with agents
        results = await self._execute_development_tasks(app_dir, tasks[:5])  # Start with first 5 tasks
        
        # 4. Create initial commit and GitHub repo (if configured)
        if self.github.is_configured():
            await self._setup_github_repository(app_dir, app)
        
        summary = f"""
🚀 **Autonomous Development Started for {app.name}**

**Project Structure Created:** {app_dir}

**Initial Development Tasks Executed:**
{chr(10).join(f"• {task.title}" for task in tasks[:5])}

**Next Actions:**
- Agents will continue developing features
- Pull requests will be created for each major component
- Testing and quality assurance will be automated
- Deployment configuration will be added

**Monitor Progress:**
Check the {app_dir} directory and any GitHub repository for ongoing development.
"""
        
        return summary.strip()
    
    async def _create_project_structure(self, app_dir: Path, app: AppSpec) -> None:
        """Create the basic project structure."""
        # Create directories based on app type and tech stack
        if app.app_type == AppType.WEB_APP:
            # React + FastAPI structure
            (app_dir / "frontend" / "src" / "components").mkdir(parents=True, exist_ok=True)
            (app_dir / "frontend" / "public").mkdir(parents=True, exist_ok=True)
            (app_dir / "backend" / "app" / "api").mkdir(parents=True, exist_ok=True)
            (app_dir / "backend" / "app" / "models").mkdir(parents=True, exist_ok=True)
            (app_dir / "backend" / "app" / "services").mkdir(parents=True, exist_ok=True)
            (app_dir / "database" / "migrations").mkdir(parents=True, exist_ok=True)
            (app_dir / "tests").mkdir(exist_ok=True)
            (app_dir / "docs").mkdir(exist_ok=True)
            
            # Create basic files
            self._create_basic_files(app_dir, app)
    
    def _create_basic_files(self, app_dir: Path, app: AppSpec) -> None:
        """Create basic project files."""
        # README
        readme_content = f"""# {app.name}

{app.description}

## Target Audience
{app.target_audience}

## Core Features
{chr(10).join(f"- {feature}" for feature in app.core_features)}

## Tech Stack
{chr(10).join(f"- **{component}**: {tech}" for component, tech in app.tech_stack.items())}

## Architecture
Pattern: {app.architecture.get('pattern', 'Modern web architecture')}

## Business Model
{app.business_model or 'Not specified'}

## Development Status
🤖 This application is being developed autonomously by Fresh AI agents.

## Generated by Fresh AI
This project was created and is being developed by the Fresh Autonomous Development System.
"""
        
        (app_dir / "README.md").write_text(readme_content)
        
        # .gitignore
        gitignore_content = """
# Dependencies
node_modules/
venv/
__pycache__/

# Environment variables
.env
.env.local

# Build outputs
dist/
build/
*.pyc

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
        (app_dir / ".gitignore").write_text(gitignore_content.strip())
        
        # Package.json for frontend
        if app.tech_stack.get("frontend") in ["React", "Vue", "Angular"]:
            package_json = {
                "name": app.name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "description": app.description,
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "test": "react-scripts test"
                },
                "dependencies": {
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0",
                    "react-scripts": "5.0.1"
                }
            }
            
            (app_dir / "frontend" / "package.json").write_text(
                json.dumps(package_json, indent=2)
            )
    
    async def _generate_development_tasks(self, app: AppSpec) -> List[DevelopmentTask]:
        """Generate a comprehensive list of development tasks."""
        tasks_prompt = f"""Create a detailed development task list for this application:

        App: {app.name}
        Description: {app.description}
        Features: {', '.join(app.core_features)}
        Tech Stack: {app.tech_stack}
        
        Generate tasks covering:
        1. Frontend components and UI
        2. Backend API endpoints
        3. Database schema and models
        4. Authentication and security
        5. Core business logic
        6. Testing
        7. Deployment configuration
        
        Return as JSON array of tasks with: id, title, description, phase, agent_type, priority (1-10), estimated_hours"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": tasks_prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            tasks_data = json.loads(response.choices[0].message.content.strip())
            
            tasks = []
            for i, task_data in enumerate(tasks_data):
                task = DevelopmentTask(
                    id=f"task_{i+1:03d}",
                    title=task_data.get("title", f"Task {i+1}"),
                    description=task_data.get("description", ""),
                    phase=DevelopmentPhase(task_data.get("phase", "development")),
                    agent_type=task_data.get("agent_type", "Developer"),
                    priority=task_data.get("priority", 5),
                    estimated_hours=task_data.get("estimated_hours", 4)
                )
                tasks.append(task)
            
            return sorted(tasks, key=lambda t: (t.priority, t.estimated_hours), reverse=True)
            
        except Exception as e:
            print(f"Error generating tasks: {e}")
            # Fallback basic tasks
            return [
                DevelopmentTask(
                    id="task_001",
                    title="Create project structure",
                    description="Set up basic project directories and files",
                    phase=DevelopmentPhase.DEVELOPMENT,
                    agent_type="Developer",
                    priority=10,
                    estimated_hours=2
                ),
                DevelopmentTask(
                    id="task_002", 
                    title="Implement basic UI",
                    description="Create main user interface components",
                    phase=DevelopmentPhase.DEVELOPMENT,
                    agent_type="Developer",
                    priority=8,
                    estimated_hours=6
                )
            ]
    
    async def _execute_development_tasks(self, app_dir: Path, tasks: List[DevelopmentTask]) -> List[AgentResult]:
        """Execute development tasks using agents."""
        results = []
        
        for task in tasks:
            print(f"🔧 Executing task: {task.title}")
            
            # Create detailed instructions for the agent
            instructions = f"""
            Project: {self.current_app.name if self.current_app else 'Unknown'}
            Task: {task.title}
            Description: {task.description}
            Phase: {task.phase.value}
            Working Directory: {app_dir}
            
            Please implement this task completely, creating all necessary files and code.
            Focus on production-quality implementation following best practices.
            """
            
            # Spawn appropriate agent
            result = self.mother_agent.run(
                name=f"task_{task.id}",
                instructions=instructions,
                model="gpt-4o",  # Using GPT-4o for development tasks
                output_type="code"
            )
            
            results.append(result)
            
            # Brief pause between tasks
            await asyncio.sleep(1)
        
        return results
    
    async def _setup_github_repository(self, app_dir: Path, app: AppSpec) -> bool:
        """Set up GitHub repository for the app."""
        try:
            # Initialize git repository
            import subprocess
            
            subprocess.run(["git", "init"], cwd=app_dir, check=True)
            subprocess.run(["git", "add", "."], cwd=app_dir, check=True)
            subprocess.run([
                "git", "commit", "-m", 
                f"🚀 Initial commit for {app.name}\n\nAutonomously generated by Fresh AI system"
            ], cwd=app_dir, check=True)
            
            print(f"✅ Git repository initialized for {app.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup GitHub repository: {e}")
            return False
    
    def get_development_status(self) -> Dict[str, Any]:
        """Get current development status."""
        if not self.current_app:
            return {"status": "no_active_project"}
        
        completed_tasks = len([t for t in self.development_tasks if hasattr(t, 'completed') and t.completed])
        total_tasks = len(self.development_tasks)
        
        return {
            "app_name": self.current_app.name,
            "phase": "development",
            "tasks_completed": completed_tasks,
            "total_tasks": total_tasks,
            "progress_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "next_tasks": [t.title for t in self.development_tasks[:3] if not hasattr(t, 'completed') or not t.completed]
        }
