# 漫剧生成 MCP 工具

基于 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 的漫剧视频生成工具。输入一段剧本，自动拆分成镜头，调用视频大模型逐个生成分镜视频片段，返回每个分镜的视频下载地址。

## 功能特性

- 🎬 剧本 → 自动分镜 → 逐镜生成视频（全自动流水线）
- 🤖 DeepSeek 智能分镜（未配置时自动降级为兜底拆分）
- 🎥 视频生成基于智谱 CogVideoX（`cogvideox-3`）
- 🔧 视频模型与分镜 LLM **均可自由替换**（换 Key、换地址、换模型名即可，代码零改动）
- ⚡ 异步任务模式：提交 → 轮询 → 返回视频 URL

## 快速开始

### 1. 安装

```bash
pip install uv        # 客户端需先装 uv（若已有可跳过）
pip install cogvideox-drama-mcp
```

### 2. 配置环境变量

> 以下环境变量按「智谱 CogVideoX 视频生成 + DeepSeek 智能分镜」的默认方案配置。 本工具的视频模型与分镜模型均为**可替换设计**：替换对应的 API Key、Base URL 与模型名，即可切换到其他视频生成或 LLM 服务，代码无需改动。 

| 变量 | 作用 | 当前示例 | 可替换为 |
| :--- | :--- | :--- | :--- |
| `SEEDANCE_API_KEY` | 视频模型鉴权 | 智谱 API Key | 其他服务商的 Key |
| `SEEDANCE_BASE_URL` | 视频服务地址 | `https://open.bigmodel.cn/api/paas/v4` | 对应服务商地址 |
| `SEEDANCE_MODEL` | 视频模型名 | `cogvideox-3` | 其他模型名 |
| `OPENAI_API_KEY` | 分镜 LLM 鉴权 | DeepSeek Key | 任意 OpenAI 兼容 LLM |
| `OPENAI_BASE_URL` | 分镜 LLM 地址 | `https://api.deepseek.com/v1` | 对应服务地址 |

### 3. 接入 MCP 客户端

以 Cherry Studio / Cline / Cursor 为例：

```json
{
  "mcpServers": {
    "cogvideox-drama": {
      "command": "uvx",
      "args": ["cogvideox-drama-mcp"]
    }
  }
}
```

## 工具说明

### generate_drama(script, shot_count)

| 参数         | 类型   | 必填 | 说明                 |
| :----------- | :----- | :--- | :------------------- |
| `script`     | string | 是   | 漫剧剧本（一段文字） |
| `shot_count` | int    | 否   | 拆分镜头数，默认 3   |

**示例**：

```
输入剧本：一名少女在雨夜捡到一只发光的小猫，从此能听见别人的心声。

返回：
{
  "title": "心声之猫",
  "shots": [
    {"index": 1, "video_url": "https://.../shot1.mp4"},
    {"index": 2, "video_url": "https://.../shot2.mp4"},
    {"index": 3, "video_url": "https://.../shot3.mp4"}
  ]
}
```

## 注意事项

- 单个分镜视频最长约 15 秒，更长的剧情需拆多个分镜
- 生成的视频 URL 有时效，请及时保存
- 视频生成耗时约 1-5 分钟（异步轮询），请耐心等待
- API Key 为调用者私有配置，请勿提交到公共仓库

## 许可

MIT