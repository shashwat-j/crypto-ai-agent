import json
import os
import openai
from tools import get_crypto_price, tools

client = openai.OpenAI(
    base_url = "https://api.together.xyz/v1",
    api_key = os.environ['TOGETHER_API_KEY'],
)

llm_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"

tool_names = [tool["function"]["name"] for tool in tools]

tool_prompt = (
    f"You are a helpful assistant that can access the following external functions: {tool_names}. "
    "The responses from these function calls will be appended to this dialogue by tool, if required. "
    f"If any query of the user requires information about one of these, {tool_names}, "
    "then please provide responses based on the information from these function calls; otherwise, "
    "Do NOT use the function calls if the answer does not require information from these functions. "
    "If the latest message is from 'tool', then use the content given in it to answer the question asked by the user. "
    "Do not mention to the user that you are using function calls or tools."
    "In case the tool gives any information which not relevant to the conversation, ignore it and do not acknowledge the presence of that disturbance or confusion to the user. "
    "Only you can see it. User cannot see it. So continue your conversation normally."
)

messages = [
    {"role": "system", "content": tool_prompt},
]


def generate_agent_response(user_message):
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
    model= llm_model,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    )
    # print("response 1: ",response)# for debugging

    tool_calls = response.choices[0].message.tool_calls
    initial_res_content = response.choices[0].message.content
    # print("tool_calls: ", tool_calls)# for debugging
    assistant_response = ""
    
    if not tool_calls:
        assistant_response = initial_res_content
    else:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_crypto_price":
                function_response = get_crypto_price(
                    crypto_name=function_args.get("crypto_name"),
                )
                print("function_response: ", function_response)# for debugging
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
        # print("messages2: ", messages)# for debugging
        function_enriched_response = client.chat.completions.create(
            model=llm_model,
            messages=messages,
        )
        # print("function_enriched_response: ", function_enriched_response)# for debugging
        assistant_response = function_enriched_response.choices[0].message.content

    print("Assistant: ", assistant_response)
    messages.append({"role": "assistant", "content": assistant_response})    
