"""
Property-related API endpoints.
"""

from ap_agent_api.infrastructure.file_repo import PropertyFileRepository
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
from typing import Dict, Any

from ap_agent_api.domain.models.property import PropertyAddress, PropertyData
from ap_agent_api.application.property_search_service import run_property_search
from ..models.responses import PropertySearchResponse, ErrorResponse
from ap_agent_api.config import PROPERTY_RESULTS_DIR


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/search",
    response_model=PropertySearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for property details and risk assessment",
    description="Searches for detailed publicly available information about a property and provides risk assessment"
)
async def search_property(address: PropertyAddress) -> PropertySearchResponse:
    """
    Search for property details and perform risk assessment.
    
    Args:
        address: Property address information
        
    Returns:
        PropertySearchResponse: Detailed property information and risk assessment
        
    Raises:
        HTTPException: If the search fails or encounters an error
    """
    try:
        logger.info(f"Starting property search for: {address.street}, {address.suburb}, {address.state}")
        
        # Call the application service
        property_data = await run_property_search(address)

        # Use environment variable or default to results directory relative to project root
        file_repo = PropertyFileRepository(base_dir=str(PROPERTY_RESULTS_DIR))
        file_path = file_repo.save(property_address=address, property_results=property_data)
        
        logger.info(f"Property search completed successfully for: {address.street} and saved to {file_path}")
        
        return PropertySearchResponse(
            success=True,
            message="Property search completed successfully",
            data=property_data
        )
        
    except Exception as e:
        logger.error(f"Property search failed for {address.street}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Property search failed: {str(e)}"
        )

@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Property service health check",
    description="Check if the property search service is operational"
)
async def property_service_health():
    """
    Health check endpoint for property service.
    """
    return {
        "service": "property-search",
        "status": "healthy",
        "capabilities": [
            "property_search",
            "risk_assessment",
            "property_details_extraction"
        ]
    }