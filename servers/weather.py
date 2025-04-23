from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather", host="127.0.0.1", port=8070)

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location.

    Args:
        location: Location string to get weather for

    Returns:
        str: Weather description for the location
    """
    return f"It's always sunny in {location}"

if __name__ == "__main__":
    mcp.run(transport="sse")