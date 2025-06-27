#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTTP 客户端演示 - 绕过 MCP 协议直接调用服务器
这是一个简化的演示，展示如何调用 FastMCP 图像分析服务器
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import requests
import json
import base64
import os
from pathlib import Path


class HTTPFastMCPClient:
    """简化的 HTTP 客户端"""
    
    def __init__(self, base_url="http://localhost:8999"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def test_server_health(self):
        """测试服务器是否可达"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            print(f"✅ 服务器响应: HTTP {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 服务器连接失败: {e}")
            return False
    
    def analyze_image_file(self, image_path, analysis_types=None, include_ocr=True):
        """
        模拟调用 analyze_image_file 工具
        注意：这是模拟实现，实际的 MCP 服务器可能需要不同的 API 端点
        """
        if analysis_types is None:
            analysis_types = ["elements", "structure"]
            
        if not os.path.exists(image_path):
            return {"error": f"图片文件不存在: {image_path}"}
        
        # 读取图片并转换为 base64
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # 构造请求数据
            request_data = {
                "tool": "analyze_image_file",
                "arguments": {
                    "image_path": image_path,
                    "analysis_types": analysis_types,
                    "include_ocr": include_ocr
                }
            }
            
            print(f"📄 图片文件: {image_path}")
            print(f"📊 分析类型: {analysis_types}")
            print(f"🔤 包含OCR: {include_ocr}")
            print(f"📦 图片大小: {len(image_data)} 字节")
            
            # 这里是模拟的结果，因为实际的 MCP 服务器需要通过 MCP 协议调用
            mock_result = {
                "status": "success",
                "image_path": image_path,
                "image_size": {"width": 300, "height": 200},
                "analysis_types": analysis_types,
                "elements": [
                    {
                        "id": "element_1",
                        "type": "button",
                        "text": "Test Button",
                        "bbox": [20, 20, 280, 60],
                        "confidence": 0.95
                    },
                    {
                        "id": "element_2", 
                        "type": "button",
                        "text": "Another Element",
                        "bbox": [20, 80, 280, 120],
                        "confidence": 0.90
                    },
                    {
                        "id": "element_3",
                        "type": "text",
                        "text": "Sample Text Content",
                        "bbox": [20, 140, 200, 160],
                        "confidence": 0.88
                    }
                ],
                "ocr_text": "Test Button\nAnother Element\nSample Text Content" if include_ocr else None,
                "timestamp": "2025-01-26T12:00:00Z",
                "processing_time": 1.23,
                "device": "cpu"
            }
            
            return mock_result
            
        except Exception as e:
            return {"error": f"处理图片失败: {e}"}
    
    def get_device_status(self):
        """获取设备状态信息"""
        # 模拟设备状态
        mock_status = {
            "device": "cpu",
            "cuda_available": False,
            "gpu_count": 0,
            "python_version": "3.12.0",
            "torch_version": "2.0.0",
            "memory_usage": "1.2GB",
            "cpu_count": 8,
            "platform": "macOS"
        }
        return mock_status


def main():
    """主演示函数"""
    print("🎯 FastMCP 图像分析器 HTTP 客户端演示")
    print("=" * 60)
    
    client = HTTPFastMCPClient()
    
    # 1. 测试服务器连接
    print("\n1️⃣ 测试服务器连接...")
    if not client.test_server_health():
        print("💡 注意：由于 MCP 协议的限制，这是一个模拟演示")
        print("   实际的工具调用需要通过 MCP 协议进行")
    
    # 2. 获取设备状态
    print("\n2️⃣ 获取设备状态...")
    status = client.get_device_status()
    print("✅ 设备状态:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 3. 查找和分析图片
    print("\n3️⃣ 图片分析演示...")
    
    # 查找可用的图片文件
    test_images = ["demo.png", "test.png", "sample.jpg", "example.png"]
    found_images = [img for img in test_images if os.path.exists(img)]
    
    if found_images:
        image_path = found_images[0]
        print(f"📸 找到测试图片: {image_path}")
        
        # 分析图片
        result = client.analyze_image_file(
            image_path=image_path,
            analysis_types=["elements", "structure"],
            include_ocr=True
        )
        
        if "error" in result:
            print(f"❌ 分析失败: {result['error']}")
        else:
            print("✅ 分析完成:")
            print(f"   状态: {result['status']}")
            print(f"   图片尺寸: {result['image_size']['width']}x{result['image_size']['height']}")
            print(f"   处理时间: {result['processing_time']}秒")
            print(f"   设备: {result['device']}")
            
            elements = result.get('elements', [])
            print(f"   找到元素: {len(elements)} 个")
            
            for i, element in enumerate(elements, 1):
                print(f"     {i}. {element['type']}: '{element['text']}'")
                print(f"        位置: {element['bbox']}")
                print(f"        置信度: {element['confidence']:.2f}")
            
            if result.get('ocr_text'):
                print(f"   OCR文本: {result['ocr_text']}")
    else:
        print("📭 未找到测试图片")
        print("💡 您可以放置以下任一图片文件来测试分析:")
        print("   • demo.png")
        print("   • test.png") 
        print("   • sample.jpg")
        print("   • example.png")
    
    print(f"\n✅ 演示完成!")
    print("\n" + "="*60)
    print("📝 说明:")
    print("   这是一个模拟的 HTTP 客户端演示")
    print("   实际的 MCP 服务器需要通过 MCP 协议调用")
    print("   要使用真正的 MCP 客户端，请运行:")
    print("   python working_mcp_client.py")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc() 