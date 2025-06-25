---
description: 
globs: 
alwaysApply: true
---
# IMPLEMENTATION_GUIDE.md
## 1. 目录结构
```
aidm/
├─ backend/
│ ├─ app/
│ │ ├─ main.py              # FastAPI 应用入口
│ │ ├─ agents/              # 联邦式 Agent 模块
│ │ │ ├─ world_builder.py   # 世界构建 Agent
│ │ │ ├─ character_manager.py # 角色管理 Agent  
│ │ │ ├─ story_parser.py    # 剧情解析 Agent
│ │ │ ├─ narrative_generator.py # 叙事生成 Agent
│ │ │ └─ state_updater.py   # 状态更新 Agent
│ │ ├─ core/                # 核心基础设施
│ │ │ ├─ chain_builder.py   # Chain 构建器
│ │ │ ├─ template_manager.py # 模板管理器
│ │ │ ├─ context_manager.py # 上下文管理器
│ │ │ └─ federation.py      # Agent 联邦协调器
│ │ ├─ models/              # 数据模型
│ │ │ ├─ game_state.py      # 游戏状态模型
│ │ │ ├─ character_state.py # 角色状态模型
│ │ │ └─ world_state.py     # 世界状态模型
│ │ ├─ services/            # 业务服务层
│ │ │ ├─ game_engine.py     # 游戏引擎服务
│ │ │ └─ session_manager.py # 会话管理服务
│ │ └─ utils/               # 工具函数
│ ├─ templates/             # Prompt 模板库
│ │ ├─ agents/              # 各 Agent 专用模板
│ │ └─ common/              # 通用模板
│ ├─ tests/                 # 测试代码
│ └─ requirements.txt
├─ frontend/
│ ├─ src/
│ │ ├─ components/          # Vue 组件
│ │ ├─ services/            # API 服务
│ │ └─ stores/              # 状态管理
│ └─ vite.config.ts
├─ docker-compose.yml
└─ .env.example
```

## 2. 开发里程碑
| 周次 | 核心任务 | 交付物 |
| --- | -------- | ------ |
| Week 1 | **基础设施搭建** | · FastAPI + Vue3 基础框架<br>· Chain Builder 核心实现<br>· Template Manager 系统 |
| Week 2 | **Agent 联邦框架** | · Federation 协调器<br>· 基础 Agent 抽象类<br>· Context Manager 实现 |
| Week 3 | **世界与角色 Agent** | · WorldBuilder Agent<br>· CharacterManager Agent<br>· 对应的 Form 系统 |
| Week 4 | **剧情引擎 Agent** | · StoryParser Agent<br>· NarrativeGenerator Agent<br>· StateUpdater Agent |
| Week 5 | **前端集成优化** | · 聊天界面完善<br>· SSE 流式输出<br>· 参数配置面板 |
| Week 6 | **测试与部署** | · 单元测试覆盖<br>· Docker 容器化<br>· CI/CD 流水线 |

## 3. 核心技术栈
- **后端框架**：Python 3.11 + FastAPI + Pydantic V2
- **前端框架**：Vue 3 + TypeScript + Vite + Pinia
- **AI 集成**：LangChain + OpenAI API / 本地模型
- **开发工具**：Conda 环境管理 + Black + Ruff + Mypy
- **测试框架**：Pytest + Vitest + 端到端测试
- **容器化**：Docker + Docker Compose
- **代码规范**：Conventional Commits + Pre-commit hooks

## 4. Agent 接口设计
```python
# Agent 基类定义
class BaseAgent(ABC):
    def __init__(self, chain_builder: ChainBuilder, template_manager: TemplateManager):
        self.chain = None
        self.template_manager = template_manager
    
    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        """处理输入并返回结果"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """返回 Agent 能力列表"""
        pass

# 联邦协调器接口
class AgentFederation:
    async def coordinate_agents(self, request: GameRequest) -> GameResponse:
        """协调多个 Agent 协作处理请求"""
        pass
```

## 5. API 契约
```http
# 游戏主循环
POST /api/game/play
Body: { 
    "session_id": str, 
    "user_input": str,
    "context": dict 
}
Response: SSE Stream

# 状态管理
GET /api/game/state/{session_id}
POST /api/game/reset/{session_id}

# Agent 管理
GET /api/agents/capabilities
POST /api/agents/{agent_type}/process
```

## 6. 开发与部署
```bash
# 环境搭建
conda create -n aidm python=3.11
conda activate aidm
pip install -r backend/requirements.txt

# 开发模式
# 后端开发服务器
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 前端开发服务器  
cd frontend && npm run dev

# 生产部署
docker-compose up --build -d

# 测试执行
pytest backend/tests/
npm run test --prefix frontend
```

## 7. 核心设计原则
- **单一职责**：每个 Agent 专注单一功能领域
- **松耦合**：Agent 间通过标准接口通信
- **可测试性**：所有组件支持单元测试和集成测试
- **可扩展性**：新增 Agent 不影响现有功能
- **性能优化**：异步处理 + 智能缓存策略
