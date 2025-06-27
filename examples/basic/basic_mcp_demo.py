#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础的 FastMCP 图像分析器客户端演示
使用最简单的方式调用 MCP 服务器
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 检查是否有 MCP 库
try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    from mcp.types import CallToolRequest, ListToolsRequest
    print("✅ MCP 库导入成功")
except ImportError as e:
    print(f"❌ 缺少 MCP 库: {e}")
    print("请运行: pip install mcp")
    sys.exit(1)


async def simple_demo():
    """简单演示"""
    print("=" * 60)
    print("🚀 FastMCP 图像分析器客户端演示")
    print("=" * 60)
    
    server_url = "http://localhost:8999/sse"
    print(f"🔗 连接到服务器: {server_url}")
    
    try:
        # 建立连接
        async with sse_client(server_url) as streams:
            print("✅ SSE 流建立成功")
            
            # 创建会话
            session = ClientSession(streams[0], streams[1])
            print("✅ 会话创建成功")
            
            # 初始化
            init_result = await session.initialize()
            print("✅ 会话初始化成功")
            print(f"   服务器名称: {init_result.server_info.name}")
            print(f"   服务器版本: {init_result.server_info.version}")
            
            # 列出工具
            print("\n📋 获取工具列表...")
            tools_result = await session.list_tools()
            print(f"✅ 找到 {len(tools_result.tools)} 个工具:")
            
            for i, tool in enumerate(tools_result.tools, 1):
                print(f"   {i}. {tool.name}")
                print(f"      描述: {tool.description}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    if hasattr(tool.inputSchema, 'properties'):
                        props = tool.inputSchema.properties
                        print(f"      参数: {list(props.keys()) if props else '无'}")
                print()
            
            # 测试第一个工具 - 获取设备状态
            print("🔧 测试工具调用...")
            print("1️⃣ 调用 get_device_status...")
            
            try:
                device_result = await session.call_tool(
                    CallToolRequest(
                        method="call_tool",
                        params={
                            "name": "get_device_status",
                            "arguments": {}
                        }
                    )
                )
                
                print("✅ 设备状态获取成功:")
                if hasattr(device_result, 'content') and device_result.content:
                    for content in device_result.content:
                        if hasattr(content, 'text'):
                            print(f"   {content.text}")
                            
            except Exception as e:
                print(f"❌ 调用失败: {e}")
            
            # 如果有测试图片，尝试分析
            test_images = ["test.png", "demo.png", "sample.jpg", "example.png"]
            found_image = None
            
            for img in test_images:
                if os.path.exists(img):
                    found_image = img
                    break
            
            if found_image:
                print(f"\n2️⃣ 分析图片: {found_image}")
                try:
                    analyze_result = await session.call_tool(
                        CallToolRequest(
                            method="call_tool",
                            params={
                                "name": "analyze_image_file",
                                "arguments": {
                                    "image_path": found_image,
                                    "analysis_types": ["elements"],
                                    "include_ocr": True
                                }
                            }
                        )
                    )
                    
                    print("✅ 图片分析成功:")
                    if hasattr(analyze_result, 'content') and analyze_result.content:
                        for content in analyze_result.content:
                            if hasattr(content, 'text'):
                                # 尝试解析 JSON
                                try:
                                    result_data = json.loads(content.text)
                                    print(f"   状态: {result_data.get('status', 'unknown')}")
                                    elements = result_data.get('elements', [])
                                    print(f"   找到元素: {len(elements)} 个")
                                    if result_data.get('ocr_text'):
                                        print(f"   OCR文本: {result_data['ocr_text'][:100]}...")
                                except json.JSONDecodeError:
                                    print(f"   结果: {content.text[:200]}...")
                                    
                except Exception as e:
                    print(f"❌ 图片分析失败: {e}")
            else:
                print("\n💡 未找到测试图片，跳过图片分析")
                print("   您可以放置 test.png、demo.png 等图片文件来测试分析功能")
            
            print(f"\n✅ 演示完成!")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("💡 请确保:")
        print("   1. FastMCP 服务器正在运行")
        print("   2. 服务器监听在端口 8999")
        print("   3. 网络连接正常")


if __name__ == "__main__":
    print("🎯 启动基础 MCP 客户端演示...")
    
    try:
        asyncio.run(simple_demo())
    except KeyboardInterrupt:
        print("\n👋 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 