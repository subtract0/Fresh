#!/usr/bin/env python3
"""Fresh Agent System Comprehensive Launcher.

This script launches the complete Fresh agent system with all integrated
components including real-time execution, status coordination, GitHub
integration, performance analytics, and Telegram bot interface.

Cross-references:
    - System Coordinator: ai/system/coordinator.py for system management
    - Agent Spawner: ai/interface/agent_spawner.py for agent lifecycle
    - Telegram Bot: ai/interface/telegram_bot.py for user interface
    - Execution Monitor: ai/execution/monitor.py for real-time execution
    - Performance Analytics: ai/analytics/performance.py for optimization

Usage:
    python launch_agent_system.py [--config CONFIG_FILE] [--debug] [--status]
"""
import asyncio
import argparse
import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or environment."""
    # Derive some env flags
    env_text = ""
    try:
        if Path(".env").exists():
            env_text = Path(".env").read_text()
    except Exception:
        env_text = ""
    
    def env_has(key: str) -> bool:
        return key in env_text
    
    def env_bool(name: str, default: bool) -> bool:
        import os
        val = os.getenv(name)
        if val is None:
            return default
        return str(val).lower() not in ("0", "false", "no")
    
    def env_int(name: str, default: int) -> int:
        import os
        try:
            return int(os.getenv(name, str(default)))
        except Exception:
            return default
    
    config = {
        "system": {
            "health_check_interval": 30,
            "startup_timeout": 120
        },
        "telegram": {
            "enabled": env_has("TELEGRAM_BOT_TOKEN"),
            "authorized_users": []
        },
        "github": {
            "enabled": env_has("GITHUB_TOKEN"),
            "auto_pr": True
        },
        "execution": {
            "timeout_minutes": 30,
            "max_concurrent_batches": 5
        },
        "analytics": {
            "enabled": True,
            "retention_days": 90
        },
        "documentation": {
            "enabled": env_bool("DOCS_CHECK_ENABLED", True),
            "interval_sec": env_int("DOCS_CHECK_INTERVAL_SEC", 600)
        }
    }
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Merge configurations
                for key, value in file_config.items():
                    if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                        config[key].update(value)
                    else:
                        config[key] = value
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            
    return config


def setup_environment():
    """Setup environment and check dependencies."""
    logger.info("Setting up environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
        
    # Check for required directories
    required_dirs = [
        "ai/memory",
        "ai/tools", 
        "ai/interface",
        "ai/agents",
        ".fresh"
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
    # Check for .env file
    env_path = Path(".env")
    if not env_path.exists():
        logger.warning(".env file not found - some features may not be available")
        logger.info("Create .env with TELEGRAM_BOT_TOKEN and GITHUB_TOKEN for full functionality")
    else:
        logger.info("Environment configuration found")
        
    logger.info("Environment setup completed")


async def run_system_status():
    """Display current system status and exit."""
    try:
        from ai.system.coordinator import get_status
        
        status = await get_status()
        
        print("\n=== Fresh Agent System Status ===")
        print(f"Overall Health: {status.overall_health.upper()}")
        print(f"Uptime: {status.uptime_seconds:.1f} seconds")
        print(f"Active Agents: {status.active_agents}")
        print(f"Active Executions: {status.active_executions}")
        
        print(f"\nComponents ({len(status.components)}):")
        for name, component_status in status.components.items():
            print(f"  {name}: {component_status}")
            
        if status.recent_errors:
            print(f"\nRecent Errors ({len(status.recent_errors)}):")
            for error in status.recent_errors[-5:]:
                print(f"  {error}")
        else:
            print("\nNo recent errors")
            
        print(f"\nPerformance Metrics:")
        for key, value in status.performance_metrics.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        print("System appears to be offline or not initialized")
        sys.exit(1)


async def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description='Fresh Agent System Launcher')
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    parser.add_argument('--status', '-s', action='store_true', help='Show system status and exit')
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
        
    # Show status and exit if requested
    if args.status:
        await run_system_status()
        return
        
    # Setup environment
    setup_environment()
    
    # Load configuration
    config = load_config(args.config)
    logger.info(f"Configuration loaded: {len(config)} sections")
    
    # Import and initialize system
    try:
        from ai.system.coordinator import initialize_system, shutdown_system, get_system
        
        logger.info("Starting Fresh Agent System initialization...")
        
        # Initialize the complete system
        success = await initialize_system(config)
        
        if not success:
            logger.error("System initialization failed")
            sys.exit(1)
            
        logger.info("Fresh Agent System is now running!")
        
        # Print system information
        system = get_system()
        status = await system.get_system_status()
        
        print("\n" + "="*60)
        print("🤖 Fresh Agent System - Fully Operational")
        print("="*60)
        print(f"System Health: {status.overall_health.upper()}")
        print(f"Components Running: {len([c for c in status.components.values() if c == 'running'])}/{len(status.components)}")
        
        if "telegram_bot" in status.components and status.components["telegram_bot"] == "running":
            print("📱 Telegram Bot: ACTIVE - Ready for user requests")
        else:
            print("📱 Telegram Bot: OFFLINE")
            
        if "execution_monitor" in status.components and status.components["execution_monitor"] == "running":
            print("⚡ Execution Monitor: ACTIVE - Real-time agent execution")
        else:
            print("⚡ Execution Monitor: OFFLINE")
            
        if "github_integration" in status.components and status.components["github_integration"] == "running":
            print("🔄 GitHub Integration: ACTIVE - Automated PR creation")
        else:
            print("🔄 GitHub Integration: OFFLINE")
            
        if "performance_analytics" in status.components and status.components["performance_analytics"] == "running":
            print("📊 Performance Analytics: ACTIVE - Optimization tracking")
        else:
            print("📊 Performance Analytics: OFFLINE")
            
        print("="*60)
        print("\nSystem Features:")
        print("• Intelligent agent spawning via Father agent")
        print("• Real-time execution monitoring and coordination")
        print("• Automatic GitHub PR creation for development tasks")  
        print("• User interaction via Telegram bot interface")
        print("• Performance tracking and optimization")
        print("• Persistent memory system for context sharing")
        print("\nPress Ctrl+C to gracefully shutdown the system")
        print("="*60)
        
        # Keep the system running
        try:
            # Wait for shutdown signal
            while True:
                await asyncio.sleep(60)
                
                # Periodic health check
                current_status = await system.get_system_status()
                if current_status.overall_health == "critical":
                    logger.error("System health is critical, initiating shutdown...")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Shutdown signal received (Ctrl+C)")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        finally:
            # Graceful shutdown
            logger.info("Initiating graceful system shutdown...")
            await shutdown_system()
            logger.info("Fresh Agent System shutdown completed")
            
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please ensure all dependencies are installed")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"System startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
