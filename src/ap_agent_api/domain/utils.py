

from ap_agent_api.config import PROPERTY_RESULTS_DIR
from pathlib import Path

def get_property_directory(property_address) -> str:
    """
    Get the directory path for a given property address.
    
    Args:
        property_address: Property address object with street attribute.
        
    Returns:
        str: The full directory path for the property.
    """
    output_dir = Path(PROPERTY_RESULTS_DIR) / (property_address.street.replace(" ", "_"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir