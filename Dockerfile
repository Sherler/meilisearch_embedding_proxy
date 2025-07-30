# 使用 Python 3.13.5 Bookworm 作为基础镜像
FROM python:3.13.5-bookworm

# 代理配置参数
ARG HTTP_PROXY
ARG HTTPS_PROXY

# 设置维护者信息
LABEL maintainer="sherler <developerlmt@gmail.com>"
LABEL description="Meilisearch Embedding Proxy Server"

# 设置环境变量（包括代理）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_CACHE_DIR=/app/.uv-cache \
    HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    http_proxy=${HTTP_PROXY} \
    https_proxy=${HTTPS_PROXY}

# 配置清华大学 Debian 软件源 (DEB822 格式)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 更新软件包列表并安装必要的系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        curl \
        ca-certificates \
        && \
    rm -rf /var/lib/apt/lists/*

# 下载并安装 uv
RUN wget -qO- https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# 创建应用目录
WORKDIR /app

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 创建必要的目录并设置权限（在复制文件之前）
RUN mkdir -p /app/.uv-cache /app/logs && \
    chown -R appuser:appuser /app

# 复制构建好的 wheel 包
COPY dist/meilisearch_embedding_proxy-0.1.0-py3-none-any.whl ./

# 再次确保权限正确
RUN chown -R appuser:appuser /app

# 切换到非 root 用户进行安装
USER appuser

# 使用 uv 安装包，指定阿里云 PyPI 源
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install \
        --index-url https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        meilisearch_embedding_proxy-0.1.0-py3-none-any.whl

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 设置默认环境变量，清理构建时的代理设置
ENV HOST=0.0.0.0 \
    PORT=8000 \
    LOG_LEVEL=INFO \
    UV_CACHE_DIR=/app/.uv-cache \
    HTTP_PROXY="" \
    HTTPS_PROXY="" \
    http_proxy="" \
    https_proxy=""

# 启动命令，使用 uv run 运行应用
CMD ["uv", "run", "meilisearch_embedding_proxy"]
