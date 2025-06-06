import re


def extract_json_array(text: str) -> str:
    """LLM 응답에서 유효한 JSON 배열 시작부터 자르기"""
    match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return "[]"
