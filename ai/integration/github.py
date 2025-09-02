"""GitHub integration for automated PR creation from agent work.

This module provides functionality to automatically create pull requests
when agents complete development tasks, including code changes, tests,
and documentation updates.

Cross-references:
    - Agent Spawner: ai/interface/agent_spawner.py for agent completion events
    - Telegram Bot: ai/interface/telegram_bot.py for user notification integration
    - Memory System: ai/memory/README.md for tracking PR status and history
    - Tool Reference: docs/TOOLS.md for GitHub tool availability

Related:
    - GitHub CLI integration for PR creation and management
    - Branch management for agent work isolation
    - Automated commit generation with context and attribution
"""
from __future__ import annotations
import os
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

from ai.utils.settings import TIMEOUT_SECONDS, is_offline

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext
from ai.interface.agent_spawner import SpawnedAgent

logger = logging.getLogger(__name__)


@dataclass
class GitHubPRRequest:
    """Request for creating a GitHub pull request from agent work."""
    pr_id: str
    agent_work: List[SpawnedAgent]
    user_request: str
    branch_name: str
    title: str
    description: str
    changes_summary: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    tests_added: List[str] = field(default_factory=list)
    docs_updated: List[str] = field(default_factory=list)


@dataclass
class PRResult:
    """Result of PR creation attempt."""
    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    branch_name: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class GitHubIntegration:
    """Manages GitHub integration for automated PR creation from agent work."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', 'subtract0')
        self.repo_name = os.getenv('GITHUB_REPO_NAME', 'Fresh')
        self.base_branch = os.getenv('GITHUB_BASE_BRANCH', 'main')
        
    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured."""
        return bool(self.github_token and self.repo_owner and self.repo_name)
        
    async def create_pr_from_agent_work(
        self, 
        spawn_request_id: str,
        user_request: str,
        completed_agents: List[SpawnedAgent]
    ) -> PRResult:
        """Create PR from completed agent work.
        
        Cross-references:
            - Agent Spawner: For completed agent tracking
            - Memory System: For work context and history
            - Documentation Standards: docs/AGENT_DEVELOPMENT.md#documentation-standards
        """
        if is_offline():
            return PRResult(success=False, error_message="Offline mode: skipping PR creation")

        if not self.is_configured():
            error_msg = "GitHub integration not configured. Set GITHUB_TOKEN and repo details."
            logger.warning(error_msg)
            return PRResult(success=False, error_message=error_msg)
            
        try:
            # 1. Analyze agent work and changes
            analysis = await self._analyze_agent_work(completed_agents, user_request)
            
            # 2. Create feature branch
            branch_name = f"agents/{spawn_request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            branch_result = await self._create_feature_branch(branch_name)
            if not branch_result:
                return PRResult(success=False, error_message="Failed to create feature branch")
            
            # 3. Commit agent changes
            commit_result = await self._commit_agent_changes(analysis, completed_agents)
            if not commit_result:
                return PRResult(success=False, error_message="Failed to commit changes")
                
            # 4. Push branch to remote
            push_result = await self._push_branch(branch_name)
            if not push_result:
                return PRResult(success=False, error_message="Failed to push branch")
                
            # 5. Create pull request
            pr_request = GitHubPRRequest(
                pr_id=f"pr_{spawn_request_id}",
                agent_work=completed_agents,
                user_request=user_request,
                branch_name=branch_name,
                title=self._generate_pr_title(user_request, analysis),
                description=self._generate_pr_description(user_request, completed_agents, analysis),
                changes_summary=analysis.get('changes_summary', []),
                files_changed=analysis.get('files_changed', []),
                tests_added=analysis.get('tests_added', []),
                docs_updated=analysis.get('docs_updated', [])
            )
            
            pr_result = await self._create_github_pr(pr_request)
            
            # 6. Record PR creation in memory
            if pr_result.success:
                WriteMemory(
                    content=f"GitHub PR created: #{pr_result.pr_number} - {pr_request.title} - {pr_result.pr_url}",
                    tags=["github", "pr", "automation", spawn_request_id]
                ).run()
                
            return pr_result
            
        except Exception as e:
            error_msg = f"Failed to create PR: {str(e)}"
            logger.error(error_msg)
            return PRResult(success=False, error_message=error_msg)
    
    async def _analyze_agent_work(
        self, 
        completed_agents: List[SpawnedAgent], 
        user_request: str
    ) -> Dict[str, Any]:
        """Analyze completed agent work to understand changes made."""
        analysis = {
            'changes_summary': [],
            'files_changed': [],
            'tests_added': [],
            'docs_updated': [],
            'agent_contributions': []
        }
        
        # Get git status to see what files were changed
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    status, filepath = line[:2], line[3:]
                    analysis['files_changed'].append(filepath)
                    
                    # Categorize changes
                    if '/test' in filepath or filepath.startswith('test') or 'test_' in filepath:
                        analysis['tests_added'].append(filepath)
                    elif filepath.endswith(('.md', '.rst', '.txt')):
                        analysis['docs_updated'].append(filepath)
                        
        except subprocess.CalledProcessError:
            logger.warning("Could not get git status for change analysis")
            
        # Analyze agent contributions from memory
        context = ReadMemoryContext(limit=20, tags=["spawn", "agent"]).run()
        agent_types = [agent.agent_type for agent in completed_agents]
        
        analysis['agent_contributions'] = [
            f"{agent.agent_type}: {agent.role} - {agent.instructions[:100]}..."
            for agent in completed_agents
        ]
        
        # Generate summary based on request type and agents involved
        if any('architect' in agent_type.lower() for agent_type in agent_types):
            analysis['changes_summary'].append("Architecture and design decisions")
        if any('developer' in agent_type.lower() for agent_type in agent_types):
            analysis['changes_summary'].append("Implementation and code changes")
        if any('qa' in agent_type.lower() for agent_type in agent_types):
            analysis['changes_summary'].append("Testing and quality assurance")
        if any('documenter' in agent_type.lower() for agent_type in agent_types):
            analysis['changes_summary'].append("Documentation updates")
            
        return analysis
    
    async def _create_feature_branch(self, branch_name: str) -> bool:
        """Create a new feature branch for agent work."""
        try:
            # Ensure we're on the base branch and up to date
            subprocess.run(['git', 'checkout', self.base_branch], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            subprocess.run(['git', 'pull', 'origin', self.base_branch], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            
            # Create and checkout new branch
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            logger.info(f"Created feature branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False
    
    async def _commit_agent_changes(
        self, 
        analysis: Dict[str, Any], 
        completed_agents: List[SpawnedAgent]
    ) -> bool:
        """Commit all changes made by agents with detailed commit message."""
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            
            # Check if there are actually changes to commit
            result = subprocess.run(['git', 'diff', '--staged', '--quiet'], capture_output=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            if result.returncode == 0:  # No changes staged
                logger.info("No changes to commit")
                return True
            
            # Generate detailed commit message
            commit_msg = self._generate_commit_message(analysis, completed_agents)
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            logger.info("Successfully committed agent changes")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit changes: {e}")
            return False
    
    async def _push_branch(self, branch_name: str) -> bool:
        """Push the feature branch to remote repository."""
        try:
            if is_offline():
                logger.info("Offline mode: skipping git push")
                return False
            subprocess.run(['git', 'push', 'origin', branch_name], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            logger.info(f"Successfully pushed branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push branch {branch_name}: {e}")
            return False
    
    async def _create_github_pr(self, pr_request: GitHubPRRequest) -> PRResult:
        """Create the actual GitHub pull request."""
        try:
            # Use GitHub CLI if available
            if self._is_gh_cli_available():
                return await self._create_pr_with_gh_cli(pr_request)
            else:
                return await self._create_pr_with_api(pr_request)
                
        except Exception as e:
            logger.error(f"Failed to create GitHub PR: {e}")
            return PRResult(success=False, error_message=str(e))
    
    def _is_gh_cli_available(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            subprocess.run(['gh', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def _create_pr_with_gh_cli(self, pr_request: GitHubPRRequest) -> PRResult:
        """Create PR using GitHub CLI."""
        try:
            # Preflight auth to avoid interactive prompts
            try:
                subprocess.run(['gh', 'auth', 'status'], check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            except Exception as e:
                return PRResult(success=False, error_message="GitHub CLI not authenticated: run `gh auth login`.")

            cmd = [
                'gh', 'pr', 'create',
                '--title', pr_request.title,
                '--body', pr_request.description,
                '--base', self.base_branch,
                '--head', pr_request.branch_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
            
            # Parse PR URL from output
            pr_url = result.stdout.strip()
            pr_number = int(pr_url.split('/')[-1]) if pr_url else None
            
            logger.info(f"Created PR #{pr_number}: {pr_url}")
            
            return PRResult(
                success=True,
                pr_number=pr_number,
                pr_url=pr_url,
                branch_name=pr_request.branch_name
            )
            
        except subprocess.CalledProcessError as e:
            error_msg = f"GitHub CLI PR creation failed: {e.stderr if e.stderr else str(e)}"
            logger.error(error_msg)
            return PRResult(success=False, error_message=error_msg)
    
    async def _create_pr_with_api(self, pr_request: GitHubPRRequest) -> PRResult:
        """Create PR using GitHub REST API (fallback).""" 
        try:
            import requests
            
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'title': pr_request.title,
                'body': pr_request.description,
                'head': pr_request.branch_name,
                'base': self.base_branch
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            
            pr_data = response.json()
            pr_number = pr_data['number']
            pr_url = pr_data['html_url']
            
            logger.info(f"Created PR #{pr_number}: {pr_url}")
            
            return PRResult(
                success=True,
                pr_number=pr_number,
                pr_url=pr_url,
                branch_name=pr_request.branch_name
            )
            
        except Exception as e:
            error_msg = f"GitHub API PR creation failed: {str(e)}"
            logger.error(error_msg)
            return PRResult(success=False, error_message=error_msg)
    
    def _generate_pr_title(self, user_request: str, analysis: Dict[str, Any]) -> str:
        """Generate a descriptive PR title based on user request and analysis."""
        # Truncate user request for title
        clean_request = user_request[:60].strip()
        if len(user_request) > 60:
            clean_request += "..."
            
        # Add type prefix based on changes
        type_prefix = "feat"
        if analysis.get('tests_added'):
            type_prefix = "test"
        elif analysis.get('docs_updated') and not analysis.get('files_changed'):
            type_prefix = "docs"
        elif any('fix' in change.lower() or 'bug' in change.lower() 
                 for change in analysis.get('changes_summary', [])):
            type_prefix = "fix"
            
        return f"{type_prefix}: {clean_request}"
    
    def _generate_pr_description(
        self,
        user_request: str,
        completed_agents: List[SpawnedAgent], 
        analysis: Dict[str, Any]
    ) -> str:
        """Generate comprehensive PR description with agent attribution."""
        description = f"""# Agent-Generated Implementation

**Original Request**: {user_request}

## 🤖 Agent Team

This PR was created by the Fresh agent system with the following specialized agents:

"""
        
        for agent in completed_agents:
            description += f"""### {agent.agent_type} ({agent.role})
- **Instructions**: {agent.instructions}
- **Tools Used**: {', '.join(agent.tools)}
- **Spawn Time**: {agent.spawn_time.strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        description += f"""## 📋 Changes Summary

"""
        
        for change in analysis.get('changes_summary', []):
            description += f"- {change}\n"
            
        if analysis.get('files_changed'):
            description += f"""
## 📁 Files Modified

"""
            for file_path in analysis['files_changed'][:20]:  # Limit to prevent huge PRs
                description += f"- `{file_path}`\n"
                
        if analysis.get('tests_added'):
            description += f"""
## ✅ Tests Added

"""
            for test_file in analysis['tests_added']:
                description += f"- `{test_file}`\n"
                
        if analysis.get('docs_updated'):
            description += f"""
## 📚 Documentation Updated

"""
            for doc_file in analysis['docs_updated']:
                description += f"- `{doc_file}`\n"
                
        description += f"""
## 🧠 Agent Memory Context

This work was coordinated through the Fresh persistent memory system, ensuring:
- Context preservation across agent handoffs
- Adherence to project documentation standards
- Integration with existing ADR decisions
- Cross-referenced documentation updates

## 🔗 Related Documentation

- [Agent Development Guide](docs/AGENT_DEVELOPMENT.md)
- [Fresh Documentation Hub](docs/INDEX.md)
- [GitHub Integration](ai/integration/github.py)

---

*This PR was automatically generated by the Fresh agent system. Review and merge when ready.*
        """
        
        return description.strip()
    
    def _generate_commit_message(
        self,
        analysis: Dict[str, Any],
        completed_agents: List[SpawnedAgent]
    ) -> str:
        """Generate detailed commit message with agent attribution."""
        agent_types = [agent.agent_type.lower() for agent in completed_agents]
        
        # Determine commit type
        if any('architect' in t for t in agent_types):
            commit_type = "feat"
        elif any('qa' in t or 'test' in t for t in agent_types):
            commit_type = "test"
        elif any('doc' in t for t in agent_types):
            commit_type = "docs"
        elif any('fix' in t or 'debug' in t for t in agent_types):
            commit_type = "fix"
        else:
            commit_type = "feat"
            
        # Create commit message
        summary = f"{commit_type}: agent-generated implementation"
        
        # Add detailed body
        body = f"""
Agent team implementation:
"""
        
        for agent in completed_agents:
            body += f"- {agent.agent_type}: {agent.role}\n"
            
        if analysis.get('changes_summary'):
            body += f"\nChanges:\n"
            for change in analysis['changes_summary']:
                body += f"- {change}\n"
                
        if analysis.get('files_changed'):
            body += f"\nFiles modified: {len(analysis['files_changed'])} files\n"
            
        body += f"\nGenerated by Fresh agent system with persistent memory coordination."
        
        return f"{summary}\n{body.strip()}"


# Global GitHub integration instance
_github_integration: Optional[GitHubIntegration] = None

def get_github_integration() -> GitHubIntegration:
    """Get the global GitHub integration instance."""
    global _github_integration
    if _github_integration is None:
        _github_integration = GitHubIntegration()
    return _github_integration
