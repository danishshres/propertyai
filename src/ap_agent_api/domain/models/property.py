from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PropertyAddress(BaseModel):
    street: str
    suburb: str
    state: str = Field(..., description="e.g. NSW, VIC, QLD, WA, SA, TAS, ACT, NT")
    postcode: str

class SchoolZone(BaseModel):
    name: str
    level: str = Field(..., description="Primary or Secondary")
    distance_km: Optional[float] = None

class SeverityLevel(str, Enum):
    LOW = "low"
    LOW_MEDIUM = "low-medium"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium-high"
    HIGH = "high"
    CRITICAL = "critical"

# class SourceLink(BaseModel):
#     title: Optional[str] = Field(None, description="Human-friendly title for the source")
#     url: Optional[HttpUrl] = Field(None, description="Link to the web source")
#     retrieved_at: Optional[datetime] = Field(
#         None, description="Timestamp when this source was fetched"
#     )

class RiskFactor(BaseModel):
    title: str = Field(..., description="Short title of risk factor (e.g., Flood risk)")
    severity: SeverityLevel = Field(..., description="Severity of the risk")
    rationale: Optional[str] = Field(None, description="Why this risk matters for the property")
    what_to_check: Optional[List[str]] = Field(
        None, description="Concrete checks/next steps the buyer should take"
    )
    # sources: Optional[List[SourceLink]] = Field(None, description="Supporting sources for this risk")

class PropertyData(BaseModel):
    # --- 1. Property Identity ---
    address: PropertyAddress
    property_type: str = Field(..., description="House, Unit, Townhouse, Villa, Land")
    lot_plan: Optional[str] = Field(None, description="e.g., Lot 12 DP 123456")
    
    # --- 2. Physical Specs ---
    land_size_sqm: Optional[int] = Field(None, description="Land size in square meters")
    internal_area_sqm: Optional[int] = None
    bed_count: int
    bath_count: int
    car_spaces: int
    year_built: Optional[int] = None
    has_solar: bool = Field(False, description="True if solar panels detected in imagery/description")

    # --- 3. Planning & Zoning (Critical for AU) ---
    zoning_code: Optional[str] = Field(None, description="e.g. R2, R3, GRZ1, LMR")
    overlays: List[str] = Field(default_factory=list, description="List of overlays: Heritage, Bushfire, Flood")
    is_heritage_listed: bool = False

    # --- 4. Financials & Outgoings ---
    last_sale_price: Optional[int] = None
    last_sale_date: Optional[str] = None
    estimated_council_rates: Optional[int] = Field(None, description="Annual estimated value in AUD")
    strata_levies_quarterly: Optional[int] = Field(None, description="Only for Strata titles")
    estimated_rent_weekly: Optional[int] = None

    # --- 5. Connectivity ---
    nbn_technology: Optional[str] = Field(
        None, 
        description="FTTP (Fibre to Premises), FTTN (Node), HFC, FTTC"
    )

    # --- 6. Schools ---
    catchment_schools: List[SchoolZone] = Field(default_factory=list)

    # --- 7. Risk Info ---
    risks: Optional[List[RiskFactor]] = Field(None, description="List of identified risk factors")

# Example Usage:
# data = PropertyData.model_validate_json(ai_response_json)
# print(data.zoning_code)