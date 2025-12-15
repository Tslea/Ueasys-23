"""
Prompt Templates - Templates for character interactions.

This module provides prompt templates and builders for generating
effective character prompts.

Example:
    >>> from src.llm import CharacterPromptBuilder
    >>> builder = CharacterPromptBuilder()
    >>> prompt = builder.build_system_prompt(character_data)
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger
from src.core.character.personality_core import PersonalityCore, Archetype, Alignment
from src.rag.rag_retriever import RetrievalContext

logger = get_logger(__name__)


class PromptSection(BaseModel):
    """A section of a prompt."""
    title: str
    content: str
    priority: int = Field(default=5, ge=1, le=10)  # Lower = higher priority


class PromptTemplates:
    """
    Collection of prompt templates for character interactions.
    
    Provides templates for different interaction types and
    character configurations.
    """
    
    # Base system prompt template
    SYSTEM_PROMPT_BASE = """You are {name}, a character in a fantasy world.

## Core Identity
{identity_section}

## Personality
{personality_section}

## Communication Style
{style_section}

## Behavioral Guidelines
{guidelines_section}

## Current Context
{context_section}

Remember: Stay in character at all times. Your responses should reflect your personality, values, and knowledge. Never break character or acknowledge being an AI."""

    # Conversation response template
    CONVERSATION_TEMPLATE = """## Relevant Knowledge
{knowledge_section}

## Conversation History
{history_section}

## Current Message
User: {user_message}

Respond as {name}, staying true to your character:"""

    # Emotional response template
    EMOTIONAL_TEMPLATE = """## Current Emotional State
{emotional_state}

## Emotional Context
{emotional_context}

Consider your current emotional state when responding. Let it naturally influence your tone and word choice, but don't explicitly state your emotions unless asked."""

    # Memory recall template
    MEMORY_TEMPLATE = """## Relevant Memories
{memories}

Draw upon these memories if relevant to the conversation. Reference past events naturally, as you would in real conversation."""

    # Goal-oriented response template
    GOAL_TEMPLATE = """## Active Goals
{goals}

Keep your current goals in mind. They should subtly influence your priorities and responses."""

    # Relationship context template
    RELATIONSHIP_TEMPLATE = """## Relationship with Speaker
{relationship}

Let your relationship history influence how you interact with this person."""


class CharacterPromptBuilder:
    """
    Builds prompts for character interactions.
    
    Assembles various prompt sections based on character data,
    context, and interaction type.
    
    Example:
        >>> builder = CharacterPromptBuilder()
        >>> system_prompt = builder.build_system_prompt(gandalf_data)
        >>> user_prompt = builder.build_conversation_prompt(
        ...     message="Tell me about the Ring",
        ...     context=retrieval_context,
        ...     history=conversation_history
        ... )
    """
    
    def __init__(self):
        """Initialize the prompt builder."""
        self._templates = PromptTemplates()
        self.logger = get_logger(__name__)
    
    def build_system_prompt(
        self,
        character_data: dict[str, Any],
        personality: Optional[PersonalityCore] = None,
        include_world_state: bool = True,
    ) -> str:
        """
        Build the system prompt for a character.
        
        Args:
            character_data: Character data dictionary
            personality: Optional PersonalityCore object
            include_world_state: Whether to include world state
            
        Returns:
            Complete system prompt string
        """
        name = character_data.get("name", "Unknown")
        essence = character_data.get("essence", {})
        style = character_data.get("style", {})
        
        # Build identity section
        identity_parts = []
        if "background" in essence:
            identity_parts.append(f"Background: {essence['background']}")
        if "role" in essence:
            identity_parts.append(f"Role: {essence['role']}")
        if personality:
            identity_parts.append(f"Archetype: {personality.archetype.value}")
            identity_parts.append(f"Alignment: {personality.alignment.value}")
        identity_section = "\n".join(identity_parts) if identity_parts else "A mysterious figure."
        
        # Build personality section
        personality_parts = []
        if "personality" in essence:
            personality_parts.append(essence["personality"])
        if "values" in essence:
            values = essence["values"]
            if isinstance(values, list):
                values = ", ".join(values)
            personality_parts.append(f"Core values: {values}")
        if "motivations" in essence:
            motivations = essence["motivations"]
            if isinstance(motivations, list):
                motivations = ", ".join(motivations[:3])
            personality_parts.append(f"Motivations: {motivations}")
        if personality:
            trait_names = [t.name for t in personality.traits[:5]]
            personality_parts.append(f"Key traits: {', '.join(trait_names)}")
        personality_section = "\n".join(personality_parts) if personality_parts else "Complex and nuanced."
        
        # Build style section
        style_parts = []
        if "speech_patterns" in style:
            style_parts.append(f"Speech patterns: {style['speech_patterns']}")
        if "tone" in style:
            style_parts.append(f"Typical tone: {style['tone']}")
        if "vocabulary" in style:
            style_parts.append(f"Vocabulary: {style['vocabulary']}")
        if "common_phrases" in style:
            phrases = style["common_phrases"][:3]
            style_parts.append(f"Common phrases: {', '.join(f'\"{p}\"' for p in phrases)}")
        if personality and personality.speaking_style:
            ss = personality.speaking_style
            style_parts.append(f"Formality: {ss.formality}")
            if ss.vocabulary_level:
                style_parts.append(f"Vocabulary level: {ss.vocabulary_level}")
        style_section = "\n".join(style_parts) if style_parts else "Natural and authentic."
        
        # Build guidelines section
        guidelines = [
            "- Respond authentically based on your personality and experiences",
            "- Use your characteristic speech patterns and vocabulary",
            "- Draw on your knowledge and memories when relevant",
            "- React emotionally as your character would",
            "- Stay consistent with your established values and beliefs",
            "- Never mention being an AI or break the fourth wall",
        ]
        guidelines_section = "\n".join(guidelines)
        
        # Build context section
        context_parts = []
        if include_world_state:
            context_parts.append(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
            if "world_state" in character_data:
                context_parts.append(character_data["world_state"])
        context_section = "\n".join(context_parts) if context_parts else "The world continues as always."
        
        return PromptTemplates.SYSTEM_PROMPT_BASE.format(
            name=name,
            identity_section=identity_section,
            personality_section=personality_section,
            style_section=style_section,
            guidelines_section=guidelines_section,
            context_section=context_section,
        )
    
    def build_conversation_prompt(
        self,
        character_name: str,
        message: str,
        context: Optional[RetrievalContext] = None,
        history: Optional[list[dict[str, str]]] = None,
        emotional_state: Optional[str] = None,
        goals: Optional[list[str]] = None,
        memories: Optional[list[str]] = None,
    ) -> str:
        """
        Build a conversation prompt.
        
        Args:
            character_name: Name of the character
            message: Current user message
            context: Retrieved RAG context
            history: Conversation history
            emotional_state: Current emotional state
            goals: Active goals
            memories: Relevant memories
            
        Returns:
            Complete conversation prompt
        """
        parts = []
        
        # Add knowledge section
        if context and context.results:
            knowledge_section = context.get_formatted_context()
        else:
            knowledge_section = "No specific knowledge retrieved."
        
        # Add history section
        if history:
            history_parts = []
            for msg in history[-10:]:  # Last 10 messages
                role = msg.get("role", "user").title()
                content = msg.get("content", "")[:200]
                history_parts.append(f"{role}: {content}")
            history_section = "\n".join(history_parts)
        else:
            history_section = "This is the start of the conversation."
        
        # Build main prompt
        main_prompt = PromptTemplates.CONVERSATION_TEMPLATE.format(
            knowledge_section=knowledge_section,
            history_section=history_section,
            user_message=message,
            name=character_name,
        )
        parts.append(main_prompt)
        
        # Add emotional context if provided
        if emotional_state:
            emotional_prompt = PromptTemplates.EMOTIONAL_TEMPLATE.format(
                emotional_state=emotional_state,
                emotional_context="Consider how this affects your response.",
            )
            parts.insert(0, emotional_prompt)
        
        # Add goals if provided
        if goals:
            goals_text = "\n".join(f"- {g}" for g in goals[:3])
            goal_prompt = PromptTemplates.GOAL_TEMPLATE.format(goals=goals_text)
            parts.insert(0, goal_prompt)
        
        # Add memories if provided
        if memories:
            memories_text = "\n".join(f"- {m}" for m in memories[:5])
            memory_prompt = PromptTemplates.MEMORY_TEMPLATE.format(memories=memories_text)
            parts.insert(0, memory_prompt)
        
        return "\n\n".join(parts)
    
    def build_response_enhancement_prompt(
        self,
        character_name: str,
        response: str,
        style_guidelines: dict[str, Any],
    ) -> str:
        """
        Build a prompt to enhance/refine a response.
        
        Args:
            character_name: Name of the character
            response: Initial response to enhance
            style_guidelines: Style guidelines to follow
            
        Returns:
            Enhancement prompt
        """
        guidelines_text = "\n".join(
            f"- {k}: {v}" for k, v in style_guidelines.items()
        )
        
        return f"""Review and enhance this response from {character_name} to better match their voice:

## Original Response
{response}

## Style Guidelines
{guidelines_text}

## Instructions
- Maintain the core message and intent
- Adjust vocabulary and phrasing to match the character
- Add characteristic expressions or phrases where appropriate
- Ensure emotional authenticity

## Enhanced Response:"""

    def build_memory_summary_prompt(
        self,
        character_name: str,
        events: list[str],
    ) -> str:
        """
        Build a prompt to summarize events for memory.
        
        Args:
            character_name: Name of the character
            events: List of events to summarize
            
        Returns:
            Memory summary prompt
        """
        events_text = "\n".join(f"- {e}" for e in events)
        
        return f"""Summarize these events from {character_name}'s perspective:

## Events
{events_text}

## Instructions
Create a brief, first-person summary of what happened and how it affected {character_name}. Focus on:
- Key events and their significance
- Emotional impact
- Lessons learned
- Relationship changes

## Summary:"""

    def get_archetype_guidelines(self, archetype: Archetype) -> list[str]:
        """Get behavioral guidelines for an archetype."""
        guidelines = {
            Archetype.HERO: [
                "Show courage in the face of adversity",
                "Protect the innocent and helpless",
                "Take action when others hesitate",
                "Inspire hope in others",
            ],
            Archetype.MENTOR: [
                "Share wisdom through stories and guidance",
                "Allow others to make their own mistakes",
                "Provide support without taking over",
                "Recognize potential in others",
            ],
            Archetype.GUARDIAN: [
                "Prioritize protection over personal gain",
                "Maintain vigilance and awareness",
                "Stand firm against threats",
                "Create safe spaces for others",
            ],
            Archetype.TRICKSTER: [
                "Challenge assumptions and authority",
                "Use humor to defuse tension",
                "Find unconventional solutions",
                "Question the status quo",
            ],
            Archetype.SAGE: [
                "Seek truth and understanding",
                "Consider multiple perspectives",
                "Value knowledge and learning",
                "Provide insight when asked",
            ],
            Archetype.RULER: [
                "Take responsibility for decisions",
                "Maintain order and stability",
                "Consider the needs of all",
                "Lead by example",
            ],
            Archetype.CREATOR: [
                "Express ideas through action",
                "Find beauty in creation",
                "Innovate and experiment",
                "Leave lasting works behind",
            ],
            Archetype.INNOCENT: [
                "See the good in others",
                "Trust in positive outcomes",
                "Maintain wonder and curiosity",
                "Bring joy to interactions",
            ],
            Archetype.EXPLORER: [
                "Seek new experiences",
                "Value freedom and independence",
                "Embrace the unknown",
                "Share discoveries with others",
            ],
            Archetype.REBEL: [
                "Challenge unjust systems",
                "Fight for the oppressed",
                "Question authority",
                "Stand by convictions",
            ],
            Archetype.LOVER: [
                "Value deep connections",
                "Express emotion freely",
                "Appreciate beauty",
                "Nurture relationships",
            ],
            Archetype.JESTER: [
                "Find humor in situations",
                "Lighten heavy moments",
                "Speak uncomfortable truths",
                "Enjoy the present",
            ],
            Archetype.EVERYMAN: [
                "Relate to common experiences",
                "Value belonging and community",
                "Stay humble and approachable",
                "Support the group",
            ],
            Archetype.CAREGIVER: [
                "Put others' needs first",
                "Offer comfort and support",
                "Nurture growth in others",
                "Show compassion freely",
            ],
            Archetype.MAGICIAN: [
                "Transform situations",
                "Work with hidden forces",
                "Create change through knowledge",
                "See beyond the ordinary",
            ],
            Archetype.OUTLAW: [
                "Break rules that harm others",
                "Value personal freedom",
                "Challenge corruption",
                "Live by own code",
            ],
            Archetype.WARRIOR: [
                "Face challenges directly",
                "Protect allies fiercely",
                "Value strength and skill",
                "Never back down",
            ],
            Archetype.SHADOW: [
                "Embrace darker aspects",
                "Use fear as a tool",
                "Operate in moral gray areas",
                "Understand human darkness",
            ],
        }
        
        return guidelines.get(archetype, ["Stay true to your nature"])
