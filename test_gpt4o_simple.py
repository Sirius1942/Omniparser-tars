#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-4o简化选择测试脚本
"""

import os
import json
import csv

def test_api():
    """测试API连接"""
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
        
        print("🤖 正在测试GPT-4o API连接...")
        response = client.chat.completions.create(
            model=openai_config["model"],
            messages=[{"role": "user", "content": "请回复'测试成功'"}],
            max_tokens=10,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API连接成功！响应: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 GPT-4o API连接测试")
    print("=" * 30)
    
    if test_api():
        print("✅ 可以开始进行真实的选择测试")
    else:
        print("❌ 需要先解决API连接问题")

if __name__ == "__main__":
    main() 