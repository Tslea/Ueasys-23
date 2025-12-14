"""
Knowledge Indexing Script

This script indexes character knowledge and world lore into the RAG system.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_settings
from src.data.character_loader import CharacterLoader


class KnowledgeIndexer:
    """
    Indexes knowledge from various sources into the RAG system.
    """
    
    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.indexed_count = 0
    
    async def index_character_knowledge(
        self,
        character_loader: CharacterLoader
    ) -> int:
        """
        Index character-specific knowledge from YAML files.
        
        Returns:
            Number of documents indexed
        """
        characters = character_loader.load_all_characters()
        indexed = 0
        
        for char in characters:
            print(f"\n📚 Indexing knowledge for: {char.name}")
            
            # Index character description
            doc = {
                "id": f"char_{char.id}_description",
                "content": char.description,
                "metadata": {
                    "type": "character_description",
                    "character_id": char.id,
                    "character_name": char.name
                }
            }
            await self._index_document(doc)
            indexed += 1
            
            # Index character history
            if char.background.history:
                doc = {
                    "id": f"char_{char.id}_history",
                    "content": char.background.history,
                    "metadata": {
                        "type": "character_history",
                        "character_id": char.id,
                        "character_name": char.name
                    }
                }
                await self._index_document(doc)
                indexed += 1
            
            # Index speech patterns as style reference
            if char.speech_pattern.catchphrases:
                catchphrases_text = "\n".join([
                    f'- "{phrase}"' for phrase in char.speech_pattern.catchphrases
                ])
                doc = {
                    "id": f"char_{char.id}_speech",
                    "content": f"Characteristic phrases of {char.name}:\n{catchphrases_text}",
                    "metadata": {
                        "type": "character_speech",
                        "character_id": char.id,
                        "character_name": char.name
                    }
                }
                await self._index_document(doc)
                indexed += 1
            
            # Index key events
            if char.background.key_events:
                events_text = "\n".join([
                    f"- {event}" for event in char.background.key_events
                ])
                doc = {
                    "id": f"char_{char.id}_events",
                    "content": f"Key events in {char.name}'s history:\n{events_text}",
                    "metadata": {
                        "type": "character_events",
                        "character_id": char.id,
                        "character_name": char.name
                    }
                }
                await self._index_document(doc)
                indexed += 1
            
            # Index relationships
            if char.relationships:
                relationships_text = []
                for rel in char.relationships:
                    relationships_text.append(
                        f"- {rel.character_name} ({rel.relationship_type}): {rel.description}"
                    )
                doc = {
                    "id": f"char_{char.id}_relationships",
                    "content": f"{char.name}'s relationships:\n" + "\n".join(relationships_text),
                    "metadata": {
                        "type": "character_relationships",
                        "character_id": char.id,
                        "character_name": char.name
                    }
                }
                await self._index_document(doc)
                indexed += 1
        
        print(f"\n✅ Indexed {indexed} character documents")
        return indexed
    
    async def index_world_knowledge(self) -> int:
        """
        Index world lore and knowledge from YAML files.
        
        Returns:
            Number of documents indexed
        """
        indexed = 0
        lore_dir = self.knowledge_dir / "lore"
        
        if not lore_dir.exists():
            print(f"⚠️  Lore directory not found: {lore_dir}")
            return 0
        
        for yaml_file in lore_dir.glob("*.yaml"):
            print(f"\n📖 Indexing: {yaml_file.name}")
            
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                # Process based on structure
                if "entries" in data:
                    for entry in data["entries"]:
                        doc = {
                            "id": f"lore_{yaml_file.stem}_{entry.get('id', indexed)}",
                            "content": entry.get("content", ""),
                            "metadata": {
                                "type": "world_lore",
                                "category": data.get("category", "general"),
                                "source": yaml_file.name,
                                **entry.get("metadata", {})
                            }
                        }
                        await self._index_document(doc)
                        indexed += 1
                
                elif "content" in data:
                    doc = {
                        "id": f"lore_{yaml_file.stem}",
                        "content": data["content"],
                        "metadata": {
                            "type": "world_lore",
                            "category": data.get("category", "general"),
                            "source": yaml_file.name
                        }
                    }
                    await self._index_document(doc)
                    indexed += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Indexed {indexed} lore documents")
        return indexed
    
    async def index_locations(self) -> int:
        """
        Index location descriptions and information.
        
        Returns:
            Number of documents indexed
        """
        indexed = 0
        locations_dir = self.knowledge_dir / "locations"
        
        if not locations_dir.exists():
            print(f"⚠️  Locations directory not found: {locations_dir}")
            return 0
        
        for yaml_file in locations_dir.glob("*.yaml"):
            print(f"\n🗺️  Indexing: {yaml_file.name}")
            
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                location_id = data.get("id", yaml_file.stem)
                
                # Index main description
                if "description" in data:
                    doc = {
                        "id": f"location_{location_id}_desc",
                        "content": data["description"],
                        "metadata": {
                            "type": "location",
                            "location_id": location_id,
                            "name": data.get("name", location_id)
                        }
                    }
                    await self._index_document(doc)
                    indexed += 1
                
                # Index history
                if "history" in data:
                    doc = {
                        "id": f"location_{location_id}_history",
                        "content": data["history"],
                        "metadata": {
                            "type": "location_history",
                            "location_id": location_id,
                            "name": data.get("name", location_id)
                        }
                    }
                    await self._index_document(doc)
                    indexed += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Indexed {indexed} location documents")
        return indexed
    
    async def _index_document(self, doc: Dict[str, Any]):
        """
        Index a single document into the RAG system.
        
        In production, this would connect to the actual RAG/vector store.
        For now, it's a placeholder that logs the operation.
        """
        self.indexed_count += 1
        print(f"   📄 [{doc['id']}] {doc['content'][:50]}...")
        
        # TODO: Connect to actual RAG system
        # await rag_system.index_document(
        #     doc_id=doc["id"],
        #     content=doc["content"],
        #     metadata=doc["metadata"]
        # )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        return {
            "total_indexed": self.indexed_count
        }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index knowledge into RAG system")
    parser.add_argument(
        "--characters-dir",
        default="data/characters",
        help="Path to characters directory"
    )
    parser.add_argument(
        "--knowledge-dir",
        default="data/knowledge",
        help="Path to knowledge directory"
    )
    parser.add_argument(
        "--characters-only",
        action="store_true",
        help="Only index character knowledge"
    )
    parser.add_argument(
        "--world-only",
        action="store_true",
        help="Only index world knowledge"
    )
    
    args = parser.parse_args()
    
    print("📚 Knowledge Indexing Script")
    print("=" * 40)
    
    indexer = KnowledgeIndexer(args.knowledge_dir)
    character_loader = CharacterLoader(args.characters_dir)
    
    total_indexed = 0
    
    if not args.world_only:
        print("\n🎭 INDEXING CHARACTER KNOWLEDGE")
        print("-" * 40)
        count = await indexer.index_character_knowledge(character_loader)
        total_indexed += count
    
    if not args.characters_only:
        print("\n🌍 INDEXING WORLD KNOWLEDGE")
        print("-" * 40)
        count = await indexer.index_world_knowledge()
        total_indexed += count
        
        print("\n🗺️  INDEXING LOCATIONS")
        print("-" * 40)
        count = await indexer.index_locations()
        total_indexed += count
    
    print("\n" + "=" * 40)
    print(f"✅ Total documents indexed: {total_indexed}")
    
    stats = indexer.get_stats()
    print(f"📊 Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
