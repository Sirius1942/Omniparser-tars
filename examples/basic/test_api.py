#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI API 连接测试脚本
使用config.json中的配置进行测试
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import json
import os
from openai import OpenAI

def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ 配置文件 config.json 不存在！")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return None

def test_api_connection(config):
    """测试API连接"""
    openai_config = config['openai']
    
    print("🔧 API配置信息:")
    print(f"   🌐 API端点: {openai_config['base_url']}")
    print(f"   🔑 API密钥: {openai_config['api_key'][:10]}...{openai_config['api_key'][-10:]}")
    print(f"   🤖 模型: {openai_config['model']}")
    print(f"   ⏱️  超时时间: {openai_config['request_timeout']}秒")
    
    try:
        # 初始化客户端
        print("\n🔌 初始化OpenAI客户端...")
        
        # 兼容不同版本的OpenAI库
        try:
            client = OpenAI(
                api_key=openai_config['api_key'],
                base_url=openai_config['base_url'],
                timeout=openai_config['request_timeout']
            )
        except TypeError:
            # 旧版本可能不支持某些参数
            client = OpenAI(
                api_key=openai_config['api_key'],
                base_url=openai_config['base_url']
            )
        
        print("✅ 客户端初始化成功")
        
        # 测试简单的文本对话
        print("\n💬 测试文本对话...")
        
        response = client.chat.completions.create(
            model=openai_config['model'],
            messages=[
                {
                    "role": "user",
                    "content": "你好，请回复'测试成功'"
                }
            ],
            max_tokens=20,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ 文本对话测试成功！")
        print(f"   📝 API回复: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败:")
        print(f"   🚫 错误信息: {e}")
        
        # 分析常见错误
        error_str = str(e)
        if "401" in error_str:
            print("\n🔍 错误分析:")
            print("   • 401错误通常表示API密钥无效或过期")
            print("   • 请检查API密钥是否正确")
            print("   • 请确认API服务是否正常")
        elif "timeout" in error_str.lower():
            print("\n🔍 错误分析:")
            print("   • 网络连接超时")
            print("   • 请检查网络连接和API服务地址")
        elif "connection" in error_str.lower():
            print("\n🔍 错误分析:")
            print("   • 无法连接到API服务")
            print("   • 请检查API服务地址是否正确")
            print("   • 请确认服务是否正在运行")
        
        return False

def test_vision_api(config):
    """测试视觉API（可选）"""
    openai_config = config['openai']
    
    print("\n👁️  测试视觉API...")
    
    try:
        client = OpenAI(
            api_key=openai_config['api_key'],
            base_url=openai_config['base_url']
        )
        
        # 创建一个简单的测试图像数据（1x1像素的PNG）
        import base64
        # 最小的PNG图像数据
        minimal_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        response = client.chat.completions.create(
            model=openai_config['model'],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这是什么颜色？"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{minimal_png}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=20,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ 视觉API测试成功！")
        print(f"   📝 API回复: {result}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  视觉API测试失败: {e}")
        return False

def main():
    print("🚀 OpenAI API 连接测试")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    if not config:
        return
    
    print("✅ 配置文件加载成功")
    
    # 测试基本连接
    if test_api_connection(config):
        print("\n🎉 基本API测试通过！")
        
        # 测试视觉API
        if test_vision_api(config):
            print("\n🎉 视觉API也工作正常！")
            print("\n✅ 所有测试通过，可以正常使用GPT-4o进行图标识别")
        else:
            print("\n⚠️  视觉API测试失败，可能影响图标识别功能")
    else:
        print("\n❌ API连接失败，无法使用GPT-4o功能")
        print("\n🛠️  建议检查:")
        print("   1. API密钥是否有效")
        print("   2. API服务是否正常运行")
        print("   3. 网络连接是否正常")
        print("   4. API服务地址是否正确")

if __name__ == "__main__":
    main() 