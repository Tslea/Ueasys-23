"""
Agent Loop - ReAct-style agent execution loop.

This module provides the agent execution loop that implements
the ReAct (Reasoning + Acting) pattern for character agents.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.agents.agent_tools import ToolRegistry, ToolResult
from src.llm.base_provider import BaseLLMProvider

logger = get_logger(__name__)


class ActionType(str, Enum):
    """Types of agent actions."""
    THINK = "think"
    OBSERVE = "observe"
    ACT = "act"
    RESPOND = "respond"


class AgentAction(BaseModel):
    """An action taken by the agent."""
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: ActionType
    description: str
    tool_name: Optional[str] = None
    tool_args: dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentThought(BaseModel):
    """A thought from the agent's reasoning."""
    thought_id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentLoopResult(BaseModel):
    """Result from an agent loop execution."""
    response: str
    thoughts: list[AgentThought] = Field(default_factory=list)
    actions: list[AgentAction] = Field(default_factory=list)
    total_steps: int = 0
    total_time_ms: int = 0
    success: bool = True
    error: Optional[str] = None


class AgentLoop(LoggerMixin):
    """
    ReAct-style agent execution loop.
    
    Implements the Reasoning + Acting pattern:
    1. Think about the situation
    2. Decide on an action
    3. Execute the action
    4. Observe the result
    5. Repeat until done
    
    Example:
        >>> loop = AgentLoop(
        ...     llm=openai_provider,
        ...     tools=tool_registry,
        ... )
        >>> result = await loop.run(
        ...     query="Tell me about the Ring",
        ...     context={"character": "gandalf"}
        ... )
    """
    
    MAX_STEPS = 5
    
    def __init__(
        self,
        llm: Optional[BaseLLMProvider],
        tools: ToolRegistry,
        system_prompt: str = "",
        max_steps: int = 5,
    ):
        """
        Initialize the agent loop.
        
        Args:
            llm: LLM provider for reasoning
            tools: Tool registry
            system_prompt: System prompt for the agent
            max_steps: Maximum steps before stopping
        """
        self._llm = llm
        self._tools = tools
        self._system_prompt = system_prompt
        self._max_steps = min(max_steps, self.MAX_STEPS)
        
        self.logger.info(
            "Initialized AgentLoop",
            max_steps=self._max_steps,
            num_tools=len(tools.list_tools()),
        )
    
    async def run(
        self,
        query: str,
        context: Optional[dict[str, Any]] = None,
    ) -> AgentLoopResult:
        """
        Run the agent loop.
        
        Args:
            query: User query/input
            context: Additional context
            
        Returns:
            AgentLoopResult with response and trace
        """
        start_time = datetime.now()
        
        thoughts: list[AgentThought] = []
        actions: list[AgentAction] = []
        step = 0
        
        # Initial observation
        observation = f"User query: {query}"
        
        try:
            while step < self._max_steps:
                step += 1
                
                # Think
                thought = await self._think(query, observation, thoughts, actions, context)
                thoughts.append(thought)
                
                # Check if we should respond
                if self._should_respond(thought, step):
                    break
                
                # Decide action
                action = await self._decide_action(thought, context)
                
                if action.action_type == ActionType.RESPOND:
                    # Ready to respond
                    actions.append(action)
                    break
                
                if action.tool_name:
                    # Execute tool
                    result = await self._execute_action(action)
                    action.result = str(result.result) if result.success else result.error
                    observation = f"Tool {action.tool_name} returned: {action.result}"
                
                actions.append(action)
            
            # Generate final response
            response = await self._generate_response(query, thoughts, actions, context)
            
            total_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentLoopResult(
                response=response,
                thoughts=thoughts,
                actions=actions,
                total_steps=step,
                total_time_ms=total_time,
                success=True,
            )
            
        except Exception as e:
            self.logger.error("Agent loop error", error=str(e))
            
            return AgentLoopResult(
                response="I apologize, but I encountered difficulty processing your request.",
                thoughts=thoughts,
                actions=actions,
                total_steps=step,
                total_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                success=False,
                error=str(e),
            )
    
    async def _think(
        self,
        query: str,
        observation: str,
        thoughts: list[AgentThought],
        actions: list[AgentAction],
        context: Optional[dict[str, Any]],
    ) -> AgentThought:
        """Generate a thought based on current state."""
        if self._llm:
            # Build thinking prompt
            prompt = self._build_thinking_prompt(
                query, observation, thoughts, actions, context
            )
            
            response = await self._llm.generate(
                prompt=prompt,
                system_prompt=self._system_prompt,
                max_tokens=256,
            )
            
            return AgentThought(
                content=response.content,
                confidence=0.7,
            )
        else:
            # Fallback thinking
            if not thoughts:
                content = f"I need to consider: {query}"
            else:
                content = f"Based on {observation}, I should determine my response."
            
            return AgentThought(content=content, confidence=0.5)
    
    def _build_thinking_prompt(
        self,
        query: str,
        observation: str,
        thoughts: list[AgentThought],
        actions: list[AgentAction],
        context: Optional[dict[str, Any]],
    ) -> str:
        """Build prompt for thinking step."""
        parts = [
            "You are reasoning through a response.",
            f"\nQuery: {query}",
            f"\nCurrent observation: {observation}",
        ]
        
        if thoughts:
            parts.append("\nPrevious thoughts:")
            for t in thoughts[-3:]:
                parts.append(f"- {t.content}")
        
        if actions:
            parts.append("\nPrevious actions:")
            for a in actions[-3:]:
                parts.append(f"- {a.description} -> {a.result}")
        
        parts.append("\nWhat should you think about or do next? Be concise.")
        
        return "\n".join(parts)
    
    def _should_respond(
        self,
        thought: AgentThought,
        step: int,
    ) -> bool:
        """Determine if agent should respond now."""
        # Check thought content for response signals
        content_lower = thought.content.lower()
        
        if any(phrase in content_lower for phrase in [
            "ready to respond",
            "can now answer",
            "have enough information",
            "should respond",
        ]):
            return True
        
        # High confidence means we can respond
        if thought.confidence > 0.85:
            return True
        
        # Force response on last step
        if step >= self._max_steps:
            return True
        
        return False
    
    async def _decide_action(
        self,
        thought: AgentThought,
        context: Optional[dict[str, Any]],
    ) -> AgentAction:
        """Decide what action to take."""
        content_lower = thought.content.lower()
        
        # Check if should use a tool
        available_tools = self._tools.list_tools()
        
        for tool_name in available_tools:
            if tool_name.replace("_", " ") in content_lower:
                return AgentAction(
                    action_type=ActionType.ACT,
                    description=f"Using tool: {tool_name}",
                    tool_name=tool_name,
                    tool_args=self._extract_tool_args(thought.content, tool_name),
                )
        
        # Check for specific intents
        if any(word in content_lower for word in ["search", "find", "look for"]):
            if "memory" in content_lower and "memory_search" in available_tools:
                return AgentAction(
                    action_type=ActionType.ACT,
                    description="Searching memories",
                    tool_name="memory_search",
                    tool_args={"query": thought.content},
                )
            elif "knowledge_search" in available_tools:
                return AgentAction(
                    action_type=ActionType.ACT,
                    description="Searching knowledge",
                    tool_name="knowledge_search",
                    tool_args={"query": thought.content},
                )
        
        # Default to respond
        return AgentAction(
            action_type=ActionType.RESPOND,
            description="Ready to respond",
        )
    
    def _extract_tool_args(
        self,
        thought_content: str,
        tool_name: str,
    ) -> dict[str, Any]:
        """Extract tool arguments from thought content."""
        # Simple extraction - in practice would use LLM
        return {"query": thought_content}
    
    async def _execute_action(self, action: AgentAction) -> ToolResult:
        """Execute an action using tools."""
        if action.tool_name:
            return await self._tools.execute(
                action.tool_name,
                **action.tool_args,
            )
        
        return ToolResult(success=True, result="No tool execution needed")
    
    async def _generate_response(
        self,
        query: str,
        thoughts: list[AgentThought],
        actions: list[AgentAction],
        context: Optional[dict[str, Any]],
    ) -> str:
        """Generate final response."""
        if self._llm:
            # Build response prompt
            prompt = self._build_response_prompt(query, thoughts, actions, context)
            
            response = await self._llm.generate(
                prompt=prompt,
                system_prompt=self._system_prompt,
            )
            
            return response.content
        else:
            # Fallback response
            if thoughts:
                return thoughts[-1].content
            return "I have considered your words carefully."
    
    def _build_response_prompt(
        self,
        query: str,
        thoughts: list[AgentThought],
        actions: list[AgentAction],
        context: Optional[dict[str, Any]],
    ) -> str:
        """Build prompt for final response."""
        parts = [
            f"Generate a response to: {query}",
            "\nYour reasoning:",
        ]
        
        for thought in thoughts[-3:]:
            parts.append(f"- {thought.content}")
        
        if actions:
            parts.append("\nInformation gathered:")
            for action in actions[-3:]:
                if action.result:
                    parts.append(f"- {action.result[:200]}")
        
        parts.append("\nNow respond in character:")
        
        return "\n".join(parts)
