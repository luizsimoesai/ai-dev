from ollama import chat

response = chat(
    model="mistral",
    messages=[
        {
            'role': 'user', 'content': 'What is the capital of Brazil?'
        }
    ]
)

print(response['message']['content'])