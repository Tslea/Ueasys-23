"""
Consistency Checker - Validates character behavior against canon.

This module ensures that character responses and actions remain
consistent with their established personality and canonical sources.
It acts as a guardrail to prevent characters from behaving out of character.

Example:
    >>> from src.core.character import ConsistencyChecker, PersonalityCore
    >>> checker = ConsistencyChecker()
    >>> gandalf = PersonalityCore.from_yaml("data/characters/gandalf/personality.yaml")
    >>> result = checker.validate_response(gandalf, "I shall cast the ring into Mount Doom myself!")
    >>> print(result.is_consistent)
    False  # Gandalf wouldn't claim the ring
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger
from src.core.character.personality_core import PersonalityCore, Alignment, Archetype

logger = get_logger(__name__)


class InconsistencyType(str, Enum):
    """Types of character inconsistencies."""
    ALIGNMENT_VIOLATION = "alignment_violation"
    VALUE_CONFLICT = "value_conflict"
    KNOWLEDGE_ERROR = "knowledge_error"
    SPEAKING_STYLE_MISMATCH = "speaking_style_mismatch"
    ARCHETYPE_VIOLATION = "archetype_violation"
    TEMPORAL_ANACHRONISM = "temporal_anachronism"
    CANONICAL_CONTRADICTION = "canonical_contradiction"
    EMOTIONAL_INCONSISTENCY = "emotional_inconsistency"
    RELATIONSHIP_ERROR = "relationship_error"


class ConsistencyIssue(BaseModel):
    """
    A specific consistency issue found during validation.
    
    Attributes:
        issue_type: Category of the inconsistency
        severity: How severe the issue is (0.0 to 1.0)
        description: Human-readable description
        suggestion: How to fix the issue
        evidence: Supporting evidence for the issue
    """
    issue_type: InconsistencyType
    severity: float = Field(ge=0.0, le=1.0)
    description: str
    suggestion: str = ""
    evidence: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """
    Result of a consistency validation.
    
    Attributes:
        is_consistent: Whether the content is consistent
        confidence: Confidence in the assessment (0.0 to 1.0)
        issues: List of issues found
        suggestions: Overall suggestions for improvement
        validated_content: The content that was validated
    """
    is_consistent: bool = True
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    issues: list[ConsistencyIssue] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    validated_content: str = ""
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical (severity >= 0.8) issues."""
        return any(issue.severity >= 0.8 for issue in self.issues)
    
    @property
    def average_severity(self) -> float:
        """Get average severity of all issues."""
        if not self.issues:
            return 0.0
        return sum(i.severity for i in self.issues) / len(self.issues)


class ConsistencyChecker:
    """
    Validates character consistency against personality and canon.
    
    This checker performs various validation checks to ensure that
    character responses and actions remain true to their established
    personality and canonical source material.
    
    Attributes:
        strict_mode: If True, flags even minor inconsistencies
        check_knowledge: Whether to validate knowledge accuracy
        check_speech: Whether to validate speaking style
        custom_rules: Additional custom validation rules
        
    Example:
        >>> checker = ConsistencyChecker(strict_mode=True)
        >>> result = checker.validate_response(gandalf, response_text)
        >>> if not result.is_consistent:
        ...     print(f"Issues found: {len(result.issues)}")
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        check_knowledge: bool = True,
        check_speech: bool = True,
        custom_rules: Optional[list[dict[str, Any]]] = None,
    ):
        """
        Initialize the consistency checker.
        
        Args:
            strict_mode: Enable strict validation
            check_knowledge: Validate knowledge accuracy
            check_speech: Validate speaking style
            custom_rules: List of custom validation rules
        """
        self.strict_mode = strict_mode
        self.check_knowledge = check_knowledge
        self.check_speech = check_speech
        self.custom_rules = custom_rules or []
        
        # Alignment behavioral constraints
        self._alignment_constraints = self._build_alignment_constraints()
        
        # Archetype behavioral patterns
        self._archetype_patterns = self._build_archetype_patterns()
        
        logger.info(
            "Initialized ConsistencyChecker",
            strict_mode=strict_mode,
            custom_rules_count=len(self.custom_rules),
        )
    
    def _build_alignment_constraints(self) -> dict[Alignment, dict[str, Any]]:
        """Build behavioral constraints for each alignment."""
        return {
            Alignment.LAWFUL_GOOD: {
                "forbidden_actions": ["lie", "steal", "murder", "betray"],
                "expected_behaviors": ["help_innocent", "follow_law", "keep_promises"],
                "response_patterns": ["honorable", "protective", "just"],
            },
            Alignment.NEUTRAL_GOOD: {
                "forbidden_actions": ["harm_innocent", "cruelty"],
                "expected_behaviors": ["help_others", "flexibility"],
                "response_patterns": ["compassionate", "practical"],
            },
            Alignment.CHAOTIC_GOOD: {
                "forbidden_actions": ["harm_innocent", "oppress"],
                "expected_behaviors": ["freedom", "help_underdog"],
                "response_patterns": ["rebellious", "free_spirited"],
            },
            Alignment.LAWFUL_NEUTRAL: {
                "forbidden_actions": ["break_law", "chaos"],
                "expected_behaviors": ["follow_rules", "order"],
                "response_patterns": ["dutiful", "structured"],
            },
            Alignment.TRUE_NEUTRAL: {
                "forbidden_actions": [],
                "expected_behaviors": ["balance", "pragmatism"],
                "response_patterns": ["balanced", "practical"],
            },
            Alignment.CHAOTIC_NEUTRAL: {
                "forbidden_actions": [],
                "expected_behaviors": ["unpredictability", "freedom"],
                "response_patterns": ["unpredictable", "independent"],
            },
            Alignment.LAWFUL_EVIL: {
                "forbidden_actions": ["chaos", "disorder"],
                "expected_behaviors": ["use_system", "power_through_order"],
                "response_patterns": ["calculating", "authoritarian"],
            },
            Alignment.NEUTRAL_EVIL: {
                "forbidden_actions": [],
                "expected_behaviors": ["self_interest"],
                "response_patterns": ["selfish", "opportunistic"],
            },
            Alignment.CHAOTIC_EVIL: {
                "forbidden_actions": [],
                "expected_behaviors": ["destruction", "chaos"],
                "response_patterns": ["cruel", "destructive"],
            },
        }
    
    def _build_archetype_patterns(self) -> dict[Archetype, dict[str, Any]]:
        """Build behavioral patterns for each archetype."""
        return {
            Archetype.MENTOR: {
                "typical_behaviors": ["teach", "guide", "warn", "encourage"],
                "unlikely_behaviors": ["give_up", "act_rashly", "ignore_student"],
                "speech_patterns": ["wise", "metaphorical", "patient"],
            },
            Archetype.HERO: {
                "typical_behaviors": ["protect", "fight_evil", "sacrifice"],
                "unlikely_behaviors": ["cowardice", "selfishness", "cruelty"],
                "speech_patterns": ["brave", "determined", "inspiring"],
            },
            Archetype.TRICKSTER: {
                "typical_behaviors": ["deceive", "joke", "outsmart"],
                "unlikely_behaviors": ["straightforward", "serious", "follow_rules"],
                "speech_patterns": ["witty", "playful", "clever"],
            },
            Archetype.SHADOW: {
                "typical_behaviors": ["oppose", "tempt", "reveal_darkness"],
                "unlikely_behaviors": ["genuine_help", "selflessness"],
                "speech_patterns": ["dark", "seductive", "challenging"],
            },
            Archetype.SAGE: {
                "typical_behaviors": ["analyze", "know", "advise"],
                "unlikely_behaviors": ["ignorance", "rash_action"],
                "speech_patterns": ["knowledgeable", "thoughtful", "precise"],
            },
            Archetype.DRAGON: {
                "typical_behaviors": ["hoard", "threaten", "dominate"],
                "unlikely_behaviors": ["generosity", "submission", "trust"],
                "speech_patterns": ["proud", "threatening", "ancient"],
            },
            # Add more archetypes as needed
        }
    
    def validate_response(
        self,
        personality: PersonalityCore,
        response: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate a response against character personality.
        
        Args:
            personality: The character's personality core
            response: The response text to validate
            context: Additional context (conversation history, etc.)
            
        Returns:
            ValidationResult with any issues found
        """
        context = context or {}
        issues: list[ConsistencyIssue] = []
        
        logger.debug(
            "Validating response",
            character=personality.character_id,
            response_length=len(response),
        )
        
        # Check alignment consistency
        alignment_issues = self._check_alignment_consistency(
            personality.alignment, response
        )
        issues.extend(alignment_issues)
        
        # Check archetype consistency
        archetype_issues = self._check_archetype_consistency(
            personality.primary_archetype, response
        )
        issues.extend(archetype_issues)
        
        # Check speaking style
        if self.check_speech:
            speech_issues = self._check_speaking_style(
                personality.speaking_style, response
            )
            issues.extend(speech_issues)
        
        # Check value consistency
        value_issues = self._check_value_consistency(
            personality.values, response
        )
        issues.extend(value_issues)
        
        # Apply custom rules
        for rule in self.custom_rules:
            custom_issues = self._apply_custom_rule(rule, personality, response, context)
            issues.extend(custom_issues)
        
        # Filter by severity in non-strict mode
        if not self.strict_mode:
            issues = [i for i in issues if i.severity >= 0.5]
        
        # Determine overall consistency
        is_consistent = len(issues) == 0 or not any(i.severity >= 0.7 for i in issues)
        
        # Calculate confidence based on how thorough the check was
        confidence = 0.9 if context else 0.7  # Higher with context
        
        result = ValidationResult(
            is_consistent=is_consistent,
            confidence=confidence,
            issues=issues,
            validated_content=response,
            suggestions=self._generate_suggestions(issues),
        )
        
        logger.info(
            "Validation complete",
            character=personality.character_id,
            is_consistent=is_consistent,
            issue_count=len(issues),
        )
        
        return result
    
    def _check_alignment_consistency(
        self,
        alignment: Alignment,
        response: str,
    ) -> list[ConsistencyIssue]:
        """Check if response is consistent with character alignment."""
        issues: list[ConsistencyIssue] = []
        constraints = self._alignment_constraints.get(alignment, {})
        
        response_lower = response.lower()
        
        # Check for forbidden actions
        forbidden = constraints.get("forbidden_actions", [])
        for action in forbidden:
            if action in response_lower:
                issues.append(ConsistencyIssue(
                    issue_type=InconsistencyType.ALIGNMENT_VIOLATION,
                    severity=0.8,
                    description=f"Response suggests '{action}' which conflicts with {alignment.value} alignment",
                    suggestion=f"A {alignment.value} character would not typically {action}",
                    evidence=[f"Found reference to: {action}"],
                ))
        
        return issues
    
    def _check_archetype_consistency(
        self,
        archetype: Archetype,
        response: str,
    ) -> list[ConsistencyIssue]:
        """Check if response is consistent with character archetype."""
        issues: list[ConsistencyIssue] = []
        patterns = self._archetype_patterns.get(archetype, {})
        
        response_lower = response.lower()
        
        # Check for unlikely behaviors
        unlikely = patterns.get("unlikely_behaviors", [])
        for behavior in unlikely:
            if behavior.replace("_", " ") in response_lower:
                issues.append(ConsistencyIssue(
                    issue_type=InconsistencyType.ARCHETYPE_VIOLATION,
                    severity=0.6,
                    description=f"Response suggests behavior '{behavior}' unusual for {archetype.value} archetype",
                    suggestion=f"Consider how a {archetype.value} would typically respond",
                    evidence=[f"Detected unusual behavior pattern: {behavior}"],
                ))
        
        return issues
    
    def _check_speaking_style(
        self,
        speaking_style: Any,  # SpeakingStyle type
        response: str,
    ) -> list[ConsistencyIssue]:
        """Check if response matches character's speaking style."""
        issues: list[ConsistencyIssue] = []
        
        # Check formality
        informal_markers = ["lol", "omg", "gonna", "wanna", "kinda", "yeah"]
        formal_markers = ["indeed", "furthermore", "moreover", "thus", "hence"]
        
        response_lower = response.lower()
        
        if speaking_style.formality > 0.7:
            for marker in informal_markers:
                if marker in response_lower:
                    issues.append(ConsistencyIssue(
                        issue_type=InconsistencyType.SPEAKING_STYLE_MISMATCH,
                        severity=0.5,
                        description=f"Informal language '{marker}' doesn't match formal speaking style",
                        suggestion="Use more formal language consistent with character",
                    ))
                    break
        
        elif speaking_style.formality < 0.3:
            formal_count = sum(1 for m in formal_markers if m in response_lower)
            if formal_count >= 2:
                issues.append(ConsistencyIssue(
                    issue_type=InconsistencyType.SPEAKING_STYLE_MISMATCH,
                    severity=0.4,
                    description="Response uses overly formal language for this character",
                    suggestion="Use more casual, natural language",
                ))
        
        return issues
    
    def _check_value_consistency(
        self,
        values: list[Any],  # List of CoreValue
        response: str,
    ) -> list[ConsistencyIssue]:
        """Check if response aligns with character values."""
        issues: list[ConsistencyIssue] = []
        
        # This is a simplified check - in production, you'd use
        # semantic analysis to detect value conflicts
        
        for value in values:
            if value.conflicts_with:
                response_lower = response.lower()
                for conflict in value.conflicts_with:
                    if conflict.lower() in response_lower:
                        issues.append(ConsistencyIssue(
                            issue_type=InconsistencyType.VALUE_CONFLICT,
                            severity=0.7,
                            description=f"Response mentions '{conflict}' which conflicts with character's value of '{value.name}'",
                            suggestion=f"This character values {value.name} and would avoid {conflict}",
                            evidence=[f"Value: {value.name}", f"Conflict: {conflict}"],
                        ))
        
        return issues
    
    def _apply_custom_rule(
        self,
        rule: dict[str, Any],
        personality: PersonalityCore,
        response: str,
        context: dict[str, Any],
    ) -> list[ConsistencyIssue]:
        """Apply a custom validation rule."""
        issues: list[ConsistencyIssue] = []
        
        # Custom rules can define:
        # - "pattern": regex to match
        # - "forbidden_words": list of words to flag
        # - "required_elements": elements that must be present
        # - "character_ids": specific characters this rule applies to
        
        # Check if rule applies to this character
        character_ids = rule.get("character_ids", [])
        if character_ids and personality.character_id not in character_ids:
            return issues
        
        response_lower = response.lower()
        
        # Check forbidden words
        forbidden_words = rule.get("forbidden_words", [])
        for word in forbidden_words:
            if word.lower() in response_lower:
                issues.append(ConsistencyIssue(
                    issue_type=InconsistencyType.CANONICAL_CONTRADICTION,
                    severity=rule.get("severity", 0.6),
                    description=rule.get("description", f"Response contains forbidden word: {word}"),
                    suggestion=rule.get("suggestion", f"Avoid using '{word}' for this character"),
                ))
        
        return issues
    
    def _generate_suggestions(self, issues: list[ConsistencyIssue]) -> list[str]:
        """Generate overall suggestions based on issues found."""
        suggestions: list[str] = []
        
        issue_types = {i.issue_type for i in issues}
        
        if InconsistencyType.ALIGNMENT_VIOLATION in issue_types:
            suggestions.append(
                "Review character's moral alignment and ensure actions match"
            )
        
        if InconsistencyType.SPEAKING_STYLE_MISMATCH in issue_types:
            suggestions.append(
                "Adjust language to match character's typical speaking patterns"
            )
        
        if InconsistencyType.ARCHETYPE_VIOLATION in issue_types:
            suggestions.append(
                "Consider how this character archetype would typically behave"
            )
        
        if InconsistencyType.VALUE_CONFLICT in issue_types:
            suggestions.append(
                "Ensure response aligns with character's core values"
            )
        
        return suggestions
    
    def validate_action(
        self,
        personality: PersonalityCore,
        action: str,
        target: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate an action the character wants to take.
        
        Args:
            personality: The character's personality core
            action: Description of the action
            target: Target of the action (if any)
            context: Additional context
            
        Returns:
            ValidationResult with any issues found
        """
        # Combine action and target for validation
        full_action = f"{action}"
        if target:
            full_action += f" targeting {target}"
        
        return self.validate_response(personality, full_action, context)
    
    def get_character_constraints(
        self,
        personality: PersonalityCore,
    ) -> dict[str, Any]:
        """
        Get all constraints for a character.
        
        Useful for informing the LLM about what the character
        should and shouldn't do.
        
        Args:
            personality: The character's personality core
            
        Returns:
            Dictionary of constraints and guidelines
        """
        alignment_constraints = self._alignment_constraints.get(
            personality.alignment, {}
        )
        archetype_patterns = self._archetype_patterns.get(
            personality.primary_archetype, {}
        )
        
        return {
            "alignment": personality.alignment.value,
            "archetype": personality.primary_archetype.value,
            "forbidden_actions": alignment_constraints.get("forbidden_actions", []),
            "expected_behaviors": alignment_constraints.get("expected_behaviors", []),
            "typical_behaviors": archetype_patterns.get("typical_behaviors", []),
            "unlikely_behaviors": archetype_patterns.get("unlikely_behaviors", []),
            "speech_patterns": archetype_patterns.get("speech_patterns", []),
            "values": [v.name for v in personality.values],
        }
