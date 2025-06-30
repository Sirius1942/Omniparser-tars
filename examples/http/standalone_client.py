#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立图像分析器客户端
使用 HTTP API 调用图像分析服务

功能特性:
- 支持文件路径和Base64图像分析
- 自动发现项目中的测试图像
- 下载标注图像
- 显示详细的分析结果统计
- 支持多种图像格式 (PNG, JPG, JPEG)

使用方法:
1. 启动服务器:
   python examples/http/standalone_image_analyzer.py

2. 运行客户端:
   python examples/http/standalone_client.py

3. 从项目根目录运行:
   python examples/http/standalone_client.py

API端点:
- GET  /health - 健康检查
- POST /analyze_file - 分析图像文件
- POST /analyze_base64 - 分析Base64图像
- GET  /annotated_image/<filename> - 获取标注图像
- GET  /results - 列出分析结果

依赖要求:
- requests
- Pillow (PIL)
- 运行中的图像分析服务器
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import requests
import json
import os
import base64
import time
from typing import Dict, Any

class ImageAnalyzerClient:
    """图像分析器 HTTP 客户端"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url.rstrip('/')
        
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_image_file(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """分析图像文件"""
        try:
            data = {
                "image_path": image_path,
                **kwargs
            }
            
            response = requests.post(
                f"{self.server_url}/analyze_file",
                json=data,
                timeout=60
            )
            
            return response.json()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_image_base64(self, image_base64: str, **kwargs) -> Dict[str, Any]:
        """分析 Base64 图像"""
        try:
            data = {
                "image_base64": image_base64,
                **kwargs
            }
            
            response = requests.post(
                f"{self.server_url}/analyze_base64",
                json=data,
                timeout=60
            )
            
            return response.json()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_annotated_image(self, filename: str, save_path: str = None) -> bool:
        """获取标注图像"""
        try:
            response = requests.get(
                f"{self.server_url}/annotated_image/{filename}",
                timeout=30
            )
            
            if response.status_code == 200:
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return True
                else:
                    return response.content
            else:
                return False
                
        except Exception as e:
            print(f"获取标注图像失败: {e}")
            return False
    
    def list_results(self) -> Dict[str, Any]:
        """列出分析结果"""
        try:
            response = requests.get(f"{self.server_url}/results", timeout=10)
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}


def display_analysis_result(result: Dict[str, Any]):
    """显示分析结果"""
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


def main():
    """主函数"""
    print("🎯 独立图像分析器客户端")
    print("=" * 50)
    
    # 测试图像路径 - 相对于项目根目录（按优先级排序）
    test_images = [
        os.path.join(project_root, "screenshots/screenshot_20250625_074204.png"),
        os.path.join(project_root, "imgs/word.png"),
        os.path.join(project_root, "imgs/windows_home.png"),
        os.path.join(project_root, "imgs/google_page.png"),
        os.path.join(project_root, "imgs/demo_image.jpg"),
        os.path.join(project_root, "imgs/excel.png")
    ]
    
    # 找到所有存在的测试图像
    available_images = []
    for img_path in test_images:
        if os.path.exists(img_path):
            available_images.append(img_path)
    
    # 选择第一个可用的图像作为主测试图像
    test_image = available_images[0] if available_images else None
    
    # 创建客户端
    client = ImageAnalyzerClient()
    
    try:
        # 1. 健康检查
        print("🔍 检查服务器状态...")
        health = client.health_check()
        if health.get("status") == "healthy":
            print("✅ 服务器运行正常")
            device_info = health.get("device_info", {})
            print(f"   🖥️  设备: {device_info.get('device', 'unknown')}")
            if device_info.get("cuda_available"):
                print(f"   🎮 GPU: {device_info.get('gpu_name', 'unknown')}")
            else:
                print("   💻 使用 CPU 模式")
            
            analyzer_ready = health.get("analyzer_ready", False)
            print(f"   🤖 分析器状态: {'就绪' if analyzer_ready else '未初始化'}")
        else:
            print(f"❌ 服务器状态异常: {health.get('error', '未知错误')}")
            return
        
        # 2. 显示可用图像
        if available_images:
            print(f"\n📂 找到 {len(available_images)} 个可用的测试图像:")
            for i, img_path in enumerate(available_images):
                file_size = os.path.getsize(img_path)
                size_mb = file_size / (1024 * 1024)
                print(f"   {i+1}. {os.path.relpath(img_path, project_root)} ({size_mb:.2f} MB)")
        
        # 3. 分析测试图像
        if test_image:
            print(f"\n📸 使用主测试图像: {os.path.relpath(test_image, project_root)}")
            
            analysis_result = client.analyze_image_file(
                test_image,
                box_threshold=0.05,
                save_annotated=True,
                output_dir="./results"
            )
            
            display_analysis_result(analysis_result)
            
            # 获取标注图像
            if analysis_result.get("success") and analysis_result.get("annotated_image_path"):
                annotated_filename = os.path.basename(analysis_result["annotated_image_path"])
                print(f"\n📥 下载标注图像: {annotated_filename}")
                
                download_path = f"downloaded_{annotated_filename}"
                success = client.get_annotated_image(annotated_filename, download_path)
                if success:
                    print(f"✅ 标注图像已下载到: {download_path}")
                    file_size = os.path.getsize(download_path)
                    print(f"   📊 文件大小: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
                else:
                    print("❌ 下载标注图像失败")
        else:
            print("⚠️ 未找到任何测试图像!")
            print("   尝试查找的路径:")
            for img_path in test_images:
                status = "✅ 存在" if os.path.exists(img_path) else "❌ 不存在"
                print(f"     • {os.path.relpath(img_path, project_root)} - {status}")
            
            # 演示 Base64 分析
            print("\n💡 演示 Base64 图像分析...")
            
            # 创建一个简单的测试图像
            from PIL import Image, ImageDraw
            test_img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(test_img)
            draw.text((50, 50), "测试图像", fill='black')
            draw.rectangle([300, 50, 350, 100], outline='blue', width=2)
            
            # 转换为 Base64
            import io
            buffer = io.BytesIO()
            test_img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # 分析 Base64 图像
            base64_result = client.analyze_image_base64(
                img_base64,
                box_threshold=0.05,
                save_annotated=True,
                output_dir="./results"
            )
            
            print("📊 Base64 图像分析结果:")
            display_analysis_result(base64_result)
        
        # 3. 列出分析结果
        print("\n📁 列出分析结果...")
        results = client.list_results()
        if results.get("success"):
            files = results.get("files", [])
            print(f"✅ 找到 {len(files)} 个结果文件:")
            for file_info in files[:10]:  # 显示前10个文件
                print(f"   • {file_info['name']} ({file_info['size']} bytes)")
        else:
            print(f"❌ 获取结果列表失败: {results.get('error')}")
        
        print("\n🎉 演示完成!")
        print("\n💡 使用提示:")
        print("   • 通过浏览器访问 http://localhost:8080/health 查看服务状态")
        print("   • 使用不同参数分析图像:")
        print("     client.analyze_image_file(image_path, box_threshold=0.1)")
        print("   • 支持的图像格式: PNG, JPG, JPEG")
        print("   • 服务器需要先启动: python examples/http/standalone_image_analyzer.py")
        
    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")


if __name__ == "__main__":
    main() 