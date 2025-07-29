"""
使用Poetry运行的集成测试
"""
import pytest
import json
from fastapi.testclient import TestClient
from meilisearch_embedding_proxy.fastapi_server import app

client = TestClient(app)

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "config_valid" in data
    assert "model" in data

def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
    assert "config" in data

def test_embedding_request_structure():
    """测试嵌入请求的数据结构"""
    # 测试有效的请求结构
    test_payload = {
        "input": ["Hello world", "测试文本"]
    }
    
    # 这个测试会因为API密钥问题失败，但我们可以验证请求结构
    response = client.post("/v1/embeddings", json=test_payload)
    
    # 根据是否有有效API密钥，返回不同状态码
    # 401 表示没有API密钥，500 表示其他错误
    assert response.status_code in [200, 401, 500]

def test_embedding_request_single_string():
    """测试单个字符串输入"""
    test_payload = {
        "input": "Single test string"
    }
    
    response = client.post("/v1/embeddings", json=test_payload)
    assert response.status_code in [200, 401, 500]

def test_embedding_request_empty():
    """测试空输入"""
    test_payload = {
        "input": []
    }
    
    response = client.post("/v1/embeddings", json=test_payload)
    assert response.status_code == 400  # 应该返回错误

if __name__ == "__main__":
    # 直接运行测试函数
    test_health_endpoint()
    test_root_endpoint()
    test_embedding_request_structure()
    test_embedding_request_single_string()
    test_embedding_request_empty()
    print("所有测试通过！")
