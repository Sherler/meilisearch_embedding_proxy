# Meilisearch Embedding Proxy

**🌐 Language / 语言选择:**
- [English](./README.md)
- [简体中文](./README_zh.md) (当前)

一个代理服务，用于连接Meilisearch嵌入器和自托管的OpenAI格式嵌入服务器。支持转发请求到SiliconFlow API并提供详细的日志记录和完整的Meilisearch集成功能。

## 功能特性

- 🚀 FastAPI框架构建的高性能代理服务
- � **Meilisearch集成**: 完整的嵌入器配置和管理功能
- �📝 使用Loguru进行结构化日志记录
- 🔧 通过环境变量进行灵活配置
- 🔌 使用OpenAI客户端进行API调用
- 📏 支持自定义token长度限制
- 🏥 内置健康检查端点
- 📚 自动生成的API文档
- 🐳 **Docker Compose**: 多服务部署就绪
- ⚡ **无缝设置**: 一键配置Meilisearch嵌入器

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd meilisearch_embedding_proxy

# 安装依赖 (使用Poetry)
poetry install

# 或者如果您希望使用pip
pip install -e .
```

## 配置

创建 `.env` 文件并配置以下环境变量：

```bash
# API配置 (必需)
API_KEY=your_siliconflow_api_key_here

# 服务器配置 (可选，带默认值)
BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME=BAAI/bge-large-zh-v1.5
MAX_TOKEN_LIMIT=10000
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
TIMEOUT=30

# Meilisearch配置 (嵌入器功能必需)
MEILISEARCH_URL=http://127.0.0.1:7750
MEILI_MASTER_KEY=your_master_key_here
MEILI_ENV=development

# 服务URL (Meilisearch嵌入器配置使用)
SERVICE_URL=http://embedding_proxy:8000
```

你可以复制 `.env.example` 文件开始：

```bash
cp .env.example .env
# 然后编辑 .env 文件填入你的配置
```

## 使用方法

### Docker Compose快速启动 (推荐)

使用Docker Compose是最简单的方式，可以同时设置嵌入代理和Meilisearch：

```bash
# 1. 克隆并配置
git clone <repository-url>
cd meilisearch_embedding_proxy
cp .env.example .env
# 编辑 .env 文件填入你的配置

# 2. 启动服务
docker compose up -d

# 3. 配置Meilisearch嵌入器 (参见Meilisearch集成部分)
```

### 命令行启动

```bash
# 使用Poetry运行 (推荐)
poetry run meilisearch_embedding_proxy

# 或者直接使用命令 (如果已安装到系统)
meilisearch_embedding_proxy

# 自定义端口
poetry run meilisearch_embedding_proxy --port 8080

# 开发模式（自动重载）
poetry run meilisearch_embedding_proxy --reload

# 查看帮助
poetry run meilisearch_embedding_proxy --help
```

### 程序化启动

```python
from meilisearch_embedding_proxy.fastapi_server import run_server

# 启动服务器
run_server(host="0.0.0.0", port=8000)
```

## API端点

### 核心嵌入服务

#### 创建嵌入 - POST /v1/embeddings

请求体：
```json
{
  "input": ["文本1", "文本2"]
}
```

响应：
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...]
    }
  ]
}
```

### Meilisearch集成

#### 配置嵌入器 - POST /v1/meilisearch/embedder

配置Meilisearch索引使用此嵌入服务：

```bash
curl -X POST "http://localhost:8000/v1/meilisearch/embedder" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "movies",
    "embedder_name": "default",
    "document_template": "{{doc.title}} {{doc.overview}}"
  }'
```

请求体：
```json
{
  "index_id": "movies",
  "embedder_name": "default", 
  "document_template": "{{doc.title}} {{doc.overview}}"
}
```

响应：
```json
{
  "success": true,
  "message": "Successfully configured embedder 'default' for index 'movies'",
  "task_uid": 123
}
```

#### 获取任务 - GET /v1/meilisearch/tasks

查看Meilisearch任务状态和历史：

```bash
curl "http://localhost:8000/v1/meilisearch/tasks"
```

#### 获取索引 - GET /v1/meilisearch/indexes

列出所有Meilisearch索引：

```bash
curl "http://localhost:8000/v1/meilisearch/indexes"
```

### 服务状态

#### 健康检查 - GET /health

```json
{
  "status": "healthy",
  "config_valid": true,
  "model": "BAAI/bge-large-zh-v1.5",
  "max_token_limit": 10000,
  "meilisearch_status": "healthy",
  "meilisearch_url": "http://127.0.0.1:7750"
}
```

#### 服务信息 - GET /

返回服务状态和配置信息。

#### API文档 - GET /docs

自动生成的交互式API文档 (Swagger UI)。

## Meilisearch集成

此服务提供与Meilisearch的无缝集成，让您轻松为语义搜索功能配置嵌入器。

### 第一步：设置服务

使用Docker Compose (推荐)：

```bash
# 启动嵌入代理和Meilisearch
docker compose up -d

# 验证服务运行状态
docker compose ps
```

Docker Compose设置包括：
- **embedding_proxy**: 嵌入服务 (端口 8000)
- **meilisearch**: Meilisearch v1.13 (端口 7750)
- **自动网络**: 服务间可相互通信

### 第二步：配置Meilisearch嵌入器

在Meilisearch中使用嵌入功能之前，您需要为索引配置嵌入器：

```bash
# 为您的索引配置嵌入器
curl -X POST "http://localhost:8000/v1/meilisearch/embedder" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "movies",
    "embedder_name": "default",
    "document_template": "{{doc.title}} {{doc.overview}}"
  }'
```

**参数说明：**
- `index_id`: 您的Meilisearch索引名称 (例如 "movies", "products")
- `embedder_name`: 嵌入器名称 (默认: "default")
- `document_template`: 定义要嵌入哪些文档字段的模板

**常用文档模板：**
```json
// 电影：嵌入标题和概述
"{{doc.title}} {{doc.overview}}"

// 产品：嵌入名称和描述  
"{{doc.name}} {{doc.description}}"

// 文章：嵌入标题和内容
"{{doc.title}} {{doc.content}}"

// 多字段自定义格式
"标题: {{doc.title}} 内容: {{doc.body}} 标签: {{doc.tags}}"
```

### 第三步：在Meilisearch中使用

配置完成后，您可以在Meilisearch操作中使用嵌入器：

**添加文档自动嵌入：**
```bash
# 文档将使用您配置的模板自动嵌入
curl -X POST "http://localhost:7750/indexes/movies/documents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_master_key" \
  -d '[
    {
      "id": 1,
      "title": "黑客帝国",
      "overview": "一个电脑黑客了解到现实的真实本质。"
    }
  ]'
```

**语义搜索：**
```bash
# 使用向量相似性搜索
curl -X POST "http://localhost:7750/indexes/movies/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_master_key" \
  -d '{
    "q": "科幻电影虚拟现实",
    "vector": {
      "embedder": "default"
    }
  }'
```

**混合搜索 (文本 + 向量)：**
```bash
# 结合关键词和语义搜索
curl -X POST "http://localhost:7750/indexes/movies/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_master_key" \
  -d '{
    "q": "黑客",
    "vector": {
      "embedder": "default"
    },
    "hybrid": {
      "semanticRatio": 0.8
    }
  }'
```

### 监控和管理

**检查配置状态：**
```bash
# 查看所有任务 (包括嵌入器配置)
curl "http://localhost:8000/v1/meilisearch/tasks"

# 查看所有索引
curl "http://localhost:8000/v1/meilisearch/indexes"

# 健康检查含Meilisearch状态
curl "http://localhost:8000/health"
```

**故障排除：**
- 检查服务日志: `docker compose logs embedding_proxy`
- 验证Meilisearch连接: `docker compose logs meilisearch`
- 测试嵌入端点: `curl -X POST "http://localhost:8000/v1/embeddings" -H "Content-Type: application/json" -d '{"input": ["测试"]}'`

返回服务状态和配置信息。

### API文档 - GET /docs

自动生成的交互式API文档（Swagger UI）。

## 测试

使用提供的测试客户端：

```bash
# 设置API密钥
export API_KEY=your_siliconflow_api_key

# 运行测试
python test_client.py
```

## 日志记录

服务使用Loguru进行结构化日志记录，包括：

- 请求和响应详情
- 错误信息和调试信息
- 性能指标
- 配置验证信息

日志级别可通过 `LOG_LEVEL` 环境变量配置：
- `CRITICAL`
- `ERROR` 
- `WARNING`
- `INFO` (默认)
- `DEBUG`
- `TRACE`

## Docker支持

### Docker Compose快速启动

```bash
# 1. 克隆并设置
git clone <repository-url>
cd meilisearch_embedding_proxy
cp .env.example .env

# 2. 在 .env 中配置您的API密钥
# 编辑 MEILI_MASTER_KEY 和 API_KEY

# 3. 启动所有服务
docker compose up -d

# 4. 配置嵌入器 (替换为您的索引名称)
curl -X POST "http://localhost:8000/v1/meilisearch/embedder" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "your_index_name",
    "embedder_name": "default",
    "document_template": "{{doc.title}} {{doc.content}}"
  }'
```

### 单独服务部署

```bash
# 构建镜像
./build.sh

# 仅运行嵌入代理
docker run -d -p 8000:8000 -e API_KEY=your_key meilisearch-embedding-proxy:latest

# 使用自定义配置运行
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your_siliconflow_key \
  -e MEILISEARCH_URL=http://your-meilisearch:7750 \
  -e MEILI_MASTER_KEY=your_master_key \
  meilisearch-embedding-proxy:latest
```

### Docker配置

Docker设置包括：
- ✅ **多服务部署**: 嵌入代理 + Meilisearch v1.13
- ✅ **自动网络**: 服务间无缝通信
- ✅ **健康检查**: 内置服务监控
- ✅ **卷持久化**: Meilisearch数据持久化
- ✅ **环境配置**: 通过 .env 文件轻松设置
- ✅ **生产就绪**: 性能和安全性优化

## 开发

```bash
# 安装开发依赖
poetry install

# 运行开发服务器
poetry run meilisearch_embedding_proxy --reload

# 运行测试
poetry run python test_local.py

# 代码格式化
poetry run black .
poetry run isort .

# 类型检查
poetry run mypy .

# 进入Poetry shell
poetry shell
```

## 项目结构

```
meilisearch_embedding_proxy/
├── src/meilisearch_embedding_proxy/
│   ├── __init__.py
│   ├── cli.py              # 命令行接口
│   ├── config.py           # 配置管理
│   └── fastapi_server.py   # FastAPI 服务器
├── tests/
│   └── test_api.py         # API 测试
├── dist/                   # Poetry 构建输出
├── pyproject.toml          # Poetry 配置
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # Docker Compose 配置
├── build.sh               # 自动化构建脚本
├── .env.example           # 环境变量示例
├── .dockerignore          # Docker 忽略文件
├── README.md              # 项目文档（英文）
├── README_zh.md           # 项目文档（中文）
├── DOCKER.md              # Docker 部署指南
├── QUICKSTART.md          # 快速开始指南
└── test_*.py              # 测试文件
```

## 贡献

1. Fork 这个仓库
2. 创建特性分支
3. 提交你的更改
4. 为新功能添加测试
5. 确保所有测试通过
6. 提交 Pull Request

## 许可证

MIT License
