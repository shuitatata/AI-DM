# Al Dungeon Master Web - API 设计文档 (v2)

**基础 URL**: `/api/v1`
**认证**: 所有需要用户隔离的接口都将通过路径中的 `session_id` 来进行会话级别的授权与识别。

---

## 1. 会话管理 (Session Management)

管理一个完整的游戏生命周期，从开始到结束。

### `POST /sessions`

* **描述**: 启动一个新的游戏会话。前端在用户点击“开始新游戏”时调用此接口。
* **请求体 (Request Body)**:
    ```json
    {
      "story_id": "string",
      "settings": {
        "model_name": "string",
        "temperature": "number"
      }
    }
    ```
* **成功响应 (201 Created)**:
    ```json
    {
      "session_id": "string",
      "initial_message": {
        "role": "assistant",
        "content": "string"
      }
    }
    ```
* **作用**: 替代了原设计中客户端自行生成 `session_id` 的模糊做法，改为由服务端统一创建和管理会话，为未来的多用户隔离打下基础 。

### `GET /sessions/{session_id}`

* **描述**: 获取指定会话的当前状态和所有历史消息。用于页面刷新或重新连接后恢复游戏场景。
* **路径参数**:
    * `session_id` (string): 会话的唯一ID。
* **成功响应 (200 OK)**:
    ```json
    {
      "session_id": "string",
      "story_id": "string",
      "settings": {
        "model_name": "string",
        "temperature": "number"
      },
      "history": [
        { "role": "assistant", "content": "string" },
        { "role": "user", "content": "string" }
      ]
    }
    ```

### `DELETE /sessions/{session_id}`

* [cite_start]**描述**: 重置或结束一个游戏会话。此接口替代了原有的 `POST /reset` ，更符合 RESTful 风格。
* **路径参数**:
    * `session_id` (string): 会话的唯一ID。
* **成功响应 (204 No Content)**:
    * 响应体为空。

---

## 2. 游戏交互 (Gameplay)

处理核心的玩家输入和游戏叙事。

### `POST /sessions/{session_id}/play`

* [cite_start]**描述**: 接收玩家的输入，并以 SSE (服务器发送事件) 流的形式返回游戏的响应 。这是核心的游戏循环接口。
* **路径参数**:
    * `session_id` (string): 会话的唯一ID。
* **请求体 (Request Body)**:
    ```json
    {
      "user_input": "string"
    }
    ```
* **响应 (Stream / `text/event-stream`)**:
    * 以 SSE 事件流的形式持续推送数据。为了支持未来的插图  和更丰富的交互，我们扩展了数据结构：
    ```text
    data: {"type": "text", "role": "assistant", "content": "你看到...", "done": false}

    data: {"type": "image", "url": "[https://example.com/scene.jpg](https://example.com/scene.jpg)", "done": false}

    data: {"type": "text", "role": "assistant", "content": "你决定做什么？", "done": true}
    ```
    * `type`: 事件类型 (`text`, `image`, `sound`, `error` 等)。
    * `role`, `content`, `done`: 与原设计保持一致 。

---

## 3. 配置与剧情 (Configuration & Stories)

提供游戏开始前所需的配置信息。

### `GET /stories`

* [cite_start]**描述**: 获取服务器上所有可玩的剧情包列表 。用于在游戏开始前让用户选择剧本。
* **成功响应 (200 OK)**:
    ```json
    [
      {
        "id": "haunted-mansion",
        "name": "诡秘庄园",
        "description": "一座废弃庄园的秘密等待着你去探索。",
        "cover_image_url": "[https://example.com/cover.jpg](https://example.com/cover.jpg)"
      }
    ]
    ```

### `GET /config`

* [cite_start]**描述**: 获取全局的游戏配置选项，例如可用的 AI 模型列表。用于前端的设置面板 。
* **成功响应 (200 OK)**:
    ```json
    {
      "available_models": [
        "gpt-4-turbo",
        "claude-3-opus",
        "gemini-1.5-pro"
      ],
      "temperature_range": {
        "min": 0.1,
        "max": 1.0
      }
    }
    ```

---

## 4. 系统状态 (System)

[cite_start]提供系统健康检查，便于运维监控 。

### `GET /health`

* **描述**: 健康检查端点。
* **成功响应 (200 OK)**:
    ```json
    {
      "status": "ok",
      "timestamp": "2025-06-22T15:03:30Z"
    }
    ```