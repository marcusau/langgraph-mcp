import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from mcp_use import MCPAgent, MCPClient
import mcp_use
import json

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(path+"/setting.json", "r") as f:
    setting = json.load(f)

host = setting["host"]
port = setting["port"]
mcp_transport = setting["transport"]
server_name = setting["server_name"]
mcp_use.set_debug(1)  # INFO level
load_dotenv(override=True)




# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# llm = ChatOpenAI(model="gpt-4o-mini",api_key=OPENAI_API_KEY,temperature=0,seed=42)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
llm = ChatDeepSeek(model="deepseek-chat", 
                  api_key=DEEPSEEK_API_KEY,
                  temperature=0,
                  seed=42,
                  max_tokens=None,
                  timeout=None,
                  max_retries=2,)

async def main():
    config = {
        "mcpServers": {
            server_name["tavily"]: { "url": f"http://{host}:{port['tavily']}/{mcp_transport}" },
            server_name["youtube_transcript"]: {"url": f"http://{host}:{port['youtube_transcript']}/{mcp_transport}" }, 
            server_name["maths"]: { "url": f"http://{host}:{port['maths']}/{mcp_transport}"},      
            server_name["weather"]: {  "url": f"http://{host}:{port['weather']}/{mcp_transport}" },
              }
    }
    # Create MCPClient from config file
    client = MCPClient.from_dict(config)

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30,use_server_manager=True,verbose=True)  # Only shows debug messages from the agent)  # Enable the Server Manager)

    # try:
    # Run the query
    query = "Any updates on the US tariff policies imposed on China?" #"What is the weather in Tokyo?" #"What are the latest US tariff policies imposed on China?"
    result = await agent.run(query,max_steps=30,   )
    print(f"\nResult: {result}")
    # finally:
    #     # Clean up all sessions
    #     await client.close_all_sessions()
   # await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())