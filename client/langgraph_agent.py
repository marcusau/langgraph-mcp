import asyncio,os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
#from langchain_ollama import ChatOllama
from langchain_deepseek import ChatDeepSeek
#from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv(override=True)

#OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
#print(f"OLLAMA_MODEL: {OLLAMA_MODEL}")
#model = ChatOllama(model=OLLAMA_MODEL)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
model = ChatDeepSeek(model="deepseek-chat", api_key=DEEPSEEK_API_KEY,temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# model = ChatOpenAI(model="gpt-4.1", api_key=OPENAI_API_KEY,temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,)

# query = input("Query:")

# Define MCP servers
async def run_agent():
    async with MultiServerMCPClient(
        # {
        #     "tavily": {
        #         "command": "python",
        #         "args": ["langgraph-mcp/servers/tavily.py"],
        #         "transport": "stdio",
        #     },
        #     "youtube_transcript": {
        #         "command": "python",
        #         "args": ["langgraph-mcp/servers/yt_transcript.py"],
        #         "transport": "stdio",
        #     }, 
        #     "maths": {
        #         "command": "python",
        #         "args": ["langgraph-mcp/servers/maths.py"],
        #         "transport": "stdio",
        #     },      
        #     "weather": {
        #         "command": "python",
        #         "args": ["langgraph-mcp/servers/weather.py"],
        #         "transport": "stdio",
        #     },
        # }
               {
            "tavily": {
                "url": "http://127.0.0.1:8060/sse",
                "transport": "sse",

            },
            "youtube_transcript": {
                   "url": "http://127.0.0.1:8080/sse",
                "transport": "sse",
            }, 
            "maths": {
                    "url": "http://127.0.0.1:8050/sse",
                "transport": "sse",
            },      
            "weather": {
                    "url": "http://127.0.0.1:8070/sse",
                "transport": "sse",
            },
        }
    ) as client:
        # Load available tools
        tools = client.get_tools()
        # print(f"Tools: {tools}")
        print("Available tools:")
        for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
        print("--------------------------------")
        agent = create_react_agent(model, tools)
        
        system_message = SystemMessage(content=(
                "You have access to multiple tools that can help answer queries. "
                "Use them dynamically and efficiently based on the user's request. "
                "Please only output the answer to the user's query, no explanation nor comment is needed."
        ))
        
        # Process the query
        query = "What are the latest US tariff policies imposed on China?" #input("Query:")
        agent_response = await agent.ainvoke({"messages": [system_message, HumanMessage(content=query)]})
        
        return agent_response["messages"][-1].content


# Run the agent
if __name__ == "__main__":
    response = asyncio.run(run_agent())
    print("\nFinal Response:", response)