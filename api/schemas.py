"""
API Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class PIIMatchSchema(BaseModel):
    """Schema for individual PII match"""
    pii_type: str = Field(..., description="Type of PII detected")
    value: str = Field(..., description="Original PII value")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    masked_value: str = Field(..., description="Masked version of the value")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "pii_type": "EMAIL",
                "value": "john@example.com",
                "start": 15,
                "end": 31,
                "confidence": 0.99,
                "masked_value": "j***n@example.com"
            }
        }
    }


class DetectionRequest(BaseModel):
    """Request schema for PII detection"""
    text: str = Field(..., description="Text to scan for PII", min_length=1)
    confidence_threshold: Optional[float] = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for detection"
    )
    mask_pii: Optional[bool] = Field(
        True,
        description="Whether to return masked text"
    )
    detect_types: Optional[List[str]] = Field(
        None,
        description="Specific PII types to detect (default: all)"
    )
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Contact John Smith at john@example.com or call 555-123-4567",
                "confidence_threshold": 0.7,
                "mask_pii": True,
                "detect_types": ["EMAIL", "PHONE", "PERSON_NAME"]
            }
        }
    }


class DetectionResponse(BaseModel):
    """Response schema for PII detection"""
    original_text: str = Field(..., description="Original input text")
    masked_text: str = Field(..., description="Text with PII masked")
    pii_found: bool = Field(..., description="Whether any PII was found")
    pii_count: int = Field(..., description="Number of PII instances detected")
    matches: List[PIIMatchSchema] = Field(..., description="List of detected PII")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="UTC timestamp of detection")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "original_text": "Email john@example.com",
                "masked_text": "Email j***n@example.com",
                "pii_found": True,
                "pii_count": 1,
                "matches": [
                    {
                        "pii_type": "EMAIL",
                        "value": "john@example.com",
                        "start": 6,
                        "end": 22,
                        "confidence": 0.99,
                        "masked_value": "j***n@example.com"
                    }
                ],
                "processing_time_ms": 12.34,
                "timestamp": "2024-02-03T10:30:00Z"
            }
        }
    }


class MaskRequest(BaseModel):
    """Request schema for simple masking"""
    text: str = Field(..., description="Text to mask", min_length=1)
    confidence_threshold: Optional[float] = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "My SSN is 123-45-6789",
                "confidence_threshold": 0.7
            }
        }
    }


class MaskResponse(BaseModel):
    """Response schema for masking"""
    masked_text: str = Field(..., description="Text with PII masked")
    pii_count: int = Field(..., description="Number of PII instances masked")
    processing_time_ms: float = Field(..., description="Processing time")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "masked_text": "My SSN is ***-**-6789",
                "pii_count": 1,
                "processing_time_ms": 8.5
            }
        }
    }


class ProxyRequest(BaseModel):
    """Request schema for AI proxy"""
    prompt: str = Field(..., description="User prompt to sanitize", min_length=1)
    model: Optional[str] = Field("gpt-4", description="Target AI model")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2000, ge=1, le=8000)
    auto_mask: Optional[bool] = Field(
        True,
        description="Automatically mask detected PII"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "Write an email to john@example.com about account 4532-1488-0343-6467",
                "model": "gpt-4",
                "auto_mask": True
            }
        }
    }


class ProxyResponse(BaseModel):
    """Response schema for AI proxy"""
    original_prompt: str = Field(..., description="Original user prompt")
    sanitized_prompt: str = Field(..., description="Sanitized prompt safe for AI")
    pii_detected: bool = Field(..., description="Whether PII was detected")
    pii_count: int = Field(..., description="Number of PII instances")
    masked_items: List[PIIMatchSchema] = Field(..., description="Detected PII items")
    ai_ready: bool = Field(..., description="Whether prompt is ready for AI")
    warnings: List[str] = Field(..., description="Any warnings or notices")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "original_prompt": "Email john@example.com",
                "sanitized_prompt": "Email j***n@example.com",
                "pii_detected": True,
                "pii_count": 1,
                "masked_items": [],
                "ai_ready": True,
                "warnings": ["Detected 1 PII instance: EMAIL"]
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    detector_loaded: bool = Field(..., description="Whether detector is loaded")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-02-03T10:30:00Z",
                "detector_loaded": True
            }
        }
    }


class StatsResponse(BaseModel):
    """Statistics response"""
    total_requests: int = Field(..., description="Total API requests")
    total_pii_detected: int = Field(..., description="Total PII instances detected")
    avg_processing_time_ms: float = Field(..., description="Average processing time")
    uptime_seconds: float = Field(..., description="Service uptime")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_requests": 1523,
                "total_pii_detected": 4892,
                "avg_processing_time_ms": 15.6,
                "uptime_seconds": 86400.0
            }
        }
    }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="Error timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Text cannot be empty",
                "timestamp": "2024-02-03T10:30:00Z"
            }
        }
    }


class PIITypesResponse(BaseModel):
    """Supported PII types response"""
    supported_types: List[str] = Field(..., description="List of supported PII types")
    descriptions: dict = Field(..., description="Descriptions of each type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "supported_types": ["CREDIT_CARD", "SSN", "EMAIL"],
                "descriptions": {
                    "CREDIT_CARD": "Credit card numbers (Visa, MC, Amex, Discover)",
                    "SSN": "Social Security Numbers",
                    "EMAIL": "Email addresses"
                }
            }
        }
    }
