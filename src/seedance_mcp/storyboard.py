import json
import os
import re
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


def _extract_json(text: str) -> dict:
    """从 LLM 返回里安全提取 JSON 字典。

    LLM 可能返回：纯 JSON、带 ```json 包裹、前后有说明文字。
    这里用正则直接抓取第一个 { ... } 块，最稳。
    """
    text = text.strip()
    # 去掉可能的 ```json ... ``` 包裹
    text = re.sub(r"```(?:json)?", "", text).strip()
    # 从第一个 { 截取到最后一个 }，中间的 JSON 主体
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"LLM 返回里没找到 JSON：{text[:200]}")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败：{e}，原文：{text[:200]}")


def generate_storyboard(script: str, shot_count: int = 6) -> dict:
    """用 LLM 把剧本拆成 shot_count 个分镜。"""
    prompt = f"""
你是漫剧分镜师。请把下面的剧本拆成 {shot_count} 个分镜。

要求：
1. 每个分镜包含：镜头序号、画面描述（含人物/场景/动作）、镜头运动（推拉摇移/景别/机位）。
2. 写 Seedance 提示词时要"过度描述"：写清视觉细节、镜头运动、色调。
3. 只输出 JSON，格式如下：
{{
  "title": "短剧标题",
  "shots": [
    {{"index": 1, "prompt": "分镜1的提示词", "duration": 10}},
    {{"index": 2, "prompt": "分镜2的提示词", "duration": 10}}
  ]
}}

剧本：
{script}
"""
    res = llm.invoke(prompt).content
    storyboard = _extract_json(res)

    # 校验并规整结构，保证每个分镜都有 index/prompt/duration
    shots = storyboard.get("shots", [])
    cleaned = []
    for i, shot in enumerate(shots, start=1):
        cleaned.append({
            "index": shot.get("index", i),
            "prompt": str(shot.get("prompt", "")).strip(),
            "duration": int(shot.get("duration", 10)),
        })
    storyboard["shots"] = cleaned
    storyboard["title"] = storyboard.get("title", "未命名短剧")
    return storyboard


if __name__ == "__main__":
    script = "一名少女在雨夜捡到一只发光的小猫，从此能听见别人的心声。"
    sb = generate_storyboard(script)
    print(json.dumps(sb, ensure_ascii=False, indent=2))
