#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MCP 服务功能测试脚本
"""

import asyncio
import requests
import time
from pathlib import Path


def test_server_status():
    """测试服务器基本状态"""
    print("🔍 测试服务器基本状态...")
    
    try:
        # 测试根路径
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ 服务器运行正常")
            print(f"   📋 服务: {info.get('service', 'Unknown')}")
            print(f"   🔢 版本: {info.get('version', 'Unknown')}")
            print(f"   🖥️  设备: {info.get('device', {}).get('device', 'Unknown')}")
        else:
            print(f"   ❌ 服务器响应异常: {response.status_code}")
            return False
            
        # 测试健康检查
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   💚 健康状态: {health.get('status', 'Unknown')}")
            print(f"   🤖 分析器就绪: {health.get('analyzer_ready', False)}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器，请确保服务已启动")
        return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


def test_file_upload():
    """测试文件上传分析"""
    print("\n📤 测试文件上传分析...")
    
    # 查找测试图像
    test_images = [
        "imgs/demo_image.jpg",
        "imgs/word.png", 
        "imgs/google_page.png"
    ]
    
    test_image = None
    for image_path in test_images:
        if Path(image_path).exists():
            test_image = image_path
            break
    
    if not test_image:
        print("   ⚠️ 没有找到测试图像文件")
        return False
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': f}
            data = {
                'box_threshold': 0.05,
                'save_annotated': False,
                'verbose': False
            }
            
            print(f"   🖼️ 分析图像: {test_image}")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/analyze/upload",
                files=files, 
                data=data,
                timeout=60  # 60秒超时
            )
            
            upload_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    element_count = result.get('element_count', {})
                    print(f"   ✅ 上传分析成功 (耗时: {upload_time:.2f}s)")
                    print(f"   📊 检测元素: 总计{element_count.get('total', 0)} (文本:{element_count.get('text', 0)}, 图标:{element_count.get('icon', 0)})")
                    
                    # 显示一些结果示例
                    text_elements = result.get('text_elements', [])[:2]
                    icon_elements = result.get('icon_elements', [])[:2]
                    
                    if text_elements:
                        print("   📝 文本示例:")
                        for i, element in enumerate(text_elements, 1):
                            content = element.get('content', 'N/A')[:50]
                            print(f"      {i}. {content}...")
                    
                    if icon_elements:
                        print("   🎯 图标示例:")
                        for i, element in enumerate(icon_elements, 1):
                            content = element.get('content', 'N/A')[:50]
                            print(f"      {i}. {content}...")
                    
                    return True
                else:
                    print(f"   ❌ 分析失败: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                print(f"   📄 响应: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时，分析可能需要更长时间")
        return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


async def test_sse_stream():
    """测试 SSE 流式通信（简化版）"""
    print("\n📡 测试 SSE 流式通信...")
    
    try:
        import aiohttp
        from mcp_client_example import ImageAnalyzerMCPClient
        
        # 查找测试图像
        test_images = [
            "imgs/demo_image.jpg",
            "imgs/word.png", 
            "imgs/google_page.png"
        ]
        
        test_image = None
        for image_path in test_images:
            if Path(image_path).exists():
                test_image = image_path
                break
        
        if not test_image:
            print("   ⚠️ 没有找到测试图像文件")
            return False
        
        async with ImageAnalyzerMCPClient() as client:
            print(f"   🖼️ 流式分析图像: {test_image}")
            
            result = await client.analyze_with_progress(
                test_image,
                show_progress=True,
                box_threshold=0.05,
                save_annotated=False,
                verbose=False
            )
            
            if result.get('success'):
                element_count = result.get('element_count', {})
                print(f"   ✅ SSE 流式分析成功")
                print(f"   📊 检测元素: 总计{element_count.get('total', 0)} (文本:{element_count.get('text', 0)}, 图标:{element_count.get('icon', 0)})")
                return True
            else:
                print(f"   ❌ SSE 流式分析失败: {result.get('error')}")
                return False
                
    except ImportError:
        print("   ⚠️ 缺少 aiohttp 依赖，跳过 SSE 测试")
        print("   💡 运行: pip install aiohttp")
        return None
    except Exception as e:
        print(f"   ❌ SSE 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 MCP 服务功能测试")
    print("=" * 50)
    
    # 测试基本状态
    if not test_server_status():
        print("\n❌ 服务器状态测试失败，请检查服务是否正常运行")
        print("💡 启动服务: python start_mcp_server.py")
        return
    
    # 等待一段时间确保服务完全启动
    print("\n⏳ 等待服务完全初始化...")
    time.sleep(3)
    
    # 测试文件上传
    upload_success = test_file_upload()
    
    # 测试 SSE 流式通信
    sse_result = asyncio.run(test_sse_stream())
    
    # 总结
    print("\n📋 测试总结")
    print("=" * 30)
    print(f"✅ 服务器状态: 正常")
    print(f"{'✅' if upload_success else '❌'} 文件上传分析: {'成功' if upload_success else '失败'}")
    
    if sse_result is not None:
        print(f"{'✅' if sse_result else '❌'} SSE 流式通信: {'成功' if sse_result else '失败'}")
    else:
        print(f"⚠️  SSE 流式通信: 跳过")
    
    if upload_success and (sse_result is None or sse_result):
        print("\n🎉 MCP 服务测试通过！服务工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查服务配置。")


if __name__ == "__main__":
    main() 