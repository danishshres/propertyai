import json
from pathlib import Path

class PropertyFileRepository:

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def save(self, property_address, property_results) -> str:
        """
        Save the property data to a JSON file.
        """
        output_dir = self.base_dir / property_address.street.replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / "property_details.json"
        output_data = {
            # "address": property_address.model_dump(),
            "details": property_results.model_dump(),
            # "school_info": [school.model_dump() for school in property_results.catchment_schools]
        }
        with open(file_path, "w") as f:
            json.dump(output_data, f)

        return str(file_path)