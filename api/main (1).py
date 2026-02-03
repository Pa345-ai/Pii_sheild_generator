"""
PII-Shield FastAPI Application
Main API endpoints for PII detection and masking
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import time
import logging
from datetime import datetime

from pii_shield import PIIDetector
from pii_shield.patterns import PIIType
from .schemas import (
    DetectionRequest, DetectionResponse, PIIMatchSchema,
    MaskRequest, MaskResponse,
    ProxyRequest, ProxyResponse,
    HealthResponse, StatsResponse, ErrorResponse, PIITypesResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PII-Shield Engine",
    description="Enterprise-grade PII detection and masking API for AI traffic protection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "PII-Shield Support",
        "email": "support@pii-shield.example.com",
    },
    license_info={
        "name": "Commercial License",
        "url": "https://pii-shield.example.com/license",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PII detector
pii_detector = PIIDetector(
    enable_context_validation=True,
    enable_strict_validation=True,
    collect_statistics=False
)

# Global statistics
stats = {
    "total_requests": 0,
    "total_pii_detected": 0,
    "total_processing_time": 0.0,
    "start_time": time.time()
}


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Completed in {process_time:.2f}ms - Status: {response.status_code}")
    
    return response


# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PII-Shield Engine",
        "version": "1.0.0",
        "description": "Enterprise PII detection and masking API",
        "documentation": "/docs",
        "health": "/health",
        "supported_pii_types": len(PIIType),
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint
    
    Returns service health status and basic information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        detector_loaded=pii_detector is not None
    )


# Statistics endpoint
@app.get("/stats", response_model=StatsResponse, tags=["General"])
async def get_stats():
    """
    Get API usage statistics
    
    Returns statistics about API usage and performance
    """
    uptime = time.time() - stats["start_time"]
    avg_time = (
        stats["total_processing_time"] / stats["total_requests"]
        if stats["total_requests"] > 0 else 0.0
    )
    
    return StatsResponse(
        total_requests=stats["total_requests"],
        total_pii_detected=stats["total_pii_detected"],
        avg_processing_time_ms=avg_time,
        uptime_seconds=uptime
    )


# Main detection endpoint
@app.post(
    "/detect",
    response_model=DetectionResponse,
    tags=["Detection"],
    summary="Detect PII in text",
    description="Scan text for personally identifiable information and return detailed results"
)
async def detect_pii(request: DetectionRequest):
    """
    Detect PII in provided text
    
    This endpoint scans text for various types of PII including:
    - Credit card numbers
    - Social Security numbers
    - Email addresses
    - Phone numbers
    - Person names
    - Street addresses
    - IP addresses
    - Dates of birth
    - And more...
    
    Returns detailed information about each detected PII instance.
    """
    start_time = time.time()
    
    try:
        # Update statistics
        stats["total_requests"] += 1
        
        # Convert requested types to PIIType enum
        pii_types = None
        if request.detect_types:
            try:
                pii_types = [PIIType[t.upper()] for t in request.detect_types]
            except KeyError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid PII type: {str(e)}"
                )
        
        # Detect PII
        matches = pii_detector.detect_all(
            request.text,
            confidence_threshold=request.confidence_threshold,
            pii_types=pii_types
        )
        
        # Update PII statistics
        stats["total_pii_detected"] += len(matches)
        
        # Mask text if requested
        masked_text = request.text
        if request.mask_pii and matches:
            masked_text = pii_detector.mask_text(request.text, matches)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        stats["total_processing_time"] += processing_time
        
        # Convert matches to response format
        match_responses = [
            PIIMatchSchema(
                pii_type=m.pii_type,
                value=m.value,
                start=m.start,
                end=m.end,
                confidence=m.confidence,
                masked_value=m.masked_value
            )
            for m in matches
        ]
        
        logger.info(
            f"Detected {len(matches)} PII instances in {processing_time:.2f}ms"
        )
        
        return DetectionResponse(
            original_text=request.text,
            masked_text=masked_text,
            pii_found=len(matches) > 0,
            pii_count=len(matches),
            matches=match_responses,
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during PII detection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )


# Simple masking endpoint
@app.post(
    "/mask",
    response_model=MaskResponse,
    tags=["Detection"],
    summary="Mask PII in text",
    description="Simple endpoint that returns only masked text without detailed match information"
)
async def mask_pii_only(request: MaskRequest):
    """
    Mask PII in text (simplified endpoint)
    
    Returns only the masked text without detailed match information.
    Useful for simple use cases where you just need the sanitized text.
    """
    start_time = time.time()
    
    try:
        stats["total_requests"] += 1
        
        matches = pii_detector.detect_all(
            request.text,
            confidence_threshold=request.confidence_threshold
        )
        
        stats["total_pii_detected"] += len(matches)
        
        masked_text = pii_detector.mask_text(request.text, matches)
        
        processing_time = (time.time() - start_time) * 1000
        stats["total_processing_time"] += processing_time
        
        return MaskResponse(
            masked_text=masked_text,
            pii_count=len(matches),
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Error during masking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Masking failed: {str(e)}"
        )


# AI proxy endpoint
@app.post(
    "/proxy/sanitize",
    response_model=ProxyResponse,
    tags=["AI Proxy"],
    summary="Sanitize prompt for AI",
    description="Pre-process user prompts before sending to AI models"
)
async def sanitize_for_ai(request: ProxyRequest):
    """
    Sanitize prompt before sending to AI
    
    This endpoint acts as a pre-processor for AI traffic, detecting and
    optionally masking PII before the prompt reaches the language model.
    
    Typical workflow:
    1. Receive user prompt
    2. Detect PII
    3. Mask PII if auto_mask is True
    4. Return sanitized prompt ready for AI
    
    This prevents sensitive information from being sent to third-party AI providers.
    """
    start_time = time.time()
    
    try:
        stats["total_requests"] += 1
        
        # Detect PII in prompt
        matches = pii_detector.detect_all(request.prompt, confidence_threshold=0.7)
        
        stats["total_pii_detected"] += len(matches)
        
        # Prepare warnings
        warnings = []
        if matches:
            pii_types = list(set(m.pii_type for m in matches))
            warnings.append(
                f"Detected {len(matches)} PII instances: {', '.join(pii_types)}"
            )
        
        # Sanitize prompt
        sanitized_prompt = request.prompt
        if request.auto_mask and matches:
            sanitized_prompt = pii_detector.mask_text(request.prompt, matches)
            warnings.append("PII has been automatically masked")
        
        # Convert matches
        masked_items = [
            PIIMatchSchema(
                pii_type=m.pii_type,
                value=m.value,
                start=m.start,
                end=m.end,
                confidence=m.confidence,
                masked_value=m.masked_value
            )
            for m in matches
        ]
        
        processing_time = (time.time() - start_time) * 1000
        stats["total_processing_time"] += processing_time
        
        logger.info(
            f"Sanitized prompt with {len(matches)} PII items in {processing_time:.2f}ms"
        )
        
        return ProxyResponse(
            original_prompt=request.prompt,
            sanitized_prompt=sanitized_prompt,
            pii_detected=len(matches) > 0,
            pii_count=len(matches),
            masked_items=masked_items,
            ai_ready=True,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Error during sanitization: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sanitization failed: {str(e)}"
        )


# Batch detection endpoint
@app.post(
    "/batch/detect",
    response_model=List[DetectionResponse],
    tags=["Detection"],
    summary="Batch PII detection",
    description="Process multiple texts in a single request for efficiency"
)
async def batch_detect_pii(requests: List[DetectionRequest]):
    """
    Batch PII detection for multiple texts
    
    Processes multiple texts in a single request for efficiency.
    Limited to 100 requests per batch.
    """
    if len(requests) > 100:
        raise HTTPException(
            status_code=400,
            detail="Batch size limited to 100 requests"
        )
    
    results = []
    
    for req in requests:
        # Process each request
        result = await detect_pii(req)
        results.append(result)
    
    return results


# Supported PII types endpoint
@app.get(
    "/types",
    response_model=PIITypesResponse,
    tags=["General"],
    summary="Get supported PII types",
    description="List all supported PII types and their descriptions"
)
async def get_supported_types():
    """
    Get list of supported PII types
    
    Returns all PII types that the engine can detect,
    along with descriptions of each type.
    """
    return PIITypesResponse(
        supported_types=[pii_type.value for pii_type in PIIType],
        descriptions={
            "CREDIT_CARD": "Credit card numbers (Visa, Mastercard, Amex, Discover)",
            "SSN": "Social Security Numbers",
            "EMAIL": "Email addresses",
            "PHONE": "Phone numbers (US and international)",
            "PERSON_NAME": "Person names with prefixes/suffixes",
            "ADDRESS": "Street addresses",
            "IP_ADDRESS": "IPv4 addresses",
            "DATE_OF_BIRTH": "Dates of birth",
            "PASSPORT": "Passport numbers",
            "DRIVER_LICENSE": "Driver license numbers",
            "BANK_ACCOUNT": "Bank account numbers",
            "TAX_ID": "Tax identification numbers",
        }
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message=str(exc),
            timestamp=datetime.utcnow().isoformat() + "Z"
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
