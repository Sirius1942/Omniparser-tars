#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phoenix Scout FastMCP Client - 凤凰侦察FastMCP客户端
连接到已运行的Phoenix Vision FastMCP SSE服务器
🔥 Phoenix Scout - 涅槃重生的智能侦察者
"""

import os
import sys
import asyncio
import json
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ✅ 正确的MCP客户端实现
try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    print("✅ MCP 库导入成功")
except ImportError:
    print("❌ MCP 库未安装，请运行: pip install mcp")
    sys.exit(1)

class PhoenixScoutFastMCPClient:
    """🔥 Phoenix Scout FastMCP Client - 凤凰侦察FastMCP客户端"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8923"):
        self.server_url = server_url.rstrip('/')
        self.sse_url = f"{self.server_url}/sse/"
        self.session = None          # ClientSession 实例
        self.sse_context = None      # SSE 连接上下文
        self.connected = False
        
    async def connect(self, timeout: float = 1800.0) -> bool:
        """连接到已运行的FastMCP SSE服务器"""
        try:
            print(f"🔗 连接到 Phoenix Vision FastMCP 服务器: {self.sse_url}")
            print(f"⏰ 连接超时设置: {timeout/60:.1f}分钟")
            # 建立 SSE 连接
            print("🔍 建立 SSE 连接...")
            self.sse_context = sse_client(self.sse_url)
            read_stream, write_stream = await self.sse_context.__aenter__()
            
            # 创建客户端会话
            print("🔄 创建客户端会话...")
            self.session = ClientSession(read_stream, write_stream)
            
            # 初始化会话
            print("🚀 初始化会话...")
            init_result = await asyncio.wait_for(
                self.session.initialize(), 
                timeout=timeout
            )
            
            # 连接成功
            self.connected = True
            print("✅ FastMCP SSE 连接成功")
            print(f"   服务器: {init_result.server_info.name}")
            print(f"   版本: {init_result.server_info.version}")
            
            return True
            
        except asyncio.TimeoutError:
            print(f"❌ 连接超时 ({timeout/60:.1f}分钟)")
            print("💡 可能的原因: 服务器响应慢或网络问题")
            return False
            
        except ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            print("💡 请确保服务器正在运行在正确的端口")
            return False
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print(f"📍 尝试连接的地址: {self.sse_url}")
            
            # 额外的调试信息
            import traceback
            print("🔍 详细错误信息:")
            traceback.print_exc()
            
            # 尝试基本的连接测试
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.server_url}/", timeout=3.0)
                    print(f"🔍 服务器基本响应: HTTP {response.status_code}")
            except Exception as test_e:
                print(f"🔍 服务器连接测试失败: {test_e}")
            
            return False

    async def disconnect(self):
        """断开连接"""
        try:
            print("🧹 正在断开连接...")
            
            if self.session:
                # 关闭会话
                self.session = None
                print("   ✅ 会话已关闭")
            
            if self.sse_context:
                # 关闭 SSE 连接
                await self.sse_context.__aexit__(None, None, None)
                self.sse_context = None
                print("   ✅ SSE 连接已关闭")
            
            self.connected = False
            print("🧹 连接已完全断开")
            
        except Exception as e:
            print(f"⚠️ 断开连接时出错: {e}")
            # 强制重置状态
            self.session = None
            self.sse_context = None
            self.connected = False
    
    async def call_tool_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """通过真正的MCP协议调用工具"""
        if not self.connected or not self.session:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            print(f"🔧 调用工具: {tool_name}")
            print(f"📝 参数: {arguments}")
            
            # 真正的 MCP 工具调用
            result = await self.session.call_tool(tool_name, arguments)
            
            # 解析结果
            if hasattr(result, 'content') and result.content:
                content_data = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        try:
                            # 尝试解析 JSON
                            parsed = json.loads(content.text)
                            content_data.append(parsed)
                        except json.JSONDecodeError:
                            # 如果不是 JSON，直接使用文本
                            content_data.append(content.text)
                
                return {"success": True, "result": content_data}
            else:
                return {"success": True, "result": "工具执行完成，但无返回内容"}
                
        except Exception as e:
            print(f"❌ 工具调用失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    # 更新获取设备状态方法
    async def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        print("🖥️ 获取设备状态...")
        return await self.call_tool_mcp("get_device_status", {})

    # 更新图像分析方法
    async def analyze_image_file(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """分析图像文件"""
        if not os.path.exists(image_path):
            return {"success": False, "error": f"文件不存在: {image_path}"}
        
        print(f"🖼️ 分析图像文件: {os.path.basename(image_path)}")
        
        # 设置默认参数
        arguments = {
            "image_path": image_path,
            "box_threshold": 0.05,
            "save_annotated": True,
            "output_dir": "./results"
        }
        arguments.update(kwargs)
        
        return await self.call_tool_mcp("analyze_image_file", arguments)
        
    async def get_device_status(self) -> Dict[str, Any]:
            """获取设备状态"""
            print("🖥️ 获取设备状态...")
            return await self.call_tool_via_sse("get_device_status", {})
        
    async def analyze_image_file(self, image_path: str, **kwargs) -> Dict[str, Any]:
            """分析图像文件"""
            if not os.path.exists(image_path):
                return {"success": False, "error": f"文件不存在: {image_path}"}
            
            print(f"🖼️ 分析图像文件: {os.path.basename(image_path)}")
            
            # 设置默认参数
            arguments = {
                "image_path": image_path,
                "box_threshold": 0.05,
                "save_annotated": True,
                "output_dir": "./results"
            }
            arguments.update(kwargs)
            
            return await self.call_tool_via_sse("analyze_image_file", arguments)
    
def display_result(result_data):
    """显示结果"""
    if isinstance(result_data, dict):
        if result_data.get("success"):
            # 显示端点测试结果
            if "endpoints" in result_data:
                print("✅ 服务器端点测试")
                print(f"   🌐 服务器地址: {result_data.get('server_url')}")
                endpoints = result_data["endpoints"]
                for endpoint, info in endpoints.items():
                    status = info.get("status_code", "UNKNOWN")
                    accessible = "✅" if info.get("accessible") else "❌"
                    print(f"   {accessible} {endpoint}: {status}")
                return
            
            # 显示其他结果
            data = result_data.get("result", {})
            print("✅ 执行成功")
            
            # 显示设备信息
            if "device_info" in data:
                device_info = data["device_info"]
                print(f"   🖥️  设备: {device_info.get('device', 'Unknown')}")
                print(f"   🎮 CUDA: {'可用' if device_info.get('cuda_available') else '不可用'}")
                print(f"   🌐 平台: {device_info.get('platform', 'Unknown')}")
                if device_info.get('cuda_available'):
                    print(f"   🎯 GPU: {device_info.get('gpu_name', 'Unknown')}")
            
            # 显示分析器状态
            if "analyzer_status" in data:
                analyzer_status = data["analyzer_status"]
                print(f"   📊 分析器: {'就绪' if analyzer_status.get('ready') else '未就绪'}")
            
            # 显示图像分析结果
            if "element_count" in data:
                element_count = data["element_count"]
                total = element_count.get("total", 0)
                text_count = element_count.get("text", 0)
                icon_count = element_count.get("icon", 0)
                print(f"   📊 检测到 {total} 个元素 (文本: {text_count}, 图标: {icon_count})")
            
            if "processing_time" in data:
                processing_time = data["processing_time"]
                if isinstance(processing_time, dict):
                    total_time = processing_time.get("total", 0)
                else:
                    total_time = processing_time
                print(f"   ⏱️  处理耗时: {total_time:.2f}秒")
            
            if "annotated_image_path" in data:
                print(f"   📸 标注图像: {data['annotated_image_path']}")
                
        else:
            print(f"❌ 执行失败: {result_data.get('error')}")
    else:
        print(f"📝 结果: {result_data}")


async def main():
    """主函数 - 连接到已运行的服务器"""
    print("🔥 Phoenix Scout FastMCP Client")
    print("🔗 连接到已运行的服务器模式")
    print("=" * 50)
    
    # 创建客户端
    client = PhoenixScoutFastMCPClient()
    
    try:
        # 1. 连接到服务器
        if not await client.connect():
            print("❌ 无法连接到服务器")
            print("💡 请先启动服务器: python start_phoenix_vision.py")
            return
        
        # 2. 测试服务器端点
        # endpoints_result = await client.test_server_endpoints()
        # display_result(endpoints_result)
        
        # 3. 获取设备状态
        print(f"\n🖥️ 设备状态:")
        device_result = await client.get_device_status()
        display_result(device_result)
        
        # 4. 尝试分析图像
        test_images = [
            os.path.join(project_root, "screenshots/screenshot_20250625_074204.png"),
            os.path.join(project_root, "imgs/demo_image.jpg"),
            os.path.join(project_root, "imgs/google_page.png"),
            os.path.join(project_root, "imgs/windows_home.png")
        ]
        
        test_image = None
        for img_path in test_images:
            if os.path.exists(img_path):
                test_image = img_path
                break
        
        if test_image:
            print(f"\n📸 测试图像: {os.path.basename(test_image)}")
            analysis_result = await client.analyze_image_file(
                test_image,
                box_threshold=0.05,
                save_annotated=True
            )
            display_result(analysis_result)
        else:
            print(f"\n⚠️ 未找到测试图像")
        
        print("\n🎉 演示完成!")
        print("\n💡 提示:")
        print("   • 服务器正在运行，但需要正确的MCP协议客户端")
        print("   • 当前为实验性HTTP/SSE连接模式")
        print("   • 要完整使用功能，建议使用标准MCP客户端库")
        print("   • 服务器SSE端点: http://127.0.0.1:8923/sse/")
        
    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理连接
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())