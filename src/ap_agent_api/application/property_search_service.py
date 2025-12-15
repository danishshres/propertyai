
from ap_agent_api.domain.models.property import PropertyAddress, PropertyData
from ap_agent_api.domain.instructions.property_detail_inst import build_property_detail_inst

from ap_agent_api.infrastructure.llm_providers.openapi import create_search_agent

from ap_agent_api.infrastructure.file_repo import PropertyFileRepository

#this was done using port last time.
from agents import Runner

import coloredlogs, logging
import logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)

async def run_property_search(address: PropertyAddress):
    
    instructions = build_property_detail_inst()

    search_agent = create_search_agent(instruction=instructions, output_type=PropertyData)

    #Start the search.
    prompt = f"""Search for detailed publicly available information about the property located at:
        {address.street}, {address.suburb}, {address.state} {address.postcode}."""
    
    logger.info("Running property search and its risk assessment ...")

    # search_results = await search_agent.run(prompt)
    search_results =  await Runner.run(search_agent, prompt)

    search_output = search_results.final_output_as(
        PropertyData
    )
    return search_output


if __name__ == '__main__':
    import asyncio
    
    test_address = PropertyAddress(
        street="1c Raymel Crescent",
        suburb="Campbelltown",
        state="SA",
        postcode="5074"
    )
    
    result = asyncio.run(run_property_search(test_address))

    logger.info(f"Property Search Result: {result}")

    file_repo = PropertyFileRepository(base_dir=r"C:\Users\d.shrestha\Desktop\danish_projects\propertyai\results")
    file_path = file_repo.save(property_address=test_address, property_results=result)
    logger.info(f"Property data saved to: {file_path}")