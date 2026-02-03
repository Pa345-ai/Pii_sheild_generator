"""
Configuration Settings
Centralized configuration management for PII-Shield
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "PII-Shield Engine"
    api_version: str = "1.0.0"
    api_description: str = "Enterprise PII detection and masking API"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 4
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Detection Settings
    default_confidence_threshold: float = 0.7
    enable_context_validation: bool = True
    enable_strict_validation: bool = True
    collect_statistics: bool = True
    
    # Performance Settings
    max_text_length: int = 1000000  # 1MB
    batch_size_limit: int = 100
    request_timeout: int = 30  # seconds
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    
    # Security Settings
    enable_rate_limiting: bool = False
    rate_limit_requests: int = 100  # requests per minute
    enable_api_key: bool = False
    api_key: Optional[str] = None
    
    # Feature Flags
    enable_batch_endpoint: bool = True
    enable_proxy_endpoint: bool = True
    enable_stats_endpoint: bool = True
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


class DetectionConfig(BaseSettings):
    """PII Detection specific configuration"""
    
    # Confidence thresholds by PII type
    credit_card_threshold: float = 0.90
    ssn_threshold: float = 0.95
    email_threshold: float = 0.99
    phone_threshold: float = 0.80
    name_threshold: float = 0.70
    address_threshold: float = 0.75
    
    # Validation settings
    validate_credit_cards: bool = True
    validate_ssn: bool = True
    validate_emails: bool = True
    validate_phones: bool = True
    
    # Context window for validation
    context_window_chars: int = 50
    
    # Name detection settings
    require_name_prefix: bool = False
    min_name_parts: int = 2
    max_name_parts: int = 4
    
    # Address detection settings
    require_street_number: bool = True
    require_street_type: bool = True
    
    model_config = {
        "env_prefix": "DETECTION_",
        "env_file": ".env"
    }


class MaskingConfig(BaseSettings):
    """Masking configuration"""
    
    # Default masking strategy
    default_strategy: str = "PARTIAL"  # FULL, PARTIAL, REDACT, HASH, TOKENIZE
    
    # Partial masking settings
    show_last_n_digits: int = 4
    show_first_initial: bool = True
    preserve_domain: bool = True  # For emails
    
    # Hash settings
    hash_algorithm: str = "sha256"
    hash_length: int = 12
    
    # Token settings
    token_prefix: str = "PII"
    token_format: str = "[{type}_{counter:04d}]"
    
    model_config = {
        "env_prefix": "MASKING_",
        "env_file": ".env"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


@lru_cache()
def get_detection_config() -> DetectionConfig:
    """Get cached detection config instance"""
    return DetectionConfig()


@lru_cache()
def get_masking_config() -> MaskingConfig:
    """Get cached masking config instance"""
    return MaskingConfig()


# Export commonly used settings
settings = get_settings()
detection_config = get_detection_config()
masking_config = get_masking_config()
