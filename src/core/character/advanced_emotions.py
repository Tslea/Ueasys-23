"""
Advanced Emotional System - Based on Modern Neuroscience & Psychology

This module implements a sophisticated emotional system based on:

1. **Dimensional Model (Russell's Circumplex)**
   - Valence: Pleasant ↔ Unpleasant
   - Arousal: High activation ↔ Low activation
   - Dominance: In control ↔ Controlled

2. **Panksepp's Affective Neuroscience (7 Primary Systems)**
   - SEEKING: Curiosity, exploration, wanting
   - RAGE: Anger, frustration when blocked
   - FEAR: Anxiety, threat response
   - LUST: Sexual desire, attraction
   - CARE: Nurturing, attachment
   - PANIC/GRIEF: Separation distress, loneliness
   - PLAY: Joy, social bonding, humor

3. **Appraisal Theory (Lazarus & Scherer)**
   - Emotions arise from cognitive evaluation of events
   - Relevance, implications, coping potential

4. **Constructed Emotion Theory (Lisa Feldman Barrett)**
   - Brain predicts and constructs emotions from:
     - Interoception (body state)
     - Context
     - Past experiences

5. **Homeostatic Regulation**
   - Emotions serve to maintain psychological balance
   - Allostasis: Anticipating needs before they arise

References:
- Panksepp, J. (2011). Affective Neuroscience
- Barrett, L.F. (2017). How Emotions Are Made
- Russell, J.A. (1980). A Circumplex Model of Affect
- Scherer, K.R. (2009). Component Process Model
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, List, Dict, Tuple
from pydantic import BaseModel, Field
import math

from src.config.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# Dimensional Model (Valence-Arousal-Dominance)
# =============================================================================

@dataclass
class AffectiveDimensions:
    """
    Core affect dimensions based on Russell's Circumplex Model.
    
    This provides the "core affect" - the neurophysiological state
    that underlies all emotional experience.
    """
    valence: float = 0.0      # -1 (unpleasant) to +1 (pleasant)
    arousal: float = 0.0      # -1 (deactivated) to +1 (activated)
    dominance: float = 0.0    # -1 (submissive) to +1 (dominant)
    
    def blend(self, other: "AffectiveDimensions", weight: float = 0.5) -> "AffectiveDimensions":
        """Blend two affective states."""
        return AffectiveDimensions(
            valence=self.valence * (1 - weight) + other.valence * weight,
            arousal=self.arousal * (1 - weight) + other.arousal * weight,
            dominance=self.dominance * (1 - weight) + other.dominance * weight,
        )
    
    def distance_to(self, other: "AffectiveDimensions") -> float:
        """Euclidean distance in affect space."""
        return math.sqrt(
            (self.valence - other.valence) ** 2 +
            (self.arousal - other.arousal) ** 2 +
            (self.dominance - other.dominance) ** 2
        )
    
    def decay_toward(self, baseline: "AffectiveDimensions", rate: float = 0.1) -> "AffectiveDimensions":
        """Decay toward baseline state (homeostatic regulation)."""
        return AffectiveDimensions(
            valence=self.valence + (baseline.valence - self.valence) * rate,
            arousal=self.arousal + (baseline.arousal - self.arousal) * rate,
            dominance=self.dominance + (baseline.dominance - self.dominance) * rate,
        )


# =============================================================================
# Panksepp's Primary Affective Systems
# =============================================================================

class AffectiveSystem(str, Enum):
    """
    Panksepp's 7 primary emotional systems.
    
    These are evolutionarily conserved brain circuits that generate
    basic emotional states in all mammals.
    """
    SEEKING = "seeking"      # Dopaminergic exploration, curiosity, wanting
    RAGE = "rage"            # Frustration when goals blocked
    FEAR = "fear"            # Threat detection, anxiety
    LUST = "lust"            # Attraction, desire (romantic contexts)
    CARE = "care"            # Nurturing, empathy, attachment
    PANIC_GRIEF = "panic_grief"  # Separation distress, loneliness
    PLAY = "play"            # Social joy, humor, bonding


# Mapping of affective systems to dimensional coordinates
SYSTEM_DIMENSIONS: Dict[AffectiveSystem, AffectiveDimensions] = {
    AffectiveSystem.SEEKING: AffectiveDimensions(valence=0.5, arousal=0.6, dominance=0.4),
    AffectiveSystem.RAGE: AffectiveDimensions(valence=-0.7, arousal=0.9, dominance=0.6),
    AffectiveSystem.FEAR: AffectiveDimensions(valence=-0.8, arousal=0.7, dominance=-0.6),
    AffectiveSystem.LUST: AffectiveDimensions(valence=0.6, arousal=0.7, dominance=0.2),
    AffectiveSystem.CARE: AffectiveDimensions(valence=0.7, arousal=0.2, dominance=0.3),
    AffectiveSystem.PANIC_GRIEF: AffectiveDimensions(valence=-0.8, arousal=0.4, dominance=-0.7),
    AffectiveSystem.PLAY: AffectiveDimensions(valence=0.8, arousal=0.6, dominance=0.3),
}


# =============================================================================
# Appraisal Dimensions (Scherer's Component Process Model)
# =============================================================================

@dataclass
class AppraisalResult:
    """
    Cognitive appraisal of a stimulus/event.
    
    Based on Scherer's Component Process Model - how we evaluate
    events determines which emotions we experience.
    """
    # Relevance check
    novelty: float = 0.0          # -1 (expected) to +1 (surprising)
    pleasantness: float = 0.0     # -1 (unpleasant) to +1 (pleasant)
    goal_relevance: float = 0.0   # 0 (irrelevant) to 1 (highly relevant)
    
    # Implication check
    goal_conduciveness: float = 0.0  # -1 (obstructive) to +1 (conducive)
    urgency: float = 0.0             # 0 (no urgency) to 1 (immediate)
    
    # Coping potential check  
    control: float = 0.0          # 0 (no control) to 1 (full control)
    power: float = 0.0            # 0 (powerless) to 1 (powerful)
    adjustment: float = 0.0       # 0 (cannot adapt) to 1 (easily adapt)
    
    # Normative significance
    internal_standards: float = 0.0  # -1 (violates) to +1 (upholds) self-image
    external_standards: float = 0.0  # -1 (violates) to +1 (upholds) social norms
    
    def to_dimensions(self) -> AffectiveDimensions:
        """Convert appraisal to affective dimensions."""
        valence = (self.pleasantness + self.goal_conduciveness) / 2
        arousal = (self.novelty + self.urgency + self.goal_relevance) / 3
        dominance = (self.control + self.power) / 2
        
        return AffectiveDimensions(
            valence=max(-1, min(1, valence)),
            arousal=max(-1, min(1, arousal)),
            dominance=max(-1, min(1, dominance)),
        )


# =============================================================================
# Emotion Labels (Constructed from Dimensions)
# =============================================================================

class EmotionLabel(str, Enum):
    """
    Emotion categories constructed from core affect + context.
    
    Based on Barrett's theory: these are not "basic" emotions but
    conceptual categories we use to make sense of core affect.
    """
    # High arousal, positive valence
    EXCITEMENT = "excitement"
    JOY = "joy"
    ENTHUSIASM = "enthusiasm"
    DELIGHT = "delight"
    
    # Low arousal, positive valence
    CONTENTMENT = "contentment"
    SERENITY = "serenity"
    CALM = "calm"
    PEACE = "peace"
    
    # High arousal, negative valence
    ANGER = "anger"
    FEAR = "fear"
    ANXIETY = "anxiety"
    FRUSTRATION = "frustration"
    PANIC = "panic"
    
    # Low arousal, negative valence
    SADNESS = "sadness"
    MELANCHOLY = "melancholy"
    GRIEF = "grief"
    DESPAIR = "despair"
    BOREDOM = "boredom"
    
    # Complex/Social emotions
    LOVE = "love"
    COMPASSION = "compassion"
    PRIDE = "pride"
    SHAME = "shame"
    GUILT = "guilt"
    CONTEMPT = "contempt"
    DISGUST = "disgust"
    ENVY = "envy"
    JEALOUSY = "jealousy"
    GRATITUDE = "gratitude"
    AWE = "awe"
    
    # Cognitive emotions
    CURIOSITY = "curiosity"
    INTEREST = "interest"
    SURPRISE = "surprise"
    CONFUSION = "confusion"
    DETERMINATION = "determination"
    HOPE = "hope"
    
    # Neutral
    NEUTRAL = "neutral"


# Mapping emotion labels to dimensional coordinates
EMOTION_COORDINATES: Dict[EmotionLabel, AffectiveDimensions] = {
    # Positive high arousal
    EmotionLabel.EXCITEMENT: AffectiveDimensions(0.7, 0.8, 0.5),
    EmotionLabel.JOY: AffectiveDimensions(0.8, 0.6, 0.4),
    EmotionLabel.ENTHUSIASM: AffectiveDimensions(0.7, 0.7, 0.6),
    EmotionLabel.DELIGHT: AffectiveDimensions(0.8, 0.5, 0.3),
    
    # Positive low arousal
    EmotionLabel.CONTENTMENT: AffectiveDimensions(0.6, -0.2, 0.3),
    EmotionLabel.SERENITY: AffectiveDimensions(0.7, -0.4, 0.4),
    EmotionLabel.CALM: AffectiveDimensions(0.4, -0.5, 0.3),
    EmotionLabel.PEACE: AffectiveDimensions(0.6, -0.6, 0.5),
    
    # Negative high arousal
    EmotionLabel.ANGER: AffectiveDimensions(-0.6, 0.8, 0.6),
    EmotionLabel.FEAR: AffectiveDimensions(-0.8, 0.7, -0.6),
    EmotionLabel.ANXIETY: AffectiveDimensions(-0.5, 0.6, -0.4),
    EmotionLabel.FRUSTRATION: AffectiveDimensions(-0.5, 0.6, -0.2),
    EmotionLabel.PANIC: AffectiveDimensions(-0.9, 0.9, -0.8),
    
    # Negative low arousal
    EmotionLabel.SADNESS: AffectiveDimensions(-0.6, -0.3, -0.3),
    EmotionLabel.MELANCHOLY: AffectiveDimensions(-0.4, -0.4, -0.2),
    EmotionLabel.GRIEF: AffectiveDimensions(-0.8, 0.2, -0.6),
    EmotionLabel.DESPAIR: AffectiveDimensions(-0.9, -0.2, -0.8),
    EmotionLabel.BOREDOM: AffectiveDimensions(-0.3, -0.6, -0.1),
    
    # Social emotions
    EmotionLabel.LOVE: AffectiveDimensions(0.9, 0.4, 0.2),
    EmotionLabel.COMPASSION: AffectiveDimensions(0.6, 0.2, 0.4),
    EmotionLabel.PRIDE: AffectiveDimensions(0.7, 0.4, 0.7),
    EmotionLabel.SHAME: AffectiveDimensions(-0.7, 0.4, -0.6),
    EmotionLabel.GUILT: AffectiveDimensions(-0.6, 0.3, -0.4),
    EmotionLabel.CONTEMPT: AffectiveDimensions(-0.5, 0.2, 0.6),
    EmotionLabel.DISGUST: AffectiveDimensions(-0.7, 0.3, 0.3),
    EmotionLabel.ENVY: AffectiveDimensions(-0.5, 0.4, -0.3),
    EmotionLabel.JEALOUSY: AffectiveDimensions(-0.6, 0.6, -0.2),
    EmotionLabel.GRATITUDE: AffectiveDimensions(0.8, 0.3, -0.1),
    EmotionLabel.AWE: AffectiveDimensions(0.6, 0.5, -0.3),
    
    # Cognitive emotions
    EmotionLabel.CURIOSITY: AffectiveDimensions(0.4, 0.5, 0.3),
    EmotionLabel.INTEREST: AffectiveDimensions(0.3, 0.4, 0.2),
    EmotionLabel.SURPRISE: AffectiveDimensions(0.1, 0.7, -0.1),
    EmotionLabel.CONFUSION: AffectiveDimensions(-0.2, 0.4, -0.3),
    EmotionLabel.DETERMINATION: AffectiveDimensions(0.3, 0.6, 0.7),
    EmotionLabel.HOPE: AffectiveDimensions(0.6, 0.3, 0.2),
    
    # Neutral
    EmotionLabel.NEUTRAL: AffectiveDimensions(0.0, 0.0, 0.0),
}


def get_closest_emotion(dimensions: AffectiveDimensions) -> Tuple[EmotionLabel, float]:
    """
    Find the emotion label closest to given dimensions.
    
    Returns emotion and confidence (inverse of distance).
    """
    min_distance = float('inf')
    closest = EmotionLabel.NEUTRAL
    
    for emotion, coords in EMOTION_COORDINATES.items():
        distance = dimensions.distance_to(coords)
        if distance < min_distance:
            min_distance = distance
            closest = emotion
    
    # Convert distance to confidence (0-1)
    confidence = max(0, 1 - min_distance / 2)
    
    return closest, confidence


# =============================================================================
# Semantic Appraisal Patterns (for text analysis)
# =============================================================================

@dataclass
class AppraisalPattern:
    """Pattern for detecting appraisal-relevant content in text."""
    keywords: List[str]
    appraisal_effects: Dict[str, float]  # Which appraisal dimensions to affect
    system_activation: Optional[AffectiveSystem] = None  # Panksepp system to activate


APPRAISAL_PATTERNS: List[AppraisalPattern] = [
    # SEEKING system - curiosity, exploration
    AppraisalPattern(
        keywords=["tell me", "what", "why", "how", "explain", "curious", "wonder", 
                  "interesting", "discover", "explore", "learn", "understand",
                  "dimmi", "cosa", "perché", "come", "spiega", "curioso"],
        appraisal_effects={"novelty": 0.5, "goal_relevance": 0.6, "pleasantness": 0.3},
        system_activation=AffectiveSystem.SEEKING,
    ),
    
    # RAGE system - frustration, blocked goals
    AppraisalPattern(
        keywords=["angry", "furious", "hate", "unfair", "frustrating", "annoying",
                  "enemy", "betrayed", "cheated", "stolen", "injustice",
                  "arrabbiato", "odio", "ingiusto", "tradito", "nemico"],
        appraisal_effects={"pleasantness": -0.7, "goal_conduciveness": -0.8, 
                         "urgency": 0.6, "power": 0.4},
        system_activation=AffectiveSystem.RAGE,
    ),
    
    # FEAR system - threat, danger
    AppraisalPattern(
        keywords=["danger", "threat", "afraid", "scared", "terrified", "attack",
                  "enemy", "death", "kill", "destroy", "monster", "dark",
                  "pericolo", "paura", "minaccia", "morte", "attacco"],
        appraisal_effects={"pleasantness": -0.8, "urgency": 0.8, "control": -0.5,
                         "goal_conduciveness": -0.6},
        system_activation=AffectiveSystem.FEAR,
    ),
    
    # CARE system - nurturing, attachment
    AppraisalPattern(
        keywords=["help", "protect", "care", "love", "friend", "family", "child",
                  "safe", "comfort", "support", "together", "trust",
                  "aiuto", "proteggere", "amore", "amico", "famiglia"],
        appraisal_effects={"pleasantness": 0.7, "goal_relevance": 0.6, 
                         "internal_standards": 0.5},
        system_activation=AffectiveSystem.CARE,
    ),
    
    # PANIC/GRIEF system - loss, separation
    AppraisalPattern(
        keywords=["lost", "gone", "died", "death", "miss", "alone", "lonely",
                  "abandoned", "left", "goodbye", "never", "farewell",
                  "perso", "morto", "solo", "addio", "abbandonato"],
        appraisal_effects={"pleasantness": -0.8, "goal_conduciveness": -0.7,
                         "control": -0.6, "adjustment": -0.5},
        system_activation=AffectiveSystem.PANIC_GRIEF,
    ),
    
    # PLAY system - joy, humor (ENHANCED)
    AppraisalPattern(
        keywords=["fun", "play", "game", "joke", "laugh", "happy", "joy", "party",
                  "celebrate", "dance", "sing", "wonderful", "amazing", "great",
                  "fantastic", "awesome", "brilliant", "lovely", "beautiful",
                  "divertente", "gioco", "ridere", "felice", "festa", "bello",
                  "fantastico", "meraviglioso", "stupendo", "magnifico"],
        appraisal_effects={"pleasantness": 0.9, "novelty": 0.4, "control": 0.5,
                         "goal_conduciveness": 0.6},
        system_activation=AffectiveSystem.PLAY,
    ),
    
    # Gratitude (ENHANCED)
    AppraisalPattern(
        keywords=["thank", "grateful", "appreciate", "thanks", "blessing",
                  "grazie", "grato", "apprezzo", "benedizione", "gentile",
                  "kind", "generous", "thoughtful"],
        appraisal_effects={"pleasantness": 0.8, "external_standards": 0.6,
                         "goal_conduciveness": 0.5, "internal_standards": 0.4},
        system_activation=AffectiveSystem.CARE,
    ),
    
    # Hope
    AppraisalPattern(
        keywords=["hope", "maybe", "possible", "future", "better", "tomorrow",
                  "chance", "opportunity", "dream", "wish",
                  "speranza", "forse", "futuro", "domani", "sogno"],
        appraisal_effects={"pleasantness": 0.6, "goal_conduciveness": 0.5,
                         "adjustment": 0.5},
        system_activation=AffectiveSystem.SEEKING,
    ),
    
    # Shame/Guilt
    AppraisalPattern(
        keywords=["sorry", "apologize", "fault", "mistake", "wrong", "failed",
                  "ashamed", "embarrassed", "regret",
                  "scusa", "errore", "sbagliato", "vergogna", "colpa"],
        appraisal_effects={"pleasantness": -0.5, "internal_standards": -0.6,
                         "external_standards": -0.5, "control": -0.3},
        system_activation=None,
    ),
    
    # Pride (ENHANCED)
    AppraisalPattern(
        keywords=["proud", "accomplished", "achieved", "success", "won", "victory",
                  "best", "excellent", "mastered", "hero", "well done", "bravo",
                  "orgoglioso", "successo", "vittoria", "eroe", "campione",
                  "complimenti", "bravissimo"],
        appraisal_effects={"pleasantness": 0.8, "internal_standards": 0.8,
                         "power": 0.7, "control": 0.6},
        system_activation=AffectiveSystem.PLAY,
    ),
    
    # Surprise
    AppraisalPattern(
        keywords=["surprise", "unexpected", "sudden", "shocking", "unbelievable",
                  "wow", "amazing", "incredible", "really",
                  "sorpresa", "improvviso", "incredibile", "davvero"],
        appraisal_effects={"novelty": 0.9, "urgency": 0.4},
        system_activation=AffectiveSystem.SEEKING,
    ),
    
    # === NEW POSITIVE PATTERNS ===
    
    # Friendly greetings / Saluti amichevoli
    AppraisalPattern(
        keywords=["hello", "hi", "hey", "good morning", "good evening", "greetings",
                  "welcome", "nice to meet", "pleasure", "good to see",
                  "ciao", "salve", "buongiorno", "buonasera", "piacere",
                  "benvenuto", "come stai", "come va"],
        appraisal_effects={"pleasantness": 0.6, "external_standards": 0.4,
                         "goal_conduciveness": 0.3},
        system_activation=AffectiveSystem.PLAY,
    ),
    
    # Compliments / Complimenti
    AppraisalPattern(
        keywords=["you're great", "you're amazing", "impressive", "admire",
                  "respect", "wise", "smart", "clever", "talented", "skilled",
                  "powerful", "strong", "beautiful", "magnificent", "noble",
                  "sei grande", "sei fantastico", "ammiro", "rispetto",
                  "saggio", "intelligente", "bravo", "forte", "potente"],
        appraisal_effects={"pleasantness": 0.85, "internal_standards": 0.7,
                         "power": 0.5, "external_standards": 0.6},
        system_activation=AffectiveSystem.PLAY,
    ),
    
    # Agreement / Accordo
    AppraisalPattern(
        keywords=["yes", "agree", "right", "true", "correct", "exactly",
                  "indeed", "absolutely", "of course", "certainly",
                  "sì", "giusto", "vero", "esatto", "certo", "certamente",
                  "proprio così", "hai ragione", "concordo"],
        appraisal_effects={"pleasantness": 0.5, "goal_conduciveness": 0.4,
                         "external_standards": 0.3},
        system_activation=AffectiveSystem.CARE,
    ),
    
    # Positive interest / Interesse positivo
    AppraisalPattern(
        keywords=["tell me more", "fascinating", "intriguing", "love to hear",
                  "want to know", "sounds good", "sounds great", "exciting",
                  "raccontami", "affascinante", "interessante", "vorrei sapere",
                  "mi piace", "che bello", "entusiasmante"],
        appraisal_effects={"pleasantness": 0.6, "novelty": 0.5, 
                         "goal_relevance": 0.5, "goal_conduciveness": 0.4},
        system_activation=AffectiveSystem.SEEKING,
    ),
    
    # Adventure / Avventura
    AppraisalPattern(
        keywords=["adventure", "quest", "journey", "mission", "let's go",
                  "ready", "brave", "courage", "together", "allies",
                  "avventura", "missione", "viaggio", "andiamo", "pronti",
                  "coraggio", "insieme", "alleati", "compagni"],
        appraisal_effects={"pleasantness": 0.7, "goal_relevance": 0.7,
                         "goal_conduciveness": 0.6, "power": 0.5},
        system_activation=AffectiveSystem.SEEKING,
    ),
    
    # Peace / Tranquillity
    AppraisalPattern(
        keywords=["peace", "calm", "quiet", "rest", "relax", "serene", "tranquil",
                  "pace", "calma", "tranquillo", "riposo", "sereno",
                  "rilassante", "quiete", "armonia"],
        appraisal_effects={"pleasantness": 0.6, "control": 0.5, 
                         "adjustment": 0.5, "urgency": -0.4},
        system_activation=AffectiveSystem.CARE,
    ),
    
    # Stories / Narrative engagement
    AppraisalPattern(
        keywords=["story", "tale", "legend", "once upon", "long ago", "tell",
                  "storia", "racconto", "leggenda", "c'era una volta",
                  "narra", "racconta"],
        appraisal_effects={"pleasantness": 0.5, "novelty": 0.6, 
                         "goal_relevance": 0.4},
        system_activation=AffectiveSystem.SEEKING,
    ),
]


# =============================================================================
# Advanced Emotional State
# =============================================================================

class AdvancedEmotionalState(BaseModel):
    """
    Sophisticated emotional state based on neuroscience research.
    
    Combines:
    - Dimensional model (core affect)
    - Panksepp's affective systems
    - Appraisal theory
    - Homeostatic regulation
    """
    
    character_id: str
    
    # Core affect (dimensional)
    current_affect: AffectiveDimensions = field(default_factory=AffectiveDimensions)
    baseline_affect: AffectiveDimensions = field(default_factory=AffectiveDimensions)
    
    # Affective system activations (0-1 for each)
    system_activations: Dict[str, float] = Field(default_factory=dict)
    
    # Most recent appraisal
    last_appraisal: Optional[AppraisalResult] = None
    
    # Emotional momentum (resistance to change)
    emotional_inertia: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Time tracking for decay
    last_update: datetime = Field(default_factory=datetime.now)
    
    # History for pattern recognition
    affect_history: List[Dict[str, Any]] = Field(default_factory=list)
    max_history: int = Field(default=50)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize system activations
        if not self.system_activations:
            self.system_activations = {s.value: 0.0 for s in AffectiveSystem}
        # Initialize affect as dataclass
        if isinstance(self.current_affect, dict):
            self.current_affect = AffectiveDimensions(**self.current_affect)
        if isinstance(self.baseline_affect, dict):
            self.baseline_affect = AffectiveDimensions(**self.baseline_affect)
    
    def appraise_message(self, message: str) -> AppraisalResult:
        """
        Perform cognitive appraisal of a message.
        
        Analyzes text to determine relevance, implications, and coping potential.
        
        Implements NEGATIVITY BIAS (Baumeister et al., 2001):
        - Negative stimuli are processed more thoroughly
        - Negative information weighs more heavily in evaluations
        - "Bad is stronger than good"
        """
        message_lower = message.lower()
        
        # Initialize appraisal
        appraisal = AppraisalResult()
        matched_patterns = []
        
        # Check each pattern
        for pattern in APPRAISAL_PATTERNS:
            matches = sum(1 for kw in pattern.keywords if kw in message_lower)
            if matches > 0:
                matched_patterns.append((pattern, matches))
                
                # Apply appraisal effects weighted by match count
                weight = min(1.0, matches * 0.3)
                
                # NEGATIVITY BIAS: Negative patterns have ~2x more impact
                # Based on Baumeister's "bad is stronger than good" principle
                is_negative_pattern = any(
                    pattern.appraisal_effects.get(k, 0) < -0.3 
                    for k in ['pleasantness', 'goal_conduciveness']
                )
                if is_negative_pattern:
                    weight *= 1.8  # Negativity amplification factor
                
                for dim, effect in pattern.appraisal_effects.items():
                    current = getattr(appraisal, dim)
                    setattr(appraisal, dim, current + effect * weight)
                
                # Activate affective system (negative systems activate more strongly)
                if pattern.system_activation:
                    system_weight = weight * 0.5
                    if pattern.system_activation in [AffectiveSystem.RAGE, 
                                                      AffectiveSystem.FEAR, 
                                                      AffectiveSystem.PANIC_GRIEF]:
                        system_weight *= 1.5  # Negative systems activate faster
                    self._activate_system(pattern.system_activation, system_weight)
        
        # Clamp all values to valid range
        for field_name in ['novelty', 'pleasantness', 'goal_relevance', 'goal_conduciveness',
                          'urgency', 'control', 'power', 'adjustment', 
                          'internal_standards', 'external_standards']:
            value = getattr(appraisal, field_name)
            setattr(appraisal, field_name, max(-1, min(1, value)))
        
        self.last_appraisal = appraisal
        return appraisal
    
    def _activate_system(self, system: AffectiveSystem, intensity: float) -> None:
        """Activate a Panksepp affective system."""
        current = self.system_activations.get(system.value, 0)
        # Systems have momentum - harder to change when already activated
        new_value = current + (intensity - current) * (1 - self.emotional_inertia)
        self.system_activations[system.value] = max(0, min(1, new_value))
    
    def update_affect(self, appraisal: AppraisalResult) -> None:
        """
        Update core affect based on appraisal result.
        
        Integrates appraisal into the dimensional affect space.
        
        Implements realistic psychological principles:
        
        1. EMOTIONAL CONTAMINATION (Forgas, 1995):
           - Negative states "contaminate" and suppress positive processing
           - When already negative, harder to shift to positive
        
        2. ASYMMETRIC TRANSITIONS (Larsen & Prizmic, 2008):
           - Easier to go from positive → negative
           - Harder to go from negative → positive
        """
        # Get target affect from appraisal
        target = appraisal.to_dimensions()
        
        # Get influence from active affective systems
        system_influence = AffectiveDimensions()
        total_activation = 0
        
        for system_name, activation in self.system_activations.items():
            if activation > 0.1:
                system = AffectiveSystem(system_name)
                system_dims = SYSTEM_DIMENSIONS[system]
                system_influence = AffectiveDimensions(
                    valence=system_influence.valence + system_dims.valence * activation,
                    arousal=system_influence.arousal + system_dims.arousal * activation,
                    dominance=system_influence.dominance + system_dims.dominance * activation,
                )
                total_activation += activation
        
        if total_activation > 0:
            system_influence = AffectiveDimensions(
                valence=system_influence.valence / total_activation,
                arousal=system_influence.arousal / total_activation,
                dominance=system_influence.dominance / total_activation,
            )
        
        # Blend appraisal and system influences
        combined_target = target.blend(system_influence, 0.4)
        
        # EMOTIONAL CONTAMINATION: If currently negative, resist positive shifts
        # This models how negative moods make it harder to feel positive
        transition_resistance = 1 - self.emotional_inertia
        
        if self.current_affect.valence < -0.3 and combined_target.valence > 0:
            # Currently negative, trying to go positive: high resistance
            # Requires stronger positive stimulus to overcome negativity
            transition_resistance *= 0.4  # 60% harder to shift positive
        elif self.current_affect.valence > 0.3 and combined_target.valence < 0:
            # Currently positive, going negative: low resistance (easy transition)
            transition_resistance *= 1.3  # 30% easier to shift negative
        
        # Apply with adjusted inertia (use transition_resistance instead of fixed inertia)
        self.current_affect = self.current_affect.blend(
            combined_target, 
            min(1.0, transition_resistance)  # Cap at 1.0
        )
        
        # Record in history
        self._record_state()
    
    def decay(self, seconds_elapsed: Optional[float] = None) -> None:
        """
        Apply homeostatic decay - emotions return toward baseline.
        
        Based on REALISTIC psychological research:
        
        1. NEGATIVITY BIAS (Baumeister et al., 2001):
           - Negative emotions are more "sticky" and decay SLOWER
           - Positive emotions are more fragile and decay FASTER
           - Ratio: ~2:1 (negative takes ~2x longer to fade)
        
        2. EMOTIONAL RECOVERY (Davidson, 2000):
           - High arousal negative states (fear, anger) persist longer
           - Recovery time varies by individual (emotional resilience)
        
        3. HEDONIC ADAPTATION (Lyubomirsky, 2011):
           - We adapt quickly to positive changes (positive emotions fade)
           - We adapt slowly to negative changes (negative lingers)
        """
        now = datetime.now()
        if seconds_elapsed is None:
            seconds_elapsed = (now - self.last_update).total_seconds()
        
        # Base decay rate per minute
        base_decay_rate = 0.05 * (seconds_elapsed / 60.0)
        
        # REALISTIC DECAY: Negative emotions decay SLOWER than positive
        # This reflects the negativity bias in human psychology
        if self.current_affect.valence < -0.2:
            # Negative emotions: slower decay (they "stick")
            # High arousal negative (fear, anger) decays even slower
            arousal_factor = 1.0 + max(0, self.current_affect.arousal) * 0.5
            decay_rate = base_decay_rate * 0.4 / arousal_factor  # 60% slower base
        elif self.current_affect.valence > 0.2:
            # Positive emotions: faster decay (hedonic adaptation)
            decay_rate = base_decay_rate * 1.5  # 50% faster decay
        else:
            # Neutral zone: normal decay
            decay_rate = base_decay_rate
        
        # Decay affect toward baseline
        self.current_affect = self.current_affect.decay_toward(
            self.baseline_affect, 
            rate=decay_rate
        )
        
        # Decay system activations (negative systems persist longer)
        for system in self.system_activations:
            if system in ['rage', 'fear', 'panic_grief']:
                # Negative systems decay 50% slower
                self.system_activations[system] *= (1 - decay_rate * 0.5)
            elif system in ['play', 'care']:
                # Positive nurturing systems decay at normal rate
                self.system_activations[system] *= (1 - decay_rate)
            else:
                # Seeking is neutral-positive, decays normally
                self.system_activations[system] *= (1 - decay_rate * 0.8)
        
        self.last_update = now
    
    def _record_state(self) -> None:
        """Record current state for history tracking."""
        self.affect_history.append({
            "timestamp": datetime.now().isoformat(),
            "valence": self.current_affect.valence,
            "arousal": self.current_affect.arousal,
            "dominance": self.current_affect.dominance,
            "systems": dict(self.system_activations),
        })
        
        # Trim history
        if len(self.affect_history) > self.max_history:
            self.affect_history = self.affect_history[-self.max_history:]
    
    def get_emotion_label(self) -> Tuple[EmotionLabel, float]:
        """
        Construct emotion label from current affect.
        
        Returns the closest emotion label and confidence.
        """
        return get_closest_emotion(self.current_affect)
    
    def get_dominant_system(self) -> Optional[Tuple[AffectiveSystem, float]]:
        """Get the most active affective system."""
        if not self.system_activations:
            return None
        
        max_system = max(self.system_activations.items(), key=lambda x: x[1])
        if max_system[1] < 0.1:
            return None
        
        return AffectiveSystem(max_system[0]), max_system[1]
    
    @property
    def dominant_emotion(self) -> str:
        """Get dominant emotion label (for compatibility)."""
        emotion, _ = self.get_emotion_label()
        return emotion.value
    
    @property
    def dominant_intensity(self) -> float:
        """Get intensity based on arousal (for compatibility)."""
        # Map arousal to 0-1 range
        return (self.current_affect.arousal + 1) / 2
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive emotional state summary."""
        emotion, confidence = self.get_emotion_label()
        dominant_system = self.get_dominant_system()
        
        return {
            "emotion": emotion.value,
            "emotion_confidence": confidence,
            "valence": self.current_affect.valence,
            "arousal": self.current_affect.arousal,
            "dominance": self.current_affect.dominance,
            "dominant_system": dominant_system[0].value if dominant_system else None,
            "system_intensity": dominant_system[1] if dominant_system else 0,
            "all_systems": {k: round(v, 2) for k, v in self.system_activations.items() if v > 0.1},
        }
    
    def get_response_modifier(self) -> str:
        """
        Get text to modify character responses based on emotional state.
        
        This is used in prompts to the LLM.
        """
        emotion, confidence = self.get_emotion_label()
        dominant_system = self.get_dominant_system()
        
        modifiers = []
        
        # Valence-based modifiers
        if self.current_affect.valence > 0.5:
            modifiers.append("feeling positively inclined")
        elif self.current_affect.valence < -0.5:
            modifiers.append("feeling negatively affected")
        
        # Arousal-based modifiers
        if self.current_affect.arousal > 0.5:
            modifiers.append("in a heightened emotional state")
        elif self.current_affect.arousal < -0.3:
            modifiers.append("in a calm, low-energy state")
        
        # Dominance-based modifiers
        if self.current_affect.dominance > 0.5:
            modifiers.append("feeling confident and in control")
        elif self.current_affect.dominance < -0.5:
            modifiers.append("feeling somewhat vulnerable")
        
        # System-based modifiers
        if dominant_system:
            system, intensity = dominant_system
            if intensity > 0.3:
                system_descriptions = {
                    AffectiveSystem.SEEKING: "curious and explorative",
                    AffectiveSystem.RAGE: "frustrated or angered",
                    AffectiveSystem.FEAR: "cautious and wary",
                    AffectiveSystem.CARE: "nurturing and protective",
                    AffectiveSystem.PANIC_GRIEF: "experiencing a sense of loss",
                    AffectiveSystem.PLAY: "playful and lighthearted",
                    AffectiveSystem.LUST: "drawn to connection",
                }
                modifiers.append(system_descriptions.get(system, ""))
        
        # Emotion label
        if confidence > 0.5:
            modifiers.append(f"experiencing {emotion.value}")
        
        if modifiers:
            return f"[Emotional state: {', '.join(filter(None, modifiers))}]"
        return "[Emotional state: neutral]"


# =============================================================================
# Factory function for creating emotional states
# =============================================================================

def create_advanced_emotional_state(
    character_id: str,
    baseline_valence: float = 0.15,  # Slightly positive baseline
    baseline_arousal: float = 0.1,   # Slightly engaged
    baseline_dominance: float = 0.0,
    emotional_inertia: float = 0.25,  # Reduced inertia for more responsiveness
) -> AdvancedEmotionalState:
    """
    Create an advanced emotional state for a character.
    
    Args:
        character_id: Character identifier
        baseline_valence: Default pleasantness (-1 to 1), default slightly positive
        baseline_arousal: Default activation level (-1 to 1), default slightly engaged
        baseline_dominance: Default sense of control (-1 to 1)
        emotional_inertia: Resistance to emotional change (0 to 1)
    
    Note: Default baseline is slightly positive to reflect that fantasy
    characters are generally "open" to interaction and engagement.
    """
    baseline = AffectiveDimensions(
        valence=baseline_valence,
        arousal=baseline_arousal,
        dominance=baseline_dominance,
    )
    
    return AdvancedEmotionalState(
        character_id=character_id,
        current_affect=baseline,
        baseline_affect=baseline,
        emotional_inertia=emotional_inertia,
    )
