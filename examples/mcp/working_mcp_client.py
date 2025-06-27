#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作的 FastMCP 图像分析器客户端演示
使用正确的 MCP 协议和 SSE 连接
"""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 尝试导入 MCP 客户端库
try:
    import httpx
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    from mcp.types import CallToolRequest, ListToolsRequest
except ImportError as e:
    print(f"❌ 缺少必要的库: {e}")
    print("请安装: pip install mcp httpx")
    sys.exit(1)


class WorkingMCPClient:
    """工作的 MCP 客户端"""
    
    def __init__(self, server_url: str = "http://localhost:8999/sse"):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        
    async def test_connection(self):
        """测试连接"""
        print(f"🔗 测试连接到: {self.server_url}")
        
        try:
            # 使用 httpx 测试基础连接
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8999", timeout=5.0)
                print(f"✅ 服务器响应状态: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False
            
        return True
    
    async def connect_and_demo(self):
        """连接并运行演示"""
        print("=" * 50)
        print("🚀 FastMCP 图像分析器客户端演示")
        print("=" * 50)
        
        # 先测试基础连接
        if not await self.test_connection():
            return
            
        try:
            print(f"\n🔗 正在建立 MCP 连接...")
            
            # 建立 SSE 连接
            async with sse_client(self.server_url) as streams:
                # 创建会话
                async with ClientSession(streams[0], streams[1]) as session:
                    print("✅ MCP 会话建立成功!")
                    
                    # 初始化会话
                    init_result = await session.initialize()
                    print(f"✅ 会话初始化完成")
                    print(f"   服务器信息: {init_result.server_info.name} v{init_result.server_info.version}")
                    
                    # 列出可用工具
                    print("\n📋 获取可用工具...")
                    tools_result = await session.list_tools()
                    
                    print(f"✅ 发现 {len(tools_result.tools)} 个工具:")
                    for tool in tools_result.tools:
                        print(f"   • {tool.name}: {tool.description}")
                    
                    # 演示调用工具
                    await self.demo_tool_calls(session)
                    
        except Exception as e:
            print(f"❌ MCP 连接失败: {e}")
            print("💡 请确保服务器正在运行并且端口 8999 可访问")
            
    async def demo_tool_calls(self, session: ClientSession):
        """演示工具调用"""
        print("\n" + "="*30)
        print("🔧 工具调用演示")
        print("="*30)
        
        # 1. 获取设备状态
        print("\n1️⃣ 获取设备状态...")
        try:
            result = await session.call_tool(
                CallToolRequest(
                    method="call_tool",
                    params={
                        "name": "get_device_status",
                        "arguments": {}
                    }
                )
            )
            print("✅ 设备状态:")
            if hasattr(result, 'content') and result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        try:
                            status = json.loads(content.text)
                            print(f"   设备: {status.get('device', 'unknown')}")
                            print(f"   CUDA可用: {status.get('cuda_available', False)}")
                            print(f"   GPU数量: {status.get('gpu_count', 0)}")
                        except:
                            print(f"   {content.text}")
        except Exception as e:
            print(f"❌ 调用失败: {e}")
        
        # 2. 查找示例图片
        print("\n2️⃣ 寻找示例图片...")
        demo_images = []
        
        # 查找常见的示例图片
        possible_paths = [
            "demo.png", "demo.jpg", "test.png", "test.jpg",
            "sample.png", "sample.jpg", "example.png", "example.jpg",
            "images/demo.png", "images/sample.jpg"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                demo_images.append(path)
                print(f"   ✅ 找到图片: {path}")
        
        if not demo_images:
            print("   ℹ️ 未找到示例图片，将创建一个测试图片...")
            await self.create_test_image()
            if os.path.exists("test_image.png"):
                demo_images.append("test_image.png")
        
        # 3. 分析图片文件
        if demo_images:
            image_path = demo_images[0]
            print(f"\n3️⃣ 分析图片文件: {image_path}")
            
            try:
                result = await session.call_tool(
                    CallToolRequest(
                        method="call_tool",
                        params={
                            "name": "analyze_image_file",
                            "arguments": {
                                "image_path": image_path,
                                "analysis_types": ["elements", "structure"],
                                "include_ocr": True
                            }
                        }
                    )
                )
                print("✅ 图片分析完成:")
                if hasattr(result, 'content') and result.content:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            try:
                                analysis = json.loads(content.text)
                                print(f"   状态: {analysis.get('status', 'unknown')}")
                                print(f"   元素数量: {len(analysis.get('elements', []))}")
                                if 'ocr_text' in analysis:
                                    print(f"   OCR文本: {analysis['ocr_text'][:100]}...")
                            except:
                                print(f"   {content.text[:200]}...")
            except Exception as e:
                print(f"❌ 图片分析失败: {e}")
        
        print(f"\n✅ 演示完成!")
        print("💡 您可以修改代码来测试其他工具和参数")
        
    async def create_test_image(self):
        """创建一个简单的测试图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建一个简单的测试图片
            img = Image.new('RGB', (400, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # 绘制一些简单的元素
            draw.rectangle([50, 50, 350, 100], fill='lightblue', outline='blue')
            draw.text((60, 65), "这是一个测试按钮", fill='black')
            
            draw.rectangle([50, 120, 350, 170], fill='lightgreen', outline='green')
            draw.text((60, 135), "另一个测试元素", fill='black')
            
            draw.text((50, 200), "测试文字内容", fill='black')
            draw.text((50, 220), "Test English Text", fill='black')
            
            img.save("test_image.png")
            print("   ✅ 创建测试图片: test_image.png")
            
        except ImportError:
            print("   ❌ 无法创建测试图片 (缺少 PIL)")
        except Exception as e:
            print(f"   ❌ 创建测试图片失败: {e}")


async def main():
    """主函数"""
    client = WorkingMCPClient()
    await client.connect_and_demo()


if __name__ == "__main__":
    print("🎯 启动 FastMCP 客户端演示...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 演示已中断")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        sys.exit(1) 