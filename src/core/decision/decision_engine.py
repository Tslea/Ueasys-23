"""
Decision Engine - Character decision-making system.

This module provides the decision-making capabilities for characters,
allowing them to evaluate options and make choices consistent with
their personality and goals.

Example:
    >>> from src.core.decision import DecisionEngine
    >>> engine = DecisionEngine(personality=gandalf_personality)
    >>> decision = await engine.decide(
    ...     situation="Enemy approaches",
    ...     options=["fight", "flee", "negotiate"]
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings
from src.core.character.personality_core import PersonalityCore, Alignment

logger = get_logger(__name__)


class DecisionType(str, Enum):
    """Types of decisions a character can make."""
    ACTION = "action"  # Physical action
    SPEECH = "speech"  # What to say
    ATTITUDE = "attitude"  # How to feel/react
    GOAL = "goal"  # Goal-related decision
    RELATIONSHIP = "relationship"  # Relationship-related
    MORAL = "moral"  # Moral dilemma


class DecisionOption(BaseModel):
    """
    A single option for a decision.
    
    Attributes:
        option_id: Unique identifier
        description: What this option entails
        alignment_score: How well it aligns with character values
        risk_level: Risk associated (0.0 to 1.0)
        reward_potential: Potential benefit (0.0 to 1.0)
        emotional_impact: Expected emotional effect
        prerequisites: Requirements for this option
        consequences: Potential consequences
    """
    option_id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    alignment_score: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_level: float = Field(default=0.5, ge=0.0, le=1.0)
    reward_potential: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_impact: Optional[str] = None
    prerequisites: list[str] = Field(default_factory=list)
    consequences: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Decision(BaseModel):
    """
    A decision made by a character.
    
    Attributes:
        decision_id: Unique identifier
        decision_type: Type of decision
        situation: The situation prompting the decision
        chosen_option: The option that was chosen
        confidence: Confidence in the decision (0.0 to 1.0)
        reasoning: Why this option was chosen
        alternatives_considered: Other options considered
        timestamp: When the decision was made
    """
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    decision_type: DecisionType = DecisionType.ACTION
    situation: str
    chosen_option: DecisionOption
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    reasoning: str = ""
    alternatives_considered: list[DecisionOption] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DecisionContext(BaseModel):
    """
    Context for making a decision.
    
    Attributes:
        situation: Description of the situation
        urgency: How urgent (0.0 to 1.0)
        stakes: How high the stakes (0.0 to 1.0)
        emotional_state: Current emotional state
        available_resources: Resources available
        constraints: Constraints on decision
        relevant_memories: Memories relevant to decision
    """
    situation: str
    urgency: float = Field(default=0.5, ge=0.0, le=1.0)
    stakes: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_state: Optional[str] = None
    available_resources: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    relevant_memories: list[str] = Field(default_factory=list)


class DecisionEngine(LoggerMixin):
    """
    Decision-making engine for characters.
    
    Evaluates options and makes decisions based on character
    personality, values, and current context.
    
    Attributes:
        personality: Character's personality core
        decision_history: Past decisions for consistency
        
    Example:
        >>> engine = DecisionEngine(personality=gandalf)
        >>> decision = await engine.decide(
        ...     situation="Balrog blocks the bridge",
        ...     options=["fight", "flee", "sacrifice"]
        ... )
        >>> print(decision.chosen_option.description)
        "Stand and fight to protect others"
    """
    
    def __init__(
        self,
        personality: PersonalityCore,
        max_history: int = 100,
    ):
        """
        Initialize the decision engine.
        
        Args:
            personality: Character's personality core
            max_history: Maximum decisions to remember
        """
        self.personality = personality
        self._settings = get_settings()
        self._max_history = max_history
        
        # Decision history for consistency
        self._decision_history: list[Decision] = []
        
        # Alignment behavior mappings
        self._alignment_preferences = self._build_alignment_preferences()
        
        self.logger.info(
            "Initialized DecisionEngine",
            character_id=personality.character_id,
        )
    
    def _build_alignment_preferences(self) -> dict[Alignment, dict[str, float]]:
        """Build decision preferences based on alignment."""
        return {
            Alignment.LAWFUL_GOOD: {
                "help_others": 0.9,
                "follow_rules": 0.8,
                "self_sacrifice": 0.7,
                "protect_innocent": 0.9,
                "risk_tolerance": 0.6,
            },
            Alignment.NEUTRAL_GOOD: {
                "help_others": 0.8,
                "follow_rules": 0.5,
                "self_sacrifice": 0.6,
                "protect_innocent": 0.8,
                "risk_tolerance": 0.5,
            },
            Alignment.CHAOTIC_GOOD: {
                "help_others": 0.8,
                "follow_rules": 0.2,
                "self_sacrifice": 0.5,
                "protect_innocent": 0.8,
                "risk_tolerance": 0.7,
            },
            Alignment.LAWFUL_NEUTRAL: {
                "help_others": 0.5,
                "follow_rules": 0.9,
                "self_sacrifice": 0.4,
                "protect_innocent": 0.5,
                "risk_tolerance": 0.4,
            },
            Alignment.TRUE_NEUTRAL: {
                "help_others": 0.5,
                "follow_rules": 0.5,
                "self_sacrifice": 0.3,
                "protect_innocent": 0.5,
                "risk_tolerance": 0.5,
            },
            Alignment.CHAOTIC_NEUTRAL: {
                "help_others": 0.4,
                "follow_rules": 0.1,
                "self_sacrifice": 0.2,
                "protect_innocent": 0.4,
                "risk_tolerance": 0.8,
            },
            Alignment.LAWFUL_EVIL: {
                "help_others": 0.2,
                "follow_rules": 0.8,
                "self_sacrifice": 0.1,
                "protect_innocent": 0.2,
                "risk_tolerance": 0.5,
            },
            Alignment.NEUTRAL_EVIL: {
                "help_others": 0.1,
                "follow_rules": 0.3,
                "self_sacrifice": 0.0,
                "protect_innocent": 0.1,
                "risk_tolerance": 0.6,
            },
            Alignment.CHAOTIC_EVIL: {
                "help_others": 0.0,
                "follow_rules": 0.0,
                "self_sacrifice": 0.0,
                "protect_innocent": 0.0,
                "risk_tolerance": 0.9,
            },
        }
    
    async def decide(
        self,
        situation: str,
        options: list[str | DecisionOption],
        context: Optional[DecisionContext] = None,
        decision_type: DecisionType = DecisionType.ACTION,
    ) -> Decision:
        """
        Make a decision given a situation and options.
        
        Args:
            situation: Description of the situation
            options: List of options (strings or DecisionOption objects)
            context: Additional decision context
            decision_type: Type of decision being made
            
        Returns:
            Decision object with chosen option and reasoning
        """
        self.logger.info(
            "Making decision",
            character_id=self.personality.character_id,
            situation_length=len(situation),
            num_options=len(options),
        )
        
        # Convert string options to DecisionOption objects
        decision_options = []
        for opt in options:
            if isinstance(opt, str):
                decision_options.append(DecisionOption(description=opt))
            else:
                decision_options.append(opt)
        
        # Create context if not provided
        if not context:
            context = DecisionContext(situation=situation)
        
        # Evaluate each option
        scored_options = []
        for option in decision_options:
            score = self._evaluate_option(option, context)
            scored_options.append((score, option))
        
        # Sort by score
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        # Choose best option
        best_score, best_option = scored_options[0]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            best_option, context, scored_options[1:3]
        )
        
        # Create decision
        decision = Decision(
            decision_type=decision_type,
            situation=situation,
            chosen_option=best_option,
            confidence=min(1.0, best_score),
            reasoning=reasoning,
            alternatives_considered=[opt for _, opt in scored_options[1:]],
            metadata={
                "context_urgency": context.urgency,
                "context_stakes": context.stakes,
            },
        )
        
        # Store in history
        self._add_to_history(decision)
        
        self.logger.info(
            "Decision made",
            character_id=self.personality.character_id,
            chosen=best_option.description[:50],
            confidence=decision.confidence,
        )
        
        return decision
    
    def _evaluate_option(
        self,
        option: DecisionOption,
        context: DecisionContext,
    ) -> float:
        """
        Evaluate an option based on personality and context.
        
        Returns a score from 0.0 to 1.0.
        """
        score = 0.5  # Base score
        
        # Get alignment preferences
        prefs = self._alignment_preferences.get(
            self.personality.alignment,
            self._alignment_preferences[Alignment.TRUE_NEUTRAL]
        )
        
        # Factor in alignment score
        score += option.alignment_score * 0.3
        
        # Factor in risk based on risk tolerance
        risk_tolerance = prefs.get("risk_tolerance", 0.5)
        if option.risk_level > risk_tolerance:
            score -= (option.risk_level - risk_tolerance) * 0.2
        
        # Factor in reward potential
        score += option.reward_potential * 0.2
        
        # Adjust for urgency
        if context.urgency > 0.7:
            # High urgency favors quicker/more direct options
            score += 0.1
        
        # Adjust for stakes
        if context.stakes > 0.7:
            # High stakes favors safer options for good alignments
            if self.personality.alignment in [
                Alignment.LAWFUL_GOOD,
                Alignment.NEUTRAL_GOOD,
                Alignment.CHAOTIC_GOOD,
            ]:
                score -= option.risk_level * 0.1
        
        # Check against character values
        for value in self.personality.values:
            value_lower = value.name.lower()
            option_lower = option.description.lower()
            
            if value_lower in option_lower:
                score += 0.15 * (1 / value.priority)  # Higher priority = higher boost
        
        # Check against character traits
        for trait in self.personality.traits:
            trait_lower = trait.name.lower()
            option_lower = option.description.lower()
            
            if trait_lower in option_lower:
                score += 0.1 * trait.intensity
        
        # Consistency with past decisions
        consistency_score = self._check_consistency(option)
        score += consistency_score * 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_consistency(self, option: DecisionOption) -> float:
        """Check if option is consistent with past decisions."""
        if not self._decision_history:
            return 0.5
        
        # Look at recent decisions
        recent = self._decision_history[-10:]
        similar_choices = 0
        
        option_lower = option.description.lower()
        
        for decision in recent:
            chosen_lower = decision.chosen_option.description.lower()
            
            # Simple word overlap check
            option_words = set(option_lower.split())
            chosen_words = set(chosen_lower.split())
            
            overlap = len(option_words & chosen_words)
            if overlap > 2:
                similar_choices += 1
        
        return similar_choices / len(recent)
    
    def _generate_reasoning(
        self,
        chosen: DecisionOption,
        context: DecisionContext,
        alternatives: list[tuple[float, DecisionOption]],
    ) -> str:
        """Generate reasoning for the decision."""
        parts = [f"Given the situation: {context.situation[:100]}..."]
        
        # Why this option
        parts.append(f"\nI chose to {chosen.description} because:")
        
        # Alignment reason
        parts.append(f"- It aligns with my {self.personality.alignment.value} nature")
        
        # Values reason
        if self.personality.values:
            top_value = self.personality.values[0]
            parts.append(f"- It honors my value of {top_value.name}")
        
        # Risk assessment
        if chosen.risk_level < 0.3:
            parts.append("- It presents an acceptable level of risk")
        elif chosen.risk_level > 0.7:
            parts.append("- Despite the high risk, the potential reward justifies it")
        
        # Alternatives considered
        if alternatives:
            parts.append("\nAlternatives considered:")
            for score, alt in alternatives[:2]:
                parts.append(f"- {alt.description[:50]}... (rejected)")
        
        return "\n".join(parts)
    
    def _add_to_history(self, decision: Decision) -> None:
        """Add decision to history."""
        self._decision_history.append(decision)
        
        # Prune if necessary
        if len(self._decision_history) > self._max_history:
            self._decision_history = self._decision_history[-self._max_history:]
    
    async def evaluate_moral_dilemma(
        self,
        dilemma: str,
        option_a: str,
        option_b: str,
    ) -> Decision:
        """
        Evaluate a moral dilemma.
        
        Special handling for moral choices that considers
        character alignment more heavily.
        
        Args:
            dilemma: Description of the moral dilemma
            option_a: First option
            option_b: Second option
            
        Returns:
            Decision with moral reasoning
        """
        context = DecisionContext(
            situation=dilemma,
            stakes=0.9,  # Moral dilemmas are high stakes
            urgency=0.5,
        )
        
        return await self.decide(
            situation=dilemma,
            options=[option_a, option_b],
            context=context,
            decision_type=DecisionType.MORAL,
        )
    
    def get_decision_history(
        self,
        limit: int = 10,
        decision_type: Optional[DecisionType] = None,
    ) -> list[Decision]:
        """
        Get recent decision history.
        
        Args:
            limit: Maximum decisions to return
            decision_type: Filter by type
            
        Returns:
            List of recent decisions
        """
        history = self._decision_history
        
        if decision_type:
            history = [d for d in history if d.decision_type == decision_type]
        
        return history[-limit:]
    
    def get_decision_patterns(self) -> dict[str, Any]:
        """
        Analyze decision patterns.
        
        Returns statistics about decision-making patterns.
        """
        if not self._decision_history:
            return {"total_decisions": 0}
        
        total = len(self._decision_history)
        
        # Count by type
        type_counts: dict[str, int] = {}
        for d in self._decision_history:
            type_counts[d.decision_type.value] = type_counts.get(
                d.decision_type.value, 0
            ) + 1
        
        # Average confidence
        avg_confidence = sum(d.confidence for d in self._decision_history) / total
        
        return {
            "total_decisions": total,
            "decisions_by_type": type_counts,
            "average_confidence": avg_confidence,
            "character_id": self.personality.character_id,
        }
