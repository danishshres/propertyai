from pydantic import BaseModel, Field
from typing import Optional

class RiskCategory(BaseModel):
    """Model representing a risk category with count and density metrics."""
    count: int = Field(..., description="Number of risk indicators in this category")
    density: float = Field(..., description="Risk density score for this category")

class ElevationRiskAssessment(BaseModel):
    """Model representing elevation-based risk assessment for a property."""
    high_risk_immediate_property: RiskCategory = Field(
        ..., 
        alias="High Risk (Immediate Property)",
        description="High risk indicators on the immediate property"
    )
    moderate_risk_adjacent_properties: RiskCategory = Field(
        ..., 
        alias="Moderate Risk (Adjacent Properties)",
        description="Moderate risk indicators on adjacent properties"
    )
    low_risk_neighborhood_scale: RiskCategory = Field(
        ..., 
        alias="Low Risk (Neighborhood Scale)",
        description="Low risk indicators at neighborhood scale"
    )
    total_risk_score: float = Field(
        ..., 
        alias="Total Risk Score",
        description="Overall risk score combining all categories"
    )
