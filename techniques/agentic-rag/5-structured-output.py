"""
Structured output: the agent must return a SearchAnswer with citations,
not free-text. Downstream code can rely on the schema. No parsing prose.

Original implementation used Pydantic AI's output_type. Framework swapped to
LangChain, running anthropic/claude-opus-4.6 through OpenRouter (OpenAI
-compatible API), same setup as 4-streaming-steps.py.
Comments below compare each step against the Pydantic AI equivalent.

More info:
- Pydantic AI: https://ai.pydantic.dev/output/
- LangChain structured output: https://docs.langchain.com/oss/python/langchain/structured-output
"""

# ----------------------------------------------------------------------------
# ORIGINAL PYDANTIC AI IMPLEMENTATION (kept for comparison, not executed)
# ----------------------------------------------------------------------------
#
# from pydantic import BaseModel, Field
# from pydantic_ai import Agent
# import nest_asyncio
#
# from utils.tools import grep, list_files, read_file
#
# nest_asyncio.apply()
#
#
# class Citation(BaseModel):
#     """One source backing a claim in the answer."""
#
#     file: str = Field(
#         description="Relative path to the markdown file, e.g. '03-incident-2024-q3.md'"
#     )
#     quote: str = Field(
#         description="The exact line(s) from the file that support the claim"
#     )
#     line_number: int = Field(description="The line number of the quote")
#
#
# class SearchAnswer(BaseModel):
#     """Structured answer with at least one citation per claim."""
#
#     answer: str = Field(description="The answer in plain English")
#     citations: list[Citation] = Field(
#         description="Files and quotes that support the answer"
#     )
#
#
# agent = Agent(
#     "openai:gpt-5.5",
#     tools=[list_files, grep, read_file],
#     output_type=SearchAnswer,
#     instructions=(
#         "Search notes with list_files, grep, read_file. Cite files. "
#         "If evidence is missing, say so."
#     ),
# )
#
# if __name__ == "__main__":
#     result = agent.run_sync(
#         "Why does our nightly deploy job run at 03:47 UTC specifically?"
#     )
#     answer = result.output
#
#     print(f"Answer: {answer.answer}")
#     print("Citations:")
#     for c in answer.citations:
#         print(f"  - {c.file}:{c.line_number}")
#         print(f"      {c.quote}")
#
# ----------------------------------------------------------------------------

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from utils.tools import grep, list_files, read_file

load_dotenv()

# --------------------------------------------------------------
# Step 1: Define the answer schema
# --------------------------------------------------------------
# Same Pydantic models either way -- this part doesn't change between
# frameworks. Pydantic AI and LangChain both accept a plain BaseModel
# subclass as the schema for the structured output.


class Citation(BaseModel):
    """One source backing a claim in the answer."""

    file: str = Field(
        description="Relative path to the markdown file, e.g. '03-incident-2024-q3.md'"
    )
    quote: str = Field(
        description="The exact line(s) from the file that support the claim"
    )
    line_number: int = Field(description="The line number of the quote")


class SearchAnswer(BaseModel):
    """Structured answer with at least one citation per claim."""

    answer: str = Field(description="The answer in plain English")
    citations: list[Citation] = Field(
        description="Files and quotes that support the answer"
    )


# --------------------------------------------------------------
# Step 2: Wire the schema into the agent
# --------------------------------------------------------------
# Pydantic AI: output_type=SearchAnswer on the Agent constructor.
# LangChain: response_format=SearchAnswer on create_agent. Passed a bare
#   schema like this, LangChain wraps it in an AutoStrategy, which picks
#   ProviderStrategy (native structured-output support, e.g. OpenAI's
#   response_format) when the model offers it, and otherwise falls back to
#   ToolStrategy -- an extra synthetic tool the model calls once it's ready
#   to answer, whose arguments are validated against SearchAnswer. Either
#   strategy can be passed explicitly too (response_format=ToolStrategy(...))
#   if you need to force one.

model = ChatOpenAI(
    model="anthropic/claude-opus-4.6",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

agent = create_agent(
    model,
    tools=[list_files, grep, read_file],
    response_format=SearchAnswer,
    system_prompt=(
        "Search notes with list_files, grep, read_file. Cite files. "
        "If evidence is missing, say so."
    ),
)


# --------------------------------------------------------------
# Step 3: Run it and pretty-print the structured result
# --------------------------------------------------------------
# Pydantic AI: result.output is already a SearchAnswer instance.
# LangChain: agent.invoke(...) returns a dict with a "messages" list, same
#   as the plain agents in 3/4 -- but with response_format set, the graph
#   also stashes the validated instance under "structured_response".

if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Why does our nightly deploy job run at 03:47 UTC specifically?",
                }
            ]
        }
    )
    answer = result["structured_response"]

    print(f"Answer: {answer.answer}")
    print("Citations:")
    for c in answer.citations:
        print(f"  - {c.file}:{c.line_number}")
        print(f"      {c.quote}")
