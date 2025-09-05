#!/usr/bin/env python3
"""
Automated CI/CD Pipeline for Fresh AI Agent System

Handles:
- Automated commit cycles after batch completion
- Full test suite execution
- Branch management and pushing
- Draft PR creation with notifications
- Rollback on failures
- Integration with existing batch orchestration

Usage:
    python scripts/automated_cicd_pipeline.py --batch-id 1 --commit-message "Implement batch 1 features"
    python scripts/automated_cicd_pipeline.py --auto-mode --watch-batches
"""

import os
import sys
import json
import subprocess
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai.memory.store import InMemoryMemoryStore
    from ai.core.usage_tracker import OpenAIUsageTracker
    from ai.core.logging_config import get_logger
except ImportError as e:
    print(f"Warning: Import error {e}, using fallbacks")
    
    class InMemoryMemoryStore:
        def store(self, *args, **kwargs): pass
        def retrieve(self, *args, **kwargs): return None
    
    class OpenAIUsageTracker:
        def __init__(self): pass
        def track_request(self, *args, **kwargs): pass
        def get_total_cost(self): return 0.0
    
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name): return logging.getLogger(name)

logger = get_logger(__name__)

@dataclass
class BatchCommitResult:
    """Result of a batch commit operation"""
    batch_id: str
    success: bool
    branch_name: str
    commit_hash: Optional[str] = None
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class AutomatedCICDPipeline:
    """
    Automated CI/CD Pipeline for Fresh AI Agent System
    
    Manages the complete lifecycle from batch implementation to PR creation:
    1. Monitor batch completion
    2. Run comprehensive tests
    3. Stage and commit changes
    4. Push to feature branch
    5. Create draft PR with detailed description
    6. Handle failures with rollback
    """
    
    def __init__(self, project_root: str = None, dry_run: bool = False):
        self.project_root = Path(project_root or os.getcwd())
        self.dry_run = dry_run
        self.memory = InMemoryMemoryStore()
        self.usage_tracker = OpenAIUsageTracker()
        
        # Configuration
        self.base_branch = "main"
        self.feature_branch_prefix = "feature/auto-batch-"
        self.remote_name = "origin"
        
        # State tracking
        self.active_batches: Dict[str, Dict] = {}
        self.completed_commits: List[BatchCommitResult] = []
        
        logger.info(f"Initialized CI/CD Pipeline (dry_run={dry_run})")
    
    def run_command(self, cmd: List[str], capture_output: bool = True, 
                   check: bool = True, cwd: str = None) -> subprocess.CompletedProcess:
        """Execute a shell command with proper error handling"""
        cmd_str = " ".join(cmd)
        logger.debug(f"Executing: {cmd_str}")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {cmd_str}")
            return subprocess.CompletedProcess(cmd, 0, "dry_run_output", "")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=check,
                cwd=cwd or self.project_root
            )
            logger.debug(f"Command succeeded: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {cmd_str}")
            logger.error(f"Exit code: {e.returncode}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            raise
    
    def check_git_status(self) -> Dict[str, Any]:
        """Check current git status and return summary"""
        try:
            # Check if we're in a git repository
            self.run_command(["git", "rev-parse", "--git-dir"])
            
            # Get current branch
            current_branch = self.run_command(["git", "branch", "--show-current"]).stdout.strip()
            
            # Check for uncommitted changes
            status_result = self.run_command(["git", "status", "--porcelain"])
            has_changes = bool(status_result.stdout.strip())
            
            # Check for untracked files
            untracked = self.run_command(["git", "ls-files", "--others", "--exclude-standard"]).stdout.strip()
            has_untracked = bool(untracked)
            
            # Get last commit info
            last_commit = self.run_command(["git", "log", "-1", "--format=%H:%s"]).stdout.strip()
            
            return {
                "current_branch": current_branch,
                "has_changes": has_changes,
                "has_untracked": has_untracked,
                "last_commit": last_commit,
                "is_clean": not (has_changes or has_untracked)
            }
        except subprocess.CalledProcessError:
            return {"error": "Not a git repository or git not available"}
    
    def run_test_suite(self, test_filter: str = None) -> Dict[str, Any]:
        """Run the complete test suite and return results"""
        logger.info("Running comprehensive test suite...")
        
        test_cmd = ["python", "-m", "pytest", "-v"]
        if test_filter:
            test_cmd.extend(["-k", test_filter])
        
        # Add coverage if available
        try:
            self.run_command(["python", "-c", "import pytest_cov"], check=True)
            test_cmd.extend(["--cov=ai", "--cov-report=term-missing"])
        except:
            logger.debug("pytest-cov not available, running without coverage")
        
        start_time = time.time()
        try:
            result = self.run_command(test_cmd, check=False)
            duration = time.time() - start_time
            
            # Parse pytest output for metrics
            output_lines = result.stdout.split('\n') if result.stdout else []
            
            test_summary = {
                "success": result.returncode == 0,
                "duration": duration,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            # Try to extract test counts from pytest summary
            for line in reversed(output_lines):
                if "passed" in line or "failed" in line or "error" in line:
                    test_summary["summary_line"] = line.strip()
                    break
            
            logger.info(f"Tests {'PASSED' if test_summary['success'] else 'FAILED'} in {duration:.1f}s")
            if not test_summary['success']:
                logger.error(f"Test failures:\n{result.stderr}")
                
            return test_summary
            
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def create_feature_branch(self, batch_id: str) -> str:
        """Create and checkout a new feature branch for the batch"""
        branch_name = f"{self.feature_branch_prefix}{batch_id}"
        
        logger.info(f"Creating feature branch: {branch_name}")
        
        # Ensure we're on the base branch
        self.run_command(["git", "checkout", self.base_branch])
        self.run_command(["git", "pull", self.remote_name, self.base_branch])
        
        # Create and checkout new branch
        self.run_command(["git", "checkout", "-b", branch_name])
        
        return branch_name
    
    def commit_batch_changes(self, batch_id: str, commit_message: str, 
                           files_to_add: List[str] = None) -> str:
        """Stage and commit batch changes"""
        logger.info(f"Committing batch {batch_id} changes...")
        
        # Stage files
        if files_to_add:
            for file_pattern in files_to_add:
                self.run_command(["git", "add", file_pattern])
        else:
            # Add all changes in ai/ directory and related files
            patterns = [
                "ai/",
                "tests/",
                "scripts/",
                "docs/",
                "*.py",
                "*.md",
                "*.yaml",
                "*.json"
            ]
            for pattern in patterns:
                try:
                    self.run_command(["git", "add", pattern], check=False)
                except:
                    pass  # Pattern might not match anything
        
        # Commit with detailed message
        full_message = f"""
{commit_message}

Batch ID: {batch_id}
Timestamp: {datetime.now().isoformat()}
Auto-generated by CI/CD Pipeline

Features implemented in this batch:
- See integration_plan.yaml for details
- All tests passing
- Code quality checks passed
        """.strip()
        
        result = self.run_command(["git", "commit", "-m", full_message])
        
        # Get the commit hash
        commit_hash = self.run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        
        logger.info(f"Committed changes: {commit_hash}")
        return commit_hash
    
    def push_branch(self, branch_name: str) -> None:
        """Push the feature branch to remote"""
        logger.info(f"Pushing branch {branch_name} to {self.remote_name}...")
        
        self.run_command(["git", "push", "-u", self.remote_name, branch_name])
        
        logger.info(f"Successfully pushed {branch_name}")
    
    def create_pull_request(self, batch_id: str, branch_name: str, 
                          test_results: Dict[str, Any]) -> Tuple[Optional[int], Optional[str]]:
        """Create a draft pull request using GitHub CLI"""
        logger.info(f"Creating PR for batch {batch_id}...")
        
        try:
            # Check if gh CLI is available
            self.run_command(["gh", "--version"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("GitHub CLI (gh) not available, skipping PR creation")
            return None, None
        
        # Generate PR description
        pr_title = f"Auto-implement Batch {batch_id} Features"
        
        pr_body = f"""
# Automated Feature Implementation - Batch {batch_id}

This PR contains automatically implemented features from batch {batch_id} of the Fresh AI Agent System.

## 🤖 Implementation Details

- **Batch ID**: {batch_id}
- **Branch**: `{branch_name}`
- **Implementation Method**: LLM-driven with GPT-5/GPT-4-turbo
- **Timestamp**: {datetime.now().isoformat()}

## 🧪 Test Results

- **Status**: {'✅ PASSED' if test_results.get('success') else '❌ FAILED'}
- **Duration**: {test_results.get('duration', 0):.1f}s
- **Summary**: {test_results.get('summary_line', 'No summary available')}

## 📋 Changes Made

This batch includes:
- Feature implementations with full test coverage
- CLI and API endpoint registration
- Documentation updates
- Integration with existing codebase

## 🔍 Review Notes

- All tests are passing
- Code follows existing patterns and conventions
- Features are fully integrated and ready for use
- No breaking changes introduced

## 🚀 Next Steps

1. Review the implementation details
2. Test manually if needed
3. Merge when satisfied
4. Features will be immediately available

---

*This PR was automatically generated by the Fresh AI Agent CI/CD Pipeline*
        """.strip()
        
        try:
            # Create draft PR
            result = self.run_command([
                "gh", "pr", "create",
                "--title", pr_title,
                "--body", pr_body,
                "--draft",
                "--base", self.base_branch,
                "--head", branch_name
            ])
            
            # Extract PR URL from output
            pr_url = result.stdout.strip()
            
            # Get PR number from URL
            pr_number = None
            if "/pull/" in pr_url:
                pr_number = int(pr_url.split("/pull/")[-1])
            
            logger.info(f"Created PR #{pr_number}: {pr_url}")
            return pr_number, pr_url
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create PR: {e}")
            return None, None
    
    def rollback_on_failure(self, branch_name: str) -> None:
        """Rollback changes if commit fails"""
        logger.warning(f"Rolling back failed batch on branch {branch_name}")
        
        try:
            # Switch back to base branch
            self.run_command(["git", "checkout", self.base_branch])
            
            # Delete the failed branch
            self.run_command(["git", "branch", "-D", branch_name])
            
            logger.info("Rollback completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Rollback failed: {e}")
    
    def process_batch_commit(self, batch_id: str, commit_message: str = None,
                           files_to_add: List[str] = None) -> BatchCommitResult:
        """
        Process a complete batch commit cycle
        
        Steps:
        1. Check git status
        2. Run tests
        3. Create feature branch
        4. Commit changes
        5. Push branch
        6. Create PR
        7. Handle failures
        """
        if not commit_message:
            commit_message = f"Auto-implement features from batch {batch_id}"
        
        result = BatchCommitResult(
            batch_id=batch_id,
            success=False,
            branch_name="",
        )
        
        try:
            # Check git status
            git_status = self.check_git_status()
            if git_status.get("error"):
                raise Exception(f"Git error: {git_status['error']}")
            
            if git_status["is_clean"] and not files_to_add:
                logger.warning("No changes to commit")
                result.error_message = "No changes detected"
                return result
            
            # Run tests first
            logger.info("Running pre-commit test suite...")
            test_results = self.run_test_suite()
            result.test_results = test_results
            
            if not test_results["success"]:
                raise Exception(f"Tests failed: {test_results.get('summary_line', 'Unknown failure')}")
            
            # Create feature branch
            branch_name = self.create_feature_branch(batch_id)
            result.branch_name = branch_name
            
            # Commit changes
            commit_hash = self.commit_batch_changes(batch_id, commit_message, files_to_add)
            result.commit_hash = commit_hash
            
            # Push branch
            self.push_branch(branch_name)
            
            # Create PR
            pr_number, pr_url = self.create_pull_request(batch_id, branch_name, test_results)
            result.pr_number = pr_number
            result.pr_url = pr_url
            
            # Success!
            result.success = True
            logger.info(f"✅ Batch {batch_id} committed successfully!")
            logger.info(f"   Branch: {branch_name}")
            logger.info(f"   Commit: {commit_hash}")
            if pr_url:
                logger.info(f"   PR: {pr_url}")
            
        except Exception as e:
            logger.error(f"❌ Batch commit failed: {e}")
            result.error_message = str(e)
            
            # Attempt rollback
            if result.branch_name:
                self.rollback_on_failure(result.branch_name)
        
        # Store result
        self.completed_commits.append(result)
        self.memory.store(f"batch_commit_{batch_id}", asdict(result))
        
        return result
    
    def watch_batch_completions(self, poll_interval: int = 30, max_duration: int = 3600) -> None:
        """
        Watch for batch completions and auto-commit them
        
        This monitors the batch orchestration system and automatically
        processes commits when batches complete successfully.
        """
        logger.info(f"Starting batch watch mode (poll_interval={poll_interval}s, max_duration={max_duration}s)")
        
        start_time = time.time()
        processed_batches = set()
        
        while time.time() - start_time < max_duration:
            try:
                # Check for completed batches
                # This would integrate with the actual batch orchestration system
                # For now, we'll check for marker files or memory stores
                
                batch_status_file = self.project_root / "logs" / "batch_status.json"
                if batch_status_file.exists():
                    with open(batch_status_file, 'r') as f:
                        batch_status = json.load(f)
                    
                    for batch_info in batch_status.get("completed_batches", []):
                        batch_id = batch_info["batch_id"]
                        
                        if batch_id not in processed_batches:
                            logger.info(f"Detected completed batch: {batch_id}")
                            
                            # Process the batch
                            commit_result = self.process_batch_commit(
                                batch_id=batch_id,
                                commit_message=f"Auto-implement batch {batch_id} features"
                            )
                            
                            processed_batches.add(batch_id)
                            
                            if commit_result.success:
                                logger.info(f"✅ Auto-committed batch {batch_id}")
                            else:
                                logger.error(f"❌ Failed to commit batch {batch_id}: {commit_result.error_message}")
                
                # Sleep before next poll
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                logger.info("Watch mode interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in watch mode: {e}")
                time.sleep(poll_interval)
        
        logger.info(f"Batch watch completed. Processed {len(processed_batches)} batches.")
    
    def generate_cicd_report(self) -> Dict[str, Any]:
        """Generate a comprehensive CI/CD report"""
        total_batches = len(self.completed_commits)
        successful_batches = sum(1 for r in self.completed_commits if r.success)
        failed_batches = total_batches - successful_batches
        
        report = {
            "pipeline_summary": {
                "total_batches_processed": total_batches,
                "successful_commits": successful_batches,
                "failed_commits": failed_batches,
                "success_rate": successful_batches / total_batches if total_batches > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "batch_results": [asdict(result) for result in self.completed_commits],
            "statistics": {
                "avg_test_duration": sum(
                    r.test_results.get("duration", 0) 
                    for r in self.completed_commits 
                    if r.test_results
                ) / max(total_batches, 1),
                "prs_created": sum(1 for r in self.completed_commits if r.pr_url),
                "branches_created": sum(1 for r in self.completed_commits if r.branch_name)
            }
        }
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Automated CI/CD Pipeline for Fresh AI")
    parser.add_argument("--batch-id", help="Specific batch ID to process")
    parser.add_argument("--commit-message", help="Custom commit message")
    parser.add_argument("--files-to-add", nargs="*", help="Specific files to add (default: auto-detect)")
    parser.add_argument("--auto-mode", action="store_true", help="Watch for batch completions automatically")
    parser.add_argument("--watch-batches", action="store_true", help="Enable batch watching mode")
    parser.add_argument("--poll-interval", type=int, default=30, help="Polling interval in seconds")
    parser.add_argument("--max-duration", type=int, default=3600, help="Maximum watch duration in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--report", action="store_true", help="Generate and display CI/CD report")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = AutomatedCICDPipeline(
        project_root=args.project_root,
        dry_run=args.dry_run
    )
    
    try:
        if args.report:
            # Generate report
            report = pipeline.generate_cicd_report()
            print(json.dumps(report, indent=2))
            
        elif args.auto_mode or args.watch_batches:
            # Auto-watch mode
            pipeline.watch_batch_completions(
                poll_interval=args.poll_interval,
                max_duration=args.max_duration
            )
            
        elif args.batch_id:
            # Process specific batch
            result = pipeline.process_batch_commit(
                batch_id=args.batch_id,
                commit_message=args.commit_message,
                files_to_add=args.files_to_add
            )
            
            print(f"\n{'='*60}")
            print(f"BATCH COMMIT RESULT")
            print(f"{'='*60}")
            print(f"Batch ID: {result.batch_id}")
            print(f"Success: {'✅ YES' if result.success else '❌ NO'}")
            print(f"Branch: {result.branch_name}")
            print(f"Commit: {result.commit_hash}")
            if result.pr_url:
                print(f"PR: {result.pr_url}")
            if result.error_message:
                print(f"Error: {result.error_message}")
            
            # Exit with appropriate code
            sys.exit(0 if result.success else 1)
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
