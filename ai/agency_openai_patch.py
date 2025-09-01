"""
Agency Swarm OpenAI Cost Tracking Patch

This module patches the openai module to use cost tracking
when imported by Agency Swarm or other parts of the system.
"""
import sys
from typing import Any

# Store original openai module
_original_openai = None

def patch_openai():
    """Patch the openai module with cost tracking."""
    global _original_openai
    
    if 'openai' in sys.modules:
        _original_openai = sys.modules['openai']
        
        # Import our cost tracking wrapper
        from ai.monitor.openai_tracker import wrap_openai_client
        
        # Wrap the OpenAI client class
        original_client_class = _original_openai.OpenAI
        
        class TrackedOpenAI(original_client_class):
            """OpenAI client with automatic cost tracking."""
            
            def __init__(self, *args, **kwargs):
                # Initialize the original client
                super().__init__(*args, **kwargs)
                
                # Wrap with cost tracking
                wrapped_client = wrap_openai_client(self)
                
                # Copy wrapped attributes back to self
                self.chat = wrapped_client.chat
                self.embeddings = wrapped_client.embeddings
                
                print("💰 OpenAI client wrapped with cost tracking")
        
        # Replace the OpenAI class in the module
        _original_openai.OpenAI = TrackedOpenAI
        
        print("✅ OpenAI module patched with cost tracking")
    
def unpatch_openai():
    """Restore original openai module.""" 
    global _original_openai
    
    if _original_openai and 'openai' in sys.modules:
        # Restore original OpenAI class
        sys.modules['openai'].OpenAI = _original_openai.OpenAI
        print("↩️ OpenAI module restored to original")

# Auto-patch when this module is imported
patch_openai()
