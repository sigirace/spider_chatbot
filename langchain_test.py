import asyncio
import json
import re
from typing import List, Dict, Any

from fastmcp import Client
from fastmcp.client import SSETransport
from mcp.types import Tool as MCPTool

from langchain_ollama import ChatOllama
from langchain_core.tools import StructuredTool


# MCP Tool → 직접 호출 가능하도록 매핑
def convert_mcp_tool(tool: MCPTool):
    async def tool_fn(params: Dict[str, Any]):
        print(f"🛠 MCP 툴 호출: {tool.name} with {params}")
        async with Client(
            transport=SSETransport(url="http://localhost:8001/sse")
        ) as client:
            result = await client.call_tool(tool.name, params)

            # DEBUG: 실제 반환값 확인
            print(f"📦 MCP 툴 원시 결과: {repr(result)}")

            # 안전하게 첫 번째 결과 추출
            if isinstance(result, list):
                value = (
                    result[0].content if hasattr(result[0], "content") else result[0]
                )
            else:
                value = result.content if hasattr(result, "content") else result

            print(f"✅ MCP 툴 결과: {value}")
            return value

    # ✅ inputSchema 기반으로 파라미터 목록 파싱
    properties = tool.inputSchema.get("properties", {})
    required = set(tool.inputSchema.get("required", []))
    parameters = [
        {
            "name": name,
            "type": props.get("type", "string"),
            "description": props.get("description", ""),
            "required": name in required,
        }
        for name, props in properties.items()
    ]

    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": parameters,
        "call": tool_fn,
    }


# MCP에서 tool 불러오기
async def get_mcp_tools():
    async with Client(
        transport=SSETransport(url="http://localhost:8001/sse")
    ) as client:
        mcp_tools: List[MCPTool] = await client.list_tools()
    return [convert_mcp_tool(tool) for tool in mcp_tools]


# system prompt 생성
def generate_system_prompt(tools: List[Dict[str, Any]]) -> str:
    tool_json = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            param["name"]: {
                                "type": param["type"],
                                "description": param["description"],
                            }
                            for param in tool["parameters"]
                        },
                        "required": [
                            param["name"]
                            for param in tool["parameters"]
                            if param.get("required", True)
                        ],
                    },
                },
            }
            for tool in tools
        ]
    }

    tools_str = json.dumps(tool_json["tools"], indent=2)
    system_prompt = (
        """
You are a helpful assistant that receives a natural language request and determines the most appropriate tool to use from the available list.

Your task is to extract the user's **intent** and all **required parameters** for the function execution. Always use the user's **exact input message** as the value for parameters that require the original input.

Respond strictly in JSON format as follows:
{
  "functionName": "function name",
  "parameters": [
    {"parameterName": "name", "parameterValue": "value"},
    ...
  ]
}

Available tools:
<TOOL LIST HERE>
        """
        f"{tools_str}"
    )
    return system_prompt


def extract_json_from_response(text: str) -> dict:
    try:
        # 가장 처음 등장하는 중괄호 블록 추출
        json_str = re.search(r"{[\s\S]+}", text).group()
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"❌ JSON 추출 실패: {e}")


# 메인 실행 로직
async def main():
    tools = await get_mcp_tools()
    system = generate_system_prompt(tools)

    llm = ChatOllama(model="gemma3", temperature=0.0)

    user_input = "올해 프리미어리그 우승팀은 맨시티가 할지 알려주고 맨유의 순위도 예측해서 알려줄래"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_input},
    ]

    print("🧠 LLM 요청:")
    for m in messages:
        print(f"{m['role'].upper()}: {m['content']}\n")

    response = await llm.ainvoke(messages)
    print("🧠 LLM 응답:")
    print(response.content)

    try:
        tool_call = extract_json_from_response(response.content)
        function_name = tool_call["functionName"]
        parameters_dict = {
            p["parameterName"]: p["parameterValue"] for p in tool_call["parameters"]
        }
    except Exception as e:
        print(f"❌ LLM 응답 파싱 실패: {e}")
        return

    # 툴 실행
    for tool in tools:
        if tool["name"] == function_name:
            result = await tool["call"](parameters_dict)
            print(f"\n✅ 최종 결과: {result}")
            break
    else:
        print(f"❌ 일치하는 툴 {function_name} 없음")


if __name__ == "__main__":
    asyncio.run(main())
