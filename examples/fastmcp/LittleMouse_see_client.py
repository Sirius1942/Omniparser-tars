#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LittleMouse MCP Client - 兼容多端口的客户端
🐭 自动检测服务器端口
"""

import asyncio
import aiohttp
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

class LittleMouseClient:
    """🐭 LittleMouse SSE 客户端 - 智能端口检测"""
    
    def __init__(self):
        # 常见的SSE端口列表
        self.possible_urls = [
            "http://localhost:3000/sse",  # 默认FastMCP端口
            "http://localhost:8000/sse",  # 常用端口
            "http://localhost:8001/sse",  # 备用端口
            "http://localhost:5000/sse",  # Flask默认端口
        ]
        self.server_url = None
        self.session: ClientSession = None
    
    async def find_server(self):
        """检测可用的服务器端口"""
        print("🔍 正在检测可用的服务器端口...")
        
        for url in self.possible_urls:
            try:
                print(f"  🔗 尝试连接: {url}")
                
                # 简单的HTTP健康检查
                timeout = aiohttp.ClientTimeout(total=2.0)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url.replace('/sse', '/health'), 
                                         allow_redirects=False) as response:
                        # 如果返回任何响应（即使是404），说明端口是开放的
                        print(f"  ✅ 端口 {url.split(':')[2].split('/')[0]} 可访问")
                        self.server_url = url
                        return True
                        
            except Exception as e:
                print(f"  ❌ {url} 不可用: {type(e).__name__}")
                continue
        
        print("❌ 未找到可用的服务器端口")
        return False
    
    async def connect(self):
        """连接到 LittleMouse 服务器"""
        print("🐭 LittleMouse SSE 客户端启动")
        print("🌐 准备连接到服务器...")
        
        # 首先检测服务器
        if not await self.find_server():
            print("\n💡 请确保服务器已启动：")
            print("   python LittleMouse_server.py")
            print("\n📋 如果服务器在其他端口，请检查启动日志中的端口信息")
            return
        
        print(f"\n🎯 找到服务器: {self.server_url}")
        
        try:
            # 使用 SSE 客户端连接
            async with sse_client(self.server_url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    self.session = session
                    
                    # 初始化连接
                    await session.initialize()
                    print("✅ 成功连接到 LittleMouse 服务器")
                    
                    # 运行演示
                    await self.run_demo()
                    
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print(f"📝 错误类型: {type(e).__name__}")
            
            # 提供更详细的诊断
            import traceback
            print("\n🔧 详细错误信息:")
            traceback.print_exc()
    
    async def run_demo(self):
        """运行演示功能"""
        print("\n" + "="*50)
        print("🐭 LittleMouse 客户端演示")
        print("="*50)
        
        # 1. 测试服务器连通性
        await self.test_ping()
        
        # 2. 列出可用工具
        await self.list_tools()
        
        # 3. 测试工具调用
        await self.test_tools()
        
        # 4. 列出可用资源
        await self.list_resources()
        
        # 5. 读取资源
        await self.read_resources()
        
        # 6. 列出可用提示
        await self.list_prompts()
    
    async def test_ping(self):
        """测试服务器连通性"""
        print("\n🏓 测试服务器连通性:")
        try:
            # 改为测试一个简单的工具调用来验证连接
            result = await self.session.call_tool("say_hello", {"name": "连接测试"})
            print("  ✅ 服务器响应正常")
            return True
        except Exception as e:
            print(f"  ❌ 连接测试失败: {e}")
            return False
    async def list_tools(self):
        """列出可用工具"""
        print("\n🔧 可用工具:")
        try:
            tools_response = await self.session.list_tools()
            for i, tool in enumerate(tools_response.tools, 1):
                print(f"  {i}. {tool.name}")
                print(f"     描述: {tool.description}")
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
    
    async def test_tools(self):
        """测试工具调用"""
        print("\n🧪 测试工具调用:")
        
        # 测试 say_hello
        try:
            result = await self.session.call_tool("say_hello", {"name": "开发者"})
            print(f"  📞 say_hello 结果: {self._format_result(result)}")
        except Exception as e:
            print(f"❌ say_hello 调用失败: {e}")
        
        # 测试 add_numbers
        try:
            result = await self.session.call_tool("add_numbers", {"a": 123, "b": 456})
            print(f"  🔢 add_numbers 结果: {self._format_result(result)}")
        except Exception as e:
            print(f"❌ add_numbers 调用失败: {e}")
        
        # 测试 get_mouse_info
        try:
            result = await self.session.call_tool("get_mouse_info", {})
            print(f"  🐭 get_mouse_info 结果: {self._format_result(result)}")
        except Exception as e:
            print(f"❌ get_mouse_info 调用失败: {e}")
    
    def _format_result(self, result):
        """格式化工具调用结果"""
        try:
            if hasattr(result, 'content') and result.content:
                if hasattr(result.content[0], 'text'):
                    return result.content[0].text
            return str(result)
        except:
            return str(result)
    
    async def list_resources(self):
        """列出可用资源"""
        print("\n📚 可用资源:")
        try:
            resources_response = await self.session.list_resources()
            for i, resource in enumerate(resources_response.resources, 1):
                print(f"  {i}. {resource.uri}")
                if hasattr(resource, 'name') and resource.name:
                    print(f"     名称: {resource.name}")
                if hasattr(resource, 'description') and resource.description:
                    print(f"     描述: {resource.description}")
        except Exception as e:
            print(f"❌ 获取资源列表失败: {e}")
    
    async def read_resources(self):
        """读取资源内容"""
        print("\n📖 读取资源内容:")
        
        resources = ["mouse://status", "mouse://config"]
        
        for uri in resources:
            try:
                result = await self.session.read_resource(uri)
                print(f"  📄 {uri}:")
                if hasattr(result, 'contents') and result.contents:
                    for content in result.contents:
                        if hasattr(content, 'text'):
                            print(f"     内容: {content.text}")
                else:
                    print(f"     内容: {result}")
            except Exception as e:
                print(f"❌ 读取资源 {uri} 失败: {e}")
    
    async def list_prompts(self):
        """列出可用提示"""
        print("\n💭 可用提示:")
        try:
            prompts_response = await self.session.list_prompts()
            for i, prompt in enumerate(prompts_response.prompts, 1):
                print(f"  {i}. {prompt.name}")
                if hasattr(prompt, 'description') and prompt.description:
                    print(f"     描述: {prompt.description}")
        except Exception as e:
            print(f"❌ 获取提示列表失败: {e}")

async def main():
    """主函数"""
    client = LittleMouseClient()
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())