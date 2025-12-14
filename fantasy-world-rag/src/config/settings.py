"""
Centralized settings configuration for Ueasys.

This module uses Pydantic Settings for type-safe configuration management
with environment variable support and validation.

Example:
    >>> from src.config import get_settings
    >>> settings = get_settings()
    >>> print(settings.app_name)
    'ueasys'
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables.
    Nested settings use double underscore separator (e.g., OPENAI__API_KEY).
    
    Attributes:
        app_name: Name of the application
        app_env: Environment (development, staging, production)
        debug: Enable debug mode
        log_level: Logging level
        secret_key: Secret key for security features
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # =========================================================================
    # Application Settings
    # =========================================================================
    app_name: str = Field(default="ueasys", description="Application name")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", 
        description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    secret_key: str = Field(
        default="change-me-in-production", 
        description="Secret key for security"
    )
    
    # =========================================================================
    # Server Configuration
    # =========================================================================
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")
    reload: bool = Field(default=True, description="Enable auto-reload")
    
    # =========================================================================
    # Database Configuration
    # =========================================================================
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="fantasy_world", description="Database name")
    postgres_user: str = Field(default="fantasy_user", description="Database user")
    postgres_password: str = Field(default="fantasy_password", description="Database password")
    
    @property
    def database_url(self) -> str:
        """Async database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL for Alembic migrations."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # =========================================================================
    # Redis Configuration
    # =========================================================================
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: str = Field(default="", description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    session_ttl: int = Field(default=86400, description="Session TTL in seconds")
    
    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # =========================================================================
    # Vector Database (Qdrant)
    # =========================================================================
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_api_key: str | None = Field(default=None, description="Qdrant API key")
    qdrant_collection_name: str = Field(
        default="fantasy_characters", 
        description="Default collection name"
    )
    vector_dimension: int = Field(default=1536, description="Embedding dimension")
    vector_distance: str = Field(default="Cosine", description="Distance metric")
    
    @property
    def qdrant_url(self) -> str:
        """Qdrant connection URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"
    
    # =========================================================================
    # Neo4j Configuration (Optional)
    # =========================================================================
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j user")
    neo4j_password: str = Field(default="neo4j_password", description="Neo4j password")
    neo4j_database: str = Field(default="neo4j", description="Neo4j database")
    
    # =========================================================================
    # LLM Provider Configuration
    # =========================================================================
    llm_provider: Literal["openai", "anthropic", "grok", "deepseek", "local"] = Field(
        default="grok", 
        description="Primary LLM provider"
    )
    
    # Default routing - which provider for which task
    default_chat_provider: str = Field(
        default="grok",
        description="Default provider for real-time chat (fast responses)"
    )
    default_analysis_provider: str = Field(
        default="deepseek",
        description="Default provider for analysis/extraction (reasoning)"
    )
    
    # Grok (xAI) - RECOMMENDED for chat
    grok_api_key: str = Field(default="", description="xAI Grok API key")
    grok_model: str = Field(default="grok-4-fast", description="Grok model")
    grok_max_tokens: int = Field(default=4096, description="Max tokens for Grok")
    grok_temperature: float = Field(default=0.7, description="Temperature for Grok")
    
    # DeepSeek - RECOMMENDED for analysis
    deepseek_api_key: str = Field(default="", description="DeepSeek API key")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek model")
    deepseek_max_tokens: int = Field(default=4096, description="Max tokens for DeepSeek")
    deepseek_temperature: float = Field(default=0.3, description="Temperature for DeepSeek (lower for analysis)")
    
    # OpenAI (fallback)
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", 
        description="OpenAI embedding model"
    )
    openai_max_tokens: int = Field(default=4096, description="Max tokens for responses")
    openai_temperature: float = Field(default=0.7, description="Temperature for generation")
    
    # Anthropic (optional)
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-opus-20240229", 
        description="Anthropic model"
    )
    anthropic_max_tokens: int = Field(default=4096, description="Max tokens")
    
    # Local LLM
    local_llm_url: str = Field(default="http://localhost:11434", description="Local LLM URL")
    local_llm_model: str = Field(default="llama2", description="Local LLM model")
    
    # =========================================================================
    # RAG Configuration
    # =========================================================================
    rag_chunk_size: int = Field(default=512, description="Chunk size for RAG")
    rag_chunk_overlap: int = Field(default=50, description="Chunk overlap")
    rag_top_k: int = Field(default=5, description="Top K results for retrieval")
    rag_rerank_top_k: int = Field(default=3, description="Top K after reranking")
    rag_min_relevance_score: float = Field(
        default=0.7, 
        description="Minimum relevance score"
    )
    
    # Knowledge tiers
    enable_knowledge_tiers: bool = Field(default=True, description="Enable tier system")
    tier_weights_essence: float = Field(default=0.3, description="Weight for essence tier")
    tier_weights_knowledge: float = Field(default=0.25, description="Weight for knowledge")
    tier_weights_relationships: float = Field(default=0.2, description="Weight for relations")
    tier_weights_style: float = Field(default=0.15, description="Weight for style")
    tier_weights_context: float = Field(default=0.1, description="Weight for context")
    
    # =========================================================================
    # Character Engine Settings
    # =========================================================================
    memory_max_episodic_items: int = Field(
        default=1000, 
        description="Max episodic memory items"
    )
    memory_max_semantic_items: int = Field(
        default=5000, 
        description="Max semantic memory items"
    )
    memory_consolidation_threshold: int = Field(
        default=100, 
        description="Memory consolidation threshold"
    )
    memory_decay_rate: float = Field(default=0.1, description="Memory decay rate")
    
    emotion_update_interval: int = Field(
        default=60, 
        description="Emotion update interval (seconds)"
    )
    emotion_decay_rate: float = Field(default=0.05, description="Emotion decay rate")
    emotion_influence_factor: float = Field(
        default=0.3, 
        description="Emotion influence on responses"
    )
    
    decision_confidence_threshold: float = Field(
        default=0.7, 
        description="Decision confidence threshold"
    )
    decision_max_options: int = Field(default=5, description="Max decision options")
    
    # =========================================================================
    # Authentication & Security
    # =========================================================================
    jwt_secret_key: str = Field(
        default="change-me-jwt-secret", 
        description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, 
        description="Access token expiry"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, 
        description="Refresh token expiry"
    )
    
    rate_limit_requests: int = Field(default=100, description="Rate limit requests")
    rate_limit_window: int = Field(default=60, description="Rate limit window (seconds)")
    
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")
    
    # =========================================================================
    # WebSocket Configuration
    # =========================================================================
    ws_heartbeat_interval: int = Field(
        default=30, 
        description="WebSocket heartbeat interval"
    )
    ws_max_connections: int = Field(default=1000, description="Max WS connections")
    ws_message_queue_size: int = Field(default=100, description="Message queue size")
    
    # =========================================================================
    # World Simulation
    # =========================================================================
    world_time_scale: int = Field(default=60, description="World time scale factor")
    world_event_check_interval: int = Field(
        default=300, 
        description="Event check interval"
    )
    world_auto_events: bool = Field(default=True, description="Enable auto events")
    
    # =========================================================================
    # Monitoring
    # =========================================================================
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN")
    sentry_traces_sample_rate: float = Field(
        default=0.1, 
        description="Sentry traces sample rate"
    )
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")
    
    log_format: Literal["json", "text"] = Field(
        default="json", 
        description="Log format"
    )
    log_file: str | None = Field(default="logs/fantasy_world.log", description="Log file")
    
    # =========================================================================
    # Development Settings
    # =========================================================================
    use_mock_llm: bool = Field(default=False, description="Use mock LLM for testing")
    seed_characters: list[str] = Field(
        default=["gandalf", "galadriel", "smaug"],
        description="Characters to seed"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("seed_characters", mode="before")
    @classmethod
    def parse_seed_characters(cls, v: Any) -> list[str]:
        """Parse seed characters from string or list."""
        if isinstance(v, str):
            return [c.strip() for c in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once.
    
    Returns:
        Settings: Application settings instance
        
    Example:
        >>> settings = get_settings()
        >>> settings.app_name
        'fantasy-world-rag'
    """
    return Settings()
