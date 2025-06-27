#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像元素分析器 MCP 客户端示例
演示如何使用 SSE 模式调用图片分析服务
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import asyncio
import aiohttp
import base64
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class ImageAnalyzerMCPClient:
    """图像分析器 MCP 客户端"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            server_url: MCP 服务器地址
        """
        self.server_url = server_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def check_health(self) -> Dict[str, Any]:
        """检查服务器健康状态"""
        async with self.session.get(f"{self.server_url}/health") as response:
            return await response.json()
    
    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        async with self.session.get(f"{self.server_url}/") as response:
            return await response.json()
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图像文件编码为 base64"""
        with open(image_path, "rb") as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
    
    async def analyze_image_upload(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        使用文件上传方式分析图像（同步）
        
        Args:
            image_path: 图像文件路径
            **kwargs: 其他分析参数
            
        Returns:
            dict: 分析结果
        """
        with open(image_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=Path(image_path).name)
            
            # 添加其他参数
            for key, value in kwargs.items():
                data.add_field(key, str(value))
            
            async with self.session.post(
                f"{self.server_url}/analyze/upload",
                data=data
            ) as response:
                return await response.json()
    
    async def analyze_image_async(self, image_path: str, **kwargs) -> str:
        """
        使用异步方式分析图像（返回任务ID）
        
        Args:
            image_path: 图像文件路径
            **kwargs: 其他分析参数
            
        Returns:
            str: 任务ID
        """
        # 编码图像
        image_base64 = self._encode_image_to_base64(image_path)
        
        # 构建请求数据
        request_data = {
            "image_base64": image_base64,
            **kwargs
        }
        
        async with self.session.post(
            f"{self.server_url}/analyze",
            json=request_data
        ) as response:
            result = await response.json()
            return result.get("task_id")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        async with self.session.get(f"{self.server_url}/status/{task_id}") as response:
            return await response.json()
    
    async def stream_analysis_progress(self, task_id: str, callback=None):
        """
        使用 SSE 流式获取分析进度
        
        Args:
            task_id: 任务ID
            callback: 进度回调函数，接收状态字典作为参数
        """
        url = f"{self.server_url}/analyze/stream/{task_id}"
        
        async with self.session.get(url) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                
                if line.startswith('data: '):
                    data_str = line[6:]  # 移除 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        
                        if callback:
                            await callback(data)
                        
                        # 如果任务完成，停止流
                        if data.get('status') in ['completed', 'failed']:
                            return data
                            
                    except json.JSONDecodeError:
                        print(f"⚠️ 无法解析数据: {data_str}")
                        continue
    
    async def analyze_with_progress(self, image_path: str, show_progress: bool = True, **kwargs) -> Dict[str, Any]:
        """
        分析图像并显示进度（使用 SSE）
        
        Args:
            image_path: 图像文件路径
            show_progress: 是否显示进度
            **kwargs: 其他分析参数
            
        Returns:
            dict: 最终分析结果
        """
        print(f"🚀 开始分析图像: {Path(image_path).name}")
        
        # 提交分析任务
        task_id = await self.analyze_image_async(image_path, **kwargs)
        print(f"📋 任务ID: {task_id}")
        
        # 定义进度回调
        async def progress_callback(status):
            if show_progress:
                progress = status.get('progress', 0)
                message = status.get('message', '')
                status_text = status.get('status', '')
                
                print(f"📊 [{status_text}] {progress}% - {message}")
        
        # 流式监听进度
        final_result = await self.stream_analysis_progress(task_id, progress_callback)
        
        if final_result.get('status') == 'completed':
            print("✅ 分析完成！")
            return final_result.get('result', {})
        else:
            print(f"❌ 分析失败: {final_result.get('error', 'Unknown error')}")
            return final_result


async def demo_client():
    """演示客户端使用"""
    print("🎯 图像元素分析器 MCP 客户端演示")
    print("=" * 50)
    
    # 测试图像
    test_images = [
        'imgs/word.png',
        'imgs/google_page.png',
        'imgs/windows_home.png'
    ]
    
    async with ImageAnalyzerMCPClient() as client:
        try:
            # 检查服务器状态
            print("🔍 检查服务器状态...")
            health = await client.check_health()
            print(f"   服务器状态: {health.get('status')}")
            print(f"   分析器就绪: {health.get('analyzer_ready')}")
            print(f"   设备: {health.get('device', {}).get('device')}")
            
            # 获取服务器信息
            server_info = await client.get_server_info()
            print(f"   服务版本: {server_info.get('version')}")
            
            if not health.get('analyzer_ready'):
                print("⚠️ 分析器未就绪，请等待初始化...")
                await asyncio.sleep(5)
            
            # 测试不同的分析方式
            for image_path in test_images:
                if not Path(image_path).exists():
                    print(f"⚠️ 跳过不存在的图像: {image_path}")
                    continue
                
                print(f"\n🖼️ 分析图像: {image_path}")
                print("-" * 40)
                
                # 方式1: 文件上传（同步）
                print("📤 方式1: 文件上传（同步）")
                start_time = time.time()
                result1 = await client.analyze_image_upload(
                    image_path,
                    box_threshold=0.05,
                    save_annotated=True,
                    output_dir="./results"
                )
                upload_time = time.time() - start_time
                
                if result1.get('success'):
                    element_count = result1.get('element_count', {})
                    print(f"   ✅ 同步分析完成 (耗时: {upload_time:.2f}s)")
                    print(f"   📊 检测元素: 总计{element_count.get('total', 0)} (文本:{element_count.get('text', 0)}, 图标:{element_count.get('icon', 0)})")
                else:
                    print(f"   ❌ 同步分析失败: {result1.get('error')}")
                
                # 方式2: 异步 + SSE 流式进度
                print("\n📡 方式2: 异步 + SSE 流式进度")
                start_time = time.time()
                result2 = await client.analyze_with_progress(
                    image_path,
                    box_threshold=0.05,
                    save_annotated=False,
                    verbose=False
                )
                async_time = time.time() - start_time
                
                if result2.get('success'):
                    element_count = result2.get('element_count', {})
                    print(f"   ✅ 异步分析完成 (总耗时: {async_time:.2f}s)")
                    print(f"   📊 检测元素: 总计{element_count.get('total', 0)} (文本:{element_count.get('text', 0)}, 图标:{element_count.get('icon', 0)})")
                    
                    # 显示一些识别结果
                    text_elements = result2.get('text_elements', [])[:3]
                    icon_elements = result2.get('icon_elements', [])[:3]
                    
                    if text_elements:
                        print("   📝 文本元素示例:")
                        for i, element in enumerate(text_elements, 1):
                            content = element.get('content', 'N/A')
                            print(f"      {i}. {content}")
                    
                    if icon_elements:
                        print("   🎯 图标元素示例:")
                        for i, element in enumerate(icon_elements, 1):
                            content = element.get('content', 'N/A')
                            print(f"      {i}. {content}")
                else:
                    print(f"   ❌ 异步分析失败: {result2.get('error')}")
                
                print("\n" + "="*60)
                await asyncio.sleep(1)  # 避免请求过于频繁
        
        except Exception as e:
            print(f"❌ 客户端错误: {e}")
            import traceback
            traceback.print_exc()


async def simple_analysis_example():
    """简单分析示例"""
    image_path = "imgs/demo_image.jpg"
    
    if not Path(image_path).exists():
        print(f"❌ 图像文件不存在: {image_path}")
        return
    
    async with ImageAnalyzerMCPClient() as client:
        # 检查服务器状态
        health = await client.check_health()
        if not health.get('analyzer_ready'):
            print("⚠️ 等待分析器初始化...")
            await asyncio.sleep(3)
        
        # 分析图像
        result = await client.analyze_with_progress(image_path)
        
        if result.get('success'):
            print("✅ 分析成功！")
            
            # 显示结果摘要
            element_count = result.get('element_count', {})
            print(f"📊 检测到 {element_count.get('total', 0)} 个元素")
            print(f"   - 文本: {element_count.get('text', 0)} 个")
            print(f"   - 图标: {element_count.get('icon', 0)} 个")
            
        else:
            print(f"❌ 分析失败: {result.get('error')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="图像元素分析器 MCP 客户端")
    parser.add_argument("--server", default="http://localhost:8000", help="MCP 服务器地址")
    parser.add_argument("--demo", action="store_true", help="运行完整演示")
    parser.add_argument("--simple", action="store_true", help="运行简单示例")
    parser.add_argument("--image", help="分析指定图像")
    
    args = parser.parse_args()
    
    if args.demo:
        asyncio.run(demo_client())
    elif args.simple:
        asyncio.run(simple_analysis_example())
    elif args.image:
        async def analyze_single():
            async with ImageAnalyzerMCPClient(args.server) as client:
                result = await client.analyze_with_progress(args.image)
                print(json.dumps(result, ensure_ascii=False, indent=2))
        
        asyncio.run(analyze_single())
    else:
        print("请指定 --demo, --simple 或 --image <路径>") 