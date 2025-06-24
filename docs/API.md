# AI Dungeon Master API 文档

## API 概览

AI Dungeon Master 基于联邦式Agent架构，提供RESTful API服务。

- **基础URL**: `http://localhost:8000`
- **版本**: v2.0.0
- **架构**: 联邦式Agent (Federated Agents)

## 系统状态

### GET `/`
获取系统基本信息和可用端点。

**响应示例:**
```json
{
  "message": "AI Dungeon Master API v2.0 - 联邦式Agent架构",
  "architecture": "federated_agents",
  "docs": "/docs",
  "available_agent_endpoints": [
    "/api/agents/world-builder/form",
    "/api/agents/world-builder/process",
    "/api/agents/character-manager/form",
    "/api/agents/character-manager/process",
    "/api/game/play"
  ]
}
```

### GET `/ping`
健康检查接口。

**响应示例:**
```json
{
  "status": "ok",
  "architecture": "federated_agents"
}
```

## 会话管理 (Session Management)

### POST `/api/sessions`
创建新的游戏会话。

**请求体:**
```json
{
  "session_id": "optional-custom-id"  // 可选，不提供会自动生成UUID
}
```

**响应示例:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "游戏会话创建成功！欢迎来到AI地下城主世界。请先使用 'world-builder' Agent创建你的世界。"
}
```

**状态码:**
- `200`: 创建成功
- `400`: 会话已存在

### GET `/api/sessions/{session_id}`
获取会话状态和信息。

**路径参数:**
- `session_id`: 会话唯一标识符

**响应示例:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "world_complete": true,
  "character_complete": true,
  "ready_for_game": true,
  "world_state": {
    "name": "艾泽拉斯",
    "geography": "一个充满魔法和战争的大陆",
    // ... 其他字段
  },
  "character_state": {
    "name": "阿尔萨斯",
    "background": "洛丹伦的王子",
    // ... 其他字段
  },
  "created_at": "2025-01-27T10:30:00.000Z",
  "updated_at": "2025-01-27T10:45:00.000Z"
}
```

**状态码:**
- `200`: 成功
- `404`: 会话不存在

### DELETE `/api/sessions/{session_id}`
删除指定会话。

**路径参数:**
- `session_id`: 会话唯一标识符

**响应示例:**
```json
{
  "message": "会话删除成功"
}
```

**状态码:**
- `200`: 删除成功
- `404`: 会话不存在

## Agent 交互 (Agent Interaction)

### GET `/api/agents/{agent_type}/form`
获取指定表单Agent的动态表单定义。

**路径参数:**
- `agent_type`: Agent类型, 可选值为 `world-builder` 或 `character-manager`。

**响应示例 (`world-builder`):**
```json
{
  "fields": ["name", "geography", "history", "cultures", "magic_system"],
  "field_map": {
    "name": "世界名称",
    "geography": "地理环境",
    "history": "历史背景",
    "cultures": "文化设定",
    "magic_system": "魔法体系"
  }
}
```

### POST `/api/agents/{agent_type}/process`
使用指定的表单Agent处理用户输入，用于创建世界或角色。

**路径参数:**
- `agent_type`: Agent类型, 可选值为 `world-builder` 或 `character-manager`。

**请求体:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_input": "我想创造一个魔法世界"
}
```

**响应示例 (`world-builder`):**
```json
{
  "response": "很棒的想法！你想要创造一个魔法世界。让我们先从给这个世界起个名字开始吧。你希望这个魔法世界叫什么名字呢？",
  "is_complete": false,
  "updated_state": {
    "name": null,
    "geography": "魔法世界",
    // ... 其他字段
  }
}
```

**状态码:**
- `200`: 处理成功
- `404`: 会话不存在
- `500`: 服务器内部错误

## 游戏主循环 (Game Loop)

### POST `/api/game/play`
进行一轮游戏。当世界和角色都创建完毕后，调用此接口开始或继续游戏。

**请求体:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_input": "我走进森林，寻找神秘的符文石"
}
```

**响应示例:**
```json
{
  "inner_monologue": "玩家选择进入森林，这是一个推动剧情的好机会。我将描述一个昏暗、神秘的场景，并设置一个小的谜题或遭遇来引导他。",
  "narrative": "你拨开缠绕的藤蔓，踏入了幽暗的森林。高大的树冠遮蔽了天空，只有斑驳的光点稀疏地洒在布满苔藓的地面上。空气中弥漫着潮湿泥土和腐朽落叶的气息。不远处，你隐约看到一块布满奇异花纹的石头，它似乎在微弱地发光。",
  "is_game_over": false
}
```

**状态码:**
- `200`: 成功
- `400`: 游戏尚未就绪 (世界或角色未创建)
- `404`: 会话不存在
- `500`: 服务器内部错误

## 数据模型

### WorldState
```json
{
  "name": "string",           // 世界名称
  "geography": "string",      // 地理环境描述
  "history": "string",        // 历史背景
  "cultures": "string",       // 文化设定
  "magic_system": "string",   // 魔法体系
  "additional_info": {}       // 额外动态信息
}
```

### CharacterState
```json
{
  "name": "string",               // 角色名称
  "physical_appearance": "string", // 外貌描述
  "background": "string",        // 背景故事
  "internal_motivation": "string", // 内在动机
  "unique_traits": "string",     // 独特特征
  "additional_info": {}          // 额外动态信息
}
```

### NarrativeResponse
`POST /api/game/play` 的响应体。
```json
{
  "inner_monologue": "string", // DM的内心思考，用于调试或扩展
  "narrative": "string",       // 呈现给玩家的故事内容
  "is_game_over": "boolean"  // 游戏是否结束的标志
}
```

## 错误处理

所有API错误都使用标准HTTP状态码和JSON格式：

```json
{
  "detail": "具体的错误描述信息"
}
```

## 使用流程

1.  **创建会话**: `POST /api/sessions` -> 获取 `session_id`。
2.  **世界设定**:
    - `GET /api/agents/world-builder/form` 获取表单定义。
    - 循环调用 `POST /api/agents/world-builder/process` 直到 `is_complete` 为 `true`。
3.  **角色创建**:
    - `GET /api/agents/character-manager/form` 获取表单定义。
    - 循环调用 `POST /api/agents/character-manager/process` 直到 `is_complete` 为 `true`。
4.  **开始游戏**:
    - 检查 `GET /api/sessions/{session_id}` 中的 `ready_for_game` 是否为 `true`。
    - 调用 `POST /api/game/play` 开始游戏，并根据玩家输入持续调用。
5.  **结束游戏**: 当 `/api/game/play` 返回 `is_game_over: true` 时，游戏流程结束。

## 开发计划

- ✅ **世界构建**: `WorldBuilderAgent` & API
- ✅ **角色管理**: `CharacterManagerAgent` & API
- ✅ **核心叙事引擎**: `NarrativeGeneratorAgent` & Game Loop API
- 🚧 **前端集成**: 聊天界面、参数设置等
- 🚧 **流式输出**: 后端使用 SSE (Server-Sent Events) 提升交互体验
- 🚧 **测试覆盖**: 为新增的 API 和 Agent 编写单元和集成测试
- ❌ `StoryParserAgent` / `StateUpdaterAgent`: 已被统一的 `NarrativeGeneratorAgent` 替代，以简化架构。