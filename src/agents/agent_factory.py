"""
Agent Factory - Create agents with the correct LLM providers.

This module provides factory functions to create agents with the
appropriate LLM provider based on task type.
"""

from typing import Optional

from src.llm import get_chat_llm, get_agent_llm, LLMConfig
from src.core.character.personality_core import PersonalityCore
from src.core.memory.memory_manager import MemoryManager
from src.rag.rag_system import RAGSystem
from src.agents.character_agent import CharacterAgent


def create_character_agent(
    personality: PersonalityCore,
    rag: Optional[RAGSystem] = None,
    memory: Optional[MemoryManager] = None,
    use_fast_model: bool = True,
) -> CharacterAgent:
    """
    Create a character agent with the appropriate LLM.
    
    Args:
        personality: Character's personality core
        rag: RAG system for knowledge
        memory: Memory manager
        use_fast_model: If True, use fast chat LLM (Grok), else use agent LLM (DeepSeek)
        
    Returns:
        CharacterAgent configured with the right provider
        
    Example:
        >>> agent = create_character_agent(gandalf_personality)
        >>> response = await agent.respond("Tell me about the Ring")
    """
    # Use Grok for fast responses, DeepSeek for complex reasoning
    llm = get_chat_llm() if use_fast_model else get_agent_llm()
    
    return CharacterAgent(
        personality=personality,
        llm=llm,
        rag=rag,
        memory=memory,
    )


def create_reasoning_agent(
    personality: PersonalityCore,
    rag: Optional[RAGSystem] = None,
    memory: Optional[MemoryManager] = None,
) -> CharacterAgent:
    """
    Create a character agent optimized for complex reasoning.
    
    Uses DeepSeek Reasoner for multi-step thinking.
    
    Args:
        personality: Character's personality core
        rag: RAG system for knowledge
        memory: Memory manager
        
    Returns:
        CharacterAgent with reasoning-optimized LLM
    """
    # Use DeepSeek Reasoner for complex decisions
    llm = get_agent_llm(LLMConfig(model="deepseek-reasoner", temperature=0.3))
    
    return CharacterAgent(
        personality=personality,
        llm=llm,
        rag=rag,
        memory=memory,
    )
