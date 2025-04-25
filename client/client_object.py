import asyncio
import sys
import logging
import json
import os
import re

from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL=os.getenv("OPENAI_MODEL")

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL=os.getenv("DEEPSEEK_BASE_URL")
DEEPSEEK_MODEL=os.getenv("DEEPSEEK_MODEL")

model =DEEPSEEK_MODEL #"deepseek-chat" #"gpt-4o-mini" #"claude-3-5-sonnet-20241022"
# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_client.log"),
        logging.StreamHandler()
    ]
)

class MCPClient:
    def __init__(self,platform:str="openai"):
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.openai_api = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.deepseek_api = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        if platform == "openai":
            self.llm_api = self.openai_api
        elif platform == "deepseek":
            self.llm_api = self.deepseek_api

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an SSE MCP server."""
        logger.debug(f"Connecting to SSE MCP server at {server_url}")
        print(f"Connecting to SSE MCP server at {server_url}")

        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Connected to SSE MCP Server at {server_url}. Available tools: {[tool.name for tool in tools]}")
        print(f"Connected to SSE MCP Server at {server_url}")
        for tool in tools:
            print(f"Tool: {tool.name}")
        print("--------------------------------")
   
    async def connect_to_server(self, server_path_or_url: str):
        """Connect to an MCP server (either stdio or SSE)."""
        # Check if the input is a URL (for SSE server)
        # url_pattern = re.compile(r'^https?://')
        
        # if url_pattern.match(server_path_or_url):
        #     # It's a URL, connect to SSE server
        #     await self.connect_to_sse_server(server_path_or_url)
        # else:
        #     # It's a script path, connect to stdio server
        #     await self.connect_to_stdio_server(server_path_or_url)
        await self.connect_to_sse_server(server_path_or_url)
    
    async def get_model_list(self)->list:
        """Get a list of available models."""
        response = await self.llm_api.models.list()
        return [model.id for model in response.data]

    async def call_llm(self,model:str,messages:list,tools:list,tool_choice:str="auto",max_tokens:int=8192,temperature:float=0.0,seed:int=42)->str:
        """Call the LLM with the given model and messages."""
        response = await self.llm_api.chat.completions.create(
                                                model=model,
                                                messages=messages,
                                                tools= tools,
                                                tool_choice=tool_choice,
                                                max_tokens=max_tokens,
                                                temperature=temperature,
                                                seed=seed,
                                            )
        return response

    async def process_query(self, query: str, previous_messages: list = None) -> tuple[str, list]:
        """Process a query using the MCP server and available tools."""
        

        if not self.session:
            raise RuntimeError("Client session is not initialized.")
        
        messages = []
        if previous_messages:
            messages.extend(previous_messages)

        messages.append(  {"role": "user","content": query }   )
        
        response = await self.session.list_tools()
        # available_tools = [{
        #     "name": tool.name,
        #     "description": tool.description,
        #     #"input_schema": dict(tool.inputSchema) if tool.inputSchema else {}
        #     "parameters": tool.inputSchema
        #      } for tool in response.tools]

        available_tools = []
        for i, tool in enumerate(response.tools):

                result={
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                
                print(f"   Tool {i}: {result}\n")
                available_tools.append(result)
        print("\n")
    
        # Initialize Claude API call
        logger.info(f"Sending query to {model}...\n")
        print(f"Sending query to {model}...\n")

        print(f"available_tools: {available_tools}\n")
        print(f"messages: {messages}\n")

        first_response =await self.call_llm(model=model,messages=messages,tools=available_tools,tool_choice="auto")
        # Process response and handle tool calls
        final_text = []
        assistant_message_content = []
        #print(f"response:  {response}")

        #print(f"response:  {response.choices}")
        for choice in first_response.choices:
            
            if choice.finish_reason == 'stop':
                final_text.append(choice.message.content)
                assistant_message_content.append(choice.message)

            elif choice.finish_reason == 'tool_calls':
                tool_name = choice.message.tool_calls[0].function.name
                print(f"tool_arg:{choice.message.tool_calls[0].function.arguments}\n")
                # try:
                tool_args = json.loads(choice.message.tool_calls[0].function.arguments)
                # except:
                #tool_args = choice.message.tool_calls[0].function.arguments
        #         tool_name = content.name
        #         tool_args = content.input

        #         # Execute tool call
                logger.debug(f"Calling tool {tool_name} with args {tool_args}...\n")
                print(f"Calling tool {tool_name} with args {tool_args}...\n")
                
                result = await self.session.call_tool(tool_name, tool_args)
                #print(f"session.call_tool result: {result}")
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                # print(f"choice.message : {choice.message}\n")
                # assistant_message_content.append(choice.message)
                # print(f"assistant_message_content: {assistant_message_content}\n")

                #messages.append({ "role": "assistant", "content":choice.message  })
                messages.append(choice.message)

                 
                #print(f"result.content[0].text type : {type(result_content)}\n")
                #print(f"result.content[0].text: {result_content}\n")
                #print(f"choice.message.tool_calls[0].id: {choice.message.tool_calls[0].id}\n")
               #messages.append({ "role": "user",  "content": [{"type": "tool_result", "tool_use_id": choice.message.tool_calls[0].id, "content": result_content} ] })
                messages.append({ "role": "tool",  "tool_call_id": choice.message.tool_calls[0].id, "content": result.content[0].text}    )

                # print(f"messages: \n")
                # for message in messages:
                #     print(f"{message}\n")
                # # Get next response from Claude
                next_response = await self.call_llm(model=model,messages=messages,tools=available_tools,tool_choice=None)
                final_text.append(next_response.choices[0].message.content)
                messages.append({ "role": "assistant","content": next_response.choices[0].message.content })

        return "\n".join(final_text), messages
    
    async def chat_loop(self):
        """Run an interactive chat loop with the server."""
        previous_messages = []
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                
                #  Check if the user wants to refresh conversation (history)
                if query.lower() == "refresh":
                    previous_messages = []
            
                response, previous_messages = await self.process_query(query, previous_messages=previous_messages)
                
                print("\nResponse:", response)
            except Exception as e:
                print("Error:", str(e))
    
    async def clenup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()
        if hasattr(self, '_session_context') and self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if hasattr(self, '_streams_context') and self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

async def main():

    client = MCPClient(platform="deepseek")
    try:
        sse_server_url = "http://127.0.0.1:8060/sse"
        await client.connect_to_server(sse_server_url)
        await client.chat_loop()
    finally:
        await client.clenup()
        print("\nMCP Client Closed!")


if __name__ == "__main__":
    asyncio.run(main())