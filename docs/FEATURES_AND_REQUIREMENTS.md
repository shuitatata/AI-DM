# FEATURES_AND_REQUIREMENTS.md
| 模块 | 必备功能 | 进阶 / 可选功能 |
| ---- | -------- | --------------- |
| **剧情逻辑** | · YAML 因果图<br>· JSON 状态持久化<br>· 前置条件校验 | · 多剧情包热加载<br>· 可视化编辑接口 |
| **意图识别 Agent** | · LLM 函数调用匹配 `action_id`<br>· 向量相似度回退 | · 多语言输入<br>· 本地小模型 |
| **叙事生成 Agent** | · Prompt 拼装（场景 + 后果）<br>· SSE 流式输出 | · 语气 / 情感切换<br>· TTS 朗读 |
| **游戏循环服务** | · FastAPI 路由 `/play` `/reset`<br>· 异常重试<br>· 调试日志 | · WebSocket 推送<br>· 多用户隔离 |
| **前端 Vue** | · 聊天 UI（打字机效果）<br>· 温度 / 模型选择<br>· 重开按钮 | · 场景插图<br>· Markdown 渲染 |
| **安全合规** | · 敏感词过滤<br>· Prompt 注入检测 | · OpenAI Moderation |
| **运维** | · `.env` 管理密钥<br>· Docker 一键启动 | · CI（pytest + lint）<br>· Prometheus 监控 |

