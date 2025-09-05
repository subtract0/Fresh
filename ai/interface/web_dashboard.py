#!/usr/bin/env python3
"""
🚀 Fresh AI Agent Web Dashboard

A comprehensive web-based interface for monitoring and controlling AI agents.
Features real-time updates, agent spawn controls, performance metrics, and activity feeds.

Usage:
    poetry run python ai/interface/web_dashboard.py
    
Then navigate to: http://localhost:8080
"""

from __future__ import annotations
import asyncio
import json
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import webbrowser
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

from ai.monitor.event_bus import get_bus
from ai.autonomous import AutonomousLoop


class AgentController:
    """Controls different types of agents"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.agent_configs = {
            'autonomous': {
                'name': '🤖 Autonomous Loop',
                'description': 'Continuous improvement and development loop',
                'command': ['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'run', '--once'],
                'continuous_command': ['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'run', '--watch'],
                'status': 'stopped'
            },
            'scanner': {
                'name': '🔍 Repository Scanner', 
                'description': 'Scan for TODOs, FIXMEs and issues',
                'command': ['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'scan', '.', '--json'],
                'status': 'stopped'
            },
            'spawn_qa': {
                'name': '🛡️ QA Agent',
                'description': 'Quality assurance and code review',
                'command': ['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'spawn', 'Review and improve code quality'],
                'status': 'stopped'
            },
            'spawn_dev': {
                'name': '👨‍💻 Developer Agent',
                'description': 'Feature development and bug fixes',
                'command': ['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'spawn', 'Implement new features and fix bugs'],
                'status': 'stopped'
            },
            'orchestrate': {
                'name': '🎭 Orchestration Agent',
                'description': 'Complex multi-agent coordination',
                'command': ['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'orchestrate', 'Coordinate development tasks'],
                'status': 'stopped'
            }
        }
        
    def start_agent(self, agent_type: str, continuous: bool = False) -> bool:
        """Start an agent process"""
        if agent_type not in self.agent_configs:
            return False
            
        if agent_type in self.processes and self.processes[agent_type].poll() is None:
            return False  # Already running
            
        config = self.agent_configs[agent_type]
        command = config.get('continuous_command', config['command']) if continuous else config['command']
        
        try:
            process = subprocess.Popen(
                command,
                cwd=Path.cwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes[agent_type] = process
            self.agent_configs[agent_type]['status'] = 'running'
            
            # Log to event bus
            get_bus().append({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'agent_start',
                'agent_name': agent_type,
                'details': f"Started {config['name']}"
            })
            
            return True
        except Exception as e:
            print(f"Failed to start {agent_type}: {e}")
            return False
    
    def stop_agent(self, agent_type: str) -> bool:
        """Stop an agent process"""
        if agent_type not in self.processes:
            return False
            
        process = self.processes[agent_type]
        if process.poll() is not None:
            return False  # Already stopped
            
        try:
            process.terminate()
            process.wait(timeout=5)
            self.agent_configs[agent_type]['status'] = 'stopped'
            del self.processes[agent_type]
            
            # Log to event bus
            get_bus().append({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'agent_stop',
                'agent_name': agent_type,
                'details': f"Stopped {self.agent_configs[agent_type]['name']}"
            })
            
            return True
        except Exception as e:
            print(f"Failed to stop {agent_type}: {e}")
            return False
    
    def get_agent_status(self, agent_type: str) -> str:
        """Get current status of an agent"""
        if agent_type not in self.agent_configs:
            return 'unknown'
            
        if agent_type in self.processes:
            if self.processes[agent_type].poll() is None:
                return 'running'
            else:
                # Process ended, clean up
                del self.processes[agent_type] 
                self.agent_configs[agent_type]['status'] = 'stopped'
                
        return self.agent_configs[agent_type]['status']
    
    def emergency_stop_all(self) -> bool:
        """Emergency stop all agents"""
        stopped_count = 0
        for agent_type in list(self.processes.keys()):
            if self.stop_agent(agent_type):
                stopped_count += 1
        
        get_bus().append({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'emergency_stop',
            'agent_name': 'system',
            'details': f"Emergency stop: stopped {stopped_count} agents"
        })
        
        return stopped_count > 0


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the web dashboard"""
    
    controller = AgentController()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/status':
            self.serve_status_api()
        elif path == '/api/events':
            self.serve_events_api()
        elif path.startswith('/api/agent/'):
            self.handle_agent_api(parsed)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        self.do_GET()  # Reuse GET handler for API endpoints
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html_content = self.get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_status_api(self):
        """Serve agent status API"""
        status_data = {}
        
        for agent_type, config in self.controller.agent_configs.items():
            current_status = self.controller.get_agent_status(agent_type)
            status_data[agent_type] = {
                'name': config['name'],
                'description': config['description'],
                'status': current_status,
                'uptime': self.get_agent_uptime(agent_type) if current_status == 'running' else None
            }
        
        self.send_json_response(status_data)
    
    def serve_events_api(self):
        """Serve recent events API"""
        events = get_bus().read_recent(50)
        self.send_json_response(events)
    
    def handle_agent_api(self, parsed):
        """Handle agent control API endpoints"""
        path_parts = parsed.path.split('/')
        if len(path_parts) < 4:
            self.send_error(400, "Invalid API endpoint")
            return
            
        agent_type = path_parts[3]
        action = path_parts[4] if len(path_parts) > 4 else None
        
        if action == 'start':
            query_params = parse_qs(parsed.query)
            continuous = 'continuous' in query_params
            success = self.controller.start_agent(agent_type, continuous)
            self.send_json_response({'success': success})
            
        elif action == 'stop':
            success = self.controller.stop_agent(agent_type)
            self.send_json_response({'success': success})
            
        elif action == 'status':
            status = self.controller.get_agent_status(agent_type)
            self.send_json_response({'status': status})
            
        else:
            self.send_error(400, "Invalid action")
    
    def send_json_response(self, data):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json_data.encode())
    
    def get_agent_uptime(self, agent_type: str) -> Optional[str]:
        """Get agent uptime in human readable format"""
        if agent_type not in self.controller.processes:
            return None
        # Simplified uptime - could track start time properly
        return "Running..."
    
    def get_dashboard_html(self) -> str:
        """Generate the dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Fresh AI Agent Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 30px;
            text-align: center;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }
        
        .agents-panel {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #e9ecef;
        }
        
        .agents-panel h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .agent-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .agent-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .agent-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status-running { background: #d4edda; color: #155724; }
        .status-stopped { background: #f8d7da; color: #721c24; }
        
        .agent-description {
            color: #6c757d;
            margin-bottom: 15px;
            font-size: 0.95em;
        }
        
        .agent-controls {
            display: flex;
            gap: 10px;
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
        
        .btn:hover { transform: translateY(-1px); }
        
        .btn-start { background: #28a745; color: white; }
        .btn-start:hover { background: #218838; }
        
        .btn-stop { background: #dc3545; color: white; }
        .btn-stop:hover { background: #c82333; }
        
        .btn-continuous { background: #17a2b8; color: white; }
        .btn-continuous:hover { background: #138496; }
        
        .activity-panel {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #e9ecef;
        }
        
        .activity-feed {
            max-height: 500px;
            overflow-y: auto;
            background: white;
            border-radius: 10px;
            padding: 15px;
        }
        
        .activity-item {
            padding: 12px;
            border-left: 4px solid #007bff;
            background: #f1f3f4;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }
        
        .activity-time {
            font-size: 0.8em;
            color: #6c757d;
            font-weight: 500;
        }
        
        .activity-details {
            margin-top: 5px;
            color: #495057;
        }
        
        .emergency-controls {
            background: #fff3cd;
            border: 2px solid #ffeaa7;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 30px;
            text-align: center;
        }
        
        .btn-emergency {
            background: #ff4757;
            color: white;
            padding: 12px 24px;
            font-size: 1.1em;
            font-weight: bold;
        }
        
        .btn-emergency:hover {
            background: #ff3742;
        }
        
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Fresh AI Agent Dashboard</h1>
            <p>Monitor and control your autonomous development agents</p>
            <p id="last-updated">Last updated: <span id="timestamp">Loading...</span></p>
        </div>
        
        <div class="emergency-controls">
            <button class="btn btn-emergency" onclick="emergencyStop()">🛑 EMERGENCY STOP ALL AGENTS</button>
        </div>
        
        <div class="dashboard-grid">
            <div class="agents-panel">
                <h2>🎛️ Agent Controls</h2>
                <div id="agents-container">
                    Loading agents...
                </div>
            </div>
            
            <div class="activity-panel">
                <h2>📊 Live Activity Feed</h2>
                <div class="activity-feed" id="activity-feed">
                    Loading activity...
                </div>
            </div>
        </div>
    </div>

    <script>
        let agents = {};
        
        // Update timestamp
        function updateTimestamp() {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }
        
        // Fetch and update agent status
        async function updateAgentStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                agents = data;
                renderAgents();
            } catch (error) {
                console.error('Failed to update status:', error);
            }
        }
        
        // Render agent cards
        function renderAgents() {
            const container = document.getElementById('agents-container');
            const html = Object.keys(agents).map(agentType => {
                const agent = agents[agentType];
                const statusClass = `status-${agent.status}`;
                const statusText = agent.status.charAt(0).toUpperCase() + agent.status.slice(1);
                
                return `
                    <div class="agent-card">
                        <div class="agent-header">
                            <div class="agent-name">${agent.name}</div>
                            <div class="status-badge ${statusClass}">${statusText}</div>
                        </div>
                        <div class="agent-description">${agent.description}</div>
                        <div class="agent-controls">
                            ${agent.status === 'stopped' ? 
                                `<button class="btn btn-start" onclick="startAgent('${agentType}')">▶️ Start</button>
                                 <button class="btn btn-continuous" onclick="startAgent('${agentType}', true)">🔄 Continuous</button>` :
                                `<button class="btn btn-stop" onclick="stopAgent('${agentType}')">⏹️ Stop</button>`
                            }
                        </div>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = html;
        }
        
        // Fetch and update activity feed
        async function updateActivity() {
            try {
                const response = await fetch('/api/events');
                const events = await response.json();
                renderActivity(events);
            } catch (error) {
                console.error('Failed to update activity:', error);
            }
        }
        
        // Render activity feed
        function renderActivity(events) {
            const feed = document.getElementById('activity-feed');
            const html = events.reverse().map(event => {
                const time = new Date(event.timestamp).toLocaleTimeString();
                const eventIcon = {
                    'agent_start': '🚀',
                    'agent_stop': '⏹️',
                    'emergency_stop': '🛑',
                    'task_complete': '✅',
                    'error': '❌'
                }[event.event_type] || '📝';
                
                return `
                    <div class="activity-item">
                        <div class="activity-time">${eventIcon} ${time} - ${event.agent_name}</div>
                        <div class="activity-details">${event.details}</div>
                    </div>
                `;
            }).join('');
            
            feed.innerHTML = html || '<div class="activity-item">No recent activity</div>';
        }
        
        // Start agent
        async function startAgent(agentType, continuous = false) {
            const url = continuous ? 
                `/api/agent/${agentType}/start?continuous=true` : 
                `/api/agent/${agentType}/start`;
                
            try {
                const response = await fetch(url, { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateAgentStatus();
                    updateActivity();
                } else {
                    alert('Failed to start agent');
                }
            } catch (error) {
                console.error('Failed to start agent:', error);
                alert('Failed to start agent');
            }
        }
        
        // Stop agent
        async function stopAgent(agentType) {
            try {
                const response = await fetch(`/api/agent/${agentType}/stop`, { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateAgentStatus();
                    updateActivity();
                } else {
                    alert('Failed to stop agent');
                }
            } catch (error) {
                console.error('Failed to stop agent:', error);
                alert('Failed to stop agent');
            }
        }
        
        // Emergency stop all agents
        async function emergencyStop() {
            if (!confirm('Are you sure you want to emergency stop ALL agents?')) {
                return;
            }
            
            try {
                // Stop all running agents
                for (const agentType in agents) {
                    if (agents[agentType].status === 'running') {
                        await fetch(`/api/agent/${agentType}/stop`, { method: 'POST' });
                    }
                }
                
                updateAgentStatus();
                updateActivity();
                alert('Emergency stop completed');
            } catch (error) {
                console.error('Emergency stop failed:', error);
                alert('Emergency stop failed');
            }
        }
        
        // Initialize dashboard
        async function init() {
            updateTimestamp();
            await updateAgentStatus();
            await updateActivity();
            
            // Auto-refresh every 5 seconds
            setInterval(() => {
                updateTimestamp();
                updateAgentStatus();
                updateActivity();
            }, 5000);
        }
        
        // Start dashboard when page loads
        window.addEventListener('load', init);
    </script>
</body>
</html>
"""


def start_dashboard(port: int = 8080, open_browser: bool = True):
    """Start the web dashboard server"""
    server = HTTPServer(('localhost', port), DashboardHandler)
    
    print(f"""
🚀 Fresh AI Agent Dashboard Starting...

📊 Dashboard URL: http://localhost:{port}
🎛️  Agent Controls: Available for all agent types
📈 Live Monitoring: Real-time status and activity feed
🛑 Emergency Stop: Available for safety

Press Ctrl+C to stop the dashboard
""")
    
    if open_browser:
        threading.Thread(
            target=lambda: (time.sleep(1), webbrowser.open(f'http://localhost:{port}')),
            daemon=True
        ).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard shutting down...")
        # Emergency stop all agents
        controller = DashboardHandler.controller
        controller.emergency_stop_all()
        server.shutdown()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fresh AI Agent Web Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run dashboard on')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    args = parser.parse_args()
    
    start_dashboard(args.port, not args.no_browser)
