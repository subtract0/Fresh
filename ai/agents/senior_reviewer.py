"""Senior Reviewer Agent for autonomous code quality control.

This agent acts as a senior developer who reviews all code changes
before they are committed, ensuring quality, security, and maintainability.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from openai import OpenAI
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class ReviewDecision(Enum):
    """Possible review decisions."""
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes" 
    REJECT = "reject"


@dataclass
class ReviewResult:
    """Result of a senior review."""
    decision: ReviewDecision
    confidence: float  # 0.0 to 1.0
    reasoning: str
    suggestions: List[str]
    security_concerns: List[str]
    maintainability_score: float  # 0.0 to 1.0
    
    def is_approved(self) -> bool:
        """Check if the review was approved."""
        return self.decision == ReviewDecision.APPROVE


class SeniorReviewer:
    """Senior Reviewer Agent for autonomous code quality control.
    
    This agent acts as an experienced senior developer who:
    - Reviews code changes for quality and maintainability
    - Checks for security vulnerabilities
    - Ensures code follows best practices
    - Makes approve/reject decisions autonomously
    """
    
    def __init__(self):
        """Initialize the Senior Reviewer."""
        self.client = OpenAI()
        self.review_criteria = self._get_review_criteria()
    
    def review_changes(
        self, 
        original_content: str,
        modified_content: str, 
        file_path: str,
        change_description: str,
        agent_type: str
    ) -> ReviewResult:
        """Review code changes and make a decision.
        
        Args:
            original_content: Original file content
            modified_content: Modified file content  
            file_path: Path to the file being changed
            change_description: Description of what was changed
            agent_type: Type of agent that made the changes
            
        Returns:
            ReviewResult with decision and reasoning
        """
        # Create review prompt
        system_prompt = self._create_review_system_prompt()
        user_prompt = self._create_review_user_prompt(
            original_content, modified_content, file_path, 
            change_description, agent_type
        )
        
        try:
            # Call OpenAI for review
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use full GPT-4 for critical review decisions
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent decisions
                timeout=45.0
            )
            
            # Parse the response
            return self._parse_review_response(response.choices[0].message.content)
            
        except Exception as e:
            # Default to requesting changes if review fails
            return ReviewResult(
                decision=ReviewDecision.REQUEST_CHANGES,
                confidence=0.0,
                reasoning=f"Review failed due to error: {str(e)}",
                suggestions=["Manual review required due to automated review failure"],
                security_concerns=["Automated security scan failed"],
                maintainability_score=0.0
            )
    
    def _create_review_system_prompt(self) -> str:
        """Create system prompt for code review."""
        return """You are a Senior Software Engineer conducting a thorough code review.
Your role is to ensure code quality, security, and maintainability.

REVIEW CRITERIA:
1. **Code Quality**: Clean, readable, well-structured code
2. **Security**: No vulnerabilities or unsafe practices  
3. **Maintainability**: Easy to understand and modify
4. **Best Practices**: Follows language and project conventions
5. **Functionality**: Changes correctly address the intended issue

RESPONSE FORMAT (JSON):
{
  "decision": "approve|request_changes|reject",
  "confidence": 0.0-1.0,
  "reasoning": "Clear explanation of decision",
  "suggestions": ["List of improvement suggestions"],
  "security_concerns": ["List of security issues found"],
  "maintainability_score": 0.0-1.0
}

DECISION GUIDELINES:
- **APPROVE**: High quality change that improves the codebase
- **REQUEST_CHANGES**: Good change but needs minor improvements  
- **REJECT**: Poor quality, security issues, or breaks functionality

Be thorough but practical. Focus on significant issues that impact code quality."""
    
    def _create_review_user_prompt(
        self,
        original_content: str,
        modified_content: str,
        file_path: str, 
        change_description: str,
        agent_type: str
    ) -> str:
        """Create user prompt with change details."""
        return f"""CHANGE REVIEW REQUEST

**Agent:** {agent_type}
**File:** {file_path}
**Description:** {change_description}

**ORIGINAL CODE:**
```
{original_content[:3000]}  
```

**MODIFIED CODE:**
```
{modified_content[:3000]}
```

Please review this change and provide your decision in the specified JSON format.

Focus on:
- Does this change correctly address the described issue?
- Are there any security vulnerabilities introduced?
- Is the code clean and maintainable?
- Does it follow best practices?

Provide your review as valid JSON."""
    
    def _parse_review_response(self, response_content: str) -> ReviewResult:
        """Parse the review response from OpenAI."""
        import json
        import re
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                review_data = json.loads(json_match.group())
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse_review(response_content)
            
            # Map decision string to enum
            decision_map = {
                "approve": ReviewDecision.APPROVE,
                "request_changes": ReviewDecision.REQUEST_CHANGES,
                "reject": ReviewDecision.REJECT
            }
            
            decision = decision_map.get(
                review_data.get("decision", "request_changes").lower(),
                ReviewDecision.REQUEST_CHANGES
            )
            
            return ReviewResult(
                decision=decision,
                confidence=float(review_data.get("confidence", 0.5)),
                reasoning=review_data.get("reasoning", "No reasoning provided"),
                suggestions=review_data.get("suggestions", []),
                security_concerns=review_data.get("security_concerns", []),
                maintainability_score=float(review_data.get("maintainability_score", 0.5))
            )
            
        except Exception as e:
            return self._fallback_parse_review(response_content, str(e))
    
    def _fallback_parse_review(self, content: str, error: str = "") -> ReviewResult:
        """Fallback parsing when JSON parsing fails."""
        # Simple heuristics to determine decision
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["approve", "looks good", "lgtm"]):
            decision = ReviewDecision.APPROVE
            confidence = 0.7
        elif any(word in content_lower for word in ["reject", "dangerous", "security risk"]):
            decision = ReviewDecision.REJECT  
            confidence = 0.8
        else:
            decision = ReviewDecision.REQUEST_CHANGES
            confidence = 0.5
        
        return ReviewResult(
            decision=decision,
            confidence=confidence,
            reasoning=f"Fallback parsing: {content[:200]}... (Error: {error})",
            suggestions=["Manual review recommended due to parsing issues"],
            security_concerns=[] if decision == ReviewDecision.APPROVE else ["Automated scan incomplete"],
            maintainability_score=0.5
        )
    
    def _get_review_criteria(self) -> Dict[str, Any]:
        """Get review criteria configuration."""
        return {
            "min_confidence_threshold": 0.7,
            "security_weight": 0.4,
            "maintainability_weight": 0.3, 
            "functionality_weight": 0.3,
            "auto_approve_threshold": 0.85
        }


def create_senior_reviewer() -> SeniorReviewer:
    """Factory function to create a Senior Reviewer instance."""
    return SeniorReviewer()
