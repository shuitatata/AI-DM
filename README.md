# AI Dungeon Master

## 架构优势
- **专业化分工**：每个 Agent 专注单一职责，提高推理质量
- **可扩展性**：新增 Agent 类型无需修改现有代码
- **状态一致性**：统一的状态模型保证游戏逻辑正确性
- **开发效率**：模板化和构建器模式减少重复代码

---

## 开发与部署

### 1. 本地开发

**环境要求**:
- Conda (或 venv)
- Node.js >= 18.0

**后端启动**:
```bash
# 1. 创建并激活 Conda 环境
conda create -n aidm python=3.11
conda activate aidm

# 2. 安装 Python 依赖
pip install -r backend/requirements.txt

# 3. 设置环境变量
#    将 .env.example 复制为 .env，并填入你的 GOOGLE_API_KEY
cp .env.example .env

# 4. 启动 FastAPI 开发服务器
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端启动**:
```bash
# 进入前端目录
cd frontend

# 安装 Node.js 依赖
npm install

# 启动 Vite 开发服务器
npm run dev
```

### 2. Docker 部署 (推荐)

本项目已完全容器化，推荐使用 Docker Compose 进行一键部署。

**环境要求**:
- Docker
- Docker Compose

**部署步骤**:

1.  **配置环境变量**:
    在项目根目录，将 `.env.example` 文件复制一份并重命名为 `.env`。然后编辑 `.env` 文件，填入你的 `API_KEY`。

    ```bash
    cp .env.example .env
    ```

2.  **构建并启动容器**:
    在项目根目录运行以下命令：

    ```bash
    docker-compose up --build
    ```
    Docker Compose 将会自动构建前端和后端的镜像，并启动所有服务。

3.  **访问应用**:
    - **前端应用**: [http://localhost:5173](http://localhost:5173)
    - **后端 API 文档**: [http://localhost:8000/docs](http://localhost:8000/docs)
