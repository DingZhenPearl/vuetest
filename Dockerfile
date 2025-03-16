FROM node:16

# 安装Python、pip和MySQL客户端工具
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    g++ \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./
RUN npm install

# 复制Python依赖
COPY requirements.txt ./
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip3 install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

EXPOSE 3000 8080

# 启动命令将在docker-compose中指定
