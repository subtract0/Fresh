"""
Safety Controller for Autonomous Loop
Ensures all autonomous operations are safe and reversible.
"""

import os
import time
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

from ai.memory.intelligent_store import IntelligentMemoryStore


@dataclass
class SafetyCheckpoint:
    """Represents a safety checkpoint for rollback."""
    id: str
    timestamp: datetime
    git_commit: str
    description: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "git_commit": self.git_commit,
            "description": self.description,
            "metadata": self.metadata
        }


@dataclass
class SafetyViolation:
    """Represents a safety violation or concern."""
    level: str  # "warning", "error", "critical"
    type: str   # "destructive_change", "large_change", "untested_change", etc.
    message: str
    details: Dict[str, Any]


class SafetyController:
    """
    Ensures all autonomous operations are safe and reversible.
    Implements comprehensive safety checks and rollback mechanisms.
    """
    
    def __init__(self, working_directory: str, memory_store: Optional[IntelligentMemoryStore] = None):
        self.working_directory = Path(working_directory)
        self.memory_store = memory_store or IntelligentMemoryStore()
        
        # Safety configuration
        self.config = {
            "max_change_size": 100,  # Maximum lines changed per operation
            "require_tests": True,   # Require tests to pass before changes
            "rollback_threshold": 0.95,  # Success rate threshold
            "max_operations_per_hour": 10,  # Rate limiting
            "emergency_stop_file": self.working_directory / ".emergency_stop"
        }
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Track checkpoints and operations
        self.checkpoints: List[SafetyCheckpoint] = []
        self.operation_history: List[Dict[str, Any]] = []
        
        # Emergency stop flag
        self._emergency_stopped = False
        
    def validate_safety(self, proposed_changes: Dict[str, Any]) -> Tuple[bool, List[SafetyViolation]]:
        """
        Comprehensive safety validation for proposed changes.
        
        Returns:
            Tuple of (is_safe, violations_list)
        """
        violations = []
        
        # Check for emergency stop
        if self.is_emergency_stopped():
            violations.append(SafetyViolation(
                level="critical",
                type="emergency_stop",
                message="Emergency stop is active",
                details={}
            ))
            return False, violations
        
        # Validate change size
        size_violations = self._validate_change_size(proposed_changes)
        violations.extend(size_violations)
        
        # Check for destructive changes
        destructive_violations = self._validate_destructive_changes(proposed_changes)
        violations.extend(destructive_violations)
        
        # Validate test requirements
        test_violations = self._validate_test_requirements(proposed_changes)
        violations.extend(test_violations)
        
        # Check rate limiting
        rate_violations = self._validate_rate_limits()
        violations.extend(rate_violations)
        
        # Check repository state
        repo_violations = self._validate_repository_state()
        violations.extend(repo_violations)
        
        # Determine overall safety
        critical_violations = [v for v in violations if v.level == "critical"]
        error_violations = [v for v in violations if v.level == "error"]
        
        is_safe = len(critical_violations) == 0 and len(error_violations) == 0
        
        return is_safe, violations
    
    def create_checkpoint(self, description: str, metadata: Optional[Dict[str, Any]] = None) -> SafetyCheckpoint:
        """
        Create a safety checkpoint for potential rollback.
        """
        metadata = metadata or {}
        
        # Get current git commit
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                check=True
            )
            git_commit = result.stdout.strip()
        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to get current git commit")
        
        # Create checkpoint
        checkpoint_id = hashlib.md5(f"{git_commit}_{time.time()}".encode()).hexdigest()[:8]
        checkpoint = SafetyCheckpoint(
            id=checkpoint_id,
            timestamp=datetime.now(),
            git_commit=git_commit,
            description=description,
            metadata=metadata
        )
        
        self.checkpoints.append(checkpoint)
        
        # Store in memory for persistence
        try:
            self.memory_store.write(
                content=f"Safety checkpoint created: {description}",
                tags=["safety", "checkpoint", checkpoint_id]
            )
        except:
            self.logger.warning("Failed to store checkpoint in memory")
        
        self.logger.info(f"Created safety checkpoint: {checkpoint_id} - {description}")
        return checkpoint
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Rollback to a specific checkpoint.
        """
        # Find checkpoint
        checkpoint = None
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                checkpoint = cp
                break
        
        if not checkpoint:
            self.logger.error(f"Checkpoint not found: {checkpoint_id}")
            return False
        
        try:
            # Reset to checkpoint commit
            subprocess.run(
                ["git", "reset", "--hard", checkpoint.git_commit],
                cwd=self.working_directory,
                check=True,
                capture_output=True
            )
            
            # Clean untracked files
            subprocess.run(
                ["git", "clean", "-fd"],
                cwd=self.working_directory,
                check=True,
                capture_output=True
            )
            
            # Record rollback
            self.operation_history.append({
                "type": "rollback",
                "timestamp": datetime.now().isoformat(),
                "checkpoint_id": checkpoint_id,
                "success": True
            })
            
            self.logger.info(f"Successfully rolled back to checkpoint: {checkpoint_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def monitor_health(self) -> Dict[str, Any]:
        """
        Monitor system health and return status.
        """
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "emergency_stopped": self.is_emergency_stopped(),
            "checkpoints_count": len(self.checkpoints),
            "operations_last_hour": self._count_recent_operations(),
            "repository_clean": self._is_repository_clean(),
            "disk_space": self._check_disk_space(),
            "memory_usage": self._check_memory_usage()
        }
        
        return health_status
    
    def emergency_stop(self, reason: str = "Manual emergency stop"):
        """
        Activate emergency stop to halt all autonomous operations.
        """
        self._emergency_stopped = True
        
        # Create emergency stop file
        emergency_file = self.config["emergency_stop_file"]
        with open(emergency_file, 'w') as f:
            json.dump({
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "active": True
            }, f, indent=2)
        
        self.logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")
        
        # Record in memory
        try:
            self.memory_store.write(
                content=f"Emergency stop activated: {reason}",
                tags=["safety", "emergency_stop", "critical"]
            )
        except:
            pass
    
    def clear_emergency_stop(self, reason: str = "Manual clear"):
        """
        Clear emergency stop and resume operations.
        """
        self._emergency_stopped = False
        
        # Remove emergency stop file
        emergency_file = self.config["emergency_stop_file"]
        if emergency_file.exists():
            emergency_file.unlink()
        
        self.logger.info(f"Emergency stop cleared: {reason}")
        
        # Record in memory
        try:
            self.memory_store.write(
                content=f"Emergency stop cleared: {reason}",
                tags=["safety", "emergency_clear"]
            )
        except:
            pass
    
    def is_emergency_stopped(self) -> bool:
        """
        Check if emergency stop is active.
        """
        emergency_file = self.config["emergency_stop_file"]
        if emergency_file.exists():
            try:
                with open(emergency_file) as f:
                    data = json.load(f)
                    return data.get("active", False)
            except:
                return True  # Assume stopped if file exists but can't be read
        
        return self._emergency_stopped
    
    def _validate_change_size(self, proposed_changes: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate that proposed changes don't exceed size limits."""
        violations = []
        
        max_size = self.config["max_change_size"]
        
        # Count total lines changed
        total_lines = 0
        if "files_changed" in proposed_changes:
            for file_change in proposed_changes["files_changed"]:
                if isinstance(file_change, dict):
                    lines = file_change.get("lines_changed", 0)
                    total_lines += lines
        
        if total_lines > max_size:
            violations.append(SafetyViolation(
                level="error",
                type="large_change",
                message=f"Change size ({total_lines} lines) exceeds limit ({max_size})",
                details={"lines_changed": total_lines, "limit": max_size}
            ))
        
        return violations
    
    def _validate_destructive_changes(self, proposed_changes: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for potentially destructive changes."""
        violations = []
        
        # Check for file deletions
        if "deleted_files" in proposed_changes:
            deleted_files = proposed_changes["deleted_files"]
            if deleted_files:
                violations.append(SafetyViolation(
                    level="critical",
                    type="destructive_change",
                    message=f"Attempting to delete {len(deleted_files)} files",
                    details={"deleted_files": deleted_files}
                ))
        
        # Check for changes to critical files
        critical_patterns = [
            ".git/",
            "pyproject.toml",
            "package.json",
            "Dockerfile",
            ".env"
        ]
        
        if "files_changed" in proposed_changes:
            for file_path in proposed_changes["files_changed"]:
                file_str = str(file_path)
                for pattern in critical_patterns:
                    if pattern in file_str:
                        violations.append(SafetyViolation(
                            level="warning",
                            type="critical_file_change",
                            message=f"Changing critical file: {file_path}",
                            details={"file": file_path, "pattern": pattern}
                        ))
        
        return violations
    
    def _validate_test_requirements(self, proposed_changes: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate test requirements for changes."""
        violations = []
        
        if not self.config["require_tests"]:
            return violations
        
        # Check if tests are included or existing tests still pass
        has_tests = False
        
        if "files_changed" in proposed_changes:
            for file_path in proposed_changes["files_changed"]:
                if "test" in str(file_path).lower():
                    has_tests = True
                    break
        
        if not has_tests:
            # Check if existing tests pass
            if not self._run_tests():
                violations.append(SafetyViolation(
                    level="error",
                    type="untested_change",
                    message="Changes would break existing tests",
                    details={}
                ))
        
        return violations
    
    def _validate_rate_limits(self) -> List[SafetyViolation]:
        """Check rate limiting for operations."""
        violations = []
        
        max_ops = self.config["max_operations_per_hour"]
        recent_ops = self._count_recent_operations()
        
        if recent_ops >= max_ops:
            violations.append(SafetyViolation(
                level="error",
                type="rate_limit_exceeded",
                message=f"Too many operations in last hour ({recent_ops}/{max_ops})",
                details={"recent_operations": recent_ops, "limit": max_ops}
            ))
        
        return violations
    
    def _validate_repository_state(self) -> List[SafetyViolation]:
        """Validate the current repository state."""
        violations = []
        
        if not self._is_repository_clean():
            violations.append(SafetyViolation(
                level="warning",
                type="dirty_repository",
                message="Repository has uncommitted changes",
                details={}
            ))
        
        return violations
    
    def _count_recent_operations(self) -> int:
        """Count operations in the last hour."""
        cutoff = datetime.now() - timedelta(hours=1)
        count = 0
        
        for operation in self.operation_history:
            try:
                op_time = datetime.fromisoformat(operation["timestamp"])
                if op_time > cutoff:
                    count += 1
            except:
                continue
        
        return count
    
    def _is_repository_clean(self) -> bool:
        """Check if repository has no uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def _run_tests(self) -> bool:
        """Run tests and return success status."""
        try:
            result = subprocess.run(
                ["poetry", "run", "pytest", "-x", "-q"],
                cwd=self.working_directory,
                capture_output=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            stat = os.statvfs(self.working_directory)
            free_bytes = stat.f_frsize * stat.f_available
            total_bytes = stat.f_frsize * stat.f_blocks
            
            return {
                "free_gb": free_bytes / (1024**3),
                "total_gb": total_bytes / (1024**3),
                "usage_percent": (1 - free_bytes/total_bytes) * 100
            }
        except:
            return {"error": "Could not check disk space"}
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "used_gb": memory.used / (1024**3),
                "total_gb": memory.total / (1024**3),
                "usage_percent": memory.percent
            }
        except ImportError:
            return {"error": "psutil not available"}
        except:
            return {"error": "Could not check memory usage"}
