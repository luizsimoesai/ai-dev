"""
Basic Agentic RAG: an agent with three tools (list_files, grep, read_file).
The agent picks tools to call iteratively until it has enough context to answer.
No vector database, no embeddings, no chunking. Just an LLM that knows how to grep.

Original implementation used Pydantic AI. Framework swapped to LangChain, running
openai/gpt-4.1-nano through OpenRouter (OpenAI-compatible API). Initially tried
nvidia/nemotron-3-ultra-550b-a55b:free, but that free model kept skipping
list_files/grep and hallucinating file paths straight into read_file, crashing
the script — swapped to gpt-4.1-nano for reliable tool-calling.
Comments below compare each step against the Pydantic AI equivalent.

More info:
- Pydantic AI: https://ai.pydantic.dev/agents/
- LangChain agents: https://docs.langchain.com/oss/python/langchain/agents
"""

# ----------------------------------------------------------------------------
# ORIGINAL PYDANTIC AI IMPLEMENTATION (kept for comparison, not executed)
# ----------------------------------------------------------------------------
#
# from pydantic_ai import Agent
# import nest_asyncio
#
# from utils.tools import grep, list_files, read_file
#
# nest_asyncio.apply()
#
# agent = Agent(
#     "openai:gpt-5.5",
#     tools=[list_files, grep, read_file],
#     instructions=(
#         "Search notes with list_files, grep, read_file. Cite files. "
#         "If evidence is missing, say so."
#     ),
# )
#
# if __name__ == "__main__":
#     question = "Why does our nightly deploy job run at 03:47 UTC specifically?"
#
#     result = agent.run_sync(question)
#
#     print(f"\nQ: {question}\n")
#     print("A:", result.output)
#     print(f"\nUsage: {result.usage()}")
#
# ----------------------------------------------------------------------------

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from utils.tools import grep, list_files, read_file

load_dotenv()

# --------------------------------------------------------------
# Step 1: Define the model
# --------------------------------------------------------------
# Pydantic AI: the model is a plain string ("openai:gpt-5.5") resolved
#   internally by the provider prefix; auth reads OPENAI_API_KEY from env.
# LangChain: the model is an explicit chat model *object*. There's no built-in
#   OpenRouter integration, but OpenRouter's API is OpenAI-compatible, so we
#   reuse ChatOpenAI and just point base_url at OpenRouter and pass its key.

model = ChatOpenAI(
    model="openai/gpt-4.1-nano",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# --------------------------------------------------------------
# Step 2: Define the agent
# --------------------------------------------------------------
# Pydantic AI: Agent(model, tools=[...], instructions="...") builds a ready
#   -to-run agent object; plain Python functions are auto-wrapped into tools
#   using their type hints and docstrings, no decorator needed.
# LangChain: create_agent(model, tools=[...], system_prompt="...") builds the
#   agent as a compiled LangGraph state graph under the hood. Plain functions
#   are also auto-converted into tools (same idea: type hints + docstring),
#   so utils/tools.py doesn't need to change at all.
# Also note: Pydantic AI needed nest_asyncio.apply() to make its async core
#   runnable synchronously (run_sync) from a plain script; LangChain's
#   create_agent graph exposes a synchronous .invoke() directly, so that
#   workaround isn't needed here.

agent = create_agent(
    model,
    tools=[list_files, grep, read_file],
    system_prompt=(
        "Search notes with list_files, grep, read_file. Cite files. "
        "If evidence is missing, say so."
    ),
)


# --------------------------------------------------------------
# Step 3: Ask a needle-in-haystack question
# --------------------------------------------------------------
# Pydantic AI: agent.run_sync(question) -> result.output / result.usage()
# LangChain: agent.invoke({"messages": [...]}) -> dict with a "messages" list;
#   the answer is the content of the last message, and token usage lives in
#   that last message's usage_metadata instead of a dedicated usage() call.
#
# Note on nest_asyncio (dropped here): Pydantic AI's run_sync() calls
#   asyncio.run() internally, which breaks inside a Jupyter/ipykernel cell
#   because the kernel already has an event loop running in that thread --
#   hence nest_asyncio.apply() to allow nesting. LangGraph's agent.invoke()
#   is genuinely synchronous (thread-based, not asyncio.run()-based), so it
#   runs fine cell-by-cell in VS Code's interactive window without the patch.

if __name__ == "__main__":
    question = "What language for the frontend?"

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    answer = result["messages"][-1]

    print(f"\nQ: {question}\n")
    print("A:", answer.content)
    print(f"\nUsage: {answer.usage_metadata}")
