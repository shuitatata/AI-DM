# --- 阶段 1: 构建阶段 ---
# 使用一个包含完整 Node.js 环境的镜像来构建项目
FROM node:20-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装项目依赖
RUN npm install

# 复制所有剩余的前端代码
COPY . .

# 执行构建命令，生成静态文件到 /app/dist 目录
RUN npm run build


# --- 阶段 2: 生产阶段 ---
# 使用一个非常轻量级的 Nginx 镜像作为最终的生产环境
FROM nginx:stable-alpine

# 将构建阶段生成的静态文件复制到 Nginx 的 web 服务器根目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义的 Nginx 配置文件
# 这个文件将确保 Vue Router 在刷新页面时能够正常工作
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 Nginx 的默认端口
EXPOSE 80

# Nginx 镜像会自动处理启动命令，所以我们不需要再写 CMD 