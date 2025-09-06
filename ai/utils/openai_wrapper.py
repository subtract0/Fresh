#!/usr/bin/env python3
"""
Resilient OpenAI Wrapper with GPT-5 Support
MCP Reference: 688cf28d-e69c-4624-b7cb-0725f36f9518
"""
import time
import json
from typing import Optional, Dict, Any, Union
from functools import wraps
import openai
from rich.console import Console

console = Console()

def exponential_backoff(max_retries=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (openai.RateLimitError, openai.Timeout) as e:
                    wait_time = 2 ** attempt
                    console.print(f"[yellow]Retry {attempt+1}/{max_retries} after {wait_time}s[/yellow]")
                    time.sleep(wait_time)
                except openai.NotFoundError:
                    # Handle model not found immediately
                    raise
            raise
        return wrapper
    return decorator

class ResilientOpenAIWrapper:
    """
    A resilient wrapper for OpenAI API calls with:
    - Exponential backoff retry logic
    - Graceful model degradation
    - Structured error handling
    """
    
    def __init__(self, fallback_model="gpt-4o"):
        self.fallback_model = fallback_model
        self.client = openai.OpenAI()
        
    @exponential_backoff()
    def call_llm(self, messages, model="gpt-5", reasoning_effort="high", verbosity="low", **kwargs) -> Dict[str, Any]:
        """
        Call LLM with intelligent fallback and error handling
        """
        try:
            # Try GPT-5 first
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
                **kwargs
            )
            return {"success": True, "response": response}
            
        except openai.NotFoundError:
            # Graceful fallback to GPT-4o
            console.print(f"[yellow]GPT-5 unavailable, falling back to {self.fallback_model}[/yellow]")
            response = self.client.chat.completions.create(
                model=self.fallback_model,
                messages=messages,
                **{k:v for k,v in kwargs.items() if k not in ['reasoning_effort', 'verbosity']}
            )
            return {"success": True, "response": response, "fallback": True}
        
        except Exception as e:
            console.print(f"[red]Error in LLM call: {str(e)}[/red]")
            raise
