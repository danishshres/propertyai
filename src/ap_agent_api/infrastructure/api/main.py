"""
FastAPI main application module.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.staticfiles import StaticFiles
import logging

from .routers import property_router, elevation_risk_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAPI tags metadata for Swagger documentation
tags_metadata = [
    {
        "name": "search",
        "description": "Property search and risk assessment endpoints. Search for detailed property information using AI agents.",
        "externalDocs": {
            "description": "Property search documentation",
            "url": "https://example.com/property-search-docs",
        },
    },
    {
        "name": "health",
        "description": "Health check and monitoring endpoints. Check API status and service availability.",
    },
]

# Create FastAPI app with enhanced Swagger configuration
app = FastAPI(
    title="Property AI Agent API",
    description="""
## Property AI Agent API

This API provides intelligent property search and risk assessment capabilities using AI agents.

### Features
* **Property Search**: Get detailed property information including zoning, schools, and financial data
* **Risk Assessment**: AI-powered analysis of property risks including flood, heritage, and planning overlays
* **Real-time Data**: Access to current market data and publicly available property information

### Usage
Use the `/search` endpoint to search for property details by providing an address.
The API returns comprehensive property data including risk factors and recommendations.
    """,
    version="0.1.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Property AI Team",
        "email": "support@propertyai.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include search route directly at root level for easier access
app.include_router(
    property_router.router,
    prefix="",
    tags=["search"]
)

app.include_router(
    elevation_risk_router.router,
    prefix="/risks",
    tags=["risks"]
)

@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint - API status check.
    
    Returns a simple message indicating the API is running and operational.
    """
    return {
        "message": "Property AI Agent API is running",
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns the current status of the API and available services.
    """
    return {
        "status": "healthy", 
        "service": "property-ai-agent-api",
        "version": "0.1.0",
        "timestamp": "2025-12-15T00:00:00Z"
    }

# Custom OpenAPI schema for enhanced Swagger documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Property AI Agent API",
        version="0.1.0",
        description="Intelligent property search and risk assessment API using AI agents",
        routes=app.routes,
    )
    
    # Add custom schema information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.propertyai.com",
            "description": "Production server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )