# Meilisearch Embedding Proxy

**🌐 Language / 语言选择:**
- [English](./README.md) (Current)
- [简体中文](./README_zh.md)

A proxy service designed to connect Meilisearch embedders with self-hosted OpenAI-format embedding servers. Supports forwarding requests to SiliconFlow API with detailed logging and provides comprehensive Meilisearch integration.

## Features

- 🚀 High-performance proxy service built with FastAPI
- 🔍 **Meilisearch Integration**: Complete embedder configuration and management
- 📝 Structured logging with Loguru
- 🔧 Flexible configuration via environment variables
- 🔌 API calls using OpenAI client
- 📏 Customizable token length limits
- 🏥 Built-in health check endpoints
- 📚 Auto-generated API documentation
- 🐳 **Docker Compose**: Multi-service deployment ready
- ⚡ **Seamless Setup**: One-command configuration for Meilisearch embedders

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd meilisearch_embedding_proxy

# Install dependencies (using Poetry)
poetry install

# Or if you prefer pip
pip install -e .
```

## Configuration

Create a `.env` file and configure the following environment variables:

```bash
# API Configuration (Required)
API_KEY=your_siliconflow_api_key_here

# Server Configuration (Optional with defaults)
BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
EMBEDDING_DIMENSIONS=1024
MAX_TOKEN_LIMIT=10000
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
TIMEOUT=30

# Meilisearch Configuration (Required for embedder features)
MEILISEARCH_URL=http://127.0.0.1:7750
MEILI_MASTER_KEY=your_master_key_here

# Service URL (Used by Meilisearch embedder configuration)
SERVICE_URL=http://embedding_proxy:8000
```

You can copy the `.env.example` file to get started:

```bash
cp .env.example .env
# Then edit .env file with your configuration
```

## Usage

### Quick Start with Docker Compose (Recommended)

The easiest way to get started is using Docker Compose, which sets up both the embedding proxy and Meilisearch:

```bash
# 1. Clone and configure
git clone <repository-url>
cd meilisearch_embedding_proxy
cp .env.example .env
# Edit .env with your configuration

# 2. Start services
docker compose up -d

# 3. Configure Meilisearch embedder (see Meilisearch Integration section)
```

### Command Line

```bash
# Run with Poetry (recommended)
poetry run meilisearch_embedding_proxy

# Or run directly (if installed to system)
meilisearch_embedding_proxy

# Custom port
poetry run meilisearch_embedding_proxy --port 8080

# Development mode (auto-reload)
poetry run meilisearch_embedding_proxy --reload

# Show help
poetry run meilisearch_embedding_proxy --help
```

### Programmatic Usage

```python
from meilisearch_embedding_proxy.fastapi_server import run_server

# Start the server
run_server(host="0.0.0.0", port=8000)
```

## API Endpoints

### Core Embedding Service

#### Create Embeddings - POST /v1/embeddings

Request body:
```json
{
  "input": ["text1", "text2"]
}
```

Response:
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...]
    }
  ]
}
```

### Meilisearch Integration

#### Configure Embedder - POST /v1/meilisearch/embedder

Configure a Meilisearch index to use this embedding service:

```bash
curl -X POST "http://localhost:8000/v1/meilisearch/embedder" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "movies",
    "embedder_name": "default",
    "document_template": "{{doc.title}} {{doc.overview}}"
  }'
```

Request body:
```json
{
  "index_id": "movies",
  "embedder_name": "default", 
  "document_template": "{{doc.title}} {{doc.overview}}"
}
```

Response:
```json
{
  "success": true,
  "message": "Successfully configured embedder 'default' for index 'movies'",
  "task_uid": 123
}
```

#### Get Tasks - GET /v1/meilisearch/tasks

View Meilisearch task status and history:

```bash
curl "http://localhost:8000/v1/meilisearch/tasks"
```

#### Get Indexes - GET /v1/meilisearch/indexes

List all Meilisearch indexes:

```bash
curl "http://localhost:8000/v1/meilisearch/indexes"
```

### Service Status

#### Health Check - GET /health

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

#### Service Info - GET /

Returns service status and configuration information.

#### API Documentation - GET /docs

Auto-generated interactive API documentation (Swagger UI).

## Meilisearch Integration

This service provides seamless integration with Meilisearch, allowing you to easily configure embedders for semantic search capabilities.

### Step 1: Setup Services

Using Docker Compose (recommended):

```bash
# Start both embedding proxy and Meilisearch
docker compose up -d

# Verify services are running
docker compose ps
```

The Docker Compose setup includes:
- **embedding_proxy**: This embedding service (port 8000)
- **meilisearch**: Meilisearch v1.13 (port 7750)
- **Automatic networking**: Services can communicate with each other

### Step 2: Configure Meilisearch Embedder

Before using embeddings in Meilisearch, you need to configure the embedder for your index:

```bash
# Configure embedder for your index
curl -X POST "http://localhost:8000/v1/meilisearch/embedder" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "movies",
    "embedder_name": "default",
    "document_template": "{{doc.title}} {{doc.overview}}"
  }'
```

**Parameters:**
- `index_id`: Your Meilisearch index name (e.g., "movies", "products")
- `embedder_name`: Name for the embedder (default: "default")
- `document_template`: Template defining which document fields to embed

**Common Document Templates:**
```json
// For movies: embed title and overview
"{{doc.title}} {{doc.overview}}"

// For products: embed name and description  
"{{doc.name}} {{doc.description}}"

// For articles: embed title and content
"{{doc.title}} {{doc.content}}"

// Multiple fields with custom format
"Title: {{doc.title}} Content: {{doc.body}} Tags: {{doc.tags}}"
```

### Step 3: Use in Meilisearch

Once configured, you can use the embedder in your Meilisearch operations:

**Add Documents with Auto-Embedding:**
```bash
# Documents will be automatically embedded using your configured template
curl -X POST "http://localhost:7750/indexes/movies/documents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_master_key" \
  -d '[
    {
      "id": 1,
      "title": "The Matrix",
      "overview": "A computer hacker learns about the true nature of reality."
    }
  ]'
```

**Semantic Search:**
```bash
# Search using vector similarity
curl -X POST "http://localhost:7750/indexes/movies/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_master_key" \
  -d '{
    "q": "sci-fi movies about virtual reality",
    "vector": {
      "embedder": "default"
    }
  }'
```

**Hybrid Search (Text + Vector):**
```bash
# Combine keyword and semantic search
curl -X POST "http://localhost:7750/indexes/movies/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_master_key" \
  -d '{
    "q": "matrix",
    "vector": {
      "embedder": "default"
    },
    "hybrid": {
      "semanticRatio": 0.8
    }
  }'
```

### Monitoring and Management

**Check Configuration Status:**
```bash
# View all tasks (including embedder configuration)
curl "http://localhost:8000/v1/meilisearch/tasks"

# View all indexes
curl "http://localhost:8000/v1/meilisearch/indexes"

# Health check with Meilisearch status
curl "http://localhost:8000/health"
```

**Troubleshooting:**
- Check service logs: `docker compose logs embedding_proxy`
- Verify Meilisearch connection: `docker compose logs meilisearch`
- Test embedding endpoint: `curl -X POST "http://localhost:8000/v1/embeddings" -H "Content-Type: application/json" -d '{"input": ["test"]}'`

## Testing

Use the provided test client:

```bash
# Set API key
export API_KEY=your_siliconflow_api_key

# Run tests
python test_client.py
```

## Logging

The service uses Loguru for structured logging, including:

- Request and response details
- Error messages and debug information
- Performance metrics
- Configuration validation information

Log level can be configured via `LOG_LEVEL` environment variable:
- `CRITICAL`
- `ERROR` 
- `WARNING`
- `INFO` (default)
- `DEBUG`
- `TRACE`

## Docker Support

### Quick Start with Docker Compose

```bash
# 1. Clone and setup
git clone <repository-url>
cd meilisearch_embedding_proxy
cp .env.example .env

# 2. Configure your API key in .env
# Edit MEILI_MASTER_KEY and API_KEY

# 3. Start all services
docker compose up -d

# 4. Configure embedder (replace with your index name)
curl -X POST "http://localhost:8000/v1/meilisearch/embedder" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "your_index_name",
    "embedder_name": "default",
    "document_template": "{{doc.title}} {{doc.content}}"
  }'
```

### Individual Service Deployment

```bash
# Build the image
./build.sh

# Run embedding proxy only
docker run -d -p 8000:8000 -e API_KEY=your_key meilisearch-embedding-proxy:latest

# Run with custom configuration
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your_siliconflow_key \
  -e MEILISEARCH_URL=http://your-meilisearch:7750 \
  -e MEILI_MASTER_KEY=your_master_key \
  meilisearch-embedding-proxy:latest
```

### Docker Configuration

The Docker setup includes:
- ✅ **Multi-service deployment**: Embedding proxy + Meilisearch v1.13
- ✅ **Automatic networking**: Services communicate seamlessly
- ✅ **Health checks**: Built-in service monitoring
- ✅ **Volume persistence**: Meilisearch data persisted
- ✅ **Environment configuration**: Easy setup via .env file
- ✅ **Production ready**: Optimized for performance and security

## Development

```bash
# Install development dependencies
poetry install

# Run development server
poetry run meilisearch_embedding_proxy --reload

# Run tests
poetry run python test_local.py

# Code formatting
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .

# Enter Poetry shell
poetry shell
```

## Project Structure

```
meilisearch_embedding_proxy/
├── src/meilisearch_embedding_proxy/
│   ├── __init__.py
│   ├── cli.py              # Command line interface
│   ├── config.py           # Configuration management
│   └── fastapi_server.py   # FastAPI server
├── tests/
│   └── test_api.py         # API tests
├── dist/                   # Poetry build output
├── pyproject.toml          # Poetry configuration
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── build.sh               # Automated build script
├── .env.example           # Environment variables example
├── .dockerignore          # Docker ignore file
├── README.md              # Project documentation
├── README_zh.md           # Chinese documentation
├── DOCKER.md              # Docker deployment guide
├── QUICKSTART.md          # Quick start guide
└── test_*.py              # Test files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License
