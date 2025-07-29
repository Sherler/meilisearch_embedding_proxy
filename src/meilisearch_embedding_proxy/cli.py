#!/usr/bin/env python3
"""
meilisearch 命令行工具
提供启动 Openai  嵌入代理服务的命令行接口
"""

import argparse
import sys
import os
import uvicorn
from pathlib import Path
from loguru import logger
from .config import config


def get_version():
    """获取版本信息"""
    return "0.1.0"


def start_server(host=None, port=None, reload=False, log_level=None):
    """启动 SiliconFlow 嵌入代理服务"""
    # 使用配置文件中的默认值
    host = host or config.host
    port = port or config.port
    log_level = log_level or config.log_level.lower()
    
    # 配置loguru日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level.upper()
    )
    
    logger.info(f"启动 SiliconFlow 嵌入代理服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"测试端点: POST http://{host}:{port}/v1/embeddings")
    logger.info(f"使用模型: {config.model_name}")
    logger.info(f"最大token限制: {config.max_token_limit}")
    logger.info(f"功能: 转发请求到 SiliconFlow API 并打印请求详情")
    logger.info("-" * 60)
    
    try:
        # 验证配置
        config.validate()
        logger.info("配置验证成功")
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        logger.error("请检查环境变量配置，特别是API_KEY")
        sys.exit(1)
    
    try:
        # 启动 FastAPI 服务
        uvicorn.run(
            "meilisearch_embedding_proxy.fastapi_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except KeyboardInterrupt:
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description="Meilisearch Embedding Proxy - SiliconFlow 嵌入代理服务命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  meilisearch-embedding-proxy                    # 启动服务 (使用配置文件默认值)
  meilisearch-embedding-proxy --port 8080       # 在端口 8080 启动服务
  meilisearch-embedding-proxy --host localhost  # 仅本地访问
  meilisearch-embedding-proxy --reload          # 开发模式，自动重载
  meilisearch-embedding-proxy --help            # 显示帮助信息

环境变量配置:
  API_KEY         - SiliconFlow API密钥 (必需)
  BASE_URL        - API基础URL (默认: https://api.siliconflow.cn/v1)
  MODEL_NAME      - 模型名称 (默认: BAAI/bge-large-zh-v1.5)
  MAX_TOKEN_LIMIT - 最大token限制 (默认: 10000)
  HOST            - 服务器主机 (默认: 0.0.0.0)
  PORT            - 服务器端口 (默认: 8000)
  LOG_LEVEL       - 日志级别 (默认: INFO)
        """
    )
    
    parser.add_argument(
        "--host",
        help=f"服务绑定的主机地址 (默认: {config.host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help=f"服务绑定的端口 (默认: {config.port})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="开启自动重载模式 (开发用)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help=f"日志级别 (默认: {config.log_level.lower()})"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"meilisearch-embedding-proxy {get_version()}"
    )
    
    args = parser.parse_args()
    
    # 启动服务
    start_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
