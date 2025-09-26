from ollama import chat

response = chat(
    model="mistral",
    messages=[
        {
            'role': 'user', 'content': 'Qual a capital do Brasil?'
        }
    ]
)

print(response['message']['content'])