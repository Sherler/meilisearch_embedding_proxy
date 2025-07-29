# 快速启动指南

## 1. 设置环境变量

创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，至少设置以下必需配置：
```bash
API_KEY=your_siliconflow_api_key_here
```

## 2. 安装依赖

```bash
poetry install
```

## 3. 启动服务

```bash
# 方法1: 使用命令行工具
meilisearch_embedding_proxy

# 方法2: 直接运行Python模块
python -m meilisearch_embedding_proxy.cli

# 方法3: 使用Poetry
poetry run meilisearch_embedding_proxy
```

## 4. 测试服务

```bash
# 健康检查
curl http://localhost:8000/health

# 测试嵌入API (需要设置API_KEY环境变量)
export API_KEY=your_api_key
python test_client.py
```

## 5. 查看API文档

打开浏览器访问: http://localhost:8000/docs

## 常见问题

### Q: 启动时报错 "API_KEY environment variable is required"
A: 请确保设置了 `API_KEY` 环境变量或在 `.env` 文件中配置。

### Q: 如何更改服务端口？
A: 方法1: 设置环境变量 `PORT=8080`
   方法2: 使用命令行参数 `meilisearch_embedding_proxy --port 8080`

### Q: 如何查看详细日志？
A: 设置环境变量 `LOG_LEVEL=DEBUG` 或使用命令行参数 `--log-level debug`

### Q: 如何自定义模型？
A: 设置环境变量 `MODEL_NAME=your_model_name`

### Q: 如何调整token限制？
A: 设置环境变量 `MAX_TOKEN_LIMIT=20000`
