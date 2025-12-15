"""
Server Runner Script

This script provides a convenient way to start the Fantasy World RAG server.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Start the server using uvicorn."""
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description="Run the Fantasy World RAG server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level"
    )
    
    args = parser.parse_args()
    
    print("🏰 Fantasy World RAG Server")
    print("=" * 40)
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {args.reload}")
    print(f"   Workers: {args.workers}")
    print(f"   Log Level: {args.log_level}")
    print("=" * 40)
    print()
    
    # Check environment
    env = os.getenv("ENVIRONMENT", "development")
    print(f"🌍 Environment: {env}")
    
    # Check for required env vars
    required_vars = []
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("   Some features may not work correctly.")
    
    print("\n🚀 Starting server...\n")
    
    uvicorn.run(
        "src.api.app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level,
        factory=True
    )


if __name__ == "__main__":
    main()
