"""Simplified GitHub integration for autonomous PR workflow.

This module provides branch-based pull request creation for the
Mother Agent workflow, integrating with the senior review system.
"""
from __future__ import annotations
import os
import subprocess
import requests
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class BranchInfo:
    """Information about a created branch."""
    name: str
    created: bool
    base_branch: str = "main"
    
    
@dataclass
class PRInfo:
    """Information about a created pull request."""
    number: int
    url: str
    title: str
    branch: str
    created: bool = True


class GitHubPRIntegration:
    """Simplified GitHub integration for autonomous PR creation."""
    
    def __init__(self):
        """Initialize GitHub integration."""
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "")
        
        # Try to detect repository info from git if not in env
        if not self.repo_owner or not self.repo_name:
            self._detect_repo_info()
        
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Fresh-Autonomous-System"
        } if self.token else {}
    
    def _detect_repo_info(self):
        """Detect repository info from git remote."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                url = result.stdout.strip()
                if "github.com" in url:
                    # Extract owner/repo from URL
                    if url.startswith("https://github.com/"):
                        path = url[19:].rstrip('.git')
                    elif url.startswith("git@github.com:"):
                        path = url[15:].rstrip('.git')
                    else:
                        return
                    
                    parts = path.split('/')
                    if len(parts) == 2:
                        self.repo_owner, self.repo_name = parts
                        print(f"🔍 Detected repository: {self.repo_owner}/{self.repo_name}")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
    
    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured."""
        return bool(self.token and self.repo_owner and self.repo_name)
    
    def create_feature_branch(self, task_description: str, agent_type: str) -> BranchInfo:
        """Create a feature branch for agent work.
        
        Args:
            task_description: Description of the task
            agent_type: Type of agent working on this
            
        Returns:
            BranchInfo object with branch details
        """
        # Generate branch name
        timestamp = int(time.time())
        safe_description = "".join(c for c in task_description.lower()[:30] 
                                 if c.isalnum() or c in '-_').rstrip('-_')
        branch_name = f"fresh/{agent_type.lower()}-{safe_description}-{timestamp}"
        
        try:
            # Ensure we're on main and up to date
            subprocess.run(["git", "checkout", "main"], 
                         capture_output=True, timeout=10)
            subprocess.run(["git", "pull", "origin", "main"], 
                         capture_output=True, timeout=30)
            
            # Create and checkout new branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"🌿 Created branch: {branch_name}")
                return BranchInfo(name=branch_name, created=True)
            else:
                print(f"⚠️ Failed to create branch: {result.stderr}")
                return BranchInfo(name=branch_name, created=False)
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            print(f"⚠️ Error creating branch: {e}")
            return BranchInfo(name=branch_name, created=False)
    
    def commit_and_push_changes(
        self, 
        branch_info: BranchInfo,
        files: List[str],
        commit_message: str
    ) -> bool:
        """Commit changes and push to remote branch.
        
        Args:
            branch_info: Branch information
            files: List of files to commit
            commit_message: Commit message
            
        Returns:
            True if successful
        """
        try:
            # Add files
            for file_path in files:
                subprocess.run(["git", "add", file_path], 
                             check=True, timeout=10)
            
            # Check if there are changes to commit
            result = subprocess.run(["git", "diff", "--staged", "--quiet"], 
                                  capture_output=True)
            if result.returncode == 0:
                print("📝 No changes to commit")
                return True
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", commit_message], 
                         check=True, timeout=10)
            
            # Push to remote
            subprocess.run(["git", "push", "-u", "origin", branch_info.name], 
                         check=True, timeout=60)
            
            print(f"📤 Pushed changes to {branch_info.name}")
            return True
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            print(f"⚠️ Error committing/pushing: {e}")
            return False
    
    def create_pull_request(
        self,
        branch_info: BranchInfo,
        title: str,
        body: str,
        reviewer_result: Optional[Dict[str, Any]] = None
    ) -> Optional[PRInfo]:
        """Create a pull request.
        
        Args:
            branch_info: Branch information
            title: PR title
            body: PR description
            reviewer_result: Senior reviewer result
            
        Returns:
            PRInfo object if successful
        """
        if not self.is_configured():
            print("⚠️ GitHub integration not configured")
            return None
        
        # Enhance body with review information
        if reviewer_result:
            body += f"""

## 🔍 Senior Review Results

**Decision**: {reviewer_result.get('review_decision', 'N/A')}
**Confidence**: {reviewer_result.get('review_confidence', 0):.2f}
**Reasoning**: {reviewer_result.get('review_reasoning', 'N/A')}

### Suggestions
{chr(10).join(f"- {s}" for s in reviewer_result.get('review_suggestions', []))}

### Security Assessment
{chr(10).join(f"- {s}" for s in reviewer_result.get('security_concerns', [])) or "No security concerns identified"}

---
*This PR was created by the Fresh autonomous system with senior-level code review.*
"""
        
        try:
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/pulls"
            data = {
                "title": title,
                "body": body,
                "head": branch_info.name,
                "base": "main"
            }
            
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            if response.status_code == 201:
                pr_data = response.json()
                pr_info = PRInfo(
                    number=pr_data["number"],
                    url=pr_data["html_url"],
                    title=title,
                    branch=branch_info.name
                )
                print(f"📋 Created PR #{pr_info.number}: {pr_info.title}")
                print(f"🔗 URL: {pr_info.url}")
                return pr_info
            else:
                print(f"⚠️ Failed to create PR: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"⚠️ Error creating PR: {e}")
            return None
    
    def add_pr_comment(self, pr_number: int, comment: str) -> bool:
        """Add a comment to a pull request.
        
        Args:
            pr_number: PR number
            comment: Comment text
            
        Returns:
            True if successful
        """
        if not self.is_configured():
            return False
        
        try:
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
            data = {"body": comment}
            
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            if response.status_code == 201:
                print(f"💬 Added comment to PR #{pr_number}")
                return True
            else:
                print(f"⚠️ Failed to add comment: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"⚠️ Error adding comment: {e}")
            return False
    
    def cleanup_on_failure(self, branch_info: BranchInfo):
        """Clean up branch if PR creation failed.
        
        Args:
            branch_info: Branch information
        """
        try:
            # Switch back to main
            subprocess.run(["git", "checkout", "main"], 
                         capture_output=True, timeout=10)
            
            # Delete local branch
            subprocess.run(["git", "branch", "-D", branch_info.name], 
                         capture_output=True, timeout=10)
            
            print(f"🧹 Cleaned up failed branch: {branch_info.name}")
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            print(f"⚠️ Could not clean up branch: {branch_info.name}")


def create_github_pr_integration() -> GitHubPRIntegration:
    """Factory function to create GitHub PR integration."""
    return GitHubPRIntegration()
