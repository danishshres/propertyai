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
from ap_agent_api.domain.models.risks import ElevationRiskAssessment
from ap_agent_api.application.elevation_risk_service import run_elevation_risk_assessment
from ..models.responses import ElevationRiskResponse, ErrorResponse
from ap_agent_api.config import PROPERTY_RESULTS_DIR


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/elevation-risk",
    response_model=ElevationRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Elevation Risk Assessment",
    description="""
    **Risk assessment based on elevation data and analysis**
    
    **Example Request:**
    ```json
    {
        "street": "1c Raymel Crescent",
        "suburb": "Campbelltown", 
        "state": "SA",
        "postcode": "5074"
    }
    ```
    
    **Response includes:**
    - Risk Assessment details
    """,
    response_description="Risk assessment results based on elevation data",
    responses={
        200: {
            "description": "Successful elevation risk assessment",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Elevation risk assessment completed successfully",
                        "data": {
                            "High Risk (Immediate Property)": {
                                "count": 542,
                                "density": 19.169328701290507
                            },
                            "Moderate Risk (Adjacent Properties)": {
                                "count": 2189,
                                "density": 6.334366735057435
                            },
                            "Low Risk (Neighborhood Scale)": {
                                "count": 13933,
                                "density": 3.2998598543145503
                            },
                            "Total Risk Score": 28.80355529066249
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error - Invalid address format",
        },
        500: {
            "description": "Internal server error - Search service failed",
        }
    }
)
async def assess_elevation_risk(address: PropertyAddress) -> ElevationRiskResponse:
    """
    Search for property details and perform risk assessment.
    
    Args:
        address: Property address information
        
    Returns:
        ElevationRiskResponse: Detailed elevation risk information and risk assessment
        
    Raises:
        HTTPException: If the search fails or encounters an error
    """
    try:
        logger.info(f"Starting elevation risk assessment for: {address.street}, {address.suburb}, {address.state}")
        
        file_repo = PropertyFileRepository()
        filename = 'elevation_risk.json'
        # check if results already exist
        risk_data = file_repo.load(address, filename=filename)
        
        if risk_data:
            logger.info(f"Property data loaded from existing file for: {address.street}")
            risk_data = ElevationRiskAssessment.model_validate_json(risk_data)
            return ElevationRiskResponse(
                success=True,
                message="Property data loaded from existing file",
                data=risk_data
            )

        # Call the application service
        risk_data = await run_elevation_risk_assessment(address)

        file_path = file_repo.save(property_address=address, data=risk_data.model_dump(), filename=filename)
        
        logger.info(f"Elevation risk assessment completed successfully for: {address.street} and saved to {file_path}")
        
        return ElevationRiskResponse(
            success=True,
            message="Elevation risk assessment completed successfully",
            data=risk_data
        )
        
    except Exception as e:
        logger.error(f"Elevation risk assessment failed for {address.street}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Elevation risk assessment failed: {str(e)}"
        )

@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Elevation risk service health check",
    description="Check if the elevation risk assessment service is operational"
)
async def elevation_risk_service_health():
    """
    Health check endpoint for elevation risk service.
    """
    return {
        "service": "elevation-risk-assessment",
        "status": "healthy",
        "capabilities": [
            "property_search",
            "risk_assessment",
            "property_details_extraction"
        ]
    }