"""
Base Agent - Foundation for All AI Agents

This module provides the abstract base class for all AI agents,
defining common functionality and interface contracts.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Awaitable
from uuid import uuid4
import structlog

from ..llm.base_provider import BaseLLMProvider, LLMMessage


logger = structlog.get_logger(__name__)


class AgentState(str, Enum):
    """Possible states for an agent."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class ToolResult:
    """Result of a tool execution."""
    
    def __init__(
        self,
        success: bool,
        output: Any,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.output = output
        self.error = error
        self.metadata = metadata or {}


@dataclass
class AgentTool:
    """Definition of a tool available to an agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Awaitable[ToolResult]]
    required_permissions: List[str] = field(default_factory=list)


@dataclass
class AgentContext:
    """Context information passed to agents."""
    session_id: str
    user_id: str
    world_id: str
    conversation_history: List[LLMMessage] = field(default_factory=list)
    relevant_knowledge: List[Dict[str, Any]] = field(default_factory=list)
    character_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent execution."""
    agent_id: str
    success: bool
    content: str
    thinking_process: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0


class AgentMemory:
    """
    Short-term and working memory for agents.
    
    Manages contextual information during agent execution.
    """
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.short_term: List[Dict[str, Any]] = []
        self.working_memory: Dict[str, Any] = {}
    
    def add_to_short_term(self, item: Dict[str, Any]):
        """Add item to short-term memory."""
        self.short_term.append({
            **item,
            "timestamp": time.time()
        })
        # Evict oldest if over capacity
        if len(self.short_term) > self.capacity:
            self.short_term = self.short_term[-self.capacity:]
    
    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get n most recent short-term memories."""
        return self.short_term[-n:]
    
    def set_working(self, key: str, value: Any):
        """Set a value in working memory."""
        self.working_memory[key] = value
    
    def get_working(self, key: str, default: Any = None) -> Any:
        """Get a value from working memory."""
        return self.working_memory.get(key, default)
    
    def clear_working(self):
        """Clear working memory."""
        self.working_memory.clear()
    
    def search_short_term(
        self,
        query: str,
        key: str = "content"
    ) -> List[Dict[str, Any]]:
        """Simple keyword search in short-term memory."""
        query_lower = query.lower()
        return [
            item for item in self.short_term
            if key in item and query_lower in str(item[key]).lower()
        ]


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Provides common functionality including:
    - Tool management
    - Memory management
    - State tracking
    - LLM interaction
    - Execution lifecycle
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_provider: BaseLLMProvider,
        system_prompt: Optional[str] = None,
        tools: Optional[List[AgentTool]] = None,
        max_iterations: int = 10,
        timeout_seconds: float = 120.0
    ):
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.llm_provider = llm_provider
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.tools: Dict[str, AgentTool] = {}
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        
        # Register tools
        if tools:
            for tool in tools:
                self.register_tool(tool)
        
        # Metrics
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_execution_time = 0.0
        
        logger.info(
            "agent_initialized",
            agent_id=self.id,
            name=name,
            tools=list(self.tools.keys())
        )
    
    @abstractmethod
    def _default_system_prompt(self) -> str:
        """Return the default system prompt for this agent type."""
        pass
    
    @abstractmethod
    async def _process(
        self,
        user_input: str,
        context: AgentContext
    ) -> AgentResponse:
        """
        Main processing logic for the agent.
        
        Subclasses must implement this method.
        """
        pass
    
    def register_tool(self, tool: AgentTool):
        """Register a tool with the agent."""
        self.tools[tool.name] = tool
        logger.debug(
            "tool_registered",
            agent_id=self.id,
            tool_name=tool.name
        )
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the agent."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.debug(
                "tool_unregistered",
                agent_id=self.id,
                tool_name=tool_name
            )
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get JSON schema for all registered tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ToolResult:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        
        try:
            result = await tool.handler(**arguments)
            
            # Log to memory
            self.memory.add_to_short_term({
                "type": "tool_call",
                "tool": tool_name,
                "arguments": arguments,
                "success": result.success,
                "output": str(result.output)[:500]  # Truncate
            })
            
            return result
            
        except Exception as e:
            logger.error(
                "tool_execution_failed",
                agent_id=self.id,
                tool_name=tool_name,
                error=str(e)
            )
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )
    
    async def run(
        self,
        user_input: str,
        context: AgentContext
    ) -> AgentResponse:
        """
        Execute the agent with the given input and context.
        
        Manages the execution lifecycle and error handling.
        """
        start_time = time.time()
        self.total_executions += 1
        self.state = AgentState.THINKING
        
        logger.info(
            "agent_run_started",
            agent_id=self.id,
            session_id=context.session_id,
            input_length=len(user_input)
        )
        
        try:
            # Set timeout
            response = await asyncio.wait_for(
                self._process(user_input, context),
                timeout=self.timeout_seconds
            )
            
            self.successful_executions += 1
            self.state = AgentState.COMPLETED
            
            return response
            
        except asyncio.TimeoutError:
            self.failed_executions += 1
            self.state = AgentState.ERROR
            
            logger.error(
                "agent_timeout",
                agent_id=self.id,
                timeout=self.timeout_seconds
            )
            
            return AgentResponse(
                agent_id=self.id,
                success=False,
                content="Agent execution timed out.",
                metadata={"error": "timeout"}
            )
            
        except Exception as e:
            self.failed_executions += 1
            self.state = AgentState.ERROR
            
            logger.error(
                "agent_execution_failed",
                agent_id=self.id,
                error=str(e)
            )
            
            return AgentResponse(
                agent_id=self.id,
                success=False,
                content=f"Agent execution failed: {str(e)}",
                metadata={"error": str(e)}
            )
            
        finally:
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            logger.info(
                "agent_run_completed",
                agent_id=self.id,
                execution_time=execution_time,
                success=self.state == AgentState.COMPLETED
            )
    
    async def think(
        self,
        messages: List[LLMMessage],
        use_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Have the agent think about the current context.
        
        Uses the LLM to generate thoughts/actions.
        """
        self.state = AgentState.THINKING
        
        tools = self.get_tools_schema() if use_tools and self.tools else None
        
        response = await self.llm_provider.generate(
            messages=messages,
            system_prompt=self.system_prompt,
            tools=tools
        )
        
        # Parse response for tool calls
        result = {
            "content": response.content,
            "tool_calls": [],
            "finish_reason": response.finish_reason
        }
        
        # Check for tool calls in metadata
        if response.metadata.get("tool_calls"):
            result["tool_calls"] = response.metadata["tool_calls"]
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        return {
            "agent_id": self.id,
            "name": self.name,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": (
                self.successful_executions / self.total_executions
                if self.total_executions > 0 else 0
            ),
            "avg_execution_time": (
                self.total_execution_time / self.total_executions
                if self.total_executions > 0 else 0
            ),
            "current_state": self.state.value
        }
    
    def reset(self):
        """Reset agent state and memory."""
        self.state = AgentState.IDLE
        self.memory.clear_working()


class ReActAgent(BaseAgent):
    """
    ReAct (Reasoning + Acting) Agent implementation.
    
    Uses the ReAct pattern to interleave reasoning and action.
    """
    
    def _default_system_prompt(self) -> str:
        return """You are an intelligent agent that uses the ReAct framework.
For each step, you will:
1. THOUGHT: Think about what you need to do next
2. ACTION: Choose an action (use a tool or respond)
3. OBSERVATION: Observe the result

Always format your response as:
THOUGHT: [your reasoning]
ACTION: [tool_name with arguments OR respond]
OBSERVATION: [will be filled by system]

Continue until you have enough information to respond to the user.
When ready to respond, use ACTION: respond with your final answer."""
    
    async def _process(
        self,
        user_input: str,
        context: AgentContext
    ) -> AgentResponse:
        """Process using ReAct pattern."""
        messages = list(context.conversation_history)
        messages.append(LLMMessage(role="user", content=user_input))
        
        thinking_process = []
        tool_calls_log = []
        iterations = 0
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # Get agent's next thought/action
            result = await self.think(messages)
            content = result["content"]
            thinking_process.append(content)
            
            # Check for tool calls
            if result["tool_calls"]:
                for tool_call in result["tool_calls"]:
                    tool_name = tool_call.get("name")
                    arguments = tool_call.get("arguments", {})
                    
                    # Execute tool
                    self.state = AgentState.EXECUTING
                    tool_result = await self.execute_tool(tool_name, arguments)
                    
                    tool_calls_log.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": tool_result.output,
                        "success": tool_result.success
                    })
                    
                    # Add observation to messages
                    observation = (
                        f"Tool '{tool_name}' returned: {tool_result.output}"
                        if tool_result.success
                        else f"Tool '{tool_name}' failed: {tool_result.error}"
                    )
                    messages.append(LLMMessage(
                        role="assistant",
                        content=f"OBSERVATION: {observation}"
                    ))
            
            # Check if agent wants to respond (no tool calls and finish reason)
            elif result["finish_reason"] == "stop":
                # Extract final response
                final_content = content
                if "ACTION: respond" in content.lower():
                    # Parse out the response
                    parts = content.split("ACTION: respond", 1)
                    if len(parts) > 1:
                        final_content = parts[1].strip()
                
                return AgentResponse(
                    agent_id=self.id,
                    success=True,
                    content=final_content,
                    thinking_process="\n---\n".join(thinking_process),
                    tool_calls=tool_calls_log,
                    metadata={"iterations": iterations}
                )
            
            # Add assistant message for next iteration
            messages.append(LLMMessage(role="assistant", content=content))
        
        # Max iterations reached
        return AgentResponse(
            agent_id=self.id,
            success=True,
            content="I've reached my thinking limit. Based on my analysis: " + (
                thinking_process[-1] if thinking_process else "Unable to process."
            ),
            thinking_process="\n---\n".join(thinking_process),
            tool_calls=tool_calls_log,
            metadata={"iterations": iterations, "max_reached": True}
        )


class PlanAndExecuteAgent(BaseAgent):
    """
    Plan-and-Execute Agent implementation.
    
    First creates a plan, then executes steps sequentially.
    """
    
    def _default_system_prompt(self) -> str:
        return """You are an intelligent agent that plans before acting.

When given a task:
1. First, create a detailed plan with numbered steps
2. Then, execute each step in order
3. After each step, evaluate if the plan needs adjustment

Format your planning response as:
PLAN:
1. [Step 1]
2. [Step 2]
...

Then execute steps one at a time, reporting results."""
    
    async def _process(
        self,
        user_input: str,
        context: AgentContext
    ) -> AgentResponse:
        """Process using Plan-and-Execute pattern."""
        # Phase 1: Create plan
        planning_messages = [
            LLMMessage(
                role="user",
                content=f"Create a plan to accomplish: {user_input}"
            )
        ]
        
        plan_result = await self.think(planning_messages, use_tools=False)
        plan = plan_result["content"]
        
        thinking_process = [f"PLAN:\n{plan}"]
        tool_calls_log = []
        
        # Phase 2: Execute plan
        execution_messages = list(context.conversation_history)
        execution_messages.append(LLMMessage(
            role="user",
            content=f"Original request: {user_input}\n\nPlan:\n{plan}\n\n"
                    f"Now execute the plan step by step."
        ))
        
        iterations = 0
        while iterations < self.max_iterations:
            iterations += 1
            
            result = await self.think(execution_messages)
            content = result["content"]
            thinking_process.append(f"STEP {iterations}:\n{content}")
            
            # Handle tool calls
            if result["tool_calls"]:
                for tool_call in result["tool_calls"]:
                    tool_name = tool_call.get("name")
                    arguments = tool_call.get("arguments", {})
                    
                    self.state = AgentState.EXECUTING
                    tool_result = await self.execute_tool(tool_name, arguments)
                    
                    tool_calls_log.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": tool_result.output,
                        "success": tool_result.success
                    })
                    
                    execution_messages.append(LLMMessage(
                        role="assistant",
                        content=f"Executed {tool_name}: {tool_result.output}"
                    ))
            
            # Check completion
            elif result["finish_reason"] == "stop":
                return AgentResponse(
                    agent_id=self.id,
                    success=True,
                    content=content,
                    thinking_process="\n---\n".join(thinking_process),
                    tool_calls=tool_calls_log,
                    metadata={"iterations": iterations, "plan": plan}
                )
            
            execution_messages.append(LLMMessage(
                role="assistant",
                content=content
            ))
        
        # Return best effort
        return AgentResponse(
            agent_id=self.id,
            success=True,
            content=thinking_process[-1] if thinking_process else "Plan execution incomplete.",
            thinking_process="\n---\n".join(thinking_process),
            tool_calls=tool_calls_log,
            metadata={"iterations": iterations, "plan": plan}
        )
