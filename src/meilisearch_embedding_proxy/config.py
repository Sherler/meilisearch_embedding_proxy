"""
配置模块，用于读取环境变量配置
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类，包含所有必要的配置项"""
    
    def __init__(self):
        # 最大token限制
        self.max_token_limit: int = int(os.getenv("MAX_TOKEN_LIMIT", "10000"))
        
        # 模型名称
        self.model_name: str = os.getenv("MODEL_NAME", "BAAI/bge-large-zh-v1.5")
        
        # API基础URL
        self.base_url: str = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")
        
        # API密钥
        self.api_key: Optional[str] = os.getenv("API_KEY")
        
        # 服务器配置
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # 日志级别
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        # 超时时间
        self.timeout: int = int(os.getenv("TIMEOUT", "30"))
        self.dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))
        
        # Meilisearch 配置
        self.meilisearch_url: str = os.getenv("MEILISEARCH_URL", "http://meilisearch:7700")
        self.meilisearch_api_key: Optional[str] = os.getenv("MEILI_MASTER_KEY")
        
        # 本服务的URL，用于配置到 Meilisearch 的 embedder
        self.service_url: str = os.getenv("SERVICE_URL", "http://embedding_proxy:8000")
        
    def validate(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            raise ValueError("API_KEY environment variable is required")
        return True
    
    def validate_meilisearch(self) -> bool:
        """验证 Meilisearch 配置是否有效"""
        if not self.meilisearch_url:
            raise ValueError("MEILISEARCH_URL environment variable is required")
        return True
    
    def get_openai_config(self) -> dict:
        """获取OpenAI客户端配置"""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout
        }

# 全局配置实例
config = Config()
