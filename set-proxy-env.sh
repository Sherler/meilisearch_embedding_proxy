#!/bin/bash

# 获取本机IP并设置环境变量的脚本
# 使用方法：source ./set-proxy-env.sh

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

echo "🌐 检测到本机IP: $LOCAL_IP"
echo "📝 设置代理环境变量..."

export PROXY_HOST="$LOCAL_IP"
export HTTP_PROXY="http://${LOCAL_IP}:7891"
export HTTPS_PROXY="http://${LOCAL_IP}:7891"
export http_proxy="http://${LOCAL_IP}:7891"
export https_proxy="http://${LOCAL_IP}:7891"

echo "✅ 代理环境变量已设置:"
echo "   PROXY_HOST=$PROXY_HOST"
echo "   HTTP_PROXY=$HTTP_PROXY"
echo "   HTTPS_PROXY=$HTTPS_PROXY"
echo ""
echo "🚀 现在可以运行:"
echo "   ./build.sh"
echo "   或"
echo "   docker-compose up --build"
