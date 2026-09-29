"""
Streaming the agent's intermediate steps.
This is where 'agentic' becomes visible. Every grep, every read, printed live.

If you've ever watched Claude Code work, this is the same loop.

Original implementation used Pydantic AI's agent.iter(). Framework swapped to
LangChain, running openai/gpt-4.1-nano through OpenRouter (OpenAI-compatible
API), same setup as 3-basic-agent.py.
Comments below compare each step against the Pydantic AI equivalent.

More info:
- Pydantic AI: https://ai.pydantic.dev/agents/#iterating-over-an-agents-graph
- LangChain streaming: https://docs.langchain.com/oss/python/langchain/streaming
"""

# ----------------------------------------------------------------------------
# ORIGINAL PYDANTIC AI IMPLEMENTATION (kept for comparison, not executed)
# ----------------------------------------------------------------------------
#
# import asyncio
#
# import nest_asyncio
# from pydantic_ai import Agent
# from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent
#
# from utils.tools import grep, list_files, read_file
# from utils.streaming import format_tool_result
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
#
# async def run_with_visible_steps(question: str, debug: bool = False) -> str:
#     print(f"\nQ: {question}\n")
#     print("--- agent steps ---")
#     tool_names: dict[str, str] = {}
#
#     async with agent.iter(question) as run:
#         async for node in run:
#             if Agent.is_call_tools_node(node):
#                 async with node.stream(run.ctx) as tool_stream:
#                     async for event in tool_stream:
#                         if isinstance(event, FunctionToolCallEvent):
#                             tool_names[event.tool_call_id] = event.part.tool_name
#                             print(
#                                 f"-> {event.part.tool_name}({event.part.args_as_json_str()})"
#                             )
#                         elif debug and isinstance(event, FunctionToolResultEvent):
#                             print(format_tool_result(event, tool_names))
#
#     print("--- done ---\n")
#     return run.result.output
#
#
# if __name__ == "__main__":
#     answer = asyncio.run(
#         run_with_visible_steps(
#             "Why does our nightly deploy job run at 03:47 UTC specifically?",
#             debug=False,
#         )
#     )
#     print("A:", answer)
#
# ----------------------------------------------------------------------------

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from utils.tools import grep, list_files, read_file
from utils.streaming import format_tool_result

load_dotenv()

# --------------------------------------------------------------
# Step 1: Same agent as 3-basic-agent.py
# --------------------------------------------------------------

model = ChatOpenAI(
    model="anthropic/claude-opus-4.6",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

agent = create_agent(
    model,
    tools=[list_files, grep, read_file],
    system_prompt=(
        "Search notes with list_files, grep, read_file. Cite files. "
        "If evidence is missing, say so."
    ),
)


# --------------------------------------------------------------
# Step 2: Stream over the agent's graph and print each tool call
# --------------------------------------------------------------
# Pydantic AI: agent.iter(question) exposes the run as an async graph of
#   nodes; you check Agent.is_call_tools_node(node) to find the node that
#   executes tools, then open a nested node.stream(run.ctx) to get individual
#   FunctionToolCallEvent / FunctionToolResultEvent events out of it. This
#   requires asyncio (and nest_asyncio, since run_sync-style iteration isn't
#   offered) even though the script is otherwise synchronous.
# LangChain: create_agent builds a LangGraph graph with just two nodes,
#   "model" (the LLM call) and "tools" (the ToolNode that executes tool
#   calls). agent.stream(..., stream_mode="updates") yields one dict per
#   super-step, keyed by node name, e.g. {"model": {"messages": [AIMessage]}}
#   or {"tools": {"messages": [ToolMessage, ...]}}. No node-type checks or
#   nested event streams are needed -- the node name alone tells you whether
#   you're looking at a tool call (on the AIMessage.tool_calls list) or a
#   tool result (a ToolMessage). And since .stream() is genuinely synchronous
#   (thread-based, like .invoke() in 3-basic-agent.py), no asyncio/
#   nest_asyncio is needed here either.


def run_with_visible_steps(question: str, debug: bool = False) -> str:
    print(f"\nQ: {question}\n")
    print("--- agent steps ---")

    answer = ""
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="updates",
    ):
        for node_name, node_output in step.items():
            for message in node_output["messages"]:
                if node_name == "model":
                    for call in message.tool_calls:
                        print(f"-> {call['name']}({call['args']})")
                    if message.content:
                        answer = message.content
                elif node_name == "tools" and debug:
                    print(format_tool_result(message))

    print("--- done ---\n")
    return answer


# --------------------------------------------------------------
# Step 3: Run it
# --------------------------------------------------------------

if __name__ == "__main__":
    answer = run_with_visible_steps(
        "Why does our nightly deploy job run at 03:47 UTC specifically?",
        debug=True,
    )
    print("A:", answer)
