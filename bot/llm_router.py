import json
from typing import Any

import httpx

from config import Settings
from tools import (
    count_students,
    get_completion_rate,
    get_groups,
    get_items,
    get_lab_names,
    get_learners,
    get_lowest_pass_rate_lab,
    get_pass_rates,
    get_scores_histogram,
    get_timeline,
)


settings = Settings()


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_lab_names",
            "description": "List all available lab names.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get LMS items data.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task pass rates for a lab code like lab-04.",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores_histogram",
            "description": "Get score histogram for a lab code like lab-04.",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance for a lab code like lab-03.",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline for a lab code like lab-05.",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate for a lab code like lab-06.",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get all learners.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_students",
            "description": "Count enrolled students.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_lowest_pass_rate_lab",
            "description": "Find which lab has the lowest average pass rate.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


async def _call_tool(name: str, arguments: dict[str, Any]) -> Any:
    if name == "get_lab_names":
        return await get_lab_names()
    if name == "get_items":
        return await get_items()
    if name == "get_pass_rates":
        return await get_pass_rates(arguments["lab"])
    if name == "get_scores_histogram":
        return await get_scores_histogram(arguments["lab"])
    if name == "get_groups":
        return await get_groups(arguments["lab"])
    if name == "get_timeline":
        return await get_timeline(arguments["lab"])
    if name == "get_completion_rate":
        return await get_completion_rate(arguments["lab"])
    if name == "get_learners":
        return await get_learners()
    if name == "count_students":
        return await count_students()
    if name == "get_lowest_pass_rate_lab":
        return await get_lowest_pass_rate_lab()
    raise ValueError(f"Unknown tool: {name}")


async def route_natural_language(query: str) -> str:
    system_prompt = (
        "You are an LMS bot router. "
        "Choose the single best function tool for the user's request. "
        "Do not answer directly before tool use when tool data is needed. "
        "Use lab codes like lab-01, lab-02, ..., lab-07 when needed."
    )

    async with httpx.AsyncClient(timeout=40.0) as client:
        resp = await client.post(
            f"{settings.llm_api_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_api_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                "tools": TOOLS,
                "tool_choice": "auto",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    message = data["choices"][0]["message"]

    tool_calls = message.get("tool_calls", [])
    if not tool_calls:
        content = message.get("content") or "I could not route this query."
        return content

    tool_call = tool_calls[0]
    fn_name = tool_call["function"]["name"]
    raw_args = tool_call["function"].get("arguments", "{}")
    args = json.loads(raw_args)

    result = await _call_tool(fn_name, args)

    async with httpx.AsyncClient(timeout=40.0) as client:
        resp = await client.post(
            f"{settings.llm_api_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_api_model,
                "messages": [
                    {"role": "system", "content": "Answer clearly using the tool result. Be concise and factual."},
                    {"role": "user", "content": query},
                    message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": fn_name,
                        "content": json.dumps(result, ensure_ascii=False),
                    },
                ],
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]
