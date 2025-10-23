# =================================================================
# 第一阶段: 构建器 (Builder)
# 这个阶段负责安装所有依赖、编译和准备应用
# =================================================================
FROM python:3.11-slim as builder

# 设置环境变量，避免 Python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 禁用 pip 的缓存，减小镜像体积
ENV PIP_NO_CACHE_DIR 1

# 设置工作目录
WORKDIR /app

# 1. 安装系统依赖
# 使用国内镜像源加速，并安装构建所需的工具和中文字体

# 2. 安装 Python 依赖
# 首先只复制 requirements.txt 来利用 Docker 的层缓存机制`
COPY requirements.txt .
# 使用国内 pypi 镜像源加速安装
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt

# 3. 复制所有源代码到镜像中
COPY . .

# 4. (可选但推荐) 预先处理 Chainlit 前端文件
# 如果你已经手动下载了 Chainlit 的前端文件 (例如在 dist 目录中)
# 这个命令会将其复制到 Python 包的正确位置，避免运行时下载
# 注意: 请确保你的 dist 目录结构是正确的
RUN if [ -d "/app/dist" ]; then \
      echo "Found /app/dist, copying to chainlit frontend directory..."; \
      mkdir -p /usr/local/lib/python3.11/site-packages/chainlit/frontend/ && \
      cp -r /app/dist/* /usr/local/lib/python3.11/site-packages/chainlit/frontend/dist/; \
    else \
      echo "Warning: /app/dist directory not found. Chainlit might try to download frontend at runtime."; \
    fi


# =================================================================
# 第二阶段: 最终镜像 (Final Image)
# 这个阶段只包含运行应用所必需的文件，体积更小，更安全
# =================================================================
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1

# 设置工作目录
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    procps \
    net-tools \
    iputils-ping \
    curl \
    vim \
    fonts-noto-cjk \
    fonts-wqy-zenhei

# 从构建器阶段复制你的应用代码
COPY --from=builder /app /app

# 暴露你应用实际使用的端口
EXPOSE 12000

# 启动应用的命令
# 注意: 修正了 "0.0.0.0 " 后面的多余空格
CMD ["uvicorn", "fast_api:app", "--host", "0.0.0.0", "--port", "12000"]