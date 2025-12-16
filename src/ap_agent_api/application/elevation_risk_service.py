from ap_agent_api.domain.models.property import PropertyAddress
from ap_agent_api.domain.utils import get_property_directory

from ap_agent_api.infrastructure import gis_image_generate
from ap_agent_api.domain.tools import elevation_risk_calculator as erc

#TODO : DO this better by checking if images exist and if not 
# they call the tools to generate them.


if __name__ == "__main__":

    test_address = PropertyAddress(
        street="1c Raymel Crescent",
        suburb="Campbelltown",
        state="SA",
        postcode="5074"
    )

    # 1. Generate the GIS images.
    output_dir = gis_image_generate.run(address=test_address)

    # 2. Check the elevation risk.
    elevation_risk = erc.calculate(output_dir / "contour_map.png")

    print(f"Elevation Risk Assessment: {elevation_risk}")