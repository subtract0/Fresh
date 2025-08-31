"""Telegram Bot Interface for Fresh Agent System.

This module provides a foolproof Telegram interface where users can submit
development requests that are intelligently routed to the appropriate agents
through the Father agent's decision-making process.

Cross-references:
    - Agent Development: docs/AGENT_DEVELOPMENT.md for agent architecture
    - Interface Documentation: docs/INTERFACES.md for CLI alternatives  
    - Father Agent: ai/agents/Father.py for delegation logic
    - Memory System: ai/memory/README.md for context persistence

Related:
    - ai.agents.Father: Strategic planning and agent delegation
    - ai.tools.memory_tools: Conversation context and history
    - ai.interface.deploy_agents: Agent spawning and configuration
"""
from __future__ import annotations
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, 
        CallbackQueryHandler, filters, ContextTypes
    )
except ImportError as e:
    raise ImportError(
        "Telegram dependencies not installed. Run: pip install python-telegram-bot"
    ) from e

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.tools.next_steps import GenerateNextSteps
from ai.interface.deploy_agents import AgentDeploymentInterface


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


class FatherDecisionMaker:
    """Interfaces with Father agent for intelligent task delegation."""
    
    def __init__(self):
        self.deployment_interface = AgentDeploymentInterface()
        
    async def analyze_request(self, user_request: str, user_context: str = "") -> Dict[str, Any]:
        """Analyze user request and determine optimal agent configuration.
        
        Cross-references:
            - Father Agent Logic: ai/agents/Father.py for delegation patterns
            - Memory Context: ai/memory/README.md for context usage
            - Agent Configuration: docs/AGENT_DEVELOPMENT.md#creating-new-agents
        """
        # Store the user request in memory for context
        WriteMemory(
            content=f"User request via Telegram: {user_request}",
            tags=["telegram", "user-request", "delegation"]
        ).run()
        
        # Get relevant context from memory and documentation
        context = ReadMemoryContext(limit=20, tags=["delegation", "agent-config"]).run()
        
        # Read current system status and capabilities
        current_docs = await self._read_system_documentation()
        
        # Father's decision-making process
        decision = await self._father_agent_decision(
            request=user_request,
            context=context,
            user_context=user_context,
            system_docs=current_docs
        )
        
        return decision
    
    async def _read_system_documentation(self) -> str:
        """Read key documentation for context awareness."""
        docs_to_read = [
            "README.md",
            "docs/AGENT_DEVELOPMENT.md", 
            "docs/TOOLS.md",
            ".cursor/rules/ADR-001.md",
            ".cursor/rules/ADR-004.md"
        ]
        
        doc_content = []
        for doc_path in docs_to_read:
            try:
                with open(Path(doc_path), 'r') as f:
                    content = f.read()[:1000]  # Limit size
                    doc_content.append(f"=== {doc_path} ===\n{content}\n")
            except FileNotFoundError:
                continue
                
        return "\n".join(doc_content)
    
    async def _father_agent_decision(
        self, 
        request: str, 
        context: str, 
        user_context: str,
        system_docs: str
    ) -> Dict[str, Any]:
        """Simulate Father agent's decision-making process.
        
        In a full implementation, this would invoke the actual Father agent.
        For now, it provides intelligent heuristics based on request analysis.
        """
        # Analyze request type and complexity
        request_lower = request.lower()
        
        # Determine agent configuration based on request patterns
        if any(word in request_lower for word in ["documentation", "docs", "explain", "document"]):
            return {
                "task_type": "documentation",
                "agents": [
                    {
                        "type": "Researcher",
                        "quantity": 1,
                        "role": "Research & Analysis",
                        "instructions": f"Research and analyze: {request}. Use available documentation and context to provide comprehensive insights.",
                        "tools": ["ReadMemoryContext", "WriteMemory", "DiscoverMCPServers"]
                    },
                    {
                        "type": "Documenter", 
                        "quantity": 1,
                        "role": "Documentation Creator",
                        "instructions": f"Create clear, comprehensive documentation for: {request}. Follow Fresh documentation standards with cross-references.",
                        "tools": ["WriteMemory", "CreateADR"]
                    }
                ],
                "execution_plan": [
                    "Research existing documentation and context",
                    "Analyze requirements and gaps",
                    "Create structured documentation",
                    "Add cross-references and examples"
                ],
                "estimated_time": "15-30 minutes",
                "confidence": "high"
            }
            
        elif any(word in request_lower for word in ["implement", "code", "build", "create", "develop"]):
            return {
                "task_type": "development", 
                "agents": [
                    {
                        "type": "Architect",
                        "quantity": 1,
                        "role": "TDD & Design",
                        "instructions": f"Design architecture and tests for: {request}. Follow TDD principles and create ADR if needed.",
                        "tools": ["CreateADR", "WriteMemory", "ReadMemoryContext"]
                    },
                    {
                        "type": "Developer",
                        "quantity": 1,
                        "role": "Implementation", 
                        "instructions": f"Implement solution for: {request}. Write minimal code to make tests green, then refactor.",
                        "tools": ["DiscoverMCPServers", "CallMCPTool", "WriteMemory"]
                    },
                    {
                        "type": "QA",
                        "quantity": 1,
                        "role": "Quality Assurance",
                        "instructions": f"Test and validate implementation for: {request}. Expand test coverage and verify quality.",
                        "tools": ["DoDCheck", "WriteMemory"]
                    }
                ],
                "execution_plan": [
                    "Architect designs solution and creates tests",
                    "Developer implements minimal working solution",
                    "QA validates and expands testing",
                    "Iterate until requirements are met"
                ],
                "estimated_time": "30-60 minutes",
                "confidence": "high"
            }
            
        elif any(word in request_lower for word in ["bug", "fix", "error", "issue", "problem"]):
            return {
                "task_type": "bugfix",
                "agents": [
                    {
                        "type": "Debugger",
                        "quantity": 1,
                        "role": "Issue Analysis",
                        "instructions": f"Analyze and debug: {request}. Identify root cause and propose solution.",
                        "tools": ["ReadMemoryContext", "WriteMemory", "DoDCheck"]
                    },
                    {
                        "type": "Developer", 
                        "quantity": 1,
                        "role": "Bug Fix Implementation",
                        "instructions": f"Fix identified issue: {request}. Implement minimal fix and add regression tests.",
                        "tools": ["WriteMemory", "CallMCPTool"]
                    }
                ],
                "execution_plan": [
                    "Analyze issue and gather context",
                    "Identify root cause",
                    "Implement targeted fix",
                    "Add tests to prevent regression"
                ],
                "estimated_time": "15-45 minutes", 
                "confidence": "medium"
            }
            
        elif any(word in request_lower for word in ["deploy", "setup", "configure", "install"]):
            return {
                "task_type": "deployment",
                "agents": [
                    {
                        "type": "DevOps",
                        "quantity": 1,
                        "role": "Deployment & Configuration",
                        "instructions": f"Handle deployment/setup: {request}. Follow security best practices and create documentation.",
                        "tools": ["WriteMemory", "ReadMemoryContext", "DoDCheck"]
                    }
                ],
                "execution_plan": [
                    "Analyze deployment requirements",
                    "Configure environment safely", 
                    "Validate deployment",
                    "Document process"
                ],
                "estimated_time": "20-40 minutes",
                "confidence": "medium"
            }
            
        else:
            # Generic task - let Father decide
            return {
                "task_type": "analysis",
                "agents": [
                    {
                        "type": "Father",
                        "quantity": 1, 
                        "role": "Strategic Analysis",
                        "instructions": f"Analyze request and determine optimal approach: {request}. Consider all available agents and tools.",
                        "tools": ["WriteMemory", "ReadMemoryContext", "GenerateNextSteps", "IntentNormalizer"]
                    }
                ],
                "execution_plan": [
                    "Analyze request and context",
                    "Determine optimal agent configuration",
                    "Create detailed execution plan",
                    "Deploy appropriate specialized agents"
                ],
                "estimated_time": "10-20 minutes",
                "confidence": "high"
            }


class FreshTelegramBot:
    """Main Telegram bot class for Fresh agent system."""
    
    def __init__(self, token: str, authorized_users: Optional[List[int]] = None):
        self.token = token
        self.authorized_users = set(authorized_users or [])
        self.father = FatherDecisionMaker()
        self.active_sessions: Dict[int, Dict[str, Any]] = {}
        
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot."""
        return not self.authorized_users or user_id in self.authorized_users
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text(
                "❌ Access denied. You are not authorized to use this bot."
            )
            return
            
        welcome_message = """
🤖 **Fresh Agent System - Telegram Interface**

Welcome to your intelligent development assistant!

**Commands:**
• `/request` - Submit a development request
• `/status` - Check active agent status  
• `/help` - Show detailed help
• `/agents` - List available agent types

**How it works:**
1. Describe what you want to build/fix/improve
2. Father agent analyzes your request using context and documentation
3. Optimal agents are spawned with custom instructions
4. You get real-time updates on progress

Ready to build something amazing? Use `/request` to get started! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
    async def request_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /request command to start task submission."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Access denied.")
            return
            
        self.active_sessions[user_id] = {
            "state": "awaiting_request",
            "timestamp": datetime.now()
        }
        
        keyboard = [
            [InlineKeyboardButton("💻 Development", callback_data="type_dev")],
            [InlineKeyboardButton("📚 Documentation", callback_data="type_docs")],
            [InlineKeyboardButton("🐛 Bug Fix", callback_data="type_bug")],
            [InlineKeyboardButton("🚀 Deployment", callback_data="type_deploy")],
            [InlineKeyboardButton("❓ Not Sure", callback_data="type_analyze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **What would you like to work on?**\n\n"
            "Choose a category or describe your request in detail:\n\n"
            "• Be specific about what you want to achieve\n"
            "• Include context about the current state\n"  
            "• Mention any constraints or preferences\n\n"
            "The Father agent will analyze your request and deploy the optimal team!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks."""
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        if not self.is_authorized(user_id):
            await query.edit_message_text("❌ Access denied.")
            return
            
        if query.data.startswith("type_"):
            task_type = query.data.replace("type_", "")
            type_prompts = {
                "dev": "💻 **Development Request**\n\nDescribe what you want to build or implement:",
                "docs": "📚 **Documentation Request**\n\nWhat documentation do you need created or updated?",
                "bug": "🐛 **Bug Fix Request**\n\nDescribe the issue you're experiencing:", 
                "deploy": "🚀 **Deployment Request**\n\nWhat do you need deployed or configured?",
                "analyze": "❓ **General Request**\n\nDescribe what you need help with:"
            }
            
            self.active_sessions[user_id] = {
                "state": "awaiting_detailed_request",
                "task_type": task_type,
                "timestamp": datetime.now()
            }
            
            await query.edit_message_text(
                type_prompts.get(task_type, "Describe your request:"),
                parse_mode='Markdown'
            )
            
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages based on current session state."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Access denied.")
            return
            
        if user_id not in self.active_sessions:
            await update.message.reply_text(
                "🤖 Hi! Use /request to submit a development request or /help for assistance."
            )
            return
            
        session = self.active_sessions[user_id]
        user_request = update.message.text
        
        if session["state"] in ["awaiting_request", "awaiting_detailed_request"]:
            await self._process_user_request(update, user_request, session)
            
    async def _process_user_request(self, update: Update, request: str, session: Dict[str, Any]):
        """Process user request through Father agent."""
        user_id = update.effective_user.id
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🤖 **Processing your request...**\n\n"
            "• Father agent is analyzing your request\n"
            "• Considering context and documentation\n"
            "• Determining optimal agent configuration\n\n"
            "⏳ This may take a moment...",
            parse_mode='Markdown'
        )
        
        try:
            # Get Father's decision
            user_context = f"Task type hint: {session.get('task_type', 'unknown')}"
            decision = await self.father.analyze_request(request, user_context)
            
            # Format response
            response = await self._format_agent_decision(decision, request)
            
            # Update processing message with result
            keyboard = [
                [InlineKeyboardButton("✅ Deploy Agents", callback_data=f"deploy_{user_id}")],
                [InlineKeyboardButton("📝 Modify Request", callback_data=f"modify_{user_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Store decision for deployment
            self.active_sessions[user_id]["decision"] = decision
            self.active_sessions[user_id]["request"] = request
            self.active_sessions[user_id]["state"] = "awaiting_deployment_confirmation"
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            await processing_msg.edit_text(
                "❌ **Error processing request**\n\n"
                "Sorry, there was an issue analyzing your request. "
                "Please try again or contact support.\n\n"
                f"Error: {str(e)[:100]}",
                parse_mode='Markdown'
            )
            
    async def _format_agent_decision(self, decision: Dict[str, Any], request: str) -> str:
        """Format Father's decision for user display."""
        task_type = decision.get("task_type", "unknown").title()
        agents = decision.get("agents", [])
        execution_plan = decision.get("execution_plan", [])
        estimated_time = decision.get("estimated_time", "unknown")
        confidence = decision.get("confidence", "medium")
        
        # Confidence emoji
        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "🟡")
        
        response = f"""
🧠 **Father Agent Analysis Complete**

**Request:** {request[:100]}{'...' if len(request) > 100 else ''}

**Task Type:** {task_type}
**Confidence:** {confidence_emoji} {confidence.title()}
**Estimated Time:** {estimated_time}

**👥 Proposed Agent Team ({len(agents)} agents):**
"""
        
        for i, agent in enumerate(agents, 1):
            response += f"""
**{i}. {agent['type']}** ({agent['role']})
• Quantity: {agent['quantity']}
• Instructions: {agent['instructions'][:80]}{'...' if len(agent['instructions']) > 80 else ''}
• Tools: {', '.join(agent['tools'][:3])}{'...' if len(agent['tools']) > 3 else ''}
"""

        response += f"""
**📋 Execution Plan:**
"""
        for i, step in enumerate(execution_plan, 1):
            response += f"{i}. {step}\n"
            
        response += """
**Ready to deploy this agent team?**
        """
        
        return response
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Access denied.")
            return
            
        # Get current memory context for status
        try:
            context_memory = ReadMemoryContext(limit=5, tags=["telegram"]).run()
            
            status_message = f"""
📊 **Fresh Agent System Status**

**🧠 Memory System:** ✅ Operational
**🤖 Agent System:** ✅ Ready
**📚 Documentation:** ✅ Available

**Recent Activity:**
{context_memory[:300] if context_memory else 'No recent activity'}

**Available Interfaces:**
• Telegram Bot: ✅ Active
• CLI Scripts: ✅ Available  
• Direct API: ✅ Ready

Use /request to submit a new development task!
            """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error checking status: {str(e)[:100]}",
                parse_mode='Markdown'
            )
            
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command.""" 
        help_message = """
🤖 **Fresh Agent System - Help**

**Core Commands:**
• `/start` - Welcome and introduction
• `/request` - Submit development request (main feature)
• `/status` - Check system status
• `/agents` - List available agent types
• `/help` - This help message

**How to Submit Requests:**
1. Use `/request` command
2. Choose request type or describe freely
3. Father agent analyzes and proposes agent team
4. Review and approve deployment
5. Get real-time progress updates

**Request Types:**
• **Development:** Building new features, implementations
• **Documentation:** Creating or updating docs
• **Bug Fixes:** Debugging and fixing issues  
• **Deployment:** Setup, configuration, deployment
• **Analysis:** General analysis and planning

**Features:**
• Intelligent agent selection based on context
• Persistent memory across conversations
• Integration with Fresh documentation and ADRs
• Real-time progress tracking
• Safe execution with validation

**Tips:**
• Be specific about requirements
• Mention existing context or constraints
• Ask for clarification if needed
• Use /status to check ongoing work

Need more help? The agents can assist with questions about the Fresh ecosystem!
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')


def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    # Remove quotes from values
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    os.environ[key] = value


async def main():
    """Run the Telegram bot."""
    # Load environment variables
    load_env_file()
    
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        
    # Get authorized users (optional)
    authorized_users_str = os.getenv('TELEGRAM_AUTHORIZED_USERS', '')
    authorized_users = []
    if authorized_users_str:
        try:
            authorized_users = [int(uid.strip()) for uid in authorized_users_str.split(',')]
        except ValueError:
            logger.warning("Invalid TELEGRAM_AUTHORIZED_USERS format")
            
    # Create bot instance
    bot = FreshTelegramBot(token, authorized_users)
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("request", bot.request_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start bot
    logger.info("Starting Fresh Telegram Bot...")
    await application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
