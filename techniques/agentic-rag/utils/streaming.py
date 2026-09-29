from typing import Any

from langchain_core.messages import ToolMessage


def preview(content: Any) -> str:
    if isinstance(content, list):
        lines = "\n      ".join(str(item) for item in content)
        return f"{len(content)} results\n      {lines}" if content else "0 results"

    return str(content).splitlines()[0][:120]


# ----------------------------------------------------------------------------
# ORIGINAL PYDANTIC AI IMPLEMENTATION (kept for comparison, not executed)
# ----------------------------------------------------------------------------
#
# from pydantic_ai.messages import FunctionToolResultEvent
#
# def format_tool_result(
#     event: FunctionToolResultEvent,
#     tool_names: dict[str, str],
# ) -> str:
#     tool_name = tool_names.get(event.tool_call_id, event.result.tool_name)
#     return f"   <- {tool_name}: {preview(event.result.content)}"
#
# ----------------------------------------------------------------------------

# Pydantic AI: the tool result arrives as a FunctionToolResultEvent, whose
#   .result.tool_name is sometimes missing, so the caller has to track a
#   tool_call_id -> tool_name map built from the earlier FunctionToolCallEvent
#   just to label the result correctly.
# LangChain: a tool result is a ToolMessage produced by the prebuilt ToolNode,
#   and it already carries .name (the tool that produced it), so no separate
#   id -> name tracking dict is needed here.


def format_tool_result(message: ToolMessage) -> str:
    return f"   <- {message.name}: {preview(message.content)}"
