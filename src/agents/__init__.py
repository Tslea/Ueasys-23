"""
Agent module for Fantasy World RAG.

This module provides the agentic layer for character behavior:
- Character Agent: Main agent coordinating all systems
- Agent Tools: Tools available to agents
- Agent Loop: ReAct-style agent loop
- Agent Factory: Create agents with correct LLM providers
"""

from src.agents.character_agent import CharacterAgent, AgentState
from src.agents.agent_tools import AgentTool, ToolRegistry
from src.agents.agent_loop import AgentLoop, AgentAction
from src.agents.agent_factory import create_character_agent, create_reasoning_agent

__all__ = [
    "CharacterAgent",
    "AgentState",
    "AgentTool",
    "ToolRegistry",
    "AgentLoop",
    "AgentAction",
    # Factory functions
    "create_character_agent",
    "create_reasoning_agent",
]
