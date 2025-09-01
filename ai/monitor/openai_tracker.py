"""
OpenAI API Usage Tracker

Tracks OpenAI API usage including token consumption, model usage, and cost estimation.
Integrates with the cost monitoring system for comprehensive billing tracking.

Features:
- Token counting for completions and embeddings
- Model-specific cost estimation
- Request tracking and rate limiting awareness  
- Integration with existing OpenAI client patterns
- Support for streaming responses
"""
from __future__ import annotations
import re
import logging
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Generator
from functools import wraps

from ai.monitor.cost_tracker import get_cost_tracker, ServiceType, OperationType

logger = logging.getLogger(__name__)


class TokenCounter:
    """Token counting utilities for OpenAI models."""
    
    @staticmethod
    def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Estimate token count for text.
        
        This is a rough estimation. For accurate counting, use tiktoken library.
        """
        # Rough approximation: ~4 characters per token for English text
        # This can vary significantly based on the text content and model
        
        if not text:
            return 0
            
        # Basic estimation
        char_count = len(text)
        
        # Adjust for different model families
        if "gpt-4" in model:
            # GPT-4 tends to be slightly more efficient
            chars_per_token = 3.8
        else:
            # GPT-3.5 and others
            chars_per_token = 4.0
            
        estimated_tokens = int(char_count / chars_per_token)
        
        # Add some overhead for formatting tokens
        return max(estimated_tokens + 10, 1)
    
    @staticmethod
    def count_messages_tokens(messages: List[Dict], model: str = "gpt-3.5-turbo") -> int:
        """Estimate tokens for a list of chat messages."""
        total_tokens = 0
        
        for message in messages:
            # Count tokens for role and content
            role_tokens = TokenCounter.estimate_tokens(message.get("role", ""), model)
            content_tokens = TokenCounter.estimate_tokens(message.get("content", ""), model)
            
            # Add overhead for message formatting
            message_tokens = role_tokens + content_tokens + 4  # overhead per message
            total_tokens += message_tokens
            
        # Add overhead for the conversation
        total_tokens += 3  # overhead for the conversation
        
        return total_tokens


class OpenAIUsageTracker:
    """Tracks OpenAI API usage and costs."""
    
    def __init__(self):
        self.cost_tracker = get_cost_tracker()
        
    def track_completion(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int = 0,
        metadata: Optional[Dict] = None
    ):
        """Track a completion API call."""
        
        # Track input tokens
        if input_tokens > 0:
            self.cost_tracker.record_usage(
                service=ServiceType.OPENAI,
                operation=OperationType.COMPLETION,
                quantity=input_tokens,
                model=model,
                metadata={
                    "token_type": "input",
                    **(metadata or {})
                }
            )
            
        # Track output tokens (different pricing)
        if output_tokens > 0:
            output_model = f"{model}-output"
            self.cost_tracker.record_usage(
                service=ServiceType.OPENAI,
                operation=OperationType.COMPLETION,
                quantity=output_tokens,
                model=output_model,
                metadata={
                    "token_type": "output",
                    **(metadata or {})
                }
            )
            
        logger.debug(f"🤖 Tracked {model}: {input_tokens} input + {output_tokens} output tokens")
        
    def track_embedding(
        self,
        model: str,
        tokens: int,
        metadata: Optional[Dict] = None
    ):
        """Track an embedding API call."""
        
        self.cost_tracker.record_usage(
            service=ServiceType.OPENAI,
            operation=OperationType.EMBEDDING,
            quantity=tokens,
            model=model,
            metadata=metadata or {}
        )
        
        logger.debug(f"🔤 Tracked {model}: {tokens} embedding tokens")
        
    def estimate_and_track_from_messages(
        self,
        model: str,
        messages: List[Dict],
        response_text: str = "",
        metadata: Optional[Dict] = None
    ):
        """Estimate and track usage from messages and response."""
        
        # Estimate input tokens from messages
        input_tokens = TokenCounter.count_messages_tokens(messages, model)
        
        # Estimate output tokens from response
        output_tokens = TokenCounter.estimate_tokens(response_text, model) if response_text else 0
        
        self.track_completion(model, input_tokens, output_tokens, metadata)
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }


def track_openai_call(
    model: str = None,
    operation: str = "completion",
    estimate_tokens: bool = True
):
    """
    Decorator to automatically track OpenAI API calls.
    
    Args:
        model: Model name (if not provided in function args)
        operation: Operation type ("completion" or "embedding")
        estimate_tokens: Whether to estimate tokens from text content
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracker = OpenAIUsageTracker()
            
            # Extract model from kwargs or use provided
            call_model = kwargs.get('model') or model or 'gpt-3.5-turbo'
            
            # Call the original function
            result = func(*args, **kwargs)
            
            try:
                if operation == "completion":
                    # Try to extract token usage from response
                    if hasattr(result, 'usage') and result.usage:
                        # Official usage statistics from OpenAI response
                        input_tokens = result.usage.prompt_tokens
                        output_tokens = result.usage.completion_tokens
                        tracker.track_completion(call_model, input_tokens, output_tokens)
                    elif estimate_tokens:
                        # Estimate from content
                        messages = kwargs.get('messages', [])
                        response_text = ""
                        
                        if hasattr(result, 'choices') and result.choices:
                            response_text = result.choices[0].message.content or ""
                            
                        tracker.estimate_and_track_from_messages(
                            call_model, messages, response_text
                        )
                        
                elif operation == "embedding":
                    if hasattr(result, 'usage') and result.usage:
                        tokens = result.usage.total_tokens
                        tracker.track_embedding(call_model, tokens)
                    elif estimate_tokens:
                        # Estimate from input text
                        input_text = kwargs.get('input', '')
                        if isinstance(input_text, list):
                            input_text = ' '.join(input_text)
                        tokens = TokenCounter.estimate_tokens(input_text, call_model)
                        tracker.track_embedding(call_model, tokens)
                        
            except Exception as e:
                logger.error(f"Failed to track OpenAI usage: {e}")
                
            return result
            
        return wrapper
    return decorator


def track_openai_streaming_call(
    model: str = None,
    estimate_response_tokens: bool = True
):
    """
    Decorator for streaming OpenAI calls.
    
    Tracks input tokens immediately and accumulates output tokens as they stream.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracker = OpenAIUsageTracker()
            call_model = kwargs.get('model') or model or 'gpt-3.5-turbo'
            
            # Estimate and track input tokens immediately
            messages = kwargs.get('messages', [])
            input_tokens = TokenCounter.count_messages_tokens(messages, call_model)
            
            if input_tokens > 0:
                tracker.track_completion(call_model, input_tokens, 0, {"streaming": True})
            
            # Call the original streaming function
            stream = func(*args, **kwargs)
            
            if estimate_response_tokens:
                # Wrap the stream to count output tokens
                return _track_streaming_tokens(stream, tracker, call_model)
            else:
                return stream
                
        return wrapper
    return decorator


def _track_streaming_tokens(stream, tracker: OpenAIUsageTracker, model: str):
    """Wrap a streaming response to track output tokens."""
    accumulated_text = ""
    
    try:
        for chunk in stream:
            # Accumulate response text
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    accumulated_text += delta.content
                    
            yield chunk
            
    finally:
        # Track output tokens when stream is complete
        if accumulated_text:
            output_tokens = TokenCounter.estimate_tokens(accumulated_text, model)
            tracker.track_completion(model, 0, output_tokens, {
                "streaming": True,
                "output_only": True
            })


class TrackedOpenAIClient:
    """OpenAI client wrapper with automatic usage tracking."""
    
    def __init__(self, client):
        """Initialize with existing OpenAI client."""
        self._client = client
        self._tracker = OpenAIUsageTracker()
        
    def chat(self):
        """Get tracked chat completions interface."""
        return TrackedChatCompletions(self._client.chat, self._tracker)
        
    def embeddings(self):
        """Get tracked embeddings interface."""
        return TrackedEmbeddings(self._client.embeddings, self._tracker)
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped client."""
        return getattr(self._client, name)


class TrackedChatCompletions:
    """Chat completions wrapper with usage tracking."""
    
    def __init__(self, chat_completions, tracker: OpenAIUsageTracker):
        self._completions = chat_completions
        self._tracker = tracker
        
    def create(self, **kwargs):
        """Create chat completion with tracking."""
        model = kwargs.get('model', 'gpt-3.5-turbo')
        messages = kwargs.get('messages', [])
        stream = kwargs.get('stream', False)
        
        # Call the API
        result = self._completions.create(**kwargs)
        
        if stream:
            # For streaming, track input immediately and wrap output
            input_tokens = TokenCounter.count_messages_tokens(messages, model)
            if input_tokens > 0:
                self._tracker.track_completion(model, input_tokens, 0, {"streaming": True})
                
            return _track_streaming_tokens(result, self._tracker, model)
        else:
            # For non-streaming, track after response
            try:
                if hasattr(result, 'usage') and result.usage:
                    input_tokens = result.usage.prompt_tokens
                    output_tokens = result.usage.completion_tokens
                    self._tracker.track_completion(model, input_tokens, output_tokens)
                else:
                    # Fallback to estimation
                    response_text = ""
                    if hasattr(result, 'choices') and result.choices:
                        response_text = result.choices[0].message.content or ""
                    self._tracker.estimate_and_track_from_messages(model, messages, response_text)
                    
            except Exception as e:
                logger.error(f"Failed to track chat completion: {e}")
                
            return result
            
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped completions."""
        return getattr(self._completions, name)


class TrackedEmbeddings:
    """Embeddings wrapper with usage tracking."""
    
    def __init__(self, embeddings, tracker: OpenAIUsageTracker):
        self._embeddings = embeddings
        self._tracker = tracker
        
    def create(self, **kwargs):
        """Create embeddings with tracking."""
        model = kwargs.get('model', 'text-embedding-ada-002')
        input_text = kwargs.get('input', '')
        
        # Call the API
        result = self._embeddings.create(**kwargs)
        
        try:
            if hasattr(result, 'usage') and result.usage:
                tokens = result.usage.total_tokens
                self._tracker.track_embedding(model, tokens)
            else:
                # Estimate tokens from input
                if isinstance(input_text, list):
                    total_tokens = sum(TokenCounter.estimate_tokens(text, model) for text in input_text)
                else:
                    total_tokens = TokenCounter.estimate_tokens(input_text, model)
                self._tracker.track_embedding(model, total_tokens)
                
        except Exception as e:
            logger.error(f"Failed to track embedding usage: {e}")
            
        return result
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped embeddings."""
        return getattr(self._embeddings, name)


def wrap_openai_client(client):
    """
    Wrap an existing OpenAI client with usage tracking.
    
    Usage:
        import openai
        from ai.monitor.openai_tracker import wrap_openai_client
        
        # Original client
        client = openai.OpenAI(api_key="your-key")
        
        # Wrapped client with cost tracking
        client = wrap_openai_client(client)
        
        # Use normally - all operations are automatically tracked
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    return TrackedOpenAIClient(client)


# Convenience functions for manual tracking
def track_completion_usage(model: str, input_tokens: int, output_tokens: int = 0):
    """Manually track completion usage."""
    tracker = OpenAIUsageTracker()
    tracker.track_completion(model, input_tokens, output_tokens)
    
    
def track_embedding_usage(model: str, tokens: int):
    """Manually track embedding usage.""" 
    tracker = OpenAIUsageTracker()
    tracker.track_embedding(model, tokens)


def estimate_cost_for_messages(model: str, messages: List[Dict], response_text: str = "") -> Dict:
    """
    Estimate cost for a chat completion without making the API call.
    
    Returns:
        Dict with token counts and estimated cost
    """
    input_tokens = TokenCounter.count_messages_tokens(messages, model)
    output_tokens = TokenCounter.estimate_tokens(response_text, model) if response_text else 0
    
    # Get cost tracker for pricing info
    tracker = get_cost_tracker()
    
    input_cost = 0.0
    output_cost = 0.0
    
    if ServiceType.OPENAI in tracker.pricing:
        pricing = tracker.pricing[ServiceType.OPENAI].pricing_per_unit
        
        if model in pricing:
            input_cost = (input_tokens / 1000.0) * pricing[model]
            
        output_model = f"{model}-output"
        if output_model in pricing:
            output_cost = (output_tokens / 1000.0) * pricing[output_model]
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
        "model": model
    }
