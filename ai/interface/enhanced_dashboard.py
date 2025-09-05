#!/usr/bin/env python3
"""
🚀 Enhanced Fresh AI Agent Dashboard

A comprehensive web-based interface with:
- Real-time Mother Agent conversation interface
- Preset prompt templates for complex orchestrations
- Live progress visualization of multi-agent tasks
- Complete CLI functionality integration
- Results management and export capabilities

Usage:
    poetry run python ai/interface/enhanced_dashboard.py
    
Then navigate to: http://localhost:8080
"""

from __future__ import annotations
import asyncio
import json
import subprocess
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
import webbrowser
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import html
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from ai.monitor.event_bus import get_bus
from ai.autonomous import AutonomousLoop
from ai.agents.mother import MotherAgent
from ai.agents.enhanced_mother import EnhancedMotherAgent
from ai.memory.intelligent_store import IntelligentMemoryStore


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestrationTask:
    id: str
    title: str
    prompt: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    progress: int = 0
    agent_count: int = 0
    current_phase: str = ""
    results: Optional[Dict] = None
    error_message: Optional[str] = None


class PresetTemplates:
    """Pre-configured prompt templates for common orchestration tasks"""
    
    TEMPLATES = {
        "doc_and_business": {
            "title": "📚 Documentation + Business Cases Analysis",
            "description": "Fix documentation then generate prioritized business cases based on earning potential",
            "prompt": """Can you make a team that will fix the whole documentation of the project and then when all is up to date and state of the art, conclusive and complete while being simple and readable, optimized for autonomous development: create and sort business cases based on their earning-potential (based on this codebase), prioritize the ones that are completely digital and passively generating solid income with little or no risk and little capital investment and biggest upside in value-creation for humans""",
            "suggested_budget": "under_$10",
            "suggested_timeline": "within_week"
        },
        "market_research": {
            "title": "🔍 Comprehensive Market Research",
            "description": "Deep market analysis with competitor assessment and opportunity identification",
            "prompt": """Research the current market landscape for AI development tools and autonomous coding systems. Analyze top competitors, identify market gaps, assess technology trends, and provide strategic recommendations for positioning our Fresh AI system. Include pricing analysis, feature comparison, and market size estimation.""",
            "suggested_budget": "under_$5",
            "suggested_timeline": "same_day"
        },
        "tech_assessment": {
            "title": "🔬 Technical Architecture Review",
            "description": "Comprehensive technical evaluation and improvement recommendations",
            "prompt": """Perform a thorough technical assessment of the Fresh AI codebase. Analyze architecture patterns, identify technical debt, evaluate scalability concerns, security vulnerabilities, and performance bottlenecks. Provide prioritized recommendations for improvements with implementation effort estimates.""",
            "suggested_budget": "under_$300",
            "suggested_timeline": "same_day"
        },
        "saas_opportunity": {
            "title": "💰 SaaS Monetization Strategy",
            "description": "Identify and plan SaaS business opportunities from existing capabilities",
            "prompt": """Analyze our Fresh AI system capabilities and create a comprehensive SaaS monetization strategy. Identify potential service offerings, pricing models, target customer segments, go-to-market strategy, and revenue projections. Focus on digital-first, scalable solutions with high automation potential.""",
            "suggested_budget": "under_$800",
            "suggested_timeline": "within_week"
        },
        "feature_roadmap": {
            "title": "🗺️ Strategic Feature Roadmap",
            "description": "Plan and prioritize feature development based on market needs and impact",
            "prompt": """Create a strategic feature roadmap for the Fresh AI system. Research user needs, analyze competitor features, estimate development effort, and prioritize features based on impact, effort, and strategic value. Include technical requirements, success metrics, and implementation timelines.""",
            "suggested_budget": "under_$600",
            "suggested_timeline": "within_week"
        }
    }


class EnhancedDashboardController:
    """Enhanced controller with Mother Agent integration and task management"""
    
    def __init__(self):
        self.tasks: Dict[str, OrchestrationTask] = {}
        self.active_conversations: Dict[str, List[Dict]] = {}  # conversation_id -> messages
        self.mother_agent = None
        self.enhanced_mother = None
        self.memory_store = IntelligentMemoryStore()
        
        # Initialize agents
        self.initialize_agents()
        
    def initialize_agents(self):
        """Initialize Mother Agent instances"""
        try:
            self.enhanced_mother = EnhancedMotherAgent()
            print("✅ Enhanced Mother Agent initialized")
        except Exception as e:
            print(f"⚠️  Enhanced Mother Agent init failed: {e}")
            
        try:
            self.mother_agent = MotherAgent()
            print("✅ Basic Mother Agent initialized")
        except Exception as e:
            print(f"⚠️  Basic Mother Agent init failed: {e}")
    
    def get_active_mother(self):
        """Get the best available Mother Agent"""
        return self.enhanced_mother or self.mother_agent
    
    async def start_conversation(self) -> str:
        """Start a new conversation with Mother Agent"""
        conversation_id = str(uuid.uuid4())
        self.active_conversations[conversation_id] = [
            {
                "role": "system",
                "content": "🤖 Enhanced Mother Agent initialized. Ready to orchestrate complex multi-agent tasks!",
                "timestamp": datetime.now().isoformat()
            }
        ]
        return conversation_id
    
    async def send_message(self, conversation_id: str, message: str) -> Dict:
        """Send message to Mother Agent and get response"""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}
            
        # Add user message
        self.active_conversations[conversation_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            mother = self.get_active_mother()
            if not mother:
                response_content = "⚠️ Mother Agent not available. Please check system configuration."
            else:
                # Use Mother Agent to process the message
                response_content = await self.process_with_mother(message)
            
            # Add response
            response = {
                "role": "assistant", 
                "content": response_content,
                "timestamp": datetime.now().isoformat()
            }
            self.active_conversations[conversation_id].append(response)
            
            return response
            
        except Exception as e:
            error_response = {
                "role": "assistant",
                "content": f"❌ Error processing message: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self.active_conversations[conversation_id].append(error_response)
            return error_response
    
    async def process_with_mother(self, message: str) -> str:
        """Process message with Mother Agent"""
        mother = self.get_active_mother()
        
        # Check if this is an orchestration request
        orchestration_keywords = [
            "orchestrate", "team", "agents", "coordinate", "manage", 
            "research", "analyze", "business case", "documentation"
        ]
        
        if any(keyword in message.lower() for keyword in orchestration_keywords):
            # This looks like an orchestration request
            return await self.handle_orchestration_request(message)
        else:
            # General conversation
            if hasattr(mother, 'process_message'):
                return await mother.process_message(message)
            else:
                return f"🤖 Mother Agent received: {message}\n\n💡 I can help you orchestrate complex tasks. Try asking me to 'create a team to analyze our market opportunity' or use one of the preset templates!"
    
    async def handle_orchestration_request(self, prompt: str) -> str:
        """Handle orchestration requests and create tasks"""
        task_id = str(uuid.uuid4())
        
        task = OrchestrationTask(
            id=task_id,
            title=f"Orchestration Task {task_id[:8]}",
            prompt=prompt,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        
        # Start orchestration in background
        asyncio.create_task(self.execute_orchestration(task_id))
        
        return f"""🚀 **Orchestration Task Created**

**Task ID:** {task_id}
**Prompt:** {prompt}

I'm analyzing your request and will spawn the appropriate agents. You can monitor progress in the Tasks panel.

**Expected agents:**
- 📊 Market Research Agent
- 🔬 Technical Assessment Agent  
- 💰 Opportunity Scoring Agent
- 📝 Documentation Agent (if needed)

Starting orchestration now..."""
    
    async def execute_orchestration(self, task_id: str):
        """Execute orchestration task in background"""
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.now()
        
        try:
            mother = self.get_active_mother()
            
            if hasattr(mother, 'orchestrate'):
                # Use Enhanced Mother Agent
                task.current_phase = "Initializing orchestration..."
                task.progress = 10
                
                results = await mother.orchestrate(
                    command=task.prompt,
                    budget="under_$10",
                    timeline="same_day"
                )
                
                task.results = results
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.current_phase = "Completed"
                
            else:
                # Fallback to basic processing
                task.current_phase = "Processing with basic agent..."
                task.progress = 50
                
                # Simulate some work
                await asyncio.sleep(5)
                
                task.results = {
                    "summary": "Task processed with basic Mother Agent",
                    "details": f"Processed prompt: {task.prompt}",
                    "recommendations": ["Enable Enhanced Mother Agent for full orchestration capabilities"]
                }
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.current_phase = "Completed"
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.current_phase = "Failed"
            
        task.updated_at = datetime.now()
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        return self.active_conversations.get(conversation_id, [])
    
    def get_tasks(self) -> List[OrchestrationTask]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def get_task(self, task_id: str) -> Optional[OrchestrationTask]:
        """Get specific task"""
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.now()
            task.current_phase = "Cancelled by user"
            return True
        return False


class EnhancedDashboardHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler with Mother Agent chat and orchestration"""
    
    controller = EnhancedDashboardController()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self.serve_enhanced_dashboard()
        elif path == '/api/conversation/start':
            self.handle_start_conversation()
        elif path.startswith('/api/conversation/'):
            self.handle_conversation_api(parsed)
        elif path.startswith('/api/tasks'):
            self.handle_tasks_api(parsed)  
        elif path.startswith('/api/export'):
            self.handle_export_api(parsed)
        elif path == '/api/templates':
            self.serve_templates_api()
        elif path == '/api/status':
            self.serve_status_api()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/conversation/'):
            self.handle_conversation_post(parsed)
        elif path.startswith('/api/orchestrate'):
            self.handle_orchestrate_post(parsed)
        elif path.startswith('/api/tasks/'):
            self.handle_tasks_post(parsed)
        else:
            self.send_error(404, "Not Found")
    
    def handle_start_conversation(self):
        """Start new conversation"""
        async def start():
            conversation_id = await self.controller.start_conversation()
            return {"conversation_id": conversation_id}
            
        result = asyncio.run(start())
        self.send_json_response(result)
    
    def handle_conversation_api(self, parsed):
        """Handle conversation API calls"""
        path_parts = parsed.path.split('/')
        if len(path_parts) < 4:
            self.send_error(400, "Invalid conversation endpoint")
            return
            
        conversation_id = path_parts[3]
        action = path_parts[4] if len(path_parts) > 4 else "messages"
        
        if action == "messages":
            messages = self.controller.get_conversation(conversation_id)
            self.send_json_response({"messages": messages})
        else:
            self.send_error(400, "Invalid conversation action")
    
    def handle_conversation_post(self, parsed):
        """Handle conversation POST requests"""
        path_parts = parsed.path.split('/')
        if len(path_parts) < 5:
            self.send_error(400, "Invalid conversation endpoint")
            return
            
        conversation_id = path_parts[3]
        action = path_parts[4]
        
        if action == "send":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            async def send_message():
                return await self.controller.send_message(
                    conversation_id, 
                    data.get('message', '')
                )
                
            result = asyncio.run(send_message())
            self.send_json_response(result)
        else:
            self.send_error(400, "Invalid conversation action")
    
    def handle_orchestrate_post(self, parsed):
        """Handle orchestration requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        async def orchestrate():
            return await self.controller.handle_orchestration_request(
                data.get('prompt', '')
            )
            
        result = asyncio.run(orchestrate())
        self.send_json_response({"response": result})
    
    def handle_tasks_api(self, parsed):
        """Handle tasks API"""
        path_parts = parsed.path.split('/')
        
        if len(path_parts) == 3:  # /api/tasks
            tasks = self.controller.get_tasks()
            tasks_data = [asdict(task) for task in tasks]
            # Convert datetime objects to ISO strings
            for task_data in tasks_data:
                task_data['created_at'] = task_data['created_at'].isoformat()
                task_data['updated_at'] = task_data['updated_at'].isoformat()
                task_data['status'] = task_data['status'].value
            self.send_json_response({"tasks": tasks_data})
            
        elif len(path_parts) >= 4:  # /api/tasks/{task_id}
            task_id = path_parts[3]
            task = self.controller.get_task(task_id)
            if task:
                task_data = asdict(task)
                task_data['created_at'] = task_data['created_at'].isoformat()
                task_data['updated_at'] = task_data['updated_at'].isoformat()
                task_data['status'] = task_data['status'].value
                self.send_json_response(task_data)
            else:
                self.send_error(404, "Task not found")
    
    def handle_tasks_post(self, parsed):
        """Handle task actions"""
        path_parts = parsed.path.split('/')
        if len(path_parts) >= 5:  # /api/tasks/{task_id}/{action}
            task_id = path_parts[3]
            action = path_parts[4]
            
            if action == "cancel":
                success = self.controller.cancel_task(task_id)
                self.send_json_response({"success": success})
            else:
                self.send_error(400, "Invalid task action")
    
    def serve_templates_api(self):
        """Serve preset templates"""
        self.send_json_response({"templates": PresetTemplates.TEMPLATES})
    
    def serve_status_api(self):
        """Serve system status"""
        status = {
            "enhanced_mother_available": self.controller.enhanced_mother is not None,
            "basic_mother_available": self.controller.mother_agent is not None,
            "active_conversations": len(self.controller.active_conversations),
            "total_tasks": len(self.controller.tasks),
            "running_tasks": len([t for t in self.controller.tasks.values() if t.status == TaskStatus.RUNNING]),
            "completed_tasks": len([t for t in self.controller.tasks.values() if t.status == TaskStatus.COMPLETED])
        }
        self.send_json_response(status)
    
    def handle_export_api(self, parsed):
        """Handle results export requests"""
        path_parts = parsed.path.split('/')
        if len(path_parts) < 4:  # /api/export/{task_id}
            self.send_error(400, "Task ID required for export")
            return
            
        task_id = path_parts[3]
        export_format = path_parts[4] if len(path_parts) > 4 else 'json'
        
        task = self.controller.get_task(task_id)
        if not task or task.status != TaskStatus.COMPLETED:
            self.send_error(404, "Task not found or not completed")
            return
        
        try:
            if export_format == 'json':
                self.export_json(task)
            elif export_format == 'markdown':
                self.export_markdown(task)
            elif export_format == 'pdf':
                self.export_pdf(task)
            else:
                self.send_error(400, "Invalid export format. Use json, markdown, or pdf")
        except Exception as e:
            self.send_error(500, f"Export failed: {str(e)}")
    
    def export_json(self, task):
        """Export task results as JSON"""
        export_data = {
            "task_id": task.id,
            "title": task.title,
            "prompt": task.prompt,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "progress": task.progress,
            "results": task.results,
            "export_timestamp": datetime.now().isoformat()
        }
        
        filename = f"fresh_orchestration_{task.id[:8]}.json"
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        
        self.wfile.write(json.dumps(export_data, indent=2).encode())
    
    def export_markdown(self, task):
        """Export task results as Markdown"""
        markdown_content = f"""# Fresh AI Orchestration Report

**Task ID:** {task.id}  
**Title:** {task.title}  
**Status:** {task.status.value.title()}  
**Created:** {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Completed:** {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}  

## Task Description

{task.prompt}

## Results

"""        
        if task.results:
            if isinstance(task.results, dict):
                if 'summary' in task.results:
                    markdown_content += f"### Summary\n\n{task.results['summary']}\n\n"
                
                if 'recommendations' in task.results:
                    markdown_content += "### Recommendations\n\n"
                    for i, rec in enumerate(task.results['recommendations'], 1):
                        markdown_content += f"{i}. {rec}\n"
                    markdown_content += "\n"
                    
                if 'final_report' in task.results:
                    markdown_content += f"### Final Report\n\n{task.results['final_report']}\n\n"
                    
                # Add any other keys
                for key, value in task.results.items():
                    if key not in ['summary', 'recommendations', 'final_report']:
                        markdown_content += f"### {key.title()}\n\n{value}\n\n"
            else:
                markdown_content += f"{task.results}\n\n"
        else:
            markdown_content += "No results available.\n\n"
        
        markdown_content += f"\n---\n\n*Generated by Fresh AI Enhanced Dashboard on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        filename = f"fresh_orchestration_{task.id[:8]}.md"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/markdown')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        
        self.wfile.write(markdown_content.encode())
    
    def export_pdf(self, task):
        """Export task results as PDF (simplified text format)"""
        # For now, we'll create a simple text-based PDF export
        # In production, you'd use a proper PDF library like reportlab
        
        content = f"""FRESH AI ORCHESTRATION REPORT

Task ID: {task.id}
Title: {task.title}
Status: {task.status.value.title()}
Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Completed: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

TASK DESCRIPTION:
{task.prompt}

RESULTS:
"""        
        if task.results:
            if isinstance(task.results, dict):
                for key, value in task.results.items():
                    content += f"\n{key.upper()}:\n{value}\n"
            else:
                content += str(task.results)
        else:
            content += "No results available."
        
        content += f"\n\nGenerated by Fresh AI Enhanced Dashboard on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        filename = f"fresh_orchestration_{task.id[:8]}.txt"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        
        self.wfile.write(content.encode())
    
    def send_json_response(self, data):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json_data.encode())
    
    def serve_enhanced_dashboard(self):
        """Serve the enhanced dashboard HTML"""
        html_content = self.get_enhanced_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def get_enhanced_dashboard_html(self) -> str:
        """Generate enhanced dashboard HTML with Mother Agent chat"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Fresh AI Enhanced Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            height: 100vh;
        }
        
        .main-content {
            display: grid;
            grid-template-rows: auto 1fr;
            gap: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 20px 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-tabs {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .tab-header {
            display: flex;
            background: #f8f9fa;
        }
        
        .tab-button {
            flex: 1;
            padding: 15px 20px;
            background: none;
            border: none;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab-button.active {
            background: white;
            color: #007bff;
            border-bottom: 3px solid #007bff;
        }
        
        .tab-content {
            padding: 30px;
            height: calc(100vh - 200px);
            overflow-y: auto;
        }
        
        .tab-panel {
            display: none;
        }
        
        .tab-panel.active {
            display: block;
        }
        
        .chat-sidebar {
            display: grid;
            grid-template-rows: auto 1fr auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h2 {
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        
        .chat-status {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            height: calc(100vh - 300px);
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 10px;
            max-width: 90%;
        }
        
        .message.user {
            background: #e3f2fd;
            color: #1565c0;
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: #f1f8e9;
            color: #2e7d32;
            margin-right: auto;
        }
        
        .message.system {
            background: #fff3e0;
            color: #e65100;
            text-align: center;
            font-style: italic;
        }
        
        .message-time {
            font-size: 0.8em;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        .chat-input-area {
            padding: 20px;
            border-top: 1px solid #e9ecef;
            background: #f8f9fa;
        }
        
        .chat-input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input:focus {
            border-color: #007bff;
        }
        
        .chat-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-1px);
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0056b3;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #545b62;
        }
        
        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .template-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .template-card:hover {
            border-color: #007bff;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.15);
        }
        
        .template-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .template-description {
            color: #6c757d;
            margin-bottom: 15px;
            font-size: 0.95em;
        }
        
        .template-meta {
            display: flex;
            gap: 10px;
            font-size: 0.85em;
        }
        
        .template-tag {
            background: #e9ecef;
            color: #495057;
            padding: 3px 8px;
            border-radius: 12px;
        }
        
        .task-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .task-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .task-title {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .task-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-pending { background: #fff3cd; color: #856404; }
        .status-running { background: #d4edda; color: #155724; }
        .status-completed { background: #d1ecf1; color: #0c5460; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .status-cancelled { background: #e2e3e5; color: #383d41; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #6c757d;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #2c3e50;
        }
        
        .form-control {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
            outline: none;
        }
        
        .form-control:focus {
            border-color: #007bff;
        }
        
        textarea.form-control {
            min-height: 120px;
            resize: vertical;
        }
        
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        .results-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .results-actions .btn {
            font-size: 0.85em;
            padding: 6px 12px;
        }
        
        @media (max-width: 1024px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: auto auto;
            }
            
            .chat-sidebar {
                order: -1;
                max-height: 400px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="header">
                <h1>🤖 Fresh AI Enhanced Dashboard</h1>
                <p>Conversational Mother Agent Interface & Orchestration Control</p>
                <p id="status-indicator">Status: <span id="system-status">Loading...</span></p>
            </div>
            
            <div class="main-tabs">
                <div class="tab-header">
                    <button class="tab-button active" onclick="switchTab('templates')">📋 Templates</button>
                    <button class="tab-button" onclick="switchTab('tasks')">⚡ Active Tasks</button>
                    <button class="tab-button" onclick="switchTab('results')">📊 Results</button>
                </div>
                
                <div class="tab-content">
                    <div id="templates-panel" class="tab-panel active">
                        <h2>🚀 Orchestration Templates</h2>
                        <p>Pre-configured prompts for common complex tasks. Click to customize and execute.</p>
                        <div id="templates-grid" class="template-grid">
                            Loading templates...
                        </div>
                    </div>
                    
                    <div id="tasks-panel" class="tab-panel">
                        <h2>⚡ Active Orchestration Tasks</h2>
                        <div id="tasks-container">
                            Loading tasks...
                        </div>
                    </div>
                    
                    <div id="results-panel" class="tab-panel">
                        <h2>📊 Task Results & Export</h2>
                        <div id="results-container">
                            Loading results...
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chat-sidebar">
            <div class="chat-header">
                <h2>🤖 Mother Agent</h2>
                <div class="chat-status" id="chat-status">Ready to orchestrate</div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message system">
                    <div>🤖 Enhanced Mother Agent initialized</div>
                    <div class="message-time">Ready to help with orchestration tasks!</div>
                </div>
            </div>
            
            <div class="chat-input-area">
                <textarea 
                    class="chat-input" 
                    id="chat-input" 
                    placeholder="Ask Mother Agent to orchestrate tasks, analyze opportunities, or coordinate teams..."
                    rows="3"
                ></textarea>
                <div class="chat-controls">
                    <button class="btn btn-primary" onclick="sendMessage()">💬 Send</button>
                    <button class="btn btn-secondary" onclick="clearChat()">🗑️ Clear</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Template Modal -->
    <div id="template-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modal-title">Customize Template</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            
            <form id="template-form">
                <div class="form-group">
                    <label class="form-label">Task Description:</label>
                    <textarea class="form-control" id="modal-prompt" rows="6"></textarea>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Budget Constraint:</label>
                    <select class="form-control" id="modal-budget">
                        <option value="under_$5">Under $5</option>
                        <option value="under_$10">Under $10</option>
                        <option value="under_$20">Under $20</option>
                        <option value="no_limit">No Limit</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Timeline:</label>
                    <select class="form-control" id="modal-timeline">
                        <option value="urgent">Urgent (same day)</option>
                        <option value="same_day">Same Day</option>
                        <option value="within_week">Within Week</option>
                        <option value="flexible">Flexible</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <button type="button" class="btn btn-primary" onclick="executeTemplate()">
                        🚀 Execute Orchestration
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="sendToChat()">
                        💬 Send to Chat
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let conversationId = null;
        let templates = {};
        let currentTemplate = null;
        
        // Initialize dashboard
        async function init() {
            try {
                console.log('Initializing dashboard...');
                await startConversation();
                await loadTemplates();
                await loadTasks();
                await updateSystemStatus();
                console.log('Dashboard initialized successfully');
                
                // Auto-refresh
                setInterval(() => {
                    loadTasks();
                    updateSystemStatus();
                }, 5000);
            } catch (error) {
                console.error('Failed to initialize dashboard:', error);
                // Show error in chat status if main init fails
                const chatStatusElement = document.getElementById('chat-status');
                if (chatStatusElement) {
                    chatStatusElement.textContent = 'Initialization Failed';
                }
            }
            
            // Enable Enter to send in chat
            document.getElementById('chat-input').addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }
        
        // Chat functionality
        async function startConversation() {
            try {
                const response = await fetch('/api/conversation/start');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                conversationId = data.conversation_id;
                console.log('Conversation started:', conversationId);
                await loadMessages();
            } catch (error) {
                console.error('Failed to start conversation:', error);
                // Show error message in chat
                addMessageToUI('system', `❌ Failed to start conversation: ${error.message}`);
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (!message || !conversationId) return;
            
            input.value = '';
            addMessageToUI('user', message);
            
            try {
                const response = await fetch(`/api/conversation/${conversationId}/send`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                addMessageToUI('assistant', data.content);
                
                // Refresh tasks in case new orchestration started
                loadTasks();
                
            } catch (error) {
                console.error('Failed to send message:', error);
                addMessageToUI('system', 'Error sending message. Please try again.');
            }
        }
        
        async function loadMessages() {
            if (!conversationId) return;
            
            try {
                const response = await fetch(`/api/conversation/${conversationId}/messages`);
                const data = await response.json();
                
                const container = document.getElementById('chat-messages');
                container.innerHTML = '';
                
                data.messages.forEach(msg => {
                    addMessageToUI(msg.role, msg.content, msg.timestamp);
                });
            } catch (error) {
                console.error('Failed to load messages:', error);
            }
        }
        
        function addMessageToUI(role, content, timestamp = null) {
            const container = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
            
            messageDiv.innerHTML = `
                <div>${content}</div>
                <div class="message-time">${time}</div>
            `;
            
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        function clearChat() {
            if (confirm('Clear chat history?')) {
                startConversation();
            }
        }
        
        // Template functionality
        async function loadTemplates() {
            try {
                const response = await fetch('/api/templates');
                const data = await response.json();
                templates = data.templates;
                renderTemplates();
            } catch (error) {
                console.error('Failed to load templates:', error);
            }
        }
        
        function renderTemplates() {
            const container = document.getElementById('templates-grid');
            const html = Object.keys(templates).map(key => {
                const template = templates[key];
                return `
                    <div class="template-card" onclick="openTemplate('${key}')">
                        <div class="template-title">${template.title}</div>
                        <div class="template-description">${template.description}</div>
                        <div class="template-meta">
                            <span class="template-tag">${template.suggested_budget}</span>
                            <span class="template-tag">${template.suggested_timeline}</span>
                        </div>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = html;
        }
        
        function openTemplate(key) {
            currentTemplate = key;
            const template = templates[key];
            
            document.getElementById('modal-title').textContent = template.title;
            document.getElementById('modal-prompt').value = template.prompt;
            document.getElementById('modal-budget').value = template.suggested_budget;
            document.getElementById('modal-timeline').value = template.suggested_timeline;
            
            document.getElementById('template-modal').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('template-modal').style.display = 'none';
        }
        
        async function executeTemplate() {
            const prompt = document.getElementById('modal-prompt').value;
            const budget = document.getElementById('modal-budget').value;
            const timeline = document.getElementById('modal-timeline').value;
            
            if (!prompt.trim()) {
                alert('Please provide a task description');
                return;
            }
            
            try {
                const response = await fetch('/api/orchestrate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        prompt: `${prompt}\n\nBudget: ${budget}\nTimeline: ${timeline}` 
                    })
                });
                
                const data = await response.json();
                addMessageToUI('assistant', data.response);
                closeModal();
                loadTasks();
                
            } catch (error) {
                console.error('Failed to execute orchestration:', error);
                alert('Failed to start orchestration. Please try again.');
            }
        }
        
        function sendToChat() {
            const prompt = document.getElementById('modal-prompt').value;
            document.getElementById('chat-input').value = prompt;
            closeModal();
            document.getElementById('chat-input').focus();
        }
        
        // Tasks functionality
        async function loadTasks() {
            try {
                const response = await fetch('/api/tasks');
                const data = await response.json();
                renderTasks(data.tasks || []);
            } catch (error) {
                console.error('Failed to load tasks:', error);
            }
        }
        
        function renderTasks(tasks) {
            const container = document.getElementById('tasks-container');
            
            if (tasks.length === 0) {
                container.innerHTML = '<div class="task-card">No active tasks. Use templates or chat to start orchestration.</div>';
                return;
            }
            
            const html = tasks.map(task => {
                const statusClass = `status-${task.status}`;
                const progress = task.progress || 0;
                
                return `
                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-title">${task.title}</div>
                            <div class="task-status ${statusClass}">${task.status}</div>
                        </div>
                        
                        <div style="margin-bottom: 10px;">
                            <strong>Current Phase:</strong> ${task.current_phase || 'Initializing...'}
                        </div>
                        
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        
                        <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 10px;">
                            Created: ${new Date(task.created_at).toLocaleString()}
                        </div>
                        
                        ${task.status === 'running' ? `
                            <button class="btn btn-secondary" onclick="cancelTask('${task.id}')">
                                ❌ Cancel Task
                            </button>
                        ` : ''}
                    </div>
                `;
            }).join('');
            
            container.innerHTML = html;
        }
        
        async function cancelTask(taskId) {
            if (!confirm('Cancel this orchestration task?')) return;
            
            try {
                const response = await fetch(`/api/tasks/${taskId}/cancel`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (data.success) {
                    loadTasks();
                    addMessageToUI('system', `Task ${taskId} cancelled successfully.`);
                } else {
                    alert('Failed to cancel task');
                }
            } catch (error) {
                console.error('Failed to cancel task:', error);
                alert('Failed to cancel task');
            }
        }
        
        // System status
        async function updateSystemStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const statusText = data.enhanced_mother_available ? 
                    '✅ Enhanced Mother Agent Ready' : 
                    '⚠️ Basic Mother Agent Only';
                    
                const statusElement = document.getElementById('system-status');
                const chatStatusElement = document.getElementById('chat-status');
                
                if (statusElement) {
                    statusElement.textContent = statusText;
                }
                
                if (chatStatusElement) {
                    chatStatusElement.textContent = 
                        `${data.active_conversations || 0} conversations • ${data.running_tasks || 0} running`;
                }
                    
            } catch (error) {
                console.error('Failed to update status:', error);
                const statusElement = document.getElementById('system-status');
                if (statusElement) {
                    statusElement.textContent = '❌ System Error';
                }
                const chatStatusElement = document.getElementById('chat-status');
                if (chatStatusElement) {
                    chatStatusElement.textContent = 'Connection Error';
                }
            }
        }
        
        // Results functionality
        async function loadResults() {
            try {
                const response = await fetch('/api/tasks');
                const data = await response.json();
                const completedTasks = (data.tasks || []).filter(task => task.status === 'completed');
                renderResults(completedTasks);
            } catch (error) {
                console.error('Failed to load results:', error);
            }
        }
        
        function renderResults(completedTasks) {
            const container = document.getElementById('results-container');
            
            if (completedTasks.length === 0) {
                container.innerHTML = `
                    <div class="task-card">
                        <h3>No completed tasks yet</h3>
                        <p>Complete some orchestration tasks to see results here.</p>
                    </div>
                `;
                return;
            }
            
            const html = completedTasks.map(task => {
                const createdDate = new Date(task.created_at).toLocaleDateString();
                const completedDate = new Date(task.updated_at).toLocaleDateString();
                
                return `
                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-title">${task.title}</div>
                            <div class="task-status status-completed">Completed</div>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <strong>Created:</strong> ${createdDate} | 
                            <strong>Completed:</strong> ${completedDate}
                        </div>
                        
                        <div style="margin-bottom: 15px; font-size: 0.9em; color: #6c757d;">
                            ${task.prompt.substring(0, 200)}${task.prompt.length > 200 ? '...' : ''}
                        </div>
                        
                        ${task.results ? `
                            <div style="margin-bottom: 15px;">
                                <strong>Results Summary:</strong>
                                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px; font-size: 0.9em;">
                                    ${typeof task.results === 'object' && task.results.summary ? 
                                        task.results.summary.substring(0, 300) + (task.results.summary.length > 300 ? '...' : '') :
                                        'Results available'
                                    }
                                </div>
                            </div>
                        ` : ''}
                        
                        <div class="results-actions">
                            <button class="btn btn-primary" onclick="exportTask('${task.id}', 'json')"
                                title="Export as JSON">
                                📄 JSON
                            </button>
                            <button class="btn btn-primary" onclick="exportTask('${task.id}', 'markdown')"
                                title="Export as Markdown">
                                📝 Markdown
                            </button>
                            <button class="btn btn-primary" onclick="exportTask('${task.id}', 'pdf')"
                                title="Export as PDF (Text)">
                                📋 PDF
                            </button>
                            <button class="btn btn-secondary" onclick="viewTaskDetails('${task.id}')"
                                title="View full details">
                                👁️ Details
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = html;
        }
        
        async function exportTask(taskId, format) {
            try {
                const link = document.createElement('a');
                link.href = `/api/export/${taskId}/${format}`;
                link.download = `fresh_orchestration_${taskId.substring(0, 8)}.${format === 'pdf' ? 'txt' : format}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                addMessageToUI('system', `Task results exported as ${format.toUpperCase()}.`);
            } catch (error) {
                console.error('Export failed:', error);
                alert('Export failed. Please try again.');
            }
        }
        
        async function viewTaskDetails(taskId) {
            try {
                const response = await fetch(`/api/tasks/${taskId}`);
                const task = await response.json();
                
                // Create a simple modal-style display in chat
                const details = `**Task Details: ${task.title}**\n\n` +
                              `**ID:** ${task.id}\n` +
                              `**Status:** ${task.status}\n` +
                              `**Created:** ${new Date(task.created_at).toLocaleString()}\n` +
                              `**Completed:** ${new Date(task.updated_at).toLocaleString()}\n\n` +
                              `**Prompt:**\n${task.prompt}\n\n` +
                              `**Results:**\n${JSON.stringify(task.results, null, 2)}`;
                
                addMessageToUI('system', details);
                
                // Switch to chat tab to show details
                // No need to switch tabs, details are shown in chat
                
            } catch (error) {
                console.error('Failed to load task details:', error);
                addMessageToUI('system', 'Failed to load task details.');
            }
        }
        
        // Tab switching
        function switchTab(tabName) {
            // Update buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update panels
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(`${tabName}-panel`).classList.add('active');
            
            // Refresh data
            if (tabName === 'tasks') {
                loadTasks();
            } else if (tabName === 'results') {
                loadResults();
            }
        }
        
        // Initialize when page loads
        window.addEventListener('load', init);
        
        // Handle modal clicks
        window.onclick = function(event) {
            const modal = document.getElementById('template-modal');
            if (event.target === modal) {
                closeModal();
            }
        };
    </script>
</body>
</html>
        """


def start_enhanced_dashboard(port: int = 8080, open_browser: bool = True):
    """Start the enhanced dashboard server"""
    server = HTTPServer(('localhost', port), EnhancedDashboardHandler)
    shutdown_event = threading.Event()
    
    print(f"""
🚀 Enhanced Fresh AI Dashboard Starting...

📊 Dashboard URL: http://localhost:{port}
🤖 Mother Agent Chat: Real-time conversation interface
📋 Template Library: Pre-configured orchestration tasks
⚡ Live Orchestration: Monitor multi-agent tasks in real-time
📈 Results Export: View and export orchestration results

🎯 Key Features:
  • Conversational Mother Agent interface
  • Preset prompt templates with customization
  • Live task progress monitoring
  • Multi-agent orchestration control
  • Results management and export

Press Ctrl+C to stop the dashboard
""")
    
    if open_browser:
        threading.Thread(
            target=lambda: (time.sleep(1), webbrowser.open(f'http://localhost:{port}')),
            daemon=True
        ).start()
    
    def signal_handler(signum, frame):
        print("\n🛑 Enhanced Dashboard shutting down...")
        shutdown_event.set()  # Signal the shutdown
        server.shutdown()  # Stop accepting new requests
        server.server_close()  # Close the server socket
        print("✅ Enhanced Dashboard stopped.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server in a separate thread to allow signal handling
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    try:
        # Main thread waits for shutdown event or keyboard interrupt
        while not shutdown_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Enhanced Dashboard shutting down...")
    finally:
        shutdown_event.set()
        server.shutdown()
        server.server_close()
        print("✅ Enhanced Dashboard stopped.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Fresh AI Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run dashboard on')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    args = parser.parse_args()
    
    start_enhanced_dashboard(args.port, not args.no_browser)
