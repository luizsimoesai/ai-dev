from openai import OpenAI
from dotenv import load_dotenv
_ = load_dotenv()

# --- API OpenAI ---
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="O que significa IA?"
)

print(response.output_text)

type(response)
# >> openai.types.responses.response.Response

response.output[0].to_dict()
"""
{'id': 'msg_68652f019df881a3aaf0a87f68cbda4f0ba14653bd57027f',
 'content': [{'annotations': [],
   'text': 'IA significa Inteligência Artificial, 
            uma abreviatura para uma área da ciência da computação 
            que desenvolve sistemas capazes de realizar 
            tarefas que normalmente exigiriam inteligência humana.',
   'type': 'output_text',
   'logprobs': []}],
 'role': 'assistant',
 'status': 'completed',
 'type': 'message'}
"""


# --- instructions ---
response = client.responses.create(
    model="gpt-4.1",
    instructions="Você e um assistente que responde apenas em uma palava ou expressão.",
    input="O que significa IA?",
)
print(response.output_text)


# -- Gerar texto com mensagens usando diferentes papéis (roles) ---
response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "system",
            "content": "Você e um assistente que responde apenas em uma palava ou expressão.",
        },
        {
            "role": "user",
            "content": "O que significa IA?",
        },
    ]
)

response.output[0].to_dict()
""" 
{'id': 'msg_686533da2290819faf8ed29ae86392b60a301ce4cd5b19bf',
 'content': [{'annotations': [],
   'text': 'Inteligência Artificial.',
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
            "content": "O que significa IA?",
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
['IA',
 ' significa',
 ' "',
 'Int',
 'elig',
 'ência',
 ' Artificial',
 '".']
"""