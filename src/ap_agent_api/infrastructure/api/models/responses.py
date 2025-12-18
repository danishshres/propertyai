"""
API response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from ap_agent_api.domain.models.property import PropertyData
from ap_agent_api.domain.models.risks import ElevationRiskAssessment

class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    success: bool
    message: str
    timestamp: Optional[str] = None

class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class PropertySearchResponse(BaseResponse):
    """Response model for property search endpoint."""
    success: bool = True
    data: Optional[PropertyData] = None

class ElevationRiskResponse(BaseResponse):
    """Response model for elevation risk assessment endpoint."""
    success: bool = True
    data: Optional[ElevationRiskAssessment] = None

class ValidationErrorResponse(BaseResponse):
    """Validation error response model."""
    success: bool = False
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list)

# Request models if needed for complex requests
class PropertySearchRequest(BaseModel):
    """Extended request model if additional parameters are needed."""
    address: str
    include_risk_assessment: bool = True
    include_financial_data: bool = True
    include_zoning_info: bool = True