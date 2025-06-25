# 1. 使用官方的 Python 3.11 slim 版本作为基础镜像
FROM python:3.11-slim

# 2. 设置环境变量
#    - PYTHONUNBUFFERED: 确保 Python 的输出（如 print 语句）能直接发送到终端，而不是先进入缓冲区，便于调试
#    - PYTHONDONTWRITEBYTECODE: 阻止 Python 生成 .pyc 文件
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 3. 设置工作目录
WORKDIR /app

# 4. 复制并安装依赖
#    - build context 已改为项目根目录, 因此需要更新路径
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 5. 复制应用代码和模板到工作目录
#    - 将 app 代码复制到 /app/app
#    - 将 templates 目录复制到容器的根目录 /templates
COPY backend/app ./app
COPY templates ../templates

# 6. 暴露端口
#    - 告诉 Docker 容器在运行时会监听 8000 端口
EXPOSE 8000

# 7. 定义容器启动时执行的命令
#    - 使用 uvicorn 启动 FastAPI 应用
#    - --host 0.0.0.0: 让服务可以从容器外部访问
#    - --port 8000: 服务的监听端口
#    - app.main:app: 指向 FastAPI 应用实例 (app/main.py 文件中的 app 对象)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 