"""
Character Agent - Main agent for character behavior.

This module provides the Character Agent that coordinates all systems
to create coherent, believable character behavior.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.core.character.character_engine import CharacterEngine
from src.core.character.personality_core import PersonalityCore
from src.core.memory.memory_manager import MemoryManager
from src.core.decision.decision_engine import DecisionEngine
from src.core.decision.goal_system import GoalSystem
from src.rag.rag_system import RAGSystem
from src.llm.base_provider import BaseLLMProvider

logger = get_logger(__name__)


class AgentState(str, Enum):
    """States of the character agent."""
    IDLE = "idle"
    THINKING = "thinking"
    RESPONDING = "responding"
    ACTING = "acting"
    REMEMBERING = "remembering"
    ERROR = "error"


class AgentContext(BaseModel):
    """Context for agent operations."""
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    turn_count: int = 0
    last_input: Optional[str] = None
    last_output: Optional[str] = None
    emotional_state: Optional[str] = None
    active_goals: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response from the character agent."""
    content: str
    action: Optional[str] = None
    emotion: Optional[str] = None
    thought_process: list[str] = Field(default_factory=list)
    context_used: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CharacterAgent(LoggerMixin):
    """
    Main agent for character behavior.
    
    Coordinates all character systems to produce coherent,
    believable behavior:
    - Personality for core identity
    - Memory for experiences
    - RAG for knowledge
    - Decision engine for choices
    - LLM for generation
    
    Example:
        >>> agent = CharacterAgent(
        ...     personality=gandalf_personality,
        ...     llm=openai_provider,
        ...     rag=rag_system
        ... )
        >>> response = await agent.respond("Tell me about the Ring")
    """
    
    def __init__(
        self,
        personality: PersonalityCore,
        llm: Optional[BaseLLMProvider] = None,
        rag: Optional[RAGSystem] = None,
        memory: Optional[MemoryManager] = None,
    ):
        """
        Initialize the character agent.
        
        Args:
            personality: Character's personality core
            llm: LLM provider for generation
            rag: RAG system for knowledge retrieval
            memory: Memory manager for experiences
        """
        self.personality = personality
        self._llm = llm
        self._rag = rag
        self._memory = memory or MemoryManager()
        
        # Initialize subsystems
        self._character_engine = CharacterEngine(personality=personality)
        self._decision_engine = DecisionEngine(personality=personality)
        self._goal_system = GoalSystem(personality=personality)
        
        # Agent state
        self._state = AgentState.IDLE
        self._context = AgentContext()
        
        self.logger.info(
            "Initialized CharacterAgent",
            character_id=personality.character_id,
            character_name=personality.name,
        )
    
    @property
    def state(self) -> AgentState:
        """Get current agent state."""
        return self._state
    
    @property
    def context(self) -> AgentContext:
        """Get current context."""
        return self._context
    
    async def respond(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Generate a response to a message.
        
        This is the main entry point for agent interactions.
        
        Args:
            message: User's message
            context: Additional context
            
        Returns:
            AgentResponse with generated content
        """
        self._state = AgentState.THINKING
        thought_process = []
        context_used = []
        
        try:
            # Update context
            self._context.turn_count += 1
            self._context.last_input = message
            
            # Step 1: Analyze input
            thought_process.append("Analyzing input message...")
            analysis = await self._analyze_input(message)
            thought_process.append(f"Intent: {analysis.get('intent', 'unknown')}")
            
            # Step 2: Check goals
            thought_process.append("Checking relevant goals...")
            relevant_goals = self._goal_system.get_relevant_goals(message)
            if relevant_goals:
                self._context.active_goals = [g.description for g in relevant_goals[:3]]
                thought_process.append(f"Active goals: {len(relevant_goals)}")
            
            # Step 3: Retrieve memories
            thought_process.append("Searching memories...")
            memories = await self._memory.retrieve(
                query=message,
                limit=5,
            )
            if memories:
                context_used.extend([m.get("summary", m.get("content", ""))[:50] for m in memories])
                thought_process.append(f"Found {len(memories)} relevant memories")
            
            # Step 4: RAG retrieval
            if self._rag:
                thought_process.append("Retrieving knowledge...")
                rag_context = await self._rag.retrieve_context(
                    character_id=self.personality.character_id,
                    query=message,
                )
                if rag_context and rag_context.results:
                    context_used.extend([r.content[:50] for r in rag_context.results[:3]])
                    thought_process.append(f"Retrieved {len(rag_context.results)} knowledge items")
            
            # Step 5: Process through character engine
            thought_process.append("Processing through character engine...")
            engine_response = await self._character_engine.process_message(
                message=message,
                context=context or {},
            )
            emotional_state = engine_response.get("emotional_state")
            self._context.emotional_state = emotional_state
            
            # Step 6: Make decisions if needed
            if analysis.get("requires_decision"):
                thought_process.append("Making decision...")
                decision = await self._decision_engine.decide(
                    situation=message,
                    options=analysis.get("options", ["respond", "ask_clarification"]),
                )
                thought_process.append(f"Decision: {decision.chosen_option.description}")
            
            # Step 7: Generate response
            self._state = AgentState.RESPONDING
            thought_process.append("Generating response...")
            
            response_content = await self._generate_response(
                message=message,
                analysis=analysis,
                memories=memories,
                engine_response=engine_response,
                context=context,
            )
            
            # Step 8: Record interaction in memory
            self._state = AgentState.REMEMBERING
            await self._memory.add_episodic(
                content=f"User said: {message[:100]}. I responded: {response_content[:100]}",
                importance=0.5,
            )
            
            self._context.last_output = response_content
            self._state = AgentState.IDLE
            
            return AgentResponse(
                content=response_content,
                emotion=emotional_state,
                thought_process=thought_process,
                context_used=context_used,
                confidence=0.8,
                metadata={
                    "turn": self._context.turn_count,
                    "goals_active": len(self._context.active_goals),
                },
            )
            
        except Exception as e:
            self._state = AgentState.ERROR
            self.logger.error("Agent error", error=str(e))
            
            return AgentResponse(
                content=self._generate_error_response(),
                thought_process=thought_process + [f"Error: {str(e)}"],
                confidence=0.3,
            )
    
    async def _analyze_input(self, message: str) -> dict[str, Any]:
        """Analyze input message to understand intent."""
        message_lower = message.lower()
        
        # Simple intent classification
        intent = "statement"
        if "?" in message:
            intent = "question"
        elif any(word in message_lower for word in ["please", "could you", "would you", "can you"]):
            intent = "request"
        elif any(word in message_lower for word in ["hello", "hi", "greetings"]):
            intent = "greeting"
        elif any(word in message_lower for word in ["goodbye", "bye", "farewell"]):
            intent = "farewell"
        
        # Check if decision needed
        requires_decision = any(
            word in message_lower
            for word in ["should", "would you", "what if", "choose"]
        )
        
        return {
            "intent": intent,
            "requires_decision": requires_decision,
            "sentiment": "neutral",  # Could use sentiment analysis
            "topics": [],  # Could extract topics
        }
    
    async def _generate_response(
        self,
        message: str,
        analysis: dict[str, Any],
        memories: list[dict[str, Any]],
        engine_response: dict[str, Any],
        context: Optional[dict[str, Any]],
    ) -> str:
        """Generate the actual response content."""
        if self._llm:
            # Build prompt with all context
            prompt = self._build_generation_prompt(
                message, analysis, memories, engine_response, context
            )
            
            system_prompt = self._build_system_prompt()
            
            llm_response = await self._llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
            )
            return llm_response.content
        else:
            # Fallback without LLM
            return self._generate_fallback_response(message, analysis)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM."""
        p = self.personality
        
        return f"""You are {p.name}, a {p.archetype.value} of {p.alignment.value} alignment.

Core traits: {', '.join(t.name for t in p.traits[:5])}
Values: {', '.join(v.name for v in p.values[:3])}
Motivations: {', '.join(p.motivations[:3])}

Stay in character at all times. Respond authentically based on your personality.
Use your characteristic speech patterns. Never break character."""

    def _build_generation_prompt(
        self,
        message: str,
        analysis: dict[str, Any],
        memories: list[dict[str, Any]],
        engine_response: dict[str, Any],
        context: Optional[dict[str, Any]],
    ) -> str:
        """Build generation prompt with all context."""
        parts = []
        
        # Add emotional state
        if engine_response.get("emotional_state"):
            parts.append(f"Current emotional state: {engine_response['emotional_state']}")
        
        # Add relevant memories
        if memories:
            parts.append("\nRelevant memories:")
            for mem in memories[:3]:
                parts.append(f"- {mem.get('content', '')[:100]}")
        
        # Add active goals
        if self._context.active_goals:
            parts.append("\nActive goals:")
            for goal in self._context.active_goals[:3]:
                parts.append(f"- {goal}")
        
        # Add the message
        parts.append(f"\nUser: {message}")
        parts.append("\nRespond in character:")
        
        return "\n".join(parts)
    
    def _generate_fallback_response(
        self,
        message: str,
        analysis: dict[str, Any],
    ) -> str:
        """Generate fallback response without LLM."""
        name = self.personality.name
        intent = analysis.get("intent", "statement")
        
        if intent == "greeting":
            return f"*{name} nods in greeting* Well met, traveler. What brings you to seek my counsel?"
        elif intent == "farewell":
            return f"*{name} inclines their head* May your path be safe. Until we meet again."
        elif intent == "question":
            return f"*{name} considers your question* That is indeed a matter worth pondering carefully."
        else:
            return f"*{name} listens thoughtfully* Your words carry weight. I shall consider them."
    
    def _generate_error_response(self) -> str:
        """Generate response when error occurs."""
        return f"*{self.personality.name} pauses, looking momentarily distant* Forgive me, my thoughts were elsewhere. Could you repeat that?"
    
    async def take_action(
        self,
        action: str,
        parameters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Have the agent take an action.
        
        Args:
            action: Action to take
            parameters: Action parameters
            
        Returns:
            Action result
        """
        self._state = AgentState.ACTING
        
        try:
            # Process action through decision engine
            decision = await self._decision_engine.decide(
                situation=f"Taking action: {action}",
                options=[action, "reconsider", "refuse"],
            )
            
            result = {
                "action": action,
                "performed": decision.chosen_option.description == action,
                "reasoning": decision.reasoning,
            }
            
            return result
            
        finally:
            self._state = AgentState.IDLE
    
    async def update_goals(
        self,
        new_goal: Optional[str] = None,
        completed_goal: Optional[str] = None,
    ) -> None:
        """
        Update agent goals.
        
        Args:
            new_goal: New goal to add
            completed_goal: Goal that was completed
        """
        if new_goal:
            await self._goal_system.add_goal(new_goal)
        
        if completed_goal:
            goals = self._goal_system.get_active_goals()
            for goal in goals:
                if goal.description == completed_goal:
                    await self._goal_system.complete_goal(goal.goal_id)
                    break
    
    def get_status(self) -> dict[str, Any]:
        """Get current agent status."""
        return {
            "character_id": self.personality.character_id,
            "name": self.personality.name,
            "state": self._state.value,
            "context": self._context.model_dump(),
            "goals": self._goal_system.get_summary(),
        }
