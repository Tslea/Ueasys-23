"""
Tests for Character Loader.
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

from src.data.character_loader import CharacterLoader


@pytest.fixture
def temp_characters_dir():
    """Create a temporary directory with test character files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test character YAML
        test_char = {
            "character": {
                "id": "test-hero",
                "name": "Test Hero",
                "full_name": "Test Hero the Brave",
                "description": "A test hero for unit testing.",
                "archetype": "hero",
                "world": "test-world"
            },
            "personality": {
                "traits": {
                    "openness": 0.7,
                    "conscientiousness": 0.8,
                    "extraversion": 0.6,
                    "agreeableness": 0.75,
                    "neuroticism": 0.3
                },
                "dominant_traits": ["brave", "honest"],
                "values": ["honor", "justice"],
                "fears": ["failure"]
            },
            "speech_patterns": {
                "formality": 0.6,
                "verbosity": 0.5,
                "complexity": 0.5,
                "warmth": 0.7,
                "catchphrases": ["For glory!", "Stand firm!"],
                "vocabulary": {
                    "preferred_words": ["honor", "duty"],
                    "avoided_words": ["retreat"]
                }
            },
            "background": {
                "origin": "The Northern Lands",
                "history": "Born a simple farmer, became a hero.",
                "key_events": ["The Great Battle"],
                "relationships": {
                    "allies": [
                        {
                            "name": "Wise Mentor",
                            "type": "mentor",
                            "strength": 0.9,
                            "description": "Teacher and guide"
                        }
                    ],
                    "enemies": [
                        {
                            "name": "Dark Lord",
                            "type": "nemesis",
                            "strength": 1.0,
                            "description": "The great enemy"
                        }
                    ]
                }
            },
            "emotional_state": {
                "default_mood": "determined",
                "mood_volatility": 0.3,
                "emotional_triggers": {
                    "joy": ["victory"],
                    "anger": ["injustice"],
                    "sadness": ["loss"],
                    "fear": ["darkness"]
                }
            },
            "goals": {
                "primary": [
                    {
                        "description": "Defeat the Dark Lord",
                        "priority": 1.0,
                        "type": "quest"
                    }
                ],
                "secondary": [
                    {
                        "description": "Protect the innocent",
                        "priority": 0.8,
                        "type": "duty"
                    }
                ]
            },
            "knowledge": {
                "expert": ["Battle tactics", "History"],
                "familiar": ["Magic basics"],
                "limited": ["Dark arts"]
            }
        }
        
        # Write the test character
        char_path = Path(tmpdir) / "test-hero.yaml"
        with open(char_path, 'w') as f:
            yaml.dump(test_char, f)
        
        yield tmpdir


class TestCharacterLoader:
    """Tests for CharacterLoader class."""
    
    def test_create_loader(self, temp_characters_dir):
        """Test creating a character loader."""
        loader = CharacterLoader(temp_characters_dir)
        
        assert loader.characters_dir == Path(temp_characters_dir)
    
    def test_get_character_ids(self, temp_characters_dir):
        """Test getting available character IDs."""
        loader = CharacterLoader(temp_characters_dir)
        
        ids = loader.get_character_ids()
        
        assert "test-hero" in ids
    
    def test_load_character(self, temp_characters_dir):
        """Test loading a single character."""
        loader = CharacterLoader(temp_characters_dir)
        
        character = loader.load_character("test-hero")
        
        assert character is not None
        assert character.id == "test-hero"
        assert character.name == "Test Hero"
        assert character.archetype == "hero"
    
    def test_load_nonexistent_character(self, temp_characters_dir):
        """Test loading a non-existent character."""
        loader = CharacterLoader(temp_characters_dir)
        
        character = loader.load_character("nonexistent")
        
        assert character is None
    
    def test_load_all_characters(self, temp_characters_dir):
        """Test loading all characters."""
        loader = CharacterLoader(temp_characters_dir)
        
        characters = loader.load_all_characters()
        
        assert len(characters) >= 1
        assert any(c.id == "test-hero" for c in characters)
    
    def test_character_personality(self, temp_characters_dir):
        """Test that personality is loaded correctly."""
        loader = CharacterLoader(temp_characters_dir)
        character = loader.load_character("test-hero")
        
        assert character.personality.openness == 0.7
        assert character.personality.conscientiousness == 0.8
        assert "brave" in character.personality.dominant_traits
        assert "honor" in character.personality.values
    
    def test_character_speech_pattern(self, temp_characters_dir):
        """Test that speech pattern is loaded correctly."""
        loader = CharacterLoader(temp_characters_dir)
        character = loader.load_character("test-hero")
        
        assert character.speech_pattern.formality == 0.6
        assert "For glory!" in character.speech_pattern.catchphrases
    
    def test_character_background(self, temp_characters_dir):
        """Test that background is loaded correctly."""
        loader = CharacterLoader(temp_characters_dir)
        character = loader.load_character("test-hero")
        
        assert character.background.origin == "The Northern Lands"
        assert "The Great Battle" in character.background.key_events
    
    def test_character_relationships(self, temp_characters_dir):
        """Test that relationships are loaded correctly."""
        loader = CharacterLoader(temp_characters_dir)
        character = loader.load_character("test-hero")
        
        assert len(character.relationships) >= 2
        
        # Check for ally
        ally = next((r for r in character.relationships if r.relationship_type == "mentor"), None)
        assert ally is not None
        assert ally.character_name == "Wise Mentor"
        
        # Check for enemy
        enemy = next((r for r in character.relationships if r.relationship_type == "nemesis"), None)
        assert enemy is not None
        assert enemy.character_name == "Dark Lord"
    
    def test_character_goals(self, temp_characters_dir):
        """Test that goals are loaded correctly."""
        loader = CharacterLoader(temp_characters_dir)
        character = loader.load_character("test-hero")
        
        assert len(character.goals) >= 2
        
        primary = next((g for g in character.goals if g.priority == 1.0), None)
        assert primary is not None
        assert "Dark Lord" in primary.description
    
    def test_caching(self, temp_characters_dir):
        """Test that characters are cached."""
        loader = CharacterLoader(temp_characters_dir)
        
        # Load twice
        char1 = loader.load_character("test-hero")
        char2 = loader.load_character("test-hero")
        
        # Should be the same object
        assert char1 is char2
    
    def test_reload_character(self, temp_characters_dir):
        """Test reloading a character bypasses cache."""
        loader = CharacterLoader(temp_characters_dir)
        
        char1 = loader.load_character("test-hero")
        char2 = loader.reload_character("test-hero")
        
        # Should be different objects (reloaded)
        assert char1 is not char2
    
    def test_clear_cache(self, temp_characters_dir):
        """Test clearing the cache."""
        loader = CharacterLoader(temp_characters_dir)
        
        loader.load_character("test-hero")
        assert len(loader._character_cache) > 0
        
        loader.clear_cache()
        assert len(loader._character_cache) == 0
    
    def test_validate_character(self, temp_characters_dir):
        """Test character validation."""
        loader = CharacterLoader(temp_characters_dir)
        
        result = loader.validate_character("test-hero")
        
        assert result["valid"] == True
        assert len(result["errors"]) == 0
    
    def test_validate_nonexistent_character(self, temp_characters_dir):
        """Test validating non-existent character."""
        loader = CharacterLoader(temp_characters_dir)
        
        result = loader.validate_character("nonexistent")
        
        assert result["valid"] == False
        assert len(result["errors"]) > 0


class TestCharacterLoaderEdgeCases:
    """Tests for edge cases in character loading."""
    
    def test_empty_directory(self):
        """Test loading from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = CharacterLoader(tmpdir)
            
            characters = loader.load_all_characters()
            
            assert len(characters) == 0
    
    def test_nonexistent_directory(self):
        """Test loading from non-existent directory."""
        loader = CharacterLoader("/nonexistent/path")
        
        characters = loader.load_all_characters()
        
        assert len(characters) == 0
    
    def test_invalid_yaml(self):
        """Test loading invalid YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid YAML
            invalid_path = Path(tmpdir) / "invalid.yaml"
            with open(invalid_path, 'w') as f:
                f.write("{{invalid: yaml: content:")
            
            loader = CharacterLoader(tmpdir)
            
            # Should not raise, but return None
            character = loader.load_character("invalid")
            assert character is None
    
    def test_minimal_character(self):
        """Test loading minimal character definition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            minimal = {
                "character": {
                    "id": "minimal",
                    "name": "Minimal Character"
                }
            }
            
            char_path = Path(tmpdir) / "minimal.yaml"
            with open(char_path, 'w') as f:
                yaml.dump(minimal, f)
            
            loader = CharacterLoader(tmpdir)
            character = loader.load_character("minimal")
            
            # Should load with defaults
            assert character is not None
            assert character.id == "minimal"
            assert character.name == "Minimal Character"
