#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最小化的 FastMCP 客户端演示
用于测试基本连接和功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import asyncio
import json
import sys

try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    from mcp.types import CallToolRequest
    print("✅ MCP 库加载成功")
except ImportError as e:
    print(f"❌ MCP 库导入失败: {e}")
    sys.exit(1)


async def minimal_test():
    """最小化测试"""
    print("🔗 连接到 FastMCP 服务器...")
    
    try:
        # 简单连接测试
        async with sse_client("http://localhost:8999/sse") as streams:
            print("✅ SSE 连接成功")
            
            session = ClientSession(streams[0], streams[1])
            print("✅ 会话创建成功")
            
            # 设置超时时间进行初始化
            init_result = await asyncio.wait_for(session.initialize(), timeout=10.0)
            print("✅ 初始化成功")
            print(f"   服务器: {init_result.server_info.name}")
            
            # 快速测试工具列表
            tools = await asyncio.wait_for(session.list_tools(), timeout=5.0)
            print(f"✅ 找到 {len(tools.tools)} 个工具")
            
            # 测试简单工具调用
            print("🔧 测试设备状态...")
            result = await asyncio.wait_for(
                session.call_tool(CallToolRequest(
                    method="call_tool",
                    params={
                        "name": "get_device_status",
                        "arguments": {}
                    }
                )), 
                timeout=10.0
            )
            
            if hasattr(result, 'content') and result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"✅ 设备状态: {content.text}")
            
            print("✅ 测试完成!")
            
    except asyncio.TimeoutError:
        print("❌ 操作超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🎯 最小化 FastMCP 客户端测试")
    print("=" * 40)
    
    try:
        asyncio.run(minimal_test())
    except KeyboardInterrupt:
        print("\n👋 测试中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}") 