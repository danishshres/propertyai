from importlib.metadata import files
import json
from pathlib import Path
from datetime import datetime
import os.path, time
from ap_agent_api.domain.utils import get_property_directory

class PropertyFileRepository:

    def save(self, property_address, data, filename) -> str:
        """
        Save the property data to a JSON file.
        """
        # output_dir = self.base_dir / (property_address.street.replace(" ", "_"))
        output_dir = get_property_directory(property_address)
        file_path = output_dir / filename
        # output_data = property_results.model_dump()
        with open(file_path, "w") as f:
            json.dump(data, f)
        return str(file_path)
    
    def load(self, property_address):
        """
        Load property data from file if it exists and was created within the last 10 days.
        
        Args:
            property_address: Property address object with street attribute
            
        Returns:
            dict: Property data if file exists and is within 10 days, None otherwise
        """
        output_dir = get_property_directory(property_address)
        file_path = output_dir / "property_details.json"
        
        # Check if file exists
        if not file_path.exists():
            return None
        
        try:
            # Get file modification time
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            current_time = datetime.now()
            
            # Calculate the difference in days
            time_diff = (current_time - file_mod_time).days
            
            # If file was modified within the last 10 days, load and return data
            if time_diff <= 10:
                with open(file_path, "r") as f:
                    data = f.read()
                return data
            else:
                # File is older than 10 days
                return None
                
        except (OSError, json.JSONDecodeError) as e:
            # Handle file access or JSON parsing errors
            print(f"Error loading property data from {file_path}: {e}")
            return None