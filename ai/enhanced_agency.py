"""
Enhanced Agency with Intelligent Memory-Powered Agents

This module provides an enhanced version of the agency that uses agents equipped
with intelligent memory capabilities including semantic search, auto-classification,
and memory analytics.

The enhanced agency provides:
- Context-aware decision making through semantic search
- Automated memory classification and tagging
- Learning from past interactions and patterns
- Memory analytics for performance optimization
- Backward compatibility with basic memory operations
"""
from __future__ import annotations
from pathlib import Path
import os
from typing import Optional

from agency_swarm import Agency
from ai.agents.EnhancedArchitect import EnhancedArchitect
from ai.agents.EnhancedDeveloper import EnhancedDeveloper
from ai.agents.EnhancedFather import EnhancedFather
from ai.agents.QA import QA
from ai.agents.Reviewer import Reviewer
from ai.agents.DocumentationAgent import DocumentationAgent

# Initialize intelligent memory store
from ai.memory.store import set_memory_store, InMemoryMemoryStore
from ai.memory.intelligent_store import IntelligentMemoryStore

try:
    from ai.memory.firestore import FirestoreMemoryStore  # type: ignore
except Exception:  # pragma: no cover
    FirestoreMemoryStore = None  # type: ignore


def initialize_intelligent_memory(use_enhanced_firestore: bool = True) -> None:
    """Initialize the intelligent memory store with fallback options.
    
    Args:
        use_enhanced_firestore: Whether to use Enhanced Firestore (production) or basic Firestore (staging)
    """
    use_firestore = (
        os.getenv("FIREBASE_PROJECT_ID")
        and os.getenv("FIREBASE_CLIENT_EMAIL")
        and os.getenv("FIREBASE_PRIVATE_KEY")
    )

    # Priority order: Enhanced Firestore (production) > Intelligent Memory (local) > Basic Firestore (staging) > InMemory (fallback)
    if use_firestore and use_enhanced_firestore:
        try:
            from ai.memory.enhanced_firestore import EnhancedFirestoreMemoryStore
            set_memory_store(EnhancedFirestoreMemoryStore())
            print("🔥 Enhanced Agency: Using Enhanced Firestore with intelligent memory and production features")
            return
        except Exception as e:
            print(f"⚠️  Failed to initialize Enhanced Firestore: {e}")
    
    try:
        # Use intelligent memory store as fallback
        set_memory_store(IntelligentMemoryStore())
        print("🧠 Enhanced Agency: Using Intelligent Memory Store with semantic search")
    except Exception as e:
        print(f"⚠️  Failed to initialize Intelligent Memory Store: {e}")
        if use_firestore and FirestoreMemoryStore is not None:
            try:
                set_memory_store(FirestoreMemoryStore())  # type: ignore
                print("☁️  Enhanced Agency: Using Basic Firestore Memory Store")
            except Exception as fe:
                print(f"⚠️  Failed to initialize Basic Firestore: {fe}")
                set_memory_store(InMemoryMemoryStore())
                print("💾 Enhanced Agency: Using InMemory Store (fallback)")
        else:
            set_memory_store(InMemoryMemoryStore())
            print("💾 Enhanced Agency: Using InMemory Store (no credentials found)")


def build_enhanced_agency(
    enable_qa: bool = True,
    enable_reviewer: bool = True,
    shared_instructions_path: Optional[str] = None,
    use_enhanced_firestore: bool = True,
    include_docs_agent: bool = True
) -> Agency:
    """
    Construct the enhanced agency with intelligent memory-powered agents.
    
    Args:
        enable_qa: Whether to include QA agent in the workflow
        enable_reviewer: Whether to include Reviewer agent in the workflow  
        shared_instructions_path: Path to shared instructions file
        use_enhanced_firestore: Whether to use Enhanced Firestore for production
    
    Returns:
        Agency instance with intelligent agents
    """
    # Initialize intelligent memory first
    initialize_intelligent_memory(use_enhanced_firestore=use_enhanced_firestore)
    
    repo_root = Path(__file__).resolve().parents[1]
    manifesto = repo_root / "agency_manifesto.md"
    
    # Build agency chart with enhanced agents
    agency_chart = [
        EnhancedFather,
        [EnhancedFather, EnhancedArchitect],
        [EnhancedArchitect, EnhancedDeveloper],
    ]

    # Optionally add Documentation agent as a parallel branch from Father
    if include_docs_agent:
        agency_chart.append([EnhancedFather, DocumentationAgent])
    
    # Add QA and Reviewer if enabled
    if enable_qa:
        agency_chart.append([EnhancedDeveloper, QA])
        if enable_reviewer:
            agency_chart.extend([
                [QA, Reviewer],
                [Reviewer, EnhancedFather],  # Close the loop back to Father
            ])
        else:
            agency_chart.append([QA, EnhancedFather])  # Direct back to Father
    else:
        agency_chart.append([EnhancedDeveloper, EnhancedFather])  # Direct back to Father
    
    kwargs = {"temperature": 0.2}
    
    # Use custom instructions if provided, otherwise check for manifesto
    if shared_instructions_path:
        instructions_file = Path(shared_instructions_path)
        if instructions_file.exists():
            kwargs["shared_instructions"] = str(instructions_file)
    elif manifesto.exists():
        kwargs["shared_instructions"] = str(manifesto)
    
    return Agency(agency_chart, **kwargs)


def build_lightweight_enhanced_agency() -> Agency:
    """
    Build a lightweight version with just Father -> Architect -> Developer flow.
    
    Useful for rapid prototyping or when QA/Review processes are handled externally.
    """
    return build_enhanced_agency(enable_qa=False, enable_reviewer=False)


def demo_enhanced_agency():
    """
    Demo function to showcase enhanced agency capabilities.
    
    This function demonstrates:
    1. Intelligent memory initialization
    2. Enhanced agent creation
    3. Sample workflow with memory intelligence
    """
    print("🚀 Enhanced Agency Demo")
    print("=" * 50)
    
    # Build and initialize the enhanced agency
    agency = build_enhanced_agency()
    
    print(f"✅ Created agency with {len(agency.agents)} intelligent agents")
    
    # Display agent capabilities
    for agent in agency.agents:
        agent_name = getattr(agent, 'name', str(type(agent).__name__))
        print(f"🤖 {agent_name}:")
        
        # Safely access tools
        agent_tools = getattr(agent, 'tools', [])
        enhanced_tools = []
        for tool in agent_tools:
            tool_name = getattr(tool, '__name__', str(tool))
            if any(keyword in tool_name for keyword in ['Enhanced', 'Smart', 'Semantic']):
                enhanced_tools.append(tool_name)
        
        if enhanced_tools:
            print(f"   🧠 Intelligent tools: {', '.join(enhanced_tools)}")
        
        agent_description = getattr(agent, 'description', 'No description available')
        print(f"   📝 Description: {agent_description}")
        print()
    
    print("🎉 Enhanced Agency ready for intelligent collaboration!")
    
    return agency


if __name__ == "__main__":
    # Run demo if script is executed directly
    demo_enhanced_agency()
