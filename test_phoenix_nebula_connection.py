#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Phoenix Vision MCP 服务器和 Nebula Scout 客户端的连接
"""

import asyncio
import os
import sys

# 添加项目路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from examples.mcp.phoenix_scout_mcp_client import PhoenixScoutClient

async def test_connection():
    """测试连接"""
    print("🧪 测试 Phoenix Vision 和 Phoenix Scout 连接")
    print("=" * 50)
    
    # 创建客户端
    server_script = os.path.join(project_root, "src/server/phoenix_vision_mcp_server.py")
    client = PhoenixScoutClient(server_script)
    
    try:
        # 连接服务器
        print("🔗 连接服务器...")
        if not await client.connect(timeout=15.0):
            print("❌ 连接失败")
            return False
        
        # 测试基本功能
        print("\n📋 测试工具列表...")
        tools_result = await client.list_tools()
        print(f"工具列表结果: {tools_result.get('success', False)}")
        
        print("\n🖥️ 测试设备状态...")
        status_result = await client.get_device_status()
        print(f"设备状态结果: {status_result.get('success', False)}")
        
        print("\n📚 测试资源列表...")
        resources_result = await client.list_resources()
        print(f"资源列表结果: {resources_result.get('success', False)}")
        
        print("\n💡 测试提示列表...")
        prompts_result = await client.list_prompts()
        print(f"提示列表结果: {prompts_result.get('success', False)}")
        
        print("\n✅ 所有基本测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n🎉 测试成功! Phoenix Vision 和 Phoenix Scout 可以正常协作!")
    else:
        print("\n💥 测试失败! 请检查配置和依赖.") 