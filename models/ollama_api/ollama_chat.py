from ollama import chat

response = chat(
    model="qwen3.5:0.8b",
    messages=[
        {
            'role': 'user', 'content': 'What is the capital of Brazil?'
        }
    ]
)

print(response['message']['content'])