"""
Character Seeding Script

This script loads character definitions from YAML files and seeds
them into the database using the current model structure.
"""

import asyncio
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.config.settings import get_settings
from src.data.character_loader import CharacterLoader
from src.db.models.character import (
    Character, 
    CharacterTrait, 
    CharacterRelationship,
    ArchetypeType,
    AlignmentType,
    CharacterStatus
)
from src.core.character.character_template import CharacterTemplate


# Mapping from YAML archetype strings to ArchetypeType enum
ARCHETYPE_MAPPING = {
    "wise_mentor": ArchetypeType.MENTOR,
    "mentor": ArchetypeType.MENTOR,
    "hero": ArchetypeType.HERO,
    "guardian": ArchetypeType.GUARDIAN,
    "trickster": ArchetypeType.TRICKSTER,
    "sage": ArchetypeType.SAGE,
    "ruler": ArchetypeType.RULER,
    "creator": ArchetypeType.CREATOR,
    "innocent": ArchetypeType.INNOCENT,
    "explorer": ArchetypeType.EXPLORER,
    "rebel": ArchetypeType.REBEL,
    "lover": ArchetypeType.LOVER,
    "jester": ArchetypeType.JESTER,
    "everyman": ArchetypeType.EVERYMAN,
    "caregiver": ArchetypeType.CAREGIVER,
    "magician": ArchetypeType.MAGICIAN,
    "outlaw": ArchetypeType.OUTLAW,
    "warrior": ArchetypeType.WARRIOR,
    "shadow": ArchetypeType.SHADOW,
    "noble_leader": ArchetypeType.RULER,
    "elven_queen": ArchetypeType.RULER,
    "ranger": ArchetypeType.EXPLORER,
    "noble_warrior": ArchetypeType.WARRIOR,
    "dragon": ArchetypeType.SHADOW,
    "antagonist": ArchetypeType.SHADOW,
    "generic": ArchetypeType.EVERYMAN,
}


def get_archetype(yaml_archetype: str) -> ArchetypeType:
    """Convert YAML archetype string to ArchetypeType enum."""
    normalized = yaml_archetype.lower().replace("-", "_").replace(" ", "_")
    return ARCHETYPE_MAPPING.get(normalized, ArchetypeType.EVERYMAN)


def determine_alignment(template: CharacterTemplate) -> AlignmentType:
    """Determine alignment based on character traits and background."""
    fears = template.personality.fears if template.personality else []
    values = template.personality.values if template.personality else []
    
    # Simple heuristic based on values
    is_good = any(v in str(values).lower() for v in ["protect", "hope", "friend", "love", "help", "innocent"])
    is_evil = any(v in str(values).lower() for v in ["power", "domination", "greed", "revenge", "destroy"])
    is_lawful = any(v in str(values).lower() for v in ["duty", "order", "law", "tradition", "honor"])
    is_chaotic = any(v in str(values).lower() for v in ["freedom", "change", "rebellion", "adventure"])
    
    if is_evil:
        if is_lawful:
            return AlignmentType.LAWFUL_EVIL
        elif is_chaotic:
            return AlignmentType.CHAOTIC_EVIL
        return AlignmentType.NEUTRAL_EVIL
    elif is_good:
        if is_lawful:
            return AlignmentType.LAWFUL_GOOD
        elif is_chaotic:
            return AlignmentType.CHAOTIC_GOOD
        return AlignmentType.NEUTRAL_GOOD
    else:
        if is_lawful:
            return AlignmentType.LAWFUL_NEUTRAL
        elif is_chaotic:
            return AlignmentType.CHAOTIC_NEUTRAL
        return AlignmentType.TRUE_NEUTRAL


async def seed_characters(
    session: AsyncSession,
    characters_dir: str = "data/characters"
) -> List[str]:
    """
    Seed characters from YAML files into the database.
    
    Args:
        session: Database session
        characters_dir: Path to characters directory
        
    Returns:
        List of seeded character names
    """
    loader = CharacterLoader(characters_dir)
    templates = loader.load_all_characters()
    
    seeded_names = []
    
    for template in templates:
        print(f"\n📝 Processing: {template.name}")
        
        # Check if character already exists by name
        existing = await session.execute(
            select(Character).where(Character.name == template.name)
        )
        if existing.scalar_one_or_none():
            print(f"   ⏩ Already exists, skipping")
            continue
        
        # Build personality JSON
        personality_json = {
            "openness": template.personality.openness,
            "conscientiousness": template.personality.conscientiousness,
            "extraversion": template.personality.extraversion,
            "agreeableness": template.personality.agreeableness,
            "neuroticism": template.personality.neuroticism,
            "dominant_traits": template.personality.dominant_traits,
            "values": template.personality.values,
            "fears": template.personality.fears,
        }
        
        # Build speaking style JSON
        speaking_style_json = {
            "formality": template.speech_pattern.formality,
            "verbosity": template.speech_pattern.verbosity,
            "complexity": template.speech_pattern.complexity,
            "warmth": template.speech_pattern.warmth,
            "catchphrases": template.speech_pattern.catchphrases,
            "vocabulary_preferences": template.speech_pattern.vocabulary_preferences,
            "avoided_words": template.speech_pattern.avoided_words,
            "style_notes": template.speech_pattern.style_notes,
        }
        
        # Build background JSON
        background_json = {
            "origin": template.background.origin,
            "history": template.background.history,
            "key_events": template.background.key_events,
            "world_knowledge": template.background.world_knowledge,
            "emotional_profile": {
                "default_mood": template.emotional_profile.default_mood,
                "mood_volatility": template.emotional_profile.mood_volatility,
                "joy_triggers": template.emotional_profile.joy_triggers,
                "anger_triggers": template.emotional_profile.anger_triggers,
                "sadness_triggers": template.emotional_profile.sadness_triggers,
                "fear_triggers": template.emotional_profile.fear_triggers,
            }
        }
        
        # Build metadata JSON
        metadata_json = {
            "yaml_id": template.id,
            "full_name": template.full_name,
            "world": getattr(template, 'world', 'middle-earth'),
            "role": getattr(template, 'role', 'npc'),
            "other_names": getattr(template, 'other_names', []),
            "knowledge_domains": getattr(template, 'knowledge_domains', {}),
            "response_config": getattr(template, 'response_config', {}),
            "interaction_patterns": getattr(template, 'interaction_patterns', {}),
            "goals": [
                {
                    "description": g.description,
                    "priority": g.priority,
                    "type": g.goal_type
                } for g in template.goals
            ]
        }
        
        # Determine archetype and alignment
        archetype = get_archetype(template.archetype)
        alignment = determine_alignment(template)
        
        # Extract title from full_name if present
        title = None
        if template.full_name and template.full_name != template.name:
            title = template.full_name.replace(template.name, "").strip()
            if not title:
                title = None
        
        # Create character model
        character = Character(
            name=template.name,
            title=title,
            description=template.description,
            archetype=archetype,
            alignment=alignment,
            status=CharacterStatus.ACTIVE,
            personality_json=personality_json,
            speaking_style_json=speaking_style_json,
            background_json=background_json,
            metadata_json=metadata_json,
        )
        
        session.add(character)
        await session.flush()  # Get the character ID
        
        # Add traits
        for trait_name in template.personality.dominant_traits:
            trait = CharacterTrait(
                character_id=character.id,
                name=trait_name,
                intensity=1.0,
                description=f"Dominant trait: {trait_name}",
                is_positive=True
            )
            session.add(trait)
        
        # Add values as traits
        for value_name in template.personality.values:
            trait = CharacterTrait(
                character_id=character.id,
                name=value_name,
                intensity=0.8,
                description=f"Core value: {value_name}",
                is_positive=True
            )
            session.add(trait)
        
        seeded_names.append(template.name)
        print(f"   ✅ Created: {template.name} ({archetype.value})")
    
    await session.commit()
    return seeded_names


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed characters into the database")
    parser.add_argument(
        "--characters-dir",
        default="data/characters",
        help="Path to characters directory"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing characters before seeding"
    )
    
    args = parser.parse_args()
    
    settings = get_settings()
    
    print("🌱 Character Seeding Script")
    print("=" * 40)
    
    # Create engine and session
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        async with async_session() as session:
            if args.clear:
                print("\n🗑️  Clearing existing characters...")
                await session.execute(
                    Character.__table__.delete()
                )
                await session.commit()
                print("   ✅ Cleared")
            
            print(f"\n📂 Loading characters from: {args.characters_dir}")
            seeded = await seed_characters(session, args.characters_dir)
            
            print("\n" + "=" * 40)
            print(f"✅ Seeded {len(seeded)} characters:")
            for name in seeded:
                print(f"   - {name}")
                
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
