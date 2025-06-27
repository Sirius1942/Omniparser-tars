#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-4o简化选择测试脚本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import os
import json
import csv
import sys
import asyncio
import traceback
from PIL import Image


def send_llm_message(message: str, max_tokens: int = 100, temperature: float = 0.1) -> dict:
    """发送LLM消息的公共方法
    
    Args:
        message: 要发送的消息内容
        max_tokens: 最大令牌数
        temperature: 温度参数
        
    Returns:
        dict: 包含success、content、error的结果字典
    """
    try:
        from openai import OpenAI
        
        # 直接从配置文件读取
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_config = config.get("openai", {})
        
        # 创建客户端
        client = OpenAI(
            api_key=openai_config["api_key"],
            base_url=openai_config["base_url"]
        )
        
        print(f"🤖 正在发送消息给LLM,model:{openai_config['model']}")
        
        response = client.chat.completions.create(
            model=openai_config["model"],
            messages=[{"role": "user", "content": message}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ LLM响应成功！")
        
        return {
            "success": True,
            "content": result,
            "error": None
        }
        
    except Exception as e:
        print(f"❌ LLM调用失败: {e}")
        return {
            "success": False,
            "content": None,
            "error": str(e)
        }

def test_api():
    """测试API连接"""
    result = send_llm_message("请回复'测试成功'", max_tokens=10)
    
    if result["success"]:
        print(f"✅ API连接成功！响应: {result['content']}")
        return True
    else:
        print(f"❌ API连接失败: {result['error']}")
        return False


if __name__ == "__main__":
    test_api()