#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
标准 MCP 协议图像分析客户端
符合 Model Context Protocol 标准规范
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
import base64
import subprocess
from typing import Dict, Any, Optional, List
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import CallToolRequest, ListToolsRequest

class MCPImageAnalyzerClient:
    """标准 MCP 图像分析客户端"""
    
    def __init__(self, server_script: str = "mcp_image_analyzer_server.py"):
        self.server_script = server_script
        self.session: Optional[ClientSession] = None
        self.stdio_context = None
        self.connected = False
        
    async def connect(self, timeout: float = 30.0) -> bool:
        """连接到 MCP 服务器"""
        try:
            print(f"🔗 启动 MCP 图像分析服务器: {self.server_script}")
            
            # 建立 stdio 连接
            print("🔍 建立 stdio 连接...")
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script]
            )
            self.stdio_context = stdio_client(server_params)
            read_stream, write_stream = await self.stdio_context.__aenter__()
            
            print("✅ stdio 连接建立成功")
            
            # 创建客户端会话
            print("🔍 创建 MCP 会话...")
            self.session = ClientSession(read_stream, write_stream)
            
            # 初始化会话
            print("🔄 初始化 MCP 会话...")
            init_result = await asyncio.wait_for(self.session.initialize(), timeout=timeout)
            
            self.connected = True
            print("✅ MCP 连接成功")
            print(f"   服务器: {init_result.server_info.name}")
            print(f"   版本: {init_result.server_info.version}")
            
            return True
            
        except asyncio.TimeoutError:
            print(f"❌ 连接超时 ({timeout}秒)")
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        try:
            if self.session:
                self.session = None
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
            self.connected = False
            print("🧹 连接已断开")
        except Exception as e:
            print(f"⚠️ 断开连接时出错: {e}")
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        if not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print("\n📋 获取工具列表...")
            result = await self.session.list_tools()
            
            tools = []
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "schema": tool.inputSchema
                })
            
            print(f"✅ 找到 {len(tools)} 个工具")
            return {"success": True, "tools": tools}
            
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print(f"🔧 调用工具: {tool_name}")
            
            # 创建工具调用请求
            request = CallToolRequest(
                method="tools/call",
                params={"name": tool_name, "arguments": arguments}
            )
            
            # 调用工具
            result = await self.session.call_tool(request)
            
            # 解析结果
            if hasattr(result, 'content') and result.content:
                content_data = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        try:
                            parsed = json.loads(content.text)
                            content_data.append(parsed)
                        except json.JSONDecodeError:
                            content_data.append(content.text)
                
                return {"success": True, "result": content_data}
            else:
                return {"success": True, "result": "工具执行完成"}
                
        except Exception as e:
            print(f"❌ 工具调用失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_image_file(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """分析图像文件"""
        if not os.path.exists(image_path):
            return {"success": False, "error": f"文件不存在: {image_path}"}
        
        print(f"\n🖼️ 分析图像文件: {os.path.basename(image_path)}")
        
        arguments = {"image_path": image_path}
        arguments.update(kwargs)
        
        return await self.call_tool("analyze_image_file", arguments)
    
    async def analyze_image_base64(self, image_base64: str, **kwargs) -> Dict[str, Any]:
        """分析 Base64 图像"""
        print(f"\n🖼️ 分析 Base64 图像...")
        
        arguments = {"image_base64": image_base64}
        arguments.update(kwargs)
        
        return await self.call_tool("analyze_image_base64", arguments)
    
    async def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        print("\n🖥️ 获取设备状态...")
        return await self.call_tool("get_device_status", {})
    
    async def list_resources(self) -> Dict[str, Any]:
        """列出可用资源"""
        if not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print("\n📚 获取资源列表...")
            result = await self.session.list_resources()
            
            resources = []
            for resource in result.resources:
                resources.append({
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                })
            
            print(f"✅ 找到 {len(resources)} 个资源")
            return {"success": True, "resources": resources}
            
        except Exception as e:
            print(f"❌ 获取资源列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """获取资源内容"""
        if not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print(f"\n📄 获取资源: {uri}")
            result = await self.session.read_resource(uri)
            
            # 解析资源内容
            content = ""
            if hasattr(result, 'contents') and result.contents:
                for content_item in result.contents:
                    if hasattr(content_item, 'text'):
                        content += content_item.text
            
            return {"success": True, "content": content}
            
        except Exception as e:
            print(f"❌ 获取资源失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_prompts(self) -> Dict[str, Any]:
        """列出可用提示"""
        if not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print("\n💡 获取提示列表...")
            result = await self.session.list_prompts()
            
            prompts = []
            for prompt in result.prompts:
                prompts.append({
                    "name": prompt.name,
                    "description": prompt.description,
                    "arguments": prompt.arguments
                })
            
            print(f"✅ 找到 {len(prompts)} 个提示")
            return {"success": True, "prompts": prompts}
            
        except Exception as e:
            print(f"❌ 获取提示列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_prompt(self, name: str, arguments: Dict[str, str] = None) -> Dict[str, Any]:
        """获取提示内容"""
        if not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print(f"\n💭 获取提示: {name}")
            result = await self.session.get_prompt(name, arguments or {})
            
            # 解析提示内容
            content = ""
            if hasattr(result, 'messages') and result.messages:
                for message in result.messages:
                    if hasattr(message, 'content') and message.content:
                        for content_item in message.content:
                            if hasattr(content_item, 'text'):
                                content += content_item.text
            
            return {"success": True, "content": content}
            
        except Exception as e:
            print(f"❌ 获取提示失败: {e}")
            return {"success": False, "error": str(e)}


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载配置文件失败: {e}")
        return {}


def display_analysis_result(result_data: List[Dict[str, Any]]):
    """显示分析结果"""
    for result in result_data:
        if isinstance(result, dict):
            if result.get("success"):
                print("✅ 分析成功")
                
                # 显示元素统计
                element_count = result.get("element_count", {})
                print(f"   📊 元素统计:")
                print(f"      • 文本元素: {element_count.get('text', 0)} 个")
                print(f"      • 图标元素: {element_count.get('icon', 0)} 个")
                print(f"      • 总计: {element_count.get('total', 0)} 个")
                
                # 显示处理时间
                processing_time = result.get("processing_time", {})
                if processing_time:
                    print(f"   ⏱️  处理耗时:")
                    print(f"      • OCR: {processing_time.get('ocr', 0):.2f}s")
                    print(f"      • 图标识别: {processing_time.get('caption', 0):.2f}s")
                    print(f"      • 总计: {processing_time.get('total', 0):.2f}s")
                
                # 显示标注图像路径
                if result.get("annotated_image_path"):
                    print(f"   📸 标注图像: {result['annotated_image_path']}")
                
                # 显示部分元素示例
                elements = result.get("elements", [])
                if elements:
                    print(f"   🔍 检测到的元素 (前5个):")
                    for i, element in enumerate(elements[:5]):
                        element_type = element.get("type", "unknown")
                        element_text = element.get("text", "").strip()
                        coordinates = element.get("coordinates", [])
                        
                        if element_text:
                            print(f"      {i+1}. [{element_type}] {element_text} @ {coordinates}")
                        else:
                            description = element.get("description", "")
                            print(f"      {i+1}. [{element_type}] {description} @ {coordinates}")
            else:
                print(f"❌ 分析失败: {result.get('error')}")
        else:
            print(f"📝 结果: {result}")


async def main():
    """主函数"""
    print("🎯 标准 MCP 协议图像分析客户端")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    
    # 测试图像路径
    test_image = "screenshots/screenshot_20250625_074204.png"
    
    # 创建客户端
    client = MCPImageAnalyzerClient()
    
    try:
        # 1. 连接到服务器
        if not await client.connect():
            print("❌ 无法连接到服务器")
            return
        
        # 2. 列出可用工具
        tools_result = await client.list_tools()
        if tools_result.get("success"):
            tools = tools_result["tools"]
            print(f"\n📋 可用工具:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")
        
        # 3. 列出可用资源
        resources_result = await client.list_resources()
        if resources_result.get("success"):
            resources = resources_result["resources"]
            print(f"\n📚 可用资源:")
            for resource in resources:
                print(f"   • {resource['name']}: {resource['description']}")
        
        # 4. 列出可用提示
        prompts_result = await client.list_prompts()
        if prompts_result.get("success"):
            prompts = prompts_result["prompts"]
            print(f"\n💡 可用提示:")
            for prompt in prompts:
                print(f"   • {prompt['name']}: {prompt['description']}")
        
        # 5. 获取设备状态
        device_result = await client.get_device_status()
        if device_result.get("success"):
            print("✅ 设备状态获取成功")
            display_analysis_result(device_result["result"])
        
        # 6. 分析测试图像
        if os.path.exists(test_image):
            print(f"\n📸 测试图像: {test_image}")
            analysis_result = await client.analyze_image_file(
                test_image,
                box_threshold=0.05,
                save_annotated=True,
                output_dir="./results"
            )
            
            if analysis_result.get("success"):
                print("✅ 图像分析完成")
                display_analysis_result(analysis_result["result"])
            else:
                print(f"❌ 图像分析失败: {analysis_result.get('error')}")
        else:
            print(f"⚠️ 测试图像不存在: {test_image}")
        
        # 7. 获取分析结果资源
        results_resource = await client.get_resource("file://results/")
        if results_resource.get("success"):
            print("\n📁 分析结果目录:")
            try:
                results_data = json.loads(results_resource["content"])
                print(f"   📂 目录: {results_data['directory']}")
                print(f"   📊 文件数: {results_data['count']}")
                for file_info in results_data.get("files", [])[:5]:  # 显示前5个文件
                    print(f"      • {file_info['name']} ({file_info['size']} bytes)")
            except:
                print(f"   📄 {results_resource['content']}")
        
        # 8. 获取分析提示
        tips_result = await client.get_prompt("analyze_image_tips", {"image_type": "screenshot"})
        if tips_result.get("success"):
            print("\n💡 图像分析提示:")
            print(tips_result["content"][:500] + "..." if len(tips_result["content"]) > 500 else tips_result["content"])
        
        print("\n🎉 演示完成!")
        
    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")
        
    finally:
        # 清理连接
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 