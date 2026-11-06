from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import json
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = []

messages.append(
    {
        "role": "system",
        "content": "Act as a technical agent and always provide responses within 80 words."
    }
)

while True:
    user_input = input("\nAmarjeet: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append({
        "role": "user",
        "content": user_input
    })
    
    response = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS,
    )

    msg = response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")

            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
            result = fn(**func_args)

            messages.append({
                "role": "tool",
                "tool_id": tool_call.id,
                "content": str(result),
            })

        # 2nd call to LLM API
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )

        msg = response.choices[0].message

    messages.append({
        "role": "assistant",
        "content": msg.content
    })

    print("Assistant: ", msg.content)