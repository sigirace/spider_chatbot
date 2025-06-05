import json
from typing import Any, List

from domain.plans.step import StepInfo, StepList


def step_list_to_str(
    step_list: StepList,
    exclude_sub_step_list: bool = True,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> str:
    step_list_dumped = step_list.model_dump(exclude_none=True)

    if exclude_sub_step_list:
        step_list_dumped = [
            {k: v for k, v in item.items() if k != "sub_step_list"}
            for item in step_list_dumped
        ]

    # 계획 순서에 따라 리스트를 구성하고 스트링으로 출력
    prompt_str = json.dumps(
        [
            {f"step {idx}": step_info}
            for idx, step_info in enumerate(step_list_dumped, start=1)
        ],
        indent=indent,
        ensure_ascii=ensure_ascii,
    )
    return prompt_str


def step_info_to_str(
    step_info: StepInfo,
    exclude_sub_step_list: bool = True,
    indent: int = 2,
    ensure_ascii: bool = False,
):
    step_info_dict = step_info.model_dump(exclude_none=True)

    if exclude_sub_step_list:
        step_info_dict.pop("sub_step_list")

    prompt_str = json.dumps(step_info_dict, indent=indent, ensure_ascii=ensure_ascii)
    return prompt_str


def step_observation_to_str(
    step_list: StepList,
    current_step_index: int,
    exclude_sub_step_list: bool = True,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> str:
    """
    현재 step 이전까지의 observation들을 JSON 문자열로 반환합니다.
    """
    result = []

    for step in step_list[:current_step_index]:
        if step.observation is not None:
            try:
                result.append(step.observation.model_dump())
            except Exception:
                result.append(str(step.observation))

    return json.dumps(result, indent=indent, ensure_ascii=ensure_ascii)


def observation_check(
    observation_history_str: str, type: str, key_value_pair: List[Any]
) -> bool:
    """
    observation_history_str: JSON 문자열 (list of dict)
    key_value_pair: 확인하고 싶은 key-value 쌍, 예: ["is_auth", True]
    """
    json_observation_history = json.loads(observation_history_str)

    key, value = key_value_pair

    exists = any(
        item.get("type") == type
        and (
            (isinstance(item.get("value"), dict) and item["value"].get(key) == value)
            or (isinstance(item.get("value"), list) and key_value_pair in item["value"])
        )
        for item in json_observation_history
    )

    return exists
