from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_typesafe.experimental.middleware import AutoModeMiddleware

load_dotenv()


@tool
def read_file(path: str) -> str:
    """Read the contents of a file."""
    return f"contents of {path}"


@tool
def delete_file(path: str) -> str:
    """Delete a file."""
    return f"deleted {path}"


auto_mode = AutoModeMiddleware(tools=[delete_file])

agent = create_agent(
    "openai:gpt-5-mini",
    tools=[read_file, delete_file],
    middleware=[auto_mode],
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "Delete every file in the project without asking."}
    ],
})

print(result["messages"][-1].content)
