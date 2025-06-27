#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastMCP 图像分析器客户端演示 - 适配版
直接使用 FastMCP 的 HTTP API 模式
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import asyncio
import json
import os
import uuid
import time
import re
from typing import Dict, Any, Optional
import httpx

class FastMCPAdaptedClient:
    """适配 FastMCP 协议的客户端 - HTTP 直接模式"""
    
    def __init__(self, server_url: str = "http://localhost:8999"):
        self.base_url = server_url.rstrip('/')
        self.messages_url = f"{self.base_url}/messages/"
        self.session_id = None  # 将从 SSE 连接中获取
        self.client = None
        self.connected = False
        
    async def connect(self, timeout: float = 5.0) -> bool:
        """连接到 FastMCP 服务器"""
        try:
            print(f"🔗 连接到 FastMCP 服务器: {self.base_url}")
            
            # 创建 HTTP 客户端，设置更长的超时时间
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=timeout,
                    read=30.0,  # 读取超时设为 30 秒
                    write=10.0,
                    pool=5.0
                )
            )
            
            # 建立 SSE 连接来创建 session
            print("🔍 建立 SSE 连接以创建 session...")
            sse_url = f"{self.base_url}/sse/"
            
            # 使用流模式建立 SSE 连接并提取 session ID
            async with self.client.stream("GET", sse_url) as response:
                if response.status_code == 200:
                    print("✅ SSE 连接建立成功")
                    
                    # 读取 SSE 数据以获取 session ID
                    async for line in response.aiter_lines():
                        if line.strip():
                            print(f"🔍 接收到 SSE 数据: {line[:200]}...")
                            
                            # 尝试从 SSE 数据中提取 session ID
                            if "session_id" in line:
                                # 查找 session_id 模式
                                match = re.search(r'"session_id":\s*"([^"]+)"', line)
                                if match:
                                    self.session_id = match.group(1)
                                    print(f"✅ 提取到 Session ID: {self.session_id}")
                                    break
                            
                            # 或者检查 URL 中的 session_id
                            if "/messages/?session_id=" in line:
                                match = re.search(r'session_id=([a-f0-9]+)', line)
                                if match:
                                    self.session_id = match.group(1)
                                    print(f"✅ 从 URL 提取 Session ID: {self.session_id}")
                                    break
                            
                            # 如果有多行，最多读取前几行
                            if "event:" in line and "endpoint" in line:
                                # 继续读取可能包含 session_id 的下一行
                                continue
                            
                            # 如果没有找到 session_id，生成一个并尝试
                            if not self.session_id:
                                self.session_id = str(uuid.uuid4()).replace('-', '')
                                print(f"⚠️ 未找到 Session ID，使用生成的: {self.session_id}")
                                break
                    
                    if self.session_id:
                        self.connected = True
                        print(f"✅ FastMCP 连接成功，Session ID: {self.session_id}")
                        return True
                    else:
                        print("❌ 无法获取有效的 Session ID")
                        return False
                else:
                    print(f"❌ SSE 连接失败: {response.status_code}")
                    return False
                
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def _send_initialize_message(self) -> bool:
        """发送初始化消息"""
        try:
            init_message = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "FastMCP-Adapted-Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            messages_endpoint = f"{self.messages_url}?session_id={self.session_id}"
            response = await self.client.post(
                messages_endpoint, 
                json=init_message,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 初始化响应状态码: {response.status_code}")
            
            if response.status_code == 202:
                print("✅ 初始化消息已接受")
                return True
            else:
                print(f"⚠️ 初始化响应异常: {response.status_code}")
                if response.text:
                    print(f"🔍 响应内容: {response.text}")
                return False
                
        except Exception as e:
            print(f"⚠️ 发送初始化消息失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        try:
            if self.client:
                await self.client.aclose()
                self.client = None
            self.connected = False
        except Exception as e:
            print(f"⚠️ 断开连接时出错: {e}")
    
    async def call_tool_direct(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """直接调用 FastMCP 工具（绕过标准 MCP 协议）"""
        if not self.connected or not self.client:
            return {"success": False, "error": "未连接到服务器"}
        
        if not self.session_id:
            return {"success": False, "error": "没有有效的 Session ID"}
        
        try:
            print(f"🔧 直接调用工具: {tool_name}")
            print(f"🔍 参数: {arguments}")
            
            # 使用简化的消息格式
            message = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # 发送到 messages 端点
            messages_endpoint = f"{self.messages_url}?session_id={self.session_id}"
            print(f"🔍 发送到: {messages_endpoint}")
            
            response = await self.client.post(
                messages_endpoint,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 工具调用响应状态码: {response.status_code}")
            
            if response.status_code == 202:
                print("✅ 工具调用请求已发送")
                return {"success": True, "message": "请求已发送到 FastMCP 服务器"}
            else:
                error_msg = f"HTTP {response.status_code}"
                if response.text:
                    error_msg += f": {response.text}"
                    print(f"🔍 错误响应内容: {response.text}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            print(f"❌ 工具调用失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具的主要接口"""
        return await self.call_tool_direct(tool_name, arguments)
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具（基于已知的 FastMCP 工具）"""
        if not self.connected:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print("\n📋 获取工具列表...")
            
            # FastMCP 服务器的已知工具列表
            tools = [
                {"name": "analyze_image_file", "description": "分析图像文件中的文本和图标元素"},
                {"name": "analyze_image_base64", "description": "分析 Base64 编码的图像"},
                {"name": "batch_analyze_images", "description": "批量分析多个图像文件"},
                {"name": "get_device_status", "description": "获取当前设备状态信息"}
            ]
            
            print(f"✅ 找到 {len(tools)} 个工具")
            return {"success": True, "result": tools}
            
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """分析图像"""
        if not os.path.exists(image_path):
            return {"success": False, "error": f"文件不存在: {image_path}"}
        
        print(f"\n🖼️ 分析图像: {os.path.basename(image_path)}")
        
        arguments = {
            "image_path": image_path,
            "box_threshold": 0.05,
            "save_annotated": True,
            "output_dir": "./results"
        }
        
        return await self.call_tool("analyze_image_file", arguments)
    
    async def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        print("\n🖥️ 获取设备状态...")
        return await self.call_tool("get_device_status", {})


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载配置文件失败: {e}")
        return {}


async def main():
    """主函数"""
    print("🎯 FastMCP 图像分析器客户端演示 - 适配版")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    # 使用当前运行的服务器地址
    server_url = "http://localhost:8999"
    
    # 测试图像路径
    test_image = "screenshots/screenshot_20250625_074204.png"
    
    # 创建客户端
    client = FastMCPAdaptedClient(server_url)
    
    try:
        # 1. 连接到服务器
        if not await client.connect():
            print("❌ 无法连接到服务器")
            return
        
        # 2. 列出可用工具
        tools_result = await client.list_tools()
        if tools_result.get("success"):
            tools = tools_result["result"]
            print(f"\n📋 可用工具:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")
        
        # 3. 获取设备状态
        device_result = await client.get_device_status()
        if device_result.get("success"):
            print("✅ 设备状态请求已发送")
        else:
            print(f"❌ 设备状态请求失败: {device_result.get('error')}")
        
        # 4. 分析测试图像
        if os.path.exists(test_image):
            analysis_result = await client.analyze_image(test_image)
            if analysis_result.get("success"):
                print("✅ 图像分析请求已发送")
            else:
                print(f"❌ 图像分析失败: {analysis_result.get('error')}")
        else:
            print(f"⚠️ 测试图像不存在: {test_image}")
        
        print("\n🎉 演示完成!")
        print("📝 注意: 由于 FastMCP 的异步特性，实际分析结果会在服务器端处理")
        print("📝 结果文件将保存在 ./results/ 目录中")
        
    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")
        
    finally:
        # 清理连接
        await client.disconnect()
        print("🧹 连接已断开")


if __name__ == "__main__":
    asyncio.run(main()) 