"""
Fantasy World RAG - Main Entry Point

Run with: python -m src.main
Or use: uvicorn src.main:app --reload
"""

import uvicorn
from src.api.app import create_app

# Create the application instance
app = create_app()


def main():
    """Run the application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fantasy World RAG - Living Character System"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of workers"
    )
    
    args = parser.parse_args()
    
    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1
    )


if __name__ == "__main__":
    main()
