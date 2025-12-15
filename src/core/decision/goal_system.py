"""
Goal System - Manages character goals and motivations.

This module provides goal management for characters, tracking
their objectives and motivations over time.

Example:
    >>> from src.core.decision import GoalSystem, Goal
    >>> goals = GoalSystem(personality=gandalf)
    >>> await goals.add_goal("Defeat Sauron", priority=1)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.core.character.personality_core import PersonalityCore

logger = get_logger(__name__)


class GoalStatus(str, Enum):
    """Status of a goal."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    BLOCKED = "blocked"
    DORMANT = "dormant"  # Low priority, not actively pursued


class GoalType(str, Enum):
    """Types of character goals."""
    MISSION = "mission"  # Core mission/quest
    PERSONAL = "personal"  # Personal development
    RELATIONSHIP = "relationship"  # Relationship goals
    SURVIVAL = "survival"  # Survival needs
    KNOWLEDGE = "knowledge"  # Learning/discovery
    MORAL = "moral"  # Moral objectives


class Goal(BaseModel):
    """
    A character goal.
    
    Attributes:
        goal_id: Unique identifier
        description: What the goal is
        goal_type: Type of goal
        status: Current status
        priority: Priority (1 = highest)
        progress: Progress toward goal (0.0 to 1.0)
        parent_goal: Parent goal if this is a sub-goal
        sub_goals: Child goals
        blockers: What's blocking progress
        created_at: When the goal was created
        deadline: Optional deadline
        motivation: Why this goal matters
    """
    goal_id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    goal_type: GoalType = GoalType.MISSION
    status: GoalStatus = GoalStatus.ACTIVE
    priority: int = Field(default=5, ge=1, le=10)
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    parent_goal: Optional[str] = None  # goal_id
    sub_goals: list[str] = Field(default_factory=list)  # goal_ids
    blockers: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    motivation: str = ""
    completion_criteria: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    def update_progress(self, amount: float) -> None:
        """Update goal progress."""
        self.progress = max(0.0, min(1.0, self.progress + amount))
        if self.progress >= 1.0:
            self.status = GoalStatus.COMPLETED
    
    def add_blocker(self, blocker: str) -> None:
        """Add a blocker."""
        if blocker not in self.blockers:
            self.blockers.append(blocker)
        if self.status == GoalStatus.ACTIVE:
            self.status = GoalStatus.BLOCKED
    
    def remove_blocker(self, blocker: str) -> None:
        """Remove a blocker."""
        if blocker in self.blockers:
            self.blockers.remove(blocker)
        if not self.blockers and self.status == GoalStatus.BLOCKED:
            self.status = GoalStatus.ACTIVE
    
    def is_urgent(self) -> bool:
        """Check if goal is urgent (deadline approaching or high priority)."""
        if self.priority <= 2:
            return True
        if self.deadline:
            time_left = (self.deadline - datetime.now()).days
            return time_left <= 3
        return False


class GoalSystem(LoggerMixin):
    """
    Goal management system for characters.
    
    Tracks and manages character goals, motivations, and objectives.
    
    Attributes:
        personality: Character's personality core
        goals: All goals (active and historical)
        
    Example:
        >>> system = GoalSystem(personality=gandalf)
        >>> goal = await system.add_goal(
        ...     description="Guide Frodo to Mount Doom",
        ...     goal_type=GoalType.MISSION,
        ...     priority=1
        ... )
    """
    
    def __init__(
        self,
        personality: PersonalityCore,
    ):
        """
        Initialize the goal system.
        
        Args:
            personality: Character's personality core
        """
        self.personality = personality
        
        # All goals
        self._goals: dict[str, Goal] = {}
        
        # Initialize default goals from personality
        self._init_default_goals()
        
        self.logger.info(
            "Initialized GoalSystem",
            character_id=personality.character_id,
        )
    
    def _init_default_goals(self) -> None:
        """Initialize default goals from personality motivations."""
        for i, motivation in enumerate(self.personality.motivations[:3]):
            goal = Goal(
                description=motivation,
                goal_type=GoalType.PERSONAL,
                priority=i + 1,
                motivation="Core character motivation",
            )
            self._goals[goal.goal_id] = goal
    
    async def add_goal(
        self,
        description: str,
        goal_type: GoalType = GoalType.MISSION,
        priority: int = 5,
        parent_goal: Optional[str] = None,
        motivation: str = "",
        completion_criteria: Optional[list[str]] = None,
        deadline: Optional[datetime] = None,
        **metadata: Any,
    ) -> Goal:
        """
        Add a new goal.
        
        Args:
            description: Goal description
            goal_type: Type of goal
            priority: Priority (1 = highest)
            parent_goal: Parent goal ID if sub-goal
            motivation: Why this goal matters
            completion_criteria: How to know it's complete
            deadline: Optional deadline
            **metadata: Additional metadata
            
        Returns:
            The created goal
        """
        goal = Goal(
            description=description,
            goal_type=goal_type,
            priority=priority,
            parent_goal=parent_goal,
            motivation=motivation,
            completion_criteria=completion_criteria or [],
            deadline=deadline,
            metadata=metadata,
        )
        
        self._goals[goal.goal_id] = goal
        
        # Update parent if exists
        if parent_goal and parent_goal in self._goals:
            self._goals[parent_goal].sub_goals.append(goal.goal_id)
        
        self.logger.info(
            "Added goal",
            character_id=self.personality.character_id,
            goal_id=goal.goal_id,
            description=description[:50],
            priority=priority,
        )
        
        return goal
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        return self._goals.get(goal_id)
    
    def get_active_goals(self) -> list[Goal]:
        """Get all active goals sorted by priority."""
        active = [
            g for g in self._goals.values()
            if g.status == GoalStatus.ACTIVE
        ]
        return sorted(active, key=lambda g: g.priority)
    
    def get_top_priority_goal(self) -> Optional[Goal]:
        """Get the highest priority active goal."""
        active = self.get_active_goals()
        return active[0] if active else None
    
    def get_goals_by_type(self, goal_type: GoalType) -> list[Goal]:
        """Get all goals of a specific type."""
        return [
            g for g in self._goals.values()
            if g.goal_type == goal_type
        ]
    
    def get_blocked_goals(self) -> list[Goal]:
        """Get all blocked goals."""
        return [
            g for g in self._goals.values()
            if g.status == GoalStatus.BLOCKED
        ]
    
    async def update_progress(
        self,
        goal_id: str,
        progress: float,
        note: str = "",
    ) -> bool:
        """
        Update progress on a goal.
        
        Args:
            goal_id: Goal to update
            progress: Progress to add (0.0 to 1.0)
            note: Optional note about the progress
            
        Returns:
            True if goal was found and updated
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        
        old_progress = goal.progress
        goal.update_progress(progress)
        
        self.logger.info(
            "Updated goal progress",
            goal_id=goal_id,
            old_progress=old_progress,
            new_progress=goal.progress,
            note=note,
        )
        
        # If completed, update parent progress
        if goal.status == GoalStatus.COMPLETED and goal.parent_goal:
            parent = self._goals.get(goal.parent_goal)
            if parent:
                # Calculate parent progress from sub-goals
                completed_subs = sum(
                    1 for sid in parent.sub_goals
                    if self._goals.get(sid) and
                    self._goals[sid].status == GoalStatus.COMPLETED
                )
                parent_progress = completed_subs / len(parent.sub_goals) if parent.sub_goals else 1.0
                parent.progress = parent_progress
        
        return True
    
    async def complete_goal(
        self,
        goal_id: str,
        success: bool = True,
    ) -> bool:
        """
        Mark a goal as completed.
        
        Args:
            goal_id: Goal to complete
            success: Whether goal was achieved successfully
            
        Returns:
            True if goal was found and updated
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        
        goal.status = GoalStatus.COMPLETED if success else GoalStatus.FAILED
        goal.progress = 1.0 if success else goal.progress
        
        self.logger.info(
            "Completed goal",
            goal_id=goal_id,
            success=success,
        )
        
        return True
    
    async def abandon_goal(
        self,
        goal_id: str,
        reason: str = "",
    ) -> bool:
        """
        Abandon a goal.
        
        Args:
            goal_id: Goal to abandon
            reason: Why it's being abandoned
            
        Returns:
            True if goal was found and updated
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        
        goal.status = GoalStatus.ABANDONED
        goal.metadata["abandon_reason"] = reason
        
        self.logger.info(
            "Abandoned goal",
            goal_id=goal_id,
            reason=reason,
        )
        
        return True
    
    def get_relevant_goals(self, context: str) -> list[Goal]:
        """
        Get goals relevant to a given context.
        
        Args:
            context: Context to match against
            
        Returns:
            List of relevant active goals
        """
        context_lower = context.lower()
        relevant = []
        
        for goal in self.get_active_goals():
            # Simple text matching (Phase 2 will use embeddings)
            if any(
                word in context_lower
                for word in goal.description.lower().split()
                if len(word) > 3
            ):
                relevant.append(goal)
        
        return relevant
    
    def generate_goal_prompt_section(self) -> str:
        """
        Generate a prompt section describing current goals.
        
        Returns:
            Formatted string for LLM prompt
        """
        active_goals = self.get_active_goals()
        
        if not active_goals:
            return "\n## Current Goals\nNo active goals at the moment."
        
        lines = ["\n## Current Goals"]
        
        for goal in active_goals[:5]:  # Top 5 goals
            status_icon = "🎯" if goal.is_urgent() else "📌"
            progress_bar = "█" * int(goal.progress * 10) + "░" * (10 - int(goal.progress * 10))
            lines.append(
                f"{status_icon} **{goal.description}** [{progress_bar}] {goal.progress:.0%}"
            )
            if goal.motivation:
                lines.append(f"   _Motivation: {goal.motivation}_")
        
        blocked = self.get_blocked_goals()
        if blocked:
            lines.append("\n### Blocked Goals")
            for goal in blocked[:3]:
                lines.append(f"⛔ {goal.description} - Blocked by: {', '.join(goal.blockers)}")
        
        return "\n".join(lines)
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of goal system."""
        all_goals = list(self._goals.values())
        
        return {
            "total_goals": len(all_goals),
            "active": sum(1 for g in all_goals if g.status == GoalStatus.ACTIVE),
            "completed": sum(1 for g in all_goals if g.status == GoalStatus.COMPLETED),
            "blocked": sum(1 for g in all_goals if g.status == GoalStatus.BLOCKED),
            "failed": sum(1 for g in all_goals if g.status == GoalStatus.FAILED),
            "by_type": {
                gt.value: sum(1 for g in all_goals if g.goal_type == gt)
                for gt in GoalType
            },
            "top_priority": (
                self.get_top_priority_goal().description[:50]
                if self.get_top_priority_goal()
                else None
            ),
        }
