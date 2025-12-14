"""
Chat Client Script

A simple command-line chat client for testing character interactions.
"""

import asyncio
import sys
from pathlib import Path
import httpx
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ChatClient:
    """Simple HTTP chat client."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.character_id: Optional[str] = None
    
    async def get_characters(self) -> list:
        """Fetch available characters."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/characters")
            response.raise_for_status()
            return response.json().get("characters", [])
    
    async def start_conversation(self, character_id: str, user_id: str = "cli_user") -> dict:
        """Start a new conversation."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/conversations",
                json={
                    "character_id": character_id,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            data = response.json()
            self.session_id = data.get("session_id")
            self.character_id = character_id
            return data
    
    async def send_message(self, content: str) -> dict:
        """Send a message and get response."""
        if not self.session_id:
            raise ValueError("No active session. Start a conversation first.")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "session_id": self.session_id,
                    "content": content
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_history(self) -> list:
        """Get conversation history."""
        if not self.session_id:
            return []
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/conversations/{self.session_id}/messages"
            )
            response.raise_for_status()
            return response.json().get("messages", [])


async def select_character(client: ChatClient) -> Optional[str]:
    """Interactive character selection."""
    print("\n🎭 Available Characters:")
    print("-" * 40)
    
    try:
        characters = await client.get_characters()
    except httpx.HTTPError as e:
        print(f"❌ Failed to fetch characters: {e}")
        print("   Make sure the server is running!")
        return None
    
    if not characters:
        print("   No characters available.")
        return None
    
    for i, char in enumerate(characters, 1):
        print(f"   {i}. {char.get('name', 'Unknown')} ({char.get('character_id', '?')})")
        if char.get('description'):
            desc = char['description'][:100] + "..." if len(char.get('description', '')) > 100 else char.get('description', '')
            print(f"      {desc}")
    
    print()
    
    while True:
        choice = input("Select a character (number or ID): ").strip()
        
        # Check if it's a number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(characters):
                return characters[idx].get('character_id')
        except ValueError:
            pass
        
        # Check if it's a character ID
        for char in characters:
            if char.get('character_id') == choice or char.get('name', '').lower() == choice.lower():
                return char.get('character_id')
        
        print("   Invalid selection. Try again.")


async def chat_loop(client: ChatClient, character_name: str):
    """Main chat loop."""
    print(f"\n💬 Chat with {character_name}")
    print("-" * 40)
    print("Type your message and press Enter.")
    print("Commands: /quit, /history, /clear")
    print("-" * 40)
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith("/"):
            cmd = user_input.lower()
            
            if cmd in ["/quit", "/exit", "/q"]:
                print("\n👋 Goodbye!")
                break
            
            elif cmd == "/history":
                history = await client.get_history()
                print(f"\n📜 History ({len(history)} messages):")
                for msg in history[-10:]:  # Last 10 messages
                    role = "You" if msg.get("role") == "user" else character_name
                    print(f"   {role}: {msg.get('content', '')[:100]}...")
                print()
                continue
            
            elif cmd == "/clear":
                # Start new conversation
                await client.start_conversation(client.character_id)
                print("🔄 New conversation started.\n")
                continue
            
            else:
                print(f"   Unknown command: {cmd}")
                continue
        
        # Send message
        try:
            print(f"\n{character_name}: ", end="", flush=True)
            response = await client.send_message(user_input)
            
            assistant_message = response.get("response", "...")
            print(assistant_message)
            
            # Show metadata if available
            metadata = response.get("metadata", {})
            if metadata.get("emotional_state"):
                print(f"   [Mood: {metadata['emotional_state']}]")
            
            print()
            
        except httpx.HTTPError as e:
            print(f"\n❌ Error: {e}")
            print()


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chat with fantasy characters")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="Server URL"
    )
    parser.add_argument(
        "--character",
        help="Character ID to chat with"
    )
    
    args = parser.parse_args()
    
    print("🏰 Fantasy World RAG - Chat Client")
    print("=" * 40)
    
    client = ChatClient(args.server)
    
    # Select character
    character_id = args.character
    if not character_id:
        character_id = await select_character(client)
    
    if not character_id:
        print("No character selected. Exiting.")
        return
    
    # Start conversation
    print(f"\n🔗 Starting conversation with {character_id}...")
    
    try:
        result = await client.start_conversation(character_id)
        character_name = result.get("character_name", character_id)
        print(f"   Session: {result.get('session_id', 'N/A')[:8]}...")
        
        # Show greeting if present
        if result.get("greeting"):
            print(f"\n{character_name}: {result['greeting']}\n")
        
    except httpx.HTTPError as e:
        print(f"❌ Failed to start conversation: {e}")
        return
    
    # Enter chat loop
    await chat_loop(client, character_name)


if __name__ == "__main__":
    asyncio.run(main())
