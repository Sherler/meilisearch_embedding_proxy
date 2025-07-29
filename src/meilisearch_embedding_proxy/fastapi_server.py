from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
import json
import time
import uvicorn
from openai import OpenAI
from loguru import logger
import meilisearch
from .config import config

app = FastAPI(
    title="SiliconFlow Embedding Proxy Server", 
    version="1.0.0",
    description="代理服务，转发嵌入请求到SiliconFlow API并打印请求详情"
)

# 配置日志
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=config.log_level
)

# 初始化OpenAI客户端
client = OpenAI(
    api_key=config.api_key,
    base_url=config.base_url,
    timeout=config.timeout
)

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]

class EmbeddingData(BaseModel):
    embedding: List[float]

class EmbeddingResponse(BaseModel):
    data: List[EmbeddingData]

class MeilisearchConfigRequest(BaseModel):
    index_id: str
    embedder_name: Optional[str] = "default"
    document_template: str

class MeilisearchConfigResponse(BaseModel):
    success: bool
    message: str
    task_uid: Optional[int] = None
    

@app.post("/v1/embeddings")
async def create_embeddings(request: EmbeddingRequest, raw_request: Request):
    """
    接收嵌入请求并转发到SiliconFlow API
    """
    
    logger.info("=== 转发请求 ===")
    
    # 检查输入并应用token限制
    if isinstance(request.input, str):
        input_list = [request.input]
    else:
        input_list = request.input
    
    final_input = []
    for input_item in input_list:
        if len(input_item) > config.max_token_limit:
            truncated_input = input_item[:config.max_token_limit]
            logger.warning(f"输入文本超过{config.max_token_limit}字符限制，已截断")
            final_input.append(truncated_input)
        else:
            final_input.append(input_item)
    
    if not final_input:
        logger.error("输入为空")
        raise HTTPException(status_code=400, detail="Input must be a string or a list of strings")
    
    # 使用配置的模型名称，如果请求中没有指定则使用默认值
    model_to_use = config.model_name
    
    logger.info(f"使用模型: {model_to_use}")
    logger.info(f"输入数量: {len(final_input)}")
    
    try:
        # 使用OpenAI客户端创建嵌入
        logger.info("正在调用OpenAI客户端...")
        
        # 构建请求参数
        embedding_params = {
            "model": model_to_use,
            "input": final_input,
        }
        
        # 添加可选参数
        
        embedding_params["encoding_format"] = "float"  # 默认使用float格式
        embedding_params["dimensions"] = config.dimensions  # 默认使用1024维度

        response = client.embeddings.create(**embedding_params)
        
        logger.info("=== SiliconFlow API 响应成功 ===")
        logger.info(f"响应数据条数: {len(response.data)}")
        logger.info(f"总token数: {response.usage.total_tokens}")
        logger.info(f"提示token数: {response.usage.prompt_tokens}")
        
        # 转换响应格式以匹配简化的数据结构
        response_data = {
            "data": [
                {
                    "embedding": item.embedding
                }
                for item in response.data
            ]
        }
        
        return response_data
            
    except Exception as e:
        logger.error(f"=== 请求失败 ===")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        
        # 根据错误类型返回适当的HTTP状态码
        if "401" in str(e) or "Unauthorized" in str(e):
            raise HTTPException(
                status_code=401,
                detail="API key is invalid or unauthorized"
            )
        elif "429" in str(e) or "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create embeddings: {str(e)}"
            )
    
    finally:
        logger.info("=" * 50)

def get_meilisearch_client():
    """获取 Meilisearch 客户端"""
    try:
        config.validate_meilisearch()
        client = meilisearch.Client(
            config.meilisearch_url, 
            config.meilisearch_api_key
        )
        return client
    except Exception as e:
        logger.error(f"创建 Meilisearch 客户端失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Meilisearch: {str(e)}"
        )

def wait_task(client: meilisearch.Client, task_info) -> bool:
    """等待 Meilisearch 任务完成"""
    logger.info(f"等待任务完成: {task_info}")
    
    if not hasattr(task_info, 'task_uid'):
        logger.error("任务信息缺少 task_uid")
        return False
    
    create_success = False
    if task_info.status == "enqueued":
        while not create_success:
            try:
                res = client.get_task(task_info.task_uid)
                if res.error:
                    logger.error(f"任务执行出错: {res.error.get('message', 'Unknown error')}")
                    return False
                
                if res.status in ["succeeded", "failed"]:
                    create_success = True
                    if res.status == "succeeded":
                        logger.info(f"任务 {task_info.task_uid} 执行成功")
                        return True
                    else:
                        logger.error(f"任务 {task_info.task_uid} 执行失败")
                        return False
                else:
                    logger.info(f"任务 {task_info.task_uid} 状态: {res.status}, 等待中...")
                    time.sleep(2)
            except Exception as e:
                logger.error(f"检查任务状态时出错: {str(e)}")
                return False
    
    return True

@app.post("/v1/meilisearch/embedder", response_model=MeilisearchConfigResponse)
async def configure_meilisearch_embedder(request: MeilisearchConfigRequest):
    """
    配置 Meilisearch 索引的 embedder
    """
    logger.info("=== 配置 Meilisearch Embedder ===")
    logger.info(f"索引ID: {request.index_id}")
    logger.info(f"Embedder名称: {request.embedder_name}")
    
    try:
        # 获取 Meilisearch 客户端
        client = get_meilisearch_client()
        
        # 获取索引
        index = client.get_index(request.index_id)
        logger.info(f"成功获取索引: {request.index_id}")
        
        # 设置默认值
        document_template = request.document_template
        
        # 构建 embedder 配置
        embedder_config = {
            request.embedder_name: {
                "source": "rest",
                "url": f"{config.service_url}/v1/embeddings",
                "request": {
                    "input": ["{{text}}", "{{..}}"]
                },
                "apiKey": config.api_key,
                "documentTemplate": document_template,
                "dimensions": config.dimensions,
                "documentTemplateMaxBytes": config.max_token_limit,
                "response": {
                    "data": [
                        {
                            "embedding": "{{embedding}}"
                        },
                        "{{..}}"
                    ]
                }
            }
        }
        
        logger.info(f"Embedder 配置: {json.dumps(embedder_config, indent=2)}")
        
        # 更新 embedder
        task_info = index.update_embedders(embedder_config)
        logger.info(f"更新任务已提交: {task_info}")
        
        # 等待任务完成
        success = wait_task(client, task_info)
        
        if success:
            return MeilisearchConfigResponse(
                success=True,
                message=f"Successfully configured embedder '{request.embedder_name}' for index '{request.index_id}'",
                task_uid=task_info.task_uid
            )
        else:
            return MeilisearchConfigResponse(
                success=False,
                message=f"Failed to configure embedder '{request.embedder_name}' for index '{request.index_id}'",
                task_uid=task_info.task_uid
            )
            
    except Exception as e:
        logger.error(f"配置 Meilisearch embedder 失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure embedder: {str(e)}"
        )
    
    finally:
        logger.info("=" * 50)

@app.get("/v1/meilisearch/tasks")
async def get_meilisearch_tasks():
    """
    获取 Meilisearch 任务列表
    """
    logger.info("获取 Meilisearch 任务列表")
    
    try:
        client = get_meilisearch_client()
        res = client.get_tasks()
        
        tasks = []
        for result in res.results:
            tasks.append(result.model_dump())
            
        logger.info(f"获取到 {len(tasks)} 个任务")
        return {
            "success": True,
            "tasks": tasks
        }
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tasks: {str(e)}"
        )

@app.get("/v1/meilisearch/indexes")
async def get_meilisearch_indexes():
    """
    获取 Meilisearch 索引列表
    """
    logger.info("获取 Meilisearch 索引列表")
    
    try:
        client = get_meilisearch_client()
        indexes = client.get_indexes()
        
        index_list = []
        for index in indexes['results']:
            index_list.append({
                'uid': index['uid'],
                'primaryKey': index.get('primaryKey'),
                'createdAt': index.get('createdAt'),
                'updatedAt': index.get('updatedAt')
            })
            
        logger.info(f"获取到 {len(index_list)} 个索引")
        return {
            "success": True,
            "indexes": index_list
        }
        
    except Exception as e:
        logger.error(f"获取索引列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get indexes: {str(e)}"
        )

@app.get("/")
async def root():
    logger.info("访问根路径")
    return {
        "message": "Meilisearch Embedding Proxy Server is running",
        "description": "This server forwards embedding requests to Self hosted openai API and configures Meilisearch embedders",
        "config": {
            "model": config.model_name,
            "max_token_limit": config.max_token_limit,
            "base_url": config.base_url,
            "meilisearch_url": config.meilisearch_url
        },
        "endpoints": {
            "embeddings": "POST /v1/embeddings",
            "meilisearch_config": "POST /v1/meilisearch/configure",
            "meilisearch_tasks": "GET /v1/meilisearch/tasks",
            "meilisearch_indexes": "GET /v1/meilisearch/indexes",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

@app.get("/health")
async def health_check():
    logger.info("健康检查")
    try:
        # 验证基本配置
        config.validate()
        
        # 检查 Meilisearch 连接
        meilisearch_status = "unknown"
        try:
            config.validate_meilisearch()
            client = meilisearch.Client(config.meilisearch_url, config.meilisearch_api_key)
            # 尝试获取版本信息来测试连接
            version_info = client.get_version()
            meilisearch_status = "healthy"
            logger.info(f"Meilisearch 连接正常，版本: {version_info}")
        except Exception as e:
            meilisearch_status = f"unhealthy: {str(e)}"
            logger.warning(f"Meilisearch 连接失败: {str(e)}")
        
        return {
            "status": "healthy",
            "config_valid": True,
            "model": config.model_name,
            "max_token_limit": config.max_token_limit,
            "meilisearch_status": meilisearch_status,
            "meilisearch_url": config.meilisearch_url
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "config_valid": False,
            "error": str(e),
            "meilisearch_status": "unknown"
        }

def create_app():
    """创建 FastAPI 应用实例"""
    return app


def run_server(host=None, port=None):
    """运行服务器"""
    # 使用配置文件中的默认值
    host = host or config.host
    port = port or config.port
    
    # 验证配置
    try:
        config.validate()
        logger.info("配置验证成功")
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        return
    
    logger.info("启动 SiliconFlow 嵌入代理服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"测试端点: POST http://{host}:{port}/v1/embeddings")
    logger.info(f"使用模型: {config.model_name}")
    logger.info(f"最大token限制: {config.max_token_limit}")
    logger.info(f"API基础URL: {config.base_url}")
    logger.info("功能: 转发请求到 SiliconFlow API 并打印请求详情")
    
    uvicorn.run(app, host=host, port=port, log_level=config.log_level.lower())


if __name__ == "__main__":
    run_server()
