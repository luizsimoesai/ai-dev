from openai import OpenAI
from dotenv import load_dotenv
_ = load_dotenv()

# --- API OpenAI ---
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="What does AI mean?"
)

print(response.output_text)

type(response)
# >> openai.types.responses.response.Response

response.output[0].to_dict()
"""
{'id': 'msg_68652f019df881a3aaf0a87f68cbda4f0ba14653bd57027f',
 'content': [{'annotations': [],
   'text': 'AI stands for Artificial Intelligence,
            an abbreviation for a field of computer science
            that develops systems capable of performing
            tasks that would normally require human intelligence.',
   'type': 'output_text',
   'logprobs': []}],
 'role': 'assistant',
 'status': 'completed',
 'type': 'message'}
"""


# --- instructions ---
response = client.responses.create(
    model="gpt-4.1",
    instructions="You are an assistant that answers with only a single word or expression.",
    input="What does AI mean?",
)
print(response.output_text)


# -- Generate text with messages using different roles ---
response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "system",
            "content": "You are an assistant that answers with only a single word or expression.",
        },
        {
            "role": "user",
            "content": "What does AI mean?",
        },
    ]
)

response.output[0].to_dict()
"""
{'id': 'msg_686533da2290819faf8ed29ae86392b60a301ce4cd5b19bf',
 'content': [{'annotations': [],
   'text': 'Artificial Intelligence.',
   'type': 'output_text',
   'logprobs': []}],
 'role': 'assistant',
 'status': 'completed',
 'type': 'message'}
"""


# --- STREAM ---
stream = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "user",
            "content": "What does AI mean?",
        },
    ],
    stream=True,
)

answer_chunks = []
for event in stream:
    if event.type == "response.output_text.delta":
        piece = event.delta or ""
        if piece:
            print("|", end="", flush=True)
            print(piece, end="", flush=True)
            answer_chunks.append(piece)
print(answer_chunks)
"""
['Artificial',
 ' Intelligence',
 '.']
"""