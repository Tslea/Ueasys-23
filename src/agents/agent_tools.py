"""
Agent Tools - Tools available to character agents.

This module provides tools that agents can use to interact
with the world and other systems.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin

logger = get_logger(__name__)


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    name: str
    description: str
    type: str = "string"
    required: bool = True
    default: Any = None


class ToolResult(BaseModel):
    """Result from a tool execution."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTool(ABC, LoggerMixin):
    """
    Base class for agent tools.
    
    Tools provide capabilities to agents for interacting
    with systems and the world.
    
    Example:
        >>> class SearchTool(AgentTool):
        ...     name = "search"
        ...     description = "Search for information"
        ...     
        ...     async def execute(self, query: str) -> ToolResult:
        ...         results = await search_engine.search(query)
        ...         return ToolResult(success=True, result=results)
    """
    
    name: str = "base_tool"
    description: str = "Base tool"
    parameters: list[ToolParameter] = []
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution outcome
        """
        pass
    
    def get_schema(self) -> dict[str, Any]:
        """Get tool schema for LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type,
                        "description": p.description,
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required],
            },
        }


class MemorySearchTool(AgentTool):
    """Tool for searching character memories."""
    
    name = "memory_search"
    description = "Search through memories for relevant information"
    parameters = [
        ToolParameter(
            name="query",
            description="Search query",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="limit",
            description="Maximum results to return",
            type="integer",
            required=False,
            default=5,
        ),
    ]
    
    def __init__(self, memory_manager: Any):
        self._memory = memory_manager
    
    async def execute(self, query: str, limit: int = 5) -> ToolResult:
        """Search memories."""
        try:
            results = await self._memory.retrieve(query=query, limit=limit)
            return ToolResult(
                success=True,
                result=results,
                metadata={"count": len(results)},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class KnowledgeSearchTool(AgentTool):
    """Tool for searching character knowledge via RAG."""
    
    name = "knowledge_search"
    description = "Search through knowledge and lore"
    parameters = [
        ToolParameter(
            name="query",
            description="Search query",
            type="string",
            required=True,
        ),
    ]
    
    def __init__(self, rag_system: Any, character_id: str):
        self._rag = rag_system
        self._character_id = character_id
    
    async def execute(self, query: str) -> ToolResult:
        """Search knowledge."""
        try:
            context = await self._rag.retrieve_context(
                character_id=self._character_id,
                query=query,
            )
            return ToolResult(
                success=True,
                result=[r.content for r in context.results],
                metadata={"total_score": context.total_score},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class EmotionUpdateTool(AgentTool):
    """Tool for updating emotional state."""
    
    name = "update_emotion"
    description = "Update the character's emotional state"
    parameters = [
        ToolParameter(
            name="emotion",
            description="The emotion to feel",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="intensity",
            description="Intensity of the emotion (0.0 to 1.0)",
            type="number",
            required=False,
            default=0.5,
        ),
    ]
    
    def __init__(self, emotional_state: Any):
        self._emotional_state = emotional_state
    
    async def execute(self, emotion: str, intensity: float = 0.5) -> ToolResult:
        """Update emotion."""
        try:
            # This would update the emotional state manager
            return ToolResult(
                success=True,
                result={"emotion": emotion, "intensity": intensity},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GoalTool(AgentTool):
    """Tool for managing goals."""
    
    name = "manage_goal"
    description = "Add, update, or complete a goal"
    parameters = [
        ToolParameter(
            name="action",
            description="Action to take: add, progress, complete",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="goal_description",
            description="Description of the goal",
            type="string",
            required=True,
        ),
    ]
    
    def __init__(self, goal_system: Any):
        self._goals = goal_system
    
    async def execute(
        self,
        action: str,
        goal_description: str,
    ) -> ToolResult:
        """Manage goal."""
        try:
            if action == "add":
                goal = await self._goals.add_goal(goal_description)
                return ToolResult(
                    success=True,
                    result={"goal_id": goal.goal_id, "description": goal_description},
                )
            elif action == "complete":
                goals = self._goals.get_active_goals()
                for goal in goals:
                    if goal.description == goal_description:
                        await self._goals.complete_goal(goal.goal_id)
                        return ToolResult(success=True, result={"completed": goal_description})
                return ToolResult(success=False, error="Goal not found")
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ToolRegistry(LoggerMixin):
    """
    Registry for agent tools.
    
    Manages available tools and provides tool lookup.
    
    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(MemorySearchTool(memory_manager))
        >>> tool = registry.get("memory_search")
    """
    
    def __init__(self):
        self._tools: dict[str, AgentTool] = {}
        self.logger.info("Initialized ToolRegistry")
    
    def register(self, tool: AgentTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self.logger.debug("Registered tool", tool_name=tool.name)
    
    def get(self, name: str) -> Optional[AgentTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_schemas(self) -> list[dict[str, Any]]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]
    
    async def execute(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}",
            )
        
        return await tool.execute(**kwargs)
