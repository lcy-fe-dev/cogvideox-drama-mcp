import json
import os
from dotenv import load_dotenv
load_dotenv()  # 本地开发：读 .env；魔搭托管时由环境变量注入，不影响

from mcp.server.fastmcp import FastMCP

# 包内相对导入（发布到 PyPI 必须用 . 开头）
from .seedance_client import submit_video, wait_video

# 创建一个 MCP 服务端
mcp = FastMCP("Seedance 漫剧生成")


def _fallback_storyboard(script: str, shot_count: int) -> list:
    """DeepSeek 不可用时的兜底分镜：直接把剧本按句号拆成若干分镜。

    保证即使没配 DeepSeek，也能让工具跑起来（虽然分镜没那么智能）。
    """
    parts = [p.strip() for p in script.replace("\n", "").split("。") if p.strip()]
    shots = []
    for i, p in enumerate(parts[:shot_count], start=1):
        shots.append({"index": i, "prompt": f"{p}，电影感，8k", "duration": 10})
    if not shots:
        shots = [{"index": 1, "prompt": f"{script}，电影感，8k", "duration": 10}]
    return shots


@mcp.tool()
def generate_drama(script: str, shot_count: int = 3) -> str:
    """根据漫剧剧本生成分镜视频。

    Args:
        script: 漫剧剧本（一段文字）。
        shot_count: 要拆成几个分镜，默认 6 个。
    Returns:
        JSON 字符串，包含每个分镜的视频下载地址。
    """
    # 1. 自动分镜（优先用 DeepSeek，失败则用兜底拆分）
    try:
        from .storyboard import generate_storyboard
        storyboard = generate_storyboard(script, shot_count)
        title = storyboard.get("title", "未命名短剧")
        shots = storyboard.get("shots", [])
    except Exception as e:
        print(f"DeepSeek 分镜失败，使用兜底分镜：{e}")
        title = "未命名短剧"
        shots = _fallback_storyboard(script, shot_count)

    # 2. 逐个分镜生成视频（单个失败不中断，记录到该分镜的 error）
    results = []
    for shot in shots:
        item = {"index": shot.get("index", len(results) + 1)}
        try:
            print(f"正在生成分镜 {item['index']} ...")
            tid = submit_video(shot["prompt"], duration=5)
            video_url = wait_video(tid)
            item["video_url"] = video_url
            print(f"  分镜 {item['index']} 完成：{video_url}")
        except Exception as e:
            item["error"] = str(e)
            print(f"  分镜 {item['index']} 失败：{e}")
        results.append(item)

    # 3. 汇总返回
    return json.dumps({
        "title": title,
        "shots": results,
    }, ensure_ascii=False)


if __name__ == "__main__":
    # 以 stdio 方式运行 MCP 服务端
    mcp.run(transport="stdio")
