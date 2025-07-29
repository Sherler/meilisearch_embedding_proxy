# Docker 部署指南

## 构建流程

本项目使用两阶段构建流程：
1. 使用 Poetry 构建 Python wheel 包
2. 在 Docker 容器中使用 uv 安装预构建的包

### 快速构建

使用提供的构建脚本：

```bash
# 使用默认代理配置构建
./build.sh

# 重新构建（不使用缓存）
./build.sh --no-cache

# 使用自定义代理构建
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
./build.sh
```

### 代理配置

构建脚本会自动检测本机IP地址，并使用 `http://{本机IP}:7891` 作为代理地址。您可以通过以下方式配置：

1. **自动检测IP（推荐）**：
   ```bash
   # 脚本会自动检测本机IP并设置代理
   ./build.sh
   ```

2. **使用辅助脚本设置环境变量**：
   ```bash
   # 运行辅助脚本设置代理环境变量
   source ./set-proxy-env.sh
   
   # 然后构建
   ./build.sh
   # 或使用 docker-compose
   docker-compose up --build
   ```

3. **手动指定代理**：
   ```bash
   export HTTP_PROXY=http://your-proxy-ip:port
   export HTTPS_PROXY=http://your-proxy-ip:port
   ./build.sh
   ```

4. **直接修改 docker-compose.yml**：
   ```yaml
   build:
     args:
       - HTTP_PROXY=http://your-proxy-ip:port
       - HTTPS_PROXY=http://your-proxy-ip:port
   ```

#### IP检测机制

构建脚本使用以下方法依次尝试获取本机IP：
1. `ip route get 8.8.8.8` - 获取到公网的路由IP
2. `hostname -I` - 获取主机名对应的IP
3. `ifconfig` - 解析网络接口配置
4. 备选方案：`127.0.0.1`

### 手动构建

```bash
# 1. 使用 Poetry 构建 Python 包
poetry build

# 2. 构建 Docker 镜像
docker build -t meilisearch-embedding-proxy .
```

## 使用 Docker 运行 Meilisearch Embedding Proxy

### 方法一：使用 Docker Compose（推荐）

1. **创建环境变量文件**
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件并设置您的配置：
   ```bash
   # 必需配置
   API_KEY=your_siliconflow_api_key_here
   
   # 可选配置（可以使用默认值）
   BASE_URL=https://api.siliconflow.cn/v1
   MODEL_NAME=BAAI/bge-large-zh-v1.5
   MAX_TOKEN_LIMIT=10000
   PORT=8000
   LOG_LEVEL=INFO
   ```

2. **构建并启动服务**
   ```bash
   docker-compose up --build -d
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f
   ```

4. **停止服务**
   ```bash
   docker-compose down
   ```

### 方法二：直接使用 Docker

1. **构建镜像**
   ```bash
   # 使用构建脚本（推荐）
   ./build.sh
   
   # 或手动构建
   poetry build
   docker build -t meilisearch-embedding-proxy .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name meilisearch-embedding-proxy \
     -p 8000:8000 \
     -e API_KEY=your_siliconflow_api_key_here \
     -e LOG_LEVEL=INFO \
     meilisearch-embedding-proxy
   ```

3. **查看日志**
   ```bash
   docker logs -f meilisearch-embedding-proxy
   ```

4. **停止容器**
   ```bash
   docker stop meilisearch-embedding-proxy
   docker rm meilisearch-embedding-proxy
   ```

### 验证部署

访问以下端点验证服务是否正常运行：

- **健康检查**: http://localhost:8000/health
- **API 文档**: http://localhost:8000/docs
- **服务信息**: http://localhost:8000/

### 测试 API

```bash
curl -X POST "http://localhost:8000/v1/embeddings" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_api_key" \
     -d '{
       "input": ["Hello world", "测试文本"]
     }'
```

### 环境变量配置

| 变量名 | 必需 | 默认值 | 描述 |
|--------|------|--------|------|
| API_KEY | ✅ | - | SiliconFlow API 密钥 |
| BASE_URL | ❌ | https://api.siliconflow.cn/v1 | API 基础 URL |
| MODEL_NAME | ❌ | BAAI/bge-large-zh-v1.5 | 模型名称 |
| MAX_TOKEN_LIMIT | ❌ | 10000 | 最大 token 限制 |
| EMBEDDING_DIMENSIONS | ❌ | 1024 | 嵌入维度 |
| HOST | ❌ | 0.0.0.0 | 服务器主机 |
| PORT | ❌ | 8000 | 服务器端口 |
| LOG_LEVEL | ❌ | INFO | 日志级别 |
| TIMEOUT | ❌ | 30 | 请求超时时间（秒） |

### 故障排除

1. **容器无法启动**
   - 检查 API_KEY 是否正确设置
   - 查看容器日志：`docker-compose logs`

2. **API 调用失败**
   - 确认 API 密钥有效
   - 检查网络连接
   - 查看服务日志

3. **健康检查失败**
   - 确认容器内部服务正常启动
   - 检查端口映射是否正确

### 技术特性

- **基础镜像**: debian:bookworm-slim
- **软件源**: 配置为清华大学镜像源（加速国内访问）
- **Python 包管理**: 使用 uv（快速的 Python 包管理器）
- **PyPI 源**: 阿里云镜像源（加速包下载）
- **构建方式**: Poetry build + uv install（预构建 wheel 包）
- **安全性**: 非 root 用户运行
- **健康检查**: 内置健康检查端点

### 性能优化

1. **资源限制**
   ```yaml
   # 在 docker-compose.yml 中添加
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '0.5'
   ```

2. **多副本部署**
   ```yaml
   # 在 docker-compose.yml 中添加
   deploy:
     replicas: 3
   ```

### 安全注意事项

1. **不要在 Dockerfile 中硬编码 API 密钥**
2. **使用 secrets 管理敏感信息**
3. **定期更新基础镜像**
4. **启用容器安全扫描**
