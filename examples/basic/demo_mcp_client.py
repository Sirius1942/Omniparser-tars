#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastMCP 图像元素分析器客户端演示
展示如何调用服务器的各种功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import asyncio
import base64
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    from mcp.types import CallToolRequest, Tool
except ImportError:
    print("❌ 缺少 MCP 客户端库，请安装: pip install mcp")
    exit(1)


class FastMCPImageAnalyzerClient:
    """FastMCP 图像分析器客户端"""
    
    def __init__(self, server_url: str = "http://localhost:8999/sse"):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        
    async def connect(self):
        """连接到 FastMCP 服务器"""
        try:
            print(f"🔗 正在连接到服务器: {self.server_url}")
            
            # 创建 SSE 客户端连接
            async with sse_client(self.server_url) as client_params:
                self.session = ClientSession(
                    client_params.read,
                    client_params.write
                )
                
                # 初始化会话
                await self.session.initialize()
                print("✅ 成功连接到 FastMCP 服务器")
                
                return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            try:
                await self.session.close()
                print("🔌 已断开连接")
            except Exception as e:
                print(f"⚠️ 断开连接时出错: {e}")
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用的工具"""
        try:
            print("\n📋 获取可用工具列表...")
            tools = await self.session.list_tools()
            
            print(f"✅ 找到 {len(tools.tools)} 个可用工具:")
            for tool in tools.tools:
                print(f"   🛠️  {tool.name}: {tool.description}")
            
            return {"success": True, "tools": tools.tools}
            
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_resources(self) -> Dict[str, Any]:
        """列出可用的资源"""
        try:
            print("\n📚 获取可用资源列表...")
            resources = await self.session.list_resources()
            
            print(f"✅ 找到 {len(resources.resources)} 个可用资源:")
            for resource in resources.resources:
                print(f"   📄 {resource.uri}: {resource.description}")
            
            return {"success": True, "resources": resources.resources}
            
        except Exception as e:
            print(f"❌ 获取资源列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            print("\n🖥️ 获取设备状态...")
            
            request = CallToolRequest(
                method="tools/call",
                params={
                    "name": "get_device_status",
                    "arguments": {}
                }
            )
            
            result = await self.session.call_tool(request)
            
            if result.isError:
                print(f"❌ 获取设备状态失败: {result.error}")
                return {"success": False, "error": result.error}
            
            device_info = json.loads(result.content[0].text)
            print("✅ 设备状态:")
            print(f"   设备类型: {device_info.get('device_info', {}).get('device', 'Unknown')}")
            print(f"   CUDA可用: {device_info.get('device_info', {}).get('cuda_available', False)}")
            print(f"   分析器状态: {'已初始化' if device_info.get('analyzer_status', {}).get('initialized', False) else '未初始化'}")
            
            return {"success": True, "data": device_info}
            
        except Exception as e:
            print(f"❌ 获取设备状态失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_image_file(self, image_path: str, box_threshold: float = 0.05) -> Dict[str, Any]:
        """分析图像文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"❌ 图像文件不存在: {image_path}")
                return {"success": False, "error": f"文件不存在: {image_path}"}
            
            print(f"\n🖼️ 分析图像文件: {os.path.basename(image_path)}")
            print(f"   路径: {image_path}")
            print(f"   阈值: {box_threshold}")
            
            request = CallToolRequest(
                method="tools/call",
                params={
                    "name": "analyze_image_file",
                    "arguments": {
                        "image_path": image_path,
                        "box_threshold": box_threshold,
                        "save_annotated": True,
                        "output_dir": "./results"
                    }
                }
            )
            
            result = await self.session.call_tool(request)
            
            if result.isError:
                print(f"❌ 分析失败: {result.error}")
                return {"success": False, "error": result.error}
            
            analysis_result = json.loads(result.content[0].text)
            
            if analysis_result.get("success", False):
                print("✅ 分析完成!")
                element_count = analysis_result.get("element_count", {})
                print(f"   📊 检测结果:")
                print(f"      文本元素: {element_count.get('text', 0)} 个")
                print(f"      图标元素: {element_count.get('icon', 0)} 个")
                print(f"      总元素: {element_count.get('total', 0)} 个")
                
                if analysis_result.get("annotated_image"):
                    print(f"   💾 标注图像: {analysis_result['annotated_image']}")
                if analysis_result.get("results_csv"):
                    print(f"   📄 结果文件: {analysis_result['results_csv']}")
            else:
                print(f"❌ 分析失败: {analysis_result.get('error', 'Unknown error')}")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ 分析图像时出错: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_image_base64(self, image_path: str, box_threshold: float = 0.05) -> Dict[str, Any]:
        """将图像转换为 Base64 并分析"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"❌ 图像文件不存在: {image_path}")
                return {"success": False, "error": f"文件不存在: {image_path}"}
            
            print(f"\n📤 Base64 分析图像: {os.path.basename(image_path)}")
            
            # 读取图像并转换为 Base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            print(f"   📦 Base64 大小: {len(image_base64)} 字符")
            
            request = CallToolRequest(
                method="tools/call",
                params={
                    "name": "analyze_image_base64",
                    "arguments": {
                        "image_base64": image_base64,
                        "box_threshold": box_threshold,
                        "save_annotated": True,
                        "output_dir": "./results"
                    }
                }
            )
            
            result = await self.session.call_tool(request)
            
            if result.isError:
                print(f"❌ Base64 分析失败: {result.error}")
                return {"success": False, "error": result.error}
            
            analysis_result = json.loads(result.content[0].text)
            
            if analysis_result.get("success", False):
                print("✅ Base64 分析完成!")
                element_count = analysis_result.get("element_count", {})
                print(f"   📊 检测结果:")
                print(f"      文本元素: {element_count.get('text', 0)} 个")
                print(f"      图标元素: {element_count.get('icon', 0)} 个")
            else:
                print(f"❌ Base64 分析失败: {analysis_result.get('error', 'Unknown error')}")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Base64 分析时出错: {e}")
            return {"success": False, "error": str(e)}
    
    async def batch_analyze_images(self, image_paths: list, box_threshold: float = 0.05) -> Dict[str, Any]:
        """批量分析多个图像"""
        try:
            print(f"\n🔄 批量分析 {len(image_paths)} 个图像...")
            
            # 过滤存在的文件
            existing_paths = [path for path in image_paths if os.path.exists(path)]
            if len(existing_paths) != len(image_paths):
                missing = len(image_paths) - len(existing_paths)
                print(f"⚠️ 跳过 {missing} 个不存在的文件")
            
            if not existing_paths:
                print("❌ 没有有效的图像文件")
                return {"success": False, "error": "没有有效的图像文件"}
            
            for i, path in enumerate(existing_paths, 1):
                print(f"   [{i}/{len(existing_paths)}] {os.path.basename(path)}")
            
            request = CallToolRequest(
                method="tools/call",
                params={
                    "name": "batch_analyze_images",
                    "arguments": {
                        "image_paths": existing_paths,
                        "box_threshold": box_threshold,
                        "save_annotated": True,
                        "output_dir": "./results"
                    }
                }
            )
            
            result = await self.session.call_tool(request)
            
            if result.isError:
                print(f"❌ 批量分析失败: {result.error}")
                return {"success": False, "error": result.error}
            
            batch_result = json.loads(result.content[0].text)
            
            if batch_result.get("success", False):
                print("✅ 批量分析完成!")
                print(f"   📊 处理统计:")
                print(f"      总图像: {batch_result.get('total_images', 0)} 个")
                print(f"      成功: {batch_result.get('success_count', 0)} 个")
                print(f"      失败: {batch_result.get('failed_count', 0)} 个")
            else:
                print(f"❌ 批量分析失败: {batch_result.get('error', 'Unknown error')}")
            
            return batch_result
            
        except Exception as e:
            print(f"❌ 批量分析时出错: {e}")
            return {"success": False, "error": str(e)}


async def main():
    """主函数 - 运行演示"""
    
    print("🎯 FastMCP 图像元素分析器客户端演示")
    print("=" * 60)
    
    # 创建客户端
    client = FastMCPImageAnalyzerClient()
    
    try:
        # 连接到服务器
        if not await client.connect():
            print("❌ 无法连接到服务器，请确保服务器正在运行")
            return
        
        # 1. 列出可用工具和资源
        await client.list_tools()
        await client.list_resources()
        
        # 2. 获取设备状态
        await client.get_device_status()
        
        # 3. 查找演示图像
        demo_images = []
        image_dirs = ["imgs", "screenshots", "."]
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
        
        for img_dir in image_dirs:
            if os.path.exists(img_dir):
                for file in os.listdir(img_dir):
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        demo_images.append(os.path.join(img_dir, file))
        
        if not demo_images:
            print("\n⚠️ 未找到演示图像，跳过图像分析演示")
        else:
            print(f"\n📸 找到 {len(demo_images)} 个演示图像:")
            for img in demo_images[:5]:  # 只显示前5个
                print(f"   🖼️  {img}")
            
            # 选择第一个图像进行演示
            test_image = demo_images[0]
            
            # 4. 演示图像文件分析
            await client.analyze_image_file(test_image, box_threshold=0.05)
            
            # 5. 演示 Base64 分析
            await client.analyze_image_base64(test_image, box_threshold=0.1)
            
            # 6. 演示批量分析（最多3个图像）
            if len(demo_images) > 1:
                batch_images = demo_images[:3]
                await client.batch_analyze_images(batch_images, box_threshold=0.08)
        
        print("\n🎉 演示完成!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
    finally:
        # 断开连接
        await client.disconnect()


if __name__ == "__main__":
    print("🚀 启动 FastMCP 客户端演示...")
    print("请确保 FastMCP 服务器正在运行在 http://localhost:8999")
    print("启动命令: python image_element_analyzer_fastmcp_server.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见!")
    except Exception as e:
        print(f"\n💥 程序异常退出: {e}") 