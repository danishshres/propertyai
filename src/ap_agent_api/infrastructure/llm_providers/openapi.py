from agents import Agent, WebSearchTool

# from ap_agent_api.domain.models.property import PropertyData

def create_search_agent(
    instruction: str,
    output_type
) -> Agent:
    """
    Factory function to create a property search agent.
    
    Args:
        instruction: Instruction string for the agent.
        address: Property address to focus the search on.
    
    Returns:
        Configured Agent instance for property searching.
    """
    
    # Create agent with WebSearchTool
    agent = Agent(
        name="PropertySearchAgent",
        instructions=instruction,
        tools=[
            WebSearchTool(
                user_location={
                    "type": "approximate",
                    "city": "Sydney"
                }
            )
        ],
        output_type=output_type
    )

    return agent