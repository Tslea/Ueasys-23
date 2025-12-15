"""
Action Planner - Plans sequences of actions for characters.

This module provides action planning capabilities, allowing characters
to plan multi-step actions to achieve goals.

Example:
    >>> from src.core.decision import ActionPlanner
    >>> planner = ActionPlanner(personality=gandalf)
    >>> plan = await planner.create_plan("Reach Rivendell safely")
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.core.character.personality_core import PersonalityCore

logger = get_logger(__name__)


class ActionStatus(str, Enum):
    """Status of a planned action."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ActionPriority(str, Enum):
    """Priority level for actions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PlannedAction(BaseModel):
    """
    A single action in a plan.
    
    Attributes:
        action_id: Unique identifier
        description: What the action is
        status: Current status
        priority: Priority level
        prerequisites: Actions that must complete first
        estimated_duration: Estimated time to complete
        actual_duration: Actual time taken
        success_criteria: How to determine success
        fallback_actions: Actions if this fails
    """
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    status: ActionStatus = ActionStatus.PENDING
    priority: ActionPriority = ActionPriority.MEDIUM
    prerequisites: list[str] = Field(default_factory=list)  # Action IDs
    estimated_duration: Optional[int] = None  # In minutes
    actual_duration: Optional[int] = None
    success_criteria: list[str] = Field(default_factory=list)
    fallback_actions: list[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    def start(self) -> None:
        """Mark action as started."""
        self.status = ActionStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, success: bool = True) -> None:
        """Mark action as completed."""
        self.status = ActionStatus.COMPLETED if success else ActionStatus.FAILED
        self.completed_at = datetime.now()
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.actual_duration = int(delta.total_seconds() / 60)
    
    def block(self) -> None:
        """Mark action as blocked."""
        self.status = ActionStatus.BLOCKED
    
    def cancel(self) -> None:
        """Cancel the action."""
        self.status = ActionStatus.CANCELLED


class ActionPlan(BaseModel):
    """
    A complete action plan.
    
    Attributes:
        plan_id: Unique identifier
        goal: The goal this plan achieves
        actions: List of planned actions
        status: Overall plan status
        created_at: When the plan was created
        priority: Overall priority
        constraints: Constraints on the plan
    """
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str
    actions: list[PlannedAction] = Field(default_factory=list)
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    priority: ActionPriority = ActionPriority.MEDIUM
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    @property
    def progress(self) -> float:
        """Calculate plan progress (0.0 to 1.0)."""
        if not self.actions:
            return 0.0
        completed = sum(
            1 for a in self.actions
            if a.status == ActionStatus.COMPLETED
        )
        return completed / len(self.actions)
    
    @property
    def next_action(self) -> Optional[PlannedAction]:
        """Get the next action to execute."""
        for action in self.actions:
            if action.status == ActionStatus.PENDING:
                # Check prerequisites
                prereqs_met = all(
                    self._get_action(pid).status == ActionStatus.COMPLETED
                    for pid in action.prerequisites
                    if self._get_action(pid)
                )
                if prereqs_met:
                    return action
        return None
    
    def _get_action(self, action_id: str) -> Optional[PlannedAction]:
        """Get action by ID."""
        for action in self.actions:
            if action.action_id == action_id:
                return action
        return None
    
    def add_action(
        self,
        description: str,
        priority: ActionPriority = ActionPriority.MEDIUM,
        prerequisites: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> PlannedAction:
        """Add an action to the plan."""
        action = PlannedAction(
            description=description,
            priority=priority,
            prerequisites=prerequisites or [],
            **kwargs,
        )
        self.actions.append(action)
        return action
    
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return all(
            a.status in [ActionStatus.COMPLETED, ActionStatus.CANCELLED]
            for a in self.actions
        )
    
    def has_failed(self) -> bool:
        """Check if any critical action has failed."""
        return any(
            a.status == ActionStatus.FAILED and a.priority == ActionPriority.CRITICAL
            for a in self.actions
        )


class ActionPlanner(LoggerMixin):
    """
    Action planner for character behavior.
    
    Creates and manages action plans for achieving goals.
    
    Attributes:
        personality: Character's personality core
        active_plans: Currently active plans
        
    Example:
        >>> planner = ActionPlanner(personality=gandalf)
        >>> plan = await planner.create_plan(
        ...     goal="Guide the Fellowship to Mordor",
        ...     constraints=["Avoid detection by Sauron"]
        ... )
    """
    
    def __init__(
        self,
        personality: PersonalityCore,
        max_active_plans: int = 5,
    ):
        """
        Initialize the action planner.
        
        Args:
            personality: Character's personality core
            max_active_plans: Maximum concurrent plans
        """
        self.personality = personality
        self._max_active_plans = max_active_plans
        
        # Active plans
        self._active_plans: dict[str, ActionPlan] = {}
        
        # Completed plans history
        self._plan_history: list[ActionPlan] = []
        
        self.logger.info(
            "Initialized ActionPlanner",
            character_id=personality.character_id,
        )
    
    async def create_plan(
        self,
        goal: str,
        constraints: Optional[list[str]] = None,
        priority: ActionPriority = ActionPriority.MEDIUM,
        context: Optional[dict[str, Any]] = None,
    ) -> ActionPlan:
        """
        Create an action plan for a goal.
        
        Args:
            goal: The goal to achieve
            constraints: Constraints on the plan
            priority: Priority of the plan
            context: Additional context
            
        Returns:
            ActionPlan with planned actions
        """
        self.logger.info(
            "Creating action plan",
            character_id=self.personality.character_id,
            goal=goal[:50],
        )
        
        # Create plan
        plan = ActionPlan(
            goal=goal,
            priority=priority,
            constraints=constraints or [],
            metadata=context or {},
        )
        
        # Generate actions based on goal
        actions = await self._generate_actions(goal, constraints or [], context or {})
        
        for action_desc in actions:
            plan.add_action(action_desc)
        
        # Store active plan
        if len(self._active_plans) >= self._max_active_plans:
            # Remove oldest completed plan
            for pid, p in list(self._active_plans.items()):
                if p.is_complete():
                    self._plan_history.append(p)
                    del self._active_plans[pid]
                    break
        
        self._active_plans[plan.plan_id] = plan
        
        self.logger.info(
            "Action plan created",
            plan_id=plan.plan_id,
            num_actions=len(plan.actions),
        )
        
        return plan
    
    async def _generate_actions(
        self,
        goal: str,
        constraints: list[str],
        context: dict[str, Any],
    ) -> list[str]:
        """
        Generate actions for a goal.
        
        This is a simplified implementation. Phase 2 will use
        LLM for more sophisticated planning.
        """
        goal_lower = goal.lower()
        actions = []
        
        # Generic action patterns
        if "reach" in goal_lower or "go to" in goal_lower:
            actions.extend([
                "Assess the current situation and resources",
                "Determine the safest route",
                "Prepare for the journey",
                "Begin traveling",
                "Monitor for threats during travel",
                "Arrive at destination",
            ])
        elif "protect" in goal_lower or "defend" in goal_lower:
            actions.extend([
                "Identify the threat",
                "Assess defensive options",
                "Position for defense",
                "Engage the threat if necessary",
                "Ensure safety of protected parties",
            ])
        elif "find" in goal_lower or "search" in goal_lower:
            actions.extend([
                "Gather information about the target",
                "Identify likely locations",
                "Search systematically",
                "Follow leads and clues",
                "Confirm when found",
            ])
        elif "help" in goal_lower or "assist" in goal_lower:
            actions.extend([
                "Understand what help is needed",
                "Assess available resources",
                "Provide immediate assistance",
                "Ensure ongoing support if needed",
            ])
        else:
            # Generic plan
            actions.extend([
                "Analyze the goal and requirements",
                "Develop a strategy",
                "Execute the strategy",
                "Monitor progress",
                "Complete the objective",
            ])
        
        # Add constraint-based actions
        for constraint in constraints:
            if "avoid" in constraint.lower():
                actions.insert(1, f"Plan to {constraint}")
            elif "must" in constraint.lower():
                actions.insert(0, f"Ensure {constraint}")
        
        return actions
    
    def get_plan(self, plan_id: str) -> Optional[ActionPlan]:
        """Get a plan by ID."""
        return self._active_plans.get(plan_id)
    
    def get_active_plans(self) -> list[ActionPlan]:
        """Get all active plans."""
        return list(self._active_plans.values())
    
    async def execute_next_action(self, plan_id: str) -> Optional[PlannedAction]:
        """
        Execute the next action in a plan.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            The action being executed, or None if no actions available
        """
        plan = self._active_plans.get(plan_id)
        if not plan:
            return None
        
        action = plan.next_action
        if action:
            action.start()
            self.logger.info(
                "Executing action",
                plan_id=plan_id,
                action_id=action.action_id,
                description=action.description[:50],
            )
        
        return action
    
    async def complete_action(
        self,
        plan_id: str,
        action_id: str,
        success: bool = True,
    ) -> bool:
        """
        Mark an action as completed.
        
        Args:
            plan_id: ID of the plan
            action_id: ID of the action
            success: Whether the action succeeded
            
        Returns:
            True if action was found and updated
        """
        plan = self._active_plans.get(plan_id)
        if not plan:
            return False
        
        for action in plan.actions:
            if action.action_id == action_id:
                action.complete(success)
                
                # Check if plan is now complete
                if plan.is_complete():
                    plan.status = ActionStatus.COMPLETED
                    self._plan_history.append(plan)
                    del self._active_plans[plan_id]
                
                return True
        
        return False
    
    async def replan(
        self,
        plan_id: str,
        reason: str,
    ) -> Optional[ActionPlan]:
        """
        Create a new plan to replace a failed one.
        
        Args:
            plan_id: ID of the plan to replace
            reason: Why replanning is needed
            
        Returns:
            New action plan, or None if original not found
        """
        old_plan = self._active_plans.get(plan_id)
        if not old_plan:
            return None
        
        self.logger.info(
            "Replanning",
            old_plan_id=plan_id,
            reason=reason,
        )
        
        # Cancel old plan
        for action in old_plan.actions:
            if action.status in [ActionStatus.PENDING, ActionStatus.IN_PROGRESS]:
                action.cancel()
        old_plan.status = ActionStatus.CANCELLED
        
        # Create new plan with updated constraints
        new_constraints = old_plan.constraints + [f"Previous attempt failed: {reason}"]
        
        new_plan = await self.create_plan(
            goal=old_plan.goal,
            constraints=new_constraints,
            priority=old_plan.priority,
            context={"replanned_from": plan_id},
        )
        
        # Move old to history
        self._plan_history.append(old_plan)
        del self._active_plans[plan_id]
        
        return new_plan
