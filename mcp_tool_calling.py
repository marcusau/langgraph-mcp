import json
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict
load_dotenv(override=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL="https://api.deepseek.com"
deepseek_model = "deepseek-chat"


def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


# Define tools for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "First number"},
                    "b": {"type": "integer", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    }
]
def call_deepseek_api(message: List[Dict[str, str]]):
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    response = client.chat.completions.create(
     model=deepseek_model,
    messages=message,
    tools=tools,
       temperature=0.1,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False,)
    return response.choices[0].message

query="Calculate 25 + 17"
message=[{"role": "user", "content": query}]
first_response_message=call_deepseek_api(message)
print(f"First response: {first_response_message}")

# Handle tool calls
if first_response_message.tool_calls:
    tool_call = first_response_message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)
    print(f"Tool call name: {tool_name}")
    print(f"Tool call arguments: {tool_args}")
   
    result = add(**tool_args)
    print(f"Tool call result: {result}")


    message.append(first_response_message)
    message.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

    
    
    final_response_message =call_deepseek_api(message)
    print(f"Final response: {final_response_message.content}")
else:
    print("No tool call")

