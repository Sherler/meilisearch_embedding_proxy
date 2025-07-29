#!/bin/bash

# 构建脚本：Poetry build + Docker build
# 
# 使用方法：
#   ./build.sh
#   ./build.sh --no-cache

set -e

echo "🚀 开始构建 Meilisearch Embedding Proxy..."

# 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf dist/
rm -rf build/

# 使用 Poetry 构建包
echo "📦 使用 Poetry 构建 Python 包..."
poetry build

# 检查构建结果
if [ ! -f "dist/meilisearch_embedding_proxy-0.1.0-py3-none-any.whl" ]; then
    echo "❌ Poetry 构建失败：找不到 wheel 文件"
    exit 1
fi

echo "✅ Poetry 构建成功"
ls -la dist/

# 构建 Docker 镜像
echo "🐳 构建 Docker 镜像..."

# 检查是否传入 --no-cache 参数
DOCKER_ARGS=""
if [ "$1" = "--no-cache" ]; then
    DOCKER_ARGS="--no-cache"
    echo "🔄 使用 --no-cache 构建"
fi

# 设置代理配置（优先使用环境变量，否则使用默认值）
# 获取本机IP地址（优先获取内网IP）
get_local_ip() {
    # 尝试获取内网IP（非127.0.0.1）
    local ip=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $7; exit}' 2>/dev/null)
    if [ -z "$ip" ] || [ "$ip" = "127.0.0.1" ]; then
        # 如果上面的方法失败，尝试其他方法
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
    if [ -z "$ip" ] || [ "$ip" = "127.0.0.1" ]; then
        # 最后备选方案
        ip=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)
    fi
    if [ -z "$ip" ]; then
        # 如果都失败了，使用127.0.0.1作为备选
        ip="127.0.0.1"
    fi
    echo "$ip"
}

LOCAL_IP=$(get_local_ip)
DEFAULT_PROXY="http://${LOCAL_IP}:7891"

HTTP_PROXY_ARG=${HTTP_PROXY:-${http_proxy:-$DEFAULT_PROXY}}
HTTPS_PROXY_ARG=${HTTPS_PROXY:-${https_proxy:-$DEFAULT_PROXY}}

PROXY_ARGS="--build-arg HTTP_PROXY=${HTTP_PROXY_ARG} --build-arg HTTPS_PROXY=${HTTPS_PROXY_ARG}"
echo "🌐 使用代理配置:"
echo "   本机IP: ${LOCAL_IP}"
echo "   HTTP_PROXY: ${HTTP_PROXY_ARG}"
echo "   HTTPS_PROXY: ${HTTPS_PROXY_ARG}"

docker build $DOCKER_ARGS $PROXY_ARGS -t meilisearch-embedding-proxy:latest . 

if [ $? -eq 0 ]; then
    echo "✅ Docker 镜像构建成功"
    echo ""
    echo "📋 构建信息："
    echo "   镜像名称: meilisearch-embedding-proxy:latest"
    echo "   包文件: dist/meilisearch_embedding_proxy-0.1.0-py3-none-any.whl"
    echo ""
    echo "🚀 运行示例："
    echo "   docker run -d -p 8000:8000 -e API_KEY=your_key meilisearch-embedding-proxy:latest"
    echo ""
    echo "📚 或使用 docker-compose："
    echo "   docker-compose up -d"
else
    echo "❌ Docker 镜像构建失败"
    exit 1
fi
