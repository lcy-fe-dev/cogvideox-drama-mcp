- # 漫剧生成 MCP 工具

  输入一段漫剧剧本，自动拆分成镜，调用智谱 CogVideoX 生成每个分镜的视频片段，返回各分镜视频下载地址。可作为 MCP 服务端接入任意支持 MCP 的 Agent（LangChain、Dify、Cline、Cherry Studio 等）。

  ## 功能

  - 输入剧本 → 自动分镜 → 逐镜生成视频
  - 支持 DeepSeek 智能分镜（未配置时自动降级为兜底拆分）
  - 视频生成基于智谱 CogVideoX（cogvideox-3）
  - 异步任务模式：提交 → 轮询 → 返回视频 URL

  ## 环境变量

  | 变量              | 必填 | 说明                                               |
  | :---------------- | :--- | :------------------------------------------------- |
  | SEEDANCE_API_KEY  | 是   | 智谱开放平台 API Key（open.bigmodel.cn）           |
  | SEEDANCE_BASE_URL | 是   | 智谱接口地址：https://open.bigmodel.cn/api/paas/v4 |
  | SEEDANCE_MODEL    | 否   | 模型名，默认 cogvideox-3                           |
  | OPENAI_API_KEY    | 否   | DeepSeek 分镜用                                    |
  | OPENAI_BASE_URL   | 否   | DeepSeek 地址：https://api.deepseek.com/v1         |

  ## 使用

  ```bash
  pip install <包名>
  ```

  配置到支持 MCP 的客户端（如 Cherry Studio / Cline）：

  ```json
  {
    "mcpServers": {
      "drama-mcp": {
        "command": "uvx",
        "args": ["<包名>"]
      }
    }
  }
  ```

  ## 工具

  - `generate_drama(script, shot_count)`：输入剧本和分镜数（默认 3），返回每个分镜的视频下载地址（JSON）。

  ## 说明

  - 每个分镜最长 15 秒，长视频需拆多个分镜。
  - 生成的视频 URL 带时效，拿到后请尽快保存。