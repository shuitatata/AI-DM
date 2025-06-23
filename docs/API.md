# AI Dungeon Master API 文档

## API 概览

AI Dungeon Master 基于联邦式Agent架构，提供RESTful API服务。

- **基础URL**: `http://localhost:8000`
- **版本**: v2.0.0
- **架构**: 联邦式Agent (Federated Agents)

## 系统状态

### GET `/`
获取系统基本信息

**响应示例:**
```json
{
  "message": "AI Dungeon Master API v2.0 - 联邦式Agent架构",
  "architecture": "federated_agents",
  "available_agents": [
    "WorldBuilderAgent",
    "CharacterManagerAgent (TODO)",
    "StoryParserAgent (TODO)",
    "NarrativeGeneratorAgent (TODO)",
    "StateUpdaterAgent (TODO)"
  ]
}
```

### GET `/ping`
健康检查接口

**响应示例:**
```json
{
  "status": "ok",
  "architecture": "federated_agents"
}
```

## 会话管理

### POST `/api/sessions`
创建新的游戏会话

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
  "message": "游戏会话创建成功！欢迎来到AI地下城主世界。让我们先创建你的世界设定吧！"
}
```

**状态码:**
- `200`: 创建成功
- `400`: 会话已存在

### GET `/api/sessions/{session_id}`
获取会话状态和信息

**路径参数:**
- `session_id`: 会话唯一标识符

**响应示例:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "world_complete": false,
  "character_complete": false,
  "ready_for_game": false,
  "world_state": {
    "name": null,
    "geography": null,
    "history": null,
    "cultures": null,
    "magic_system": null,
    "additional_info": {}
  },
  "character_state": {
    "name": null,
    "physical_appearance": null,
    "background": null,
    "internal_motivation": null,
    "unique_traits": null,
    "additional_info": {}
  },
  "created_at": "2025-01-27T10:30:00.000000",
  "updated_at": "2025-01-27T10:30:00.000000"
}
```

**状态码:**
- `200`: 成功
- `404`: 会话不存在

### DELETE `/api/sessions/{session_id}`
删除指定会话

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

## Agent 交互

### POST `/api/world-form`
世界设定表单处理 (WorldBuilderAgent)

**请求体:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_input": "我想创造一个魔法世界"
}
```

**响应示例:**
```json
{
  "response": "很棒的想法！你想要创造一个魔法世界。让我们先从给这个世界起个名字开始吧。你希望这个魔法世界叫什么名字呢？",
  "is_world_complete": false,
  "world_state": {
    "name": null,
    "geography": "魔法世界",
    "history": null,
    "cultures": null,
    "magic_system": null,
    "additional_info": {}
  }
}
```

**状态码:**
- `200`: 处理成功
- `404`: 会话不存在
- `500`: 处理失败

### GET `/api/agents/capabilities`
获取所有Agent的能力信息

**响应示例:**
```json
{
  "world_builder": [
    "world_setting_collection",
    "world_data_validation", 
    "world_state_management"
  ],
  "template_manager": {
    "available_templates": [
      "world_form",
      "character_form",
      "story_opener",
      "narrative_generator"
    ]
  }
}
```

## 调试接口

### GET `/api/debug/sessions`
获取所有会话列表（仅用于开发调试）

**响应示例:**
```json
{
  "sessions": [
    "123e4567-e89b-12d3-a456-426614174000",
    "456e7890-e89b-12d3-a456-426614174001"
  ],
  "total": 2
}
```

## 数据模型

### WorldState
```json
{
  "name": "string",           // 世界名称
  "geography": "string",      // 地理环境描述
  "history": "string",        // 历史背景
  "cultures": "string",       // 文化设定
  "magic_system": "string",   // 魔法体系
  "additional_info": {}       // 额外信息
}
```

### CharacterState
```json
{
  "name": "string",              // 角色名称
  "physical_appearance": "string", // 外貌描述
  "background": "string",        // 背景故事
  "internal_motivation": "string", // 内在动机
  "unique_traits": "string",     // 独特特征
  "additional_info": {}          // 额外信息
}
```

### GameSession
```json
{
  "session_id": "string",
  "world_state": "WorldState",
  "character_state": "CharacterState", 
  "current_scene": "string",
  "game_history": [
    {
      "role": "string",
      "content": "string",
      "timestamp": "string"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 错误处理

所有API错误都使用标准HTTP状态码和JSON格式：

```json
{
  "detail": "错误描述信息"
}
```

常见状态码：
- `400`: 请求参数错误
- `404`: 资源不存在  
- `500`: 服务器内部错误

## 使用流程

1. **创建会话**: `POST /api/sessions`
2. **世界设定**: 通过 `POST /api/world-form` 逐步收集世界信息
3. **角色创建**: 通过角色管理Agent收集角色信息 (TODO)
4. **开始游戏**: 当世界和角色都完整后，开始游戏循环 (TODO)

## 开发计划

- ✅ WorldBuilderAgent - 世界设定收集
- 🚧 CharacterManagerAgent - 角色创建管理
- 🚧 NarrativeGeneratorAgent - 动态叙事生成
- 🚧 StoryParserAgent - 玩家输入解析
- 🚧 StateUpdaterAgent - 游戏状态更新
- 🚧 SSE流式输出 - 实时游戏体验