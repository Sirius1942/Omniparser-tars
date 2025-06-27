#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的 MCP 客户端测试
验证与服务端的基本通信
"""

import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import CallToolRequest

async def test_mcp_connection():
    """测试 MCP 连接"""
    print("🎯 简单 MCP 客户端测试")
    print("=" * 40)
    
    try:
        # 连接到服务器
        print("🔗 连接到测试服务器...")
        server_params = StdioServerParameters(
            command="python",
            args=["simple_mcp_test.py"]
        )
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("✅ stdio 连接成功")
            
            # 创建会话
            session = ClientSession(read_stream, write_stream)
            
            # 初始化
            print("🔄 初始化会话...")
            init_result = await session.initialize()
            print(f"✅ 连接成功: {init_result.server_info.name}")
            
            # 列出工具
            print("\n📋 获取工具列表...")
            tools_result = await session.list_tools()
            print(f"✅ 找到 {len(tools_result.tools)} 个工具:")
            for tool in tools_result.tools:
                print(f"   • {tool.name}: {tool.description}")
            
            # 调用工具
            print("\n🔧 调用测试工具...")
            request = CallToolRequest(
                method="tools/call",
                params={
                    "name": "test_tool", 
                    "arguments": {"message": "Hello from MCP client!"}
                }
            )
            
            result = await session.call_tool(request)
            print("✅ 工具调用成功")
            
            # 显示结果
            if result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        response_data = json.loads(content.text)
                        print(f"📝 响应: {response_data}")
            
            print("\n🎉 测试完成!")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection()) 