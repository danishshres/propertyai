from ap_agent_api.domain.models.property import PropertyAddress
from ap_agent_api.domain.models.risks import ElevationRiskAssessment
from ap_agent_api.domain.utils import get_property_directory

from ap_agent_api.infrastructure import gis_image_generate
from ap_agent_api.domain.tools import elevation_risk_calculator as erc

# from ap_agent_api.infrastructure.file_repo import PropertyFileRepository

#TODO : DO this better by checking if images exist and if not 
# they call the tools to generate them.

import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)


async def run_elevation_risk_assessment(address: PropertyAddress):

    logger.info("Running elevation risk assessment ...")
    
    # 1. Generate the GIS images.
    output_dir = gis_image_generate.run(address=address)

    # 2. Check the elevation risk.
    elevation_risk_dict = erc.calculate(output_dir / "contour_map.png")

    # file_repo = PropertyFileRepository()
    # file_path = file_repo.save(property_address=address, data=elevation_risk_dict, filename='elevation_risk.json')

    # Convert dictionary to ElevationRiskAssessment pydantic model
    elevation_risk_assessment = ElevationRiskAssessment(**elevation_risk_dict)

    logger.info(f"Elevation Risk Assessment: {elevation_risk_assessment}")

    return elevation_risk_assessment

if __name__ == "__main__":

    test_address = PropertyAddress(
        street="1A Ormbsy Street",
        suburb="Widsor Gardens",
        state="SA",
        postcode="5087"
    )

    run_elevation_risk_assessment(test_address)