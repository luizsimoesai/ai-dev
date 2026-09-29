from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_typesafe.experimental.middleware import ModelChoice, ModelRouterMiddleware

load_dotenv()

router = ModelRouterMiddleware(
    choices={
        "fast": ModelChoice(
            model="openai:gpt-5-mini",
            criteria="Simple, well-scoped tasks.",
        ),
        "powerful": ModelChoice(
            model="openai:gpt-5.5",
            criteria="Complex tasks requiring deeper reasoning.",
        ),
    },
    instructions="Choose the least costly model suited to the task.",
)

agent = create_agent("openai:gpt-5-mini", middleware=[router])

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What's the capital of France?"}
    ],
})

print(result["messages"][-1].content)
print(result["model_route"].choice)
