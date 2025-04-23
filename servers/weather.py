from mcp.server.fastmcp import FastMCP
import json
import os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
with open(path+"/setting.json", "r") as f:
    setting = json.load(f)

host = setting["host"]
port = setting["port"]["weather"]
mcp_transport = setting["transport"]
server_name = setting["server_name"]["weather"]

mcp = FastMCP(server_name , host=host, port=port )

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
    mcp.run(transport=mcp_transport)