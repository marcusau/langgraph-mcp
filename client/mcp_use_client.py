import asyncio
import os
from dotenv import load_dotenv
#from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

load_dotenv(override=True)

#DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
async def main():


    # # Create configuration dictionary
    # config = {
    #   "mcpServers": {
    #     "tavily": {
    #       "command": "python",
    #       "args": ["langgraph-mcp/servers/tavily.py"],
    #       "env": {  "DISPLAY": ":1"}
    #             }
    #                 }
    #       }
    config = {
        "mcpServers": {
            "http": {
                "url": "http://localhost:8080"
            }
        }
    }
    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)
    
    llm = ChatOpenAI(model="gpt-4o-mini",api_key=OPENAI_API_KEY,temperature=0,seed=42)
    # llm= ChatDeepSeek(model="deepseek-chat", 
    #                   api_key=DEEPSEEK_API_KEY,
    #                   temperature=0,
    #                   max_tokens=None,
    #                   timeout=None,
    #                   max_retries=2,)
    
   # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    
    # # Run the query
    query = input("Query:")
    result = await agent.run( query )
    print(f"\nResult: {result}")
    
if __name__ == "__main__":
    asyncio.run(main())
    