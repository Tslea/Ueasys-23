"""
Character Loader - Load and Parse Character YAML Files

This module handles loading character definitions from YAML files
and converting them to CharacterTemplate objects.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import structlog

from ..core.character.character_template import (
    CharacterTemplate,
    PersonalityTraits,
    EmotionalProfile,
    SpeechPattern,
    CharacterBackground,
    CharacterGoal,
    CharacterRelationship
)


logger = structlog.get_logger(__name__)


class CharacterLoader:
    """
    Loads and parses character definitions from YAML files.
    """
    
    def __init__(self, characters_dir: str = "data/characters"):
        """
        Initialize the character loader.
        
        Args:
            characters_dir: Directory containing character YAML files
        """
        self.characters_dir = Path(characters_dir)
        self._character_cache: Dict[str, CharacterTemplate] = {}
    
    def load_character(self, character_id: str) -> Optional[CharacterTemplate]:
        """
        Load a single character by ID.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            CharacterTemplate if found, None otherwise
        """
        # Check cache first
        if character_id in self._character_cache:
            return self._character_cache[character_id]
        
        # Try to find the YAML file
        yaml_path = self.characters_dir / f"{character_id}.yaml"
        if not yaml_path.exists():
            yaml_path = self.characters_dir / f"{character_id}.yml"
        
        if not yaml_path.exists():
            logger.warning("character_file_not_found", character_id=character_id)
            return None
        
        try:
            character = self._load_from_file(yaml_path)
            if character:
                self._character_cache[character_id] = character
            return character
        except Exception as e:
            logger.error(
                "character_load_failed",
                character_id=character_id,
                error=str(e)
            )
            return None
    
    def load_all_characters(self) -> List[CharacterTemplate]:
        """
        Load all characters from the characters directory.
        
        Returns:
            List of loaded CharacterTemplate objects
        """
        characters = []
        
        if not self.characters_dir.exists():
            logger.warning(
                "characters_dir_not_found",
                path=str(self.characters_dir)
            )
            return characters
        
        for yaml_file in self.characters_dir.glob("*.yaml"):
            try:
                character = self._load_from_file(yaml_file)
                if character:
                    characters.append(character)
                    self._character_cache[character.id] = character
            except Exception as e:
                logger.error(
                    "character_load_failed",
                    file=str(yaml_file),
                    error=str(e)
                )
        
        # Also check .yml files
        for yaml_file in self.characters_dir.glob("*.yml"):
            try:
                character = self._load_from_file(yaml_file)
                if character:
                    if character.id not in self._character_cache:
                        characters.append(character)
                        self._character_cache[character.id] = character
            except Exception as e:
                logger.error(
                    "character_load_failed",
                    file=str(yaml_file),
                    error=str(e)
                )
        
        logger.info("characters_loaded", count=len(characters))
        return characters
    
    def _load_from_file(self, path: Path) -> Optional[CharacterTemplate]:
        """
        Load a character from a YAML file.
        
        Args:
            path: Path to the YAML file
            
        Returns:
            CharacterTemplate if successful, None otherwise
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._parse_character_data(data)
    
    def _parse_character_data(self, data: Dict[str, Any]) -> Optional[CharacterTemplate]:
        """
        Parse raw YAML data into a CharacterTemplate.
        
        Args:
            data: Raw dictionary from YAML
            
        Returns:
            CharacterTemplate if parsing succeeds
        """
        try:
            char_data = data.get("character", {})
            personality_data = data.get("personality", {})
            speech_data = data.get("speech_patterns", {})
            background_data = data.get("background", {})
            goals_data = data.get("goals", {})
            emotional_data = data.get("emotional_state", {})
            response_config = data.get("response_config", {})
            
            # Parse personality traits
            traits_data = personality_data.get("traits", {})
            personality_traits = PersonalityTraits(
                openness=traits_data.get("openness", 0.5),
                conscientiousness=traits_data.get("conscientiousness", 0.5),
                extraversion=traits_data.get("extraversion", 0.5),
                agreeableness=traits_data.get("agreeableness", 0.5),
                neuroticism=traits_data.get("neuroticism", 0.5),
                dominant_traits=personality_data.get("dominant_traits", []),
                values=personality_data.get("values", []),
                fears=personality_data.get("fears", [])
            )
            
            # Parse emotional profile
            triggers = emotional_data.get("emotional_triggers", {})
            emotional_profile = EmotionalProfile(
                default_mood=emotional_data.get("default_mood", "neutral"),
                mood_volatility=emotional_data.get("mood_volatility", 0.3),
                joy_triggers=triggers.get("joy", []),
                anger_triggers=triggers.get("anger", []),
                sadness_triggers=triggers.get("sadness", []),
                fear_triggers=triggers.get("fear", triggers.get("concern", []))
            )
            
            # Parse speech pattern
            vocab_data = speech_data.get("vocabulary", {})
            speech_pattern = SpeechPattern(
                formality=speech_data.get("formality", 0.5),
                verbosity=speech_data.get("verbosity", 0.5),
                complexity=speech_data.get("complexity", 0.5),
                warmth=speech_data.get("warmth", 0.5),
                catchphrases=speech_data.get("catchphrases", []),
                vocabulary_preferences=vocab_data.get("preferred_words", []),
                avoided_words=vocab_data.get("avoided_words", []),
                style_notes=speech_data.get("style_notes", [])
            )
            
            # Parse background
            background = CharacterBackground(
                origin=background_data.get("origin", "Unknown"),
                history=background_data.get("history", ""),
                key_events=background_data.get("key_events", []),
                secrets=[],  # Not in YAML by default
                world_knowledge=data.get("knowledge", {}).get("expert", [])
            )
            
            # Parse goals
            goals = []
            for goal_data in goals_data.get("primary", []):
                goals.append(CharacterGoal(
                    description=goal_data.get("description", ""),
                    priority=goal_data.get("priority", 0.5),
                    goal_type=goal_data.get("type", "general"),
                    progress=0.0
                ))
            for goal_data in goals_data.get("secondary", []):
                goals.append(CharacterGoal(
                    description=goal_data.get("description", ""),
                    priority=goal_data.get("priority", 0.5),
                    goal_type=goal_data.get("type", "general"),
                    progress=0.0
                ))
            
            # Parse relationships
            relationships = []
            rel_data = background_data.get("relationships", {})
            for ally in rel_data.get("allies", []):
                relationships.append(CharacterRelationship(
                    character_id=ally.get("name", "").lower().replace(" ", "_"),
                    character_name=ally.get("name", ""),
                    relationship_type=ally.get("type", "ally"),
                    strength=ally.get("strength", 0.5),
                    description=ally.get("description", "")
                ))
            for enemy in rel_data.get("enemies", []):
                relationships.append(CharacterRelationship(
                    character_id=enemy.get("name", "").lower().replace(" ", "_"),
                    character_name=enemy.get("name", ""),
                    relationship_type=enemy.get("type", "enemy"),
                    strength=-enemy.get("strength", 0.5),
                    description=enemy.get("description", "")
                ))
            
            # Create the character template
            template = CharacterTemplate(
                id=char_data.get("id", "unknown"),
                name=char_data.get("name", "Unknown"),
                full_name=char_data.get("full_name"),
                description=char_data.get("description", ""),
                archetype=char_data.get("archetype", "generic"),
                personality=personality_traits,
                emotional_profile=emotional_profile,
                speech_pattern=speech_pattern,
                background=background,
                goals=goals,
                relationships=relationships
            )
            
            # Add extra metadata
            template.world = char_data.get("world", "fantasy")
            template.role = char_data.get("role", "npc")
            template.other_names = char_data.get("other_names", [])
            template.knowledge_domains = data.get("knowledge", {})
            template.response_config = response_config
            template.interaction_patterns = data.get("interaction_patterns", {})
            
            logger.info(
                "character_parsed",
                character_id=template.id,
                name=template.name
            )
            
            return template
            
        except Exception as e:
            logger.error("character_parse_failed", error=str(e))
            raise
    
    def reload_character(self, character_id: str) -> Optional[CharacterTemplate]:
        """
        Reload a character, bypassing the cache.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Reloaded CharacterTemplate
        """
        if character_id in self._character_cache:
            del self._character_cache[character_id]
        return self.load_character(character_id)
    
    def clear_cache(self):
        """Clear the character cache."""
        self._character_cache.clear()
        logger.info("character_cache_cleared")
    
    def get_character_ids(self) -> List[str]:
        """
        Get list of available character IDs.
        
        Returns:
            List of character IDs (file names without extension)
        """
        ids = []
        
        if self.characters_dir.exists():
            for yaml_file in self.characters_dir.glob("*.yaml"):
                ids.append(yaml_file.stem)
            for yaml_file in self.characters_dir.glob("*.yml"):
                if yaml_file.stem not in ids:
                    ids.append(yaml_file.stem)
        
        return ids
    
    def validate_character(self, character_id: str) -> Dict[str, Any]:
        """
        Validate a character definition.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Validation results with any errors/warnings
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        yaml_path = self.characters_dir / f"{character_id}.yaml"
        if not yaml_path.exists():
            yaml_path = self.characters_dir / f"{character_id}.yml"
        
        if not yaml_path.exists():
            result["valid"] = False
            result["errors"].append(f"Character file not found: {character_id}")
            return result
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check required sections
            required_sections = ["character", "personality", "speech_patterns", "background"]
            for section in required_sections:
                if section not in data:
                    result["warnings"].append(f"Missing section: {section}")
            
            # Check character basics
            char_data = data.get("character", {})
            if not char_data.get("id"):
                result["errors"].append("Missing character id")
                result["valid"] = False
            if not char_data.get("name"):
                result["errors"].append("Missing character name")
                result["valid"] = False
            if not char_data.get("description"):
                result["warnings"].append("Missing character description")
            
            # Check personality
            personality = data.get("personality", {})
            traits = personality.get("traits", {})
            for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
                if trait not in traits:
                    result["warnings"].append(f"Missing personality trait: {trait}")
            
            # Check speech patterns
            speech = data.get("speech_patterns", {})
            if not speech.get("catchphrases"):
                result["warnings"].append("No catchphrases defined")
            
        except yaml.YAMLError as e:
            result["valid"] = False
            result["errors"].append(f"YAML parsing error: {str(e)}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result


# Global loader instance
_loader: Optional[CharacterLoader] = None


def get_character_loader(characters_dir: str = "data/characters") -> CharacterLoader:
    """Get or create the global character loader instance."""
    global _loader
    if _loader is None:
        _loader = CharacterLoader(characters_dir)
    return _loader
