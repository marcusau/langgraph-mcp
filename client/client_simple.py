import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
import openai
load_dotenv(override=True)

nest_asyncio.apply()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL=os.getenv("DEEPSEEK_API_URL")
# Global variables to store session state
session = None
exit_stack = AsyncExitStack()
llm_client = AsyncOpenAI( api_key=OPENAI_API_KEY)
#print(f"llm_client: {llm_client.list_models()}")

model = "gpt-4.1"#"deepseek-chat"#"gpt-4o"
stdio = None
write = None


async def connect_to_server(server_script_path: str ):
    """Connect to an MCP server.

    Args:
        server_script_path: Path to the server script.
    """
    global session, stdio, write, exit_stack

    # Server configuration
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Connect to the server
    stdio_client_=stdio_client(server_params)
    stdio_transport = await exit_stack.enter_async_context(stdio_client_)
    stdio, write = stdio_transport
    client_session = ClientSession(stdio, write)
    session = await exit_stack.enter_async_context(client_session)

    # Initialize the connection
    await session.initialize()

    # List available tools
    tools_result = await session.list_tools()

    print("\nConnected to server with tools:")
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")




async def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get available tools from the MCP server in OpenAI format.

    Returns:
        A list of tools in OpenAI format.
    """
    global session

    tools_result = await session.list_tools()

    print(f"get_mcp_tools:")
    results = []
    for i, tool in enumerate(tools_result.tools):

        result={
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
        
        print(f"   Tool {i}: {result}")
        results.append(result)
    print(f"\n")
    return results



async def process_query(query: str) -> str:
    """Process a query using OpenAI and available MCP tools.

    Args:
        query: The user query.

    Returns:
        The response from OpenAI.
    """
    global session, openai_client, model

    # Get available tools
    tools = await get_mcp_tools()

    # Initial OpenAI API call
    first_response = await llm_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="auto",
        temperature=0.0,
        seed=42,
    )

    print(f"first_response assistant_message: {first_response.choices[0].message}")
    print(f"first_response assistant_message.tool_calls: {first_response.choices[0].message.tool_calls}")
    print(f"first_response assistant_message content: {first_response.choices[0].message.content}")

    # Get assistant's response
    assistant_message = first_response.choices[0].message

    # Initialize conversation with user query and assistant response
    messages = [ {"role": "user", "content": query},  assistant_message,  ]

    # Handle tool calls if present
    if not assistant_message.tool_calls:
        return assistant_message.content
    
    else:
        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            # Execute tool call
            result = await session.call_tool(
                tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )

            #print(f"tool_call in first response assistant_message: id: {tool_call.id}, function name: {tool_call.function.name}, arguments: {tool_call.function.arguments}")

            # Add tool response to conversation
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content[0].text,
                }
            )
        print(f"\ntype of  result.content[0].text: { type(result.content[0].text)}\n")
        print(f"\n\nmessages: \n")
        for message in messages:
            print(f"message type: {type(message)}")
            print(f"{message}\n")

        # Get final response from OpenAI with tool results
        final_response = await llm_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="none",  # Don't allow more tool calls
            temperature=0.0,
            seed=42,
        )
        #print(f"\nfinal_response content: {final_response.choices[0].message.content}")
        return final_response.choices[0].message.content

    # No tool calls, just return the direct response
    #return assistant_message.content

async def cleanup():
    """Clean up resources."""
    global exit_stack
    await exit_stack.aclose()



async def main():
    """Main entry point for the client."""
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))  )
    python_script_path= os.path.join(path,r"servers\tavily_stdio.py")
    print(f"python_script_path: {python_script_path}")
    await connect_to_server(python_script_path)

    # # Example: Ask about company vacation policy
    query = "What are the latest US tariff polices imposed on China in 2025?"
    print(f"\nQuery: {query}")

    response = await process_query(query)
    #print(f"\nResponse: {response}")

    await cleanup()

if __name__ == "__main__":
    asyncio.run(main())