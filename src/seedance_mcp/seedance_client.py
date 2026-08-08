import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()

SEEDANCE_API_KEY = os.getenv("SEEDANCE_API_KEY")
SEEDANCE_BASE_URL = os.getenv("SEEDANCE_BASE_URL")
SEEDANCE_MODEL = os.getenv("SEEDANCE_MODEL")

HEADERS = {
    "Authorization": f"Bearer {SEEDANCE_API_KEY}",
    "Content-Type": "application/json",
}


def _extract(data: dict, *paths):
    """从多层嵌套字典里安全取值，任意一层缺失都返回 None（避免报错）。"""
    for p in paths:
        node = data
        ok = True
        for key in p:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                ok = False
                break
        if ok and node is not None:
            return node
    return None


def submit_video(prompt: str, duration: int = 10,
                 resolution: str = "720p",
                 aspect_ratio: str = "16:9",
                 ) -> str:
    url = f"{SEEDANCE_BASE_URL}/videos/generations"
    payload = {
        "model": SEEDANCE_MODEL,
        "prompt": prompt,
        "quality": "speed",          # speed 快 / quality 质量好
        "with_audio": True,          # 是否生成音效
        "size": "1080P",             # 分辨率
    }
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # task_id 可能在顶层，也可能在 data.output 里，用多种路径找
    task_id = _extract(data, ["id"], ["data", "task_id"],
                       ["output", "task_id"], ["data", "output", "task_id"])
    if not task_id:
        raise RuntimeError(f"提交失败，响应里没有 task_id：{data}")
    return task_id


def wait_video(task_id: str, timeout: int = 600, interval: int = 5) -> str:
    """轮询任务直到成功，返回视频 url。

    状态机：pending → queued → in_progress → succeeded / failed
    """
    url = f"{SEEDANCE_BASE_URL}/async-result/{task_id}"
    start = time.time()

    while time.time() - start < timeout:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # 状态可能在顶层 / data / data.output，统一取
        status = (_extract(data, ["task_status"],["status"], ["data", "status"],["output", "task_status"],
                           ["data", "output", "status"]) or "").lower()
        remaining = int(timeout - (time.time() - start))
        print(f"  任务 {task_id} 状态：{status}（剩余 {remaining}s）")

        # 成功：不同渠道用 succeeded / success / completed / done / SUCCEEDED
        if status in ("succeeded", "success", "completed", "done", "finished"):
            video_url = None
            # 智谱的 video_result 是 list，要单独处理
            video_result = data.get("video_result") or []
            if isinstance(video_result, list) and video_result:
                video_url = video_result[0].get("url")
            # 兜底：再用 _extract 试别的字段路径（百炼等其他渠道）
            if not video_url:
                video_url = _extract(
                    data,
                    ["output", "video_url"], ["data", "video_url"], ["video_url"],
                    ["data", "output", "video_url"], ["output", "videos", "0", "url"],
                )
            if not video_url:
                raise RuntimeError(f"任务成功但没找到视频地址，请检查字段：{data}")
            return video_url    
        # 失败
        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"任务失败：{data}")

        time.sleep(interval)

    raise TimeoutError(f"任务 {task_id} 超过 {timeout}s 未完成")


if __name__ == "__main__":
    # 自测：生成一段视频
    prompt = "深夜雨巷，一位少女撑着透明的伞独行，镜头从远景缓慢推进到中景，雨滴在地面溅起水花，冷色调，电影感，8k"
    tid = submit_video(prompt, duration=10)
    print("已提交任务：", tid)
    url = wait_video(tid)
    print("视频已生成：", url)
