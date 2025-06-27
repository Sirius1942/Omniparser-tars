#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-4o简化选择测试脚本
"""

import os
import json
import csv
import sys
import asyncio
import traceback
from PIL import Image

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.image_element_analyzer import ImageElementAnalyzer
from util.config import get_config

from util.adb_mcp_driver import (
    test_mcp_connection,
    get_mcp_tools_list,
    execute_mcp_tool,
    load_client_config
)




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
        
        print(f"🤖 正在发送消息给LLM...")
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

def test_main():
    """主函数"""
    print("🚀 GPT-4o API连接测试")
    print("=" * 30)
    
    if test_api():
        print("✅ 可以开始进行真实的选择测试")
    else:
        print("❌ 需要先解决API连接问题")

def main():

    # 初始化system message
    system_message = """
    你是一个任务选择助手，根据用户输入的任务，选择最合适的任务。
    """
    #发送消息给LLM
    result = send_llm_message(system_message)
    print(result)

    # 发送消息给LLM
    # 命令行接收一个任务输入
    task = input("请输入任务: ")
    

    # 编写任务提示词，并发送给LLM
    prompt = """
    你是一个任务选择助手，根据用户输入的任务，选择最合适的任务。
    用户输入的任务是：{task}
    请根据任务选择最合适的任务。你可以控制设备，也可以进行截图，也可以进行文字输入。
    请根据任务选择最合适的任务。
            ADB MCP Demo 命令帮助:

        基础命令:
        connect              - 测试MCP服务器连接
        tools                - 获取可用工具列表
        help                 - 显示此帮助信息

        屏幕操作:
        wake                 - 唤醒屏幕
        screenshot [c]       - 截图 (c=压缩)
        click <x> <y>        - 点击屏幕坐标
        swipe <x1> <y1> <x2> <y2> [duration] - 滑动屏幕
        home                 - 回到主屏幕
        back                 - 按返回键

        文本输入:
        input <text>         - 输入文本

        示例:
        click 100 200        - 点击坐标(100, 200)
        input hello world    - 输入"hello world"
        screenshot c         - 压缩截图
        swipe 100 500 100 200 1000 - 从(100,500)滑动到(100,200)，持续1秒

        你需要返回一个list格式，包含多个操作步骤包含以下字段：  
    """
    llm_message = {
        "role": "user",
        "content": task
    }

    # 调用LLM进行选择
    result = send_llm_message(llm_message)
    

if __name__ == "__main__":
    main() 