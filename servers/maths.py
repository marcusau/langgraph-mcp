# Rename this file to avoid conflict with Python's built-in math module
# The error occurs because this file is named 'math.py' which conflicts with Python's math module
# This creates a circular import when other modules try to import the built-in math module

from mcp.server.fastmcp import FastMCP
from typing import Any
import sys
import json
import os   

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
with open(path+"/setting.json", "r") as f:
    setting = json.load(f)

host = setting["host"]
port = setting["port"]["maths"]
mcp_transport = setting["transport"]
server_name = setting["server_name"]["maths"]

mcp = FastMCP(server_name, host=host, port=port )

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     return a + b

@mcp.tool()
async def add_numbers(value1: int, value2:int) -> int:
    """Add Two numbers

    Args:
        value1: First Integer value
        value2: Second Integer value

    Returns:
        int: Addition of two numbers
    """
    return value1 + value2

# @mcp.tool()
# def multiply(a: int, b: int) -> int:
#     return a * b

@mcp.tool()
async def multiply_numbers(value1: int, value2:int) -> int:
    """Multiply Two numbers

    Args:
        value1: First Integer value
        value2: Second Integer value


    Returns:
        int: Multiplication of two numbers
    """
    
    return value1 * value2

if __name__ == "__main__":
    print("Server env is ", sys.prefix)
    mcp.run(transport=mcp_transport)