#!/usr/bin/env python
"""Fresh App Genesis CLI - Build entire applications through AI conversation.

This CLI allows users to create complete applications by having intelligent
conversations with AI agents that then autonomously develop the entire project.

Usage:
    python fresh_app_genesis.py create "I want to build a spiritual chatbot platform"
    python fresh_app_genesis.py continue
    python fresh_app_genesis.py status
    python fresh_app_genesis.py develop
"""
import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add ai module to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.agents.app_genesis import AppGenesisAgent


class AppGenesisCLI:
    """Command-line interface for App Genesis Agent."""
    
    def __init__(self):
        self.agent = AppGenesisAgent()
        self.state_file = Path("./app_genesis_state.json")
        self.load_state()
    
    def save_state(self):
        """Save current conversation state."""
        state = {
            "conversation_history": self.agent.conversation_history,
            "current_app": None,
            "development_tasks": []
        }
        
        if self.agent.current_app:
            # Serialize app spec
            app = self.agent.current_app
            state["current_app"] = {
                "name": app.name,
                "description": app.description,
                "app_type": app.app_type.value,
                "target_audience": app.target_audience,
                "core_features": app.core_features,
                "tech_stack": app.tech_stack,
                "architecture": app.architecture,
                "business_model": app.business_model,
                "created_at": app.created_at.isoformat()
            }
        
        # Serialize development tasks
        state["development_tasks"] = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "phase": task.phase.value,
                "agent_type": task.agent_type,
                "priority": task.priority,
                "estimated_hours": task.estimated_hours
            }
            for task in self.agent.development_tasks
        ]
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load previous conversation state."""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            self.agent.conversation_history = state.get("conversation_history", [])
            
            # Restore app spec if exists
            if state.get("current_app"):
                from ai.agents.app_genesis import AppSpec, AppType
                from datetime import datetime
                
                app_data = state["current_app"]
                self.agent.current_app = AppSpec(
                    name=app_data["name"],
                    description=app_data["description"],
                    app_type=AppType(app_data["app_type"]),
                    target_audience=app_data["target_audience"],
                    core_features=app_data["core_features"],
                    tech_stack=app_data["tech_stack"],
                    architecture=app_data["architecture"],
                    business_model=app_data.get("business_model"),
                    requirements=[],  # Not serialized yet
                    created_at=datetime.fromisoformat(app_data["created_at"])
                )
            
        except Exception as e:
            print(f"⚠️ Warning: Could not load previous state: {e}")
    
    async def create_app(self, initial_idea: str):
        """Start creating a new app."""
        print("🎯 Fresh App Genesis - Autonomous Application Development")
        print("=" * 60)
        print()
        
        # Start the creation process
        first_question = await self.agent.start_app_creation(initial_idea)
        
        print("🤖 AI Agent:")
        print(first_question)
        print()
        
        # Save state after first question
        self.save_state()
        
        # Continue conversation
        await self.interactive_conversation()
    
    async def continue_conversation(self):
        """Continue an existing conversation."""
        if not self.agent.conversation_history:
            print("❌ No active conversation. Start a new one with 'create' command.")
            return
        
        if self.agent.current_app:
            print("✅ App specification complete! Use 'develop' command to start building.")
            return
        
        print("🔄 Continuing conversation...")
        print()
        
        # Show last few messages for context
        recent_messages = self.agent.conversation_history[-4:]
        for msg in recent_messages:
            role = "🤖 AI Agent" if msg["role"] == "assistant" else "👤 You"
            print(f"{role}: {msg['content']}")
        print()
        
        await self.interactive_conversation()
    
    async def interactive_conversation(self):
        """Handle interactive Q&A conversation."""
        while True:
            try:
                # Get user input
                user_input = input("👤 Your response: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Use 'continue' command to resume later.")
                    break
                
                # Process response
                print("\n🤔 Thinking...")
                response, is_ready = await self.agent.continue_conversation(user_input)
                
                print(f"\n🤖 AI Agent:")
                print(response)
                print()
                
                # Save state after each exchange
                self.save_state()
                
                # Check if ready to build
                if is_ready:
                    print("🎉 App specification complete!")
                    print("\nType 'python fresh_app_genesis.py develop' to start autonomous development!")
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 Conversation paused. Use 'continue' command to resume.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.")
    
    async def develop_app(self):
        """Start autonomous development."""
        if not self.agent.current_app:
            print("❌ No app specification available. Complete the Q&A process first.")
            return
        
        print("🚀 Starting Autonomous Development")
        print("=" * 40)
        print()
        
        try:
            result = await self.agent.start_autonomous_development()
            print(result)
            
            # Save updated state
            self.save_state()
            
            print()
            print("🎯 Development Status:")
            status = self.agent.get_development_status()
            print(f"App: {status['app_name']}")
            print(f"Progress: {status['progress_percentage']:.1f}%")
            print(f"Tasks: {status['tasks_completed']}/{status['total_tasks']}")
            
        except Exception as e:
            print(f"❌ Development failed: {e}")
    
    def show_status(self):
        """Show current status."""
        print("📊 App Genesis Status")
        print("=" * 25)
        print()
        
        if not self.agent.conversation_history:
            print("❌ No active project")
            return
        
        print(f"💬 Conversation messages: {len(self.agent.conversation_history)}")
        
        if self.agent.current_app:
            app = self.agent.current_app
            print(f"✅ App specification: {app.name}")
            print(f"📝 Description: {app.description}")
            print(f"🎯 Target audience: {app.target_audience}")
            print(f"⚙️ App type: {app.app_type.value}")
            print(f"🔧 Tech stack: {', '.join(app.tech_stack.values())}")
            
            status = self.agent.get_development_status()
            if status.get("total_tasks", 0) > 0:
                print(f"🏗️ Development progress: {status['progress_percentage']:.1f}%")
                print(f"📋 Tasks: {status['tasks_completed']}/{status['total_tasks']}")
                
                if status.get("next_tasks"):
                    print("🔜 Next tasks:")
                    for task in status["next_tasks"]:
                        print(f"   • {task}")
        else:
            print("🔄 Conversation in progress...")
            if self.agent.conversation_history:
                last_msg = self.agent.conversation_history[-1]
                print(f"💭 Last message: {last_msg['content'][:60]}...")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fresh App Genesis - Build entire applications through AI conversation"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Start creating a new app')
    create_parser.add_argument('idea', help='Initial app idea')
    
    # Continue command
    subparsers.add_parser('continue', help='Continue existing conversation')
    
    # Develop command
    subparsers.add_parser('develop', help='Start autonomous development')
    
    # Status command
    subparsers.add_parser('status', help='Show current status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AppGenesisCLI()
    
    try:
        if args.command == 'create':
            await cli.create_app(args.idea)
        elif args.command == 'continue':
            await cli.continue_conversation()
        elif args.command == 'develop':
            await cli.develop_app()
        elif args.command == 'status':
            cli.show_status()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
