import json
import requests
from openai import OpenAI

from pprint import pprint
from dotenv import load_dotenv
_ = load_dotenv()

# --- Function that returns the weather ---
def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']


# --- Step 1: call the model with the get_weather tool defined ---
# Model call with functions defined – along with its system and user messages.


client = OpenAI()

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}]

input_messages = [{"role": "user", "content": "What is the weather like in São Paulo today?"}]

response = client.responses.create(
    model="gpt-4.1",
    input=input_messages,
    tools=tools,
)

# --- Step 2: the model decides to call function(s) – the model returns the name and input arguments. ---
pprint(response.output[0].model_dump())

# --- Step 3: execute function code – parse the model's response and handle function calls. ---
tool_call = response.output[0]
args = json.loads(tool_call.arguments)

result = get_weather(args["latitude"], args["longitude"])

# --- Step 4: supply results to the model – so it can incorporate them into its final response. ---
input_messages.append(tool_call)  # append model's function call message
input_messages.append({           # append result message
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(result)
})

response_2 = client.responses.create(
    model="gpt-4.1",
    input=input_messages,
    tools=tools,
)

# --- Step 5: the model responds – incorporating the result into its output. ---
print(response_2.output_text)


