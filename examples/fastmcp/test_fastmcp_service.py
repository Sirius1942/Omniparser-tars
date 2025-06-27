#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastMCP 服务功能测试脚本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import asyncio
import json
import time
from pathlib import Path

try:
    from fastmcp import Client
except ImportError:
    print("❌ FastMCP 未安装，请运行: pip install fastmcp")
    exit(1)


async def test_server_connection():
    """测试服务器连接"""
    print("🔍 测试服务器连接...")
    
    try:
        async with Client("./image_element_analyzer_fastmcp_server.py") as client:
            # 列出可用工具
            tools = await client.list_tools()
            print(f"   ✅ 连接成功! 发现 {len(tools)} 个工具:")
            for tool in tools:
                print(f"      • {tool.name} - {tool.description or '无描述'}")
            
            # 列出可用资源
            try:
                resources = await client.list_resources()
                print(f"   ✅ 发现 {len(resources)} 个资源:")
                for resource in resources:
                    print(f"      • {resource.uri} - {resource.description or '无描述'}")
            except:
                print("   ⚠️  无法获取资源列表")
            
            # 列出可用提示
            try:
                prompts = await client.list_prompts()
                print(f"   ✅ 发现 {len(prompts)} 个提示:")
                for prompt in prompts:
                    print(f"      • {prompt.name} - {prompt.description or '无描述'}")
            except:
                print("   ⚠️  无法获取提示列表")
                
            return True
            
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False


async def test_device_status():
    """测试设备状态获取"""
    print("\n📊 测试设备状态获取...")
    
    try:
        async with Client("./image_element_analyzer_fastmcp_server.py") as client:
            # 测试设备状态工具
            result = await client.call_tool("get_device_status", {})
            
            if hasattr(result, 'content') and result.content:
                try:
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        device_info = data.get("device_info", {})
                        print(f"   ✅ 设备: {device_info.get('device', 'Unknown')}")
                        print(f"   ✅ CUDA 可用: {device_info.get('cuda_available', False)}")
                        if device_info.get('cuda_available'):
                            print(f"   ✅ GPU: {device_info.get('gpu_name', 'Unknown')}")
                        
                        analyzer_status = data.get("analyzer_status", {})
                        print(f"   ✅ 分析器就绪: {analyzer_status.get('ready', False)}")
                        return True
                    else:
                        print(f"   ❌ 工具调用失败: {data.get('error', 'Unknown error')}")
                        return False
                except json.JSONDecodeError:
                    print(f"   ❌ 无法解析返回结果")
                    return False
            else:
                print("   ❌ 未收到有效响应")
                return False
                
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


async def test_resource_access():
    """测试资源访问"""
    print("\n📄 测试资源访问...")
    
    try:
        async with Client("./image_element_analyzer_fastmcp_server.py") as client:
            # 测试设备状态资源
            try:
                result = await client.read_resource("device://status")
                if hasattr(result, 'contents') and result.contents:
                    content = result.contents[0].text
                    print("   ✅ 设备状态资源访问成功:")
                    print(f"      {content[:100]}..." if len(content) > 100 else f"      {content}")
                else:
                    print("   ❌ 设备状态资源访问失败")
                    return False
            except Exception as e:
                print(f"   ❌ 设备状态资源访问异常: {e}")
                return False
            
            # 测试最近分析资源
            try:
                result = await client.read_resource("image://recent/test")
                if hasattr(result, 'contents') and result.contents:
                    content = result.contents[0].text
                    print("   ✅ 最近分析资源访问成功:")
                    print(f"      {content[:100]}..." if len(content) > 100 else f"      {content}")
                else:
                    print("   ⚠️  最近分析资源为空 (这是正常的)")
            except Exception as e:
                print(f"   ⚠️  最近分析资源访问异常: {e}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ 资源访问测试失败: {e}")
        return False


async def test_image_analysis():
    """测试图像分析功能"""
    print("\n🖼️  测试图像分析功能...")
    
    # 查找测试图像
    test_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        test_images.extend(Path("imgs").glob(ext))
    
    if not test_images:
        print("   ⚠️  未找到测试图像，跳过图像分析测试")
        return True
    
    test_image = str(test_images[0])
    print(f"   📸 使用测试图像: {test_image}")
    
    try:
        async with Client("./image_element_analyzer_fastmcp_server.py") as client:
            # 测试图像分析
            result = await client.call_tool("analyze_image_file", {
                "image_path": test_image,
                "box_threshold": 0.1,  # 使用较高阈值加快测试
                "save_annotated": False,
                "output_dir": "./test_results"
            })
            
            if hasattr(result, 'content') and result.content:
                try:
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print("   ✅ 图像分析成功!")
                        
                        # 显示统计信息
                        if "element_count" in data:
                            count = data["element_count"]
                            print(f"      文本元素: {count.get('text', 0)}")
                            print(f"      图标元素: {count.get('icon', 0)}")
                        
                        if "processing_time" in data:
                            print(f"      处理时间: {data['processing_time']:.2f}s")
                            
                        return True
                    else:
                        print(f"   ❌ 图像分析失败: {data.get('error', 'Unknown error')}")
                        return False
                except json.JSONDecodeError:
                    print(f"   ❌ 无法解析分析结果")
                    return False
            else:
                print("   ❌ 未收到分析结果")
                return False
                
    except Exception as e:
        print(f"   ❌ 图像分析测试失败: {e}")
        return False


async def test_prompt_functionality():
    """测试提示功能"""
    print("\n💡 测试提示功能...")
    
    try:
        async with Client("./image_element_analyzer_fastmcp_server.py") as client:
            # 获取可用提示
            prompts = await client.list_prompts()
            
            if not prompts:
                print("   ⚠️  未发现可用提示")
                return True
            
            # 测试第一个提示
            prompt = prompts[0]
            print(f"   🧪 测试提示: {prompt.name}")
            
            # 根据提示名称提供测试参数
            if "debug_analysis_error" in prompt.name:
                test_args = {
                    "error_message": "测试错误信息",
                    "image_path": "test.png"
                }
            elif "optimize_analysis_settings" in prompt.name:
                test_args = {
                    "image_type": "screenshot",
                    "quality_priority": "balanced"
                }
            else:
                test_args = {}
            
            try:
                result = await client.get_prompt(prompt.name, test_args)
                if hasattr(result, 'messages') and result.messages:
                    print("   ✅ 提示生成成功!")
                    message = result.messages[0]
                    if hasattr(message, 'content') and message.content:
                        content = message.content[0].text
                        print(f"      提示内容: {content[:100]}..." if len(content) > 100 else f"      提示内容: {content}")
                    return True
                else:
                    print("   ❌ 提示生成失败")
                    return False
            except Exception as e:
                print(f"   ❌ 提示测试异常: {e}")
                return False
                
    except Exception as e:
        print(f"   ❌ 提示功能测试失败: {e}")
        return False


async def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    try:
        async with Client("./image_element_analyzer_fastmcp_server.py") as client:
            # 测试不存在的图像文件
            result = await client.call_tool("analyze_image_file", {
                "image_path": "/nonexistent/path/image.png",
                "box_threshold": 0.05
            })
            
            if hasattr(result, 'content') and result.content:
                try:
                    data = json.loads(result.content[0].text)
                    if not data.get("success") and "error" in data:
                        print("   ✅ 错误处理正常 - 正确返回错误信息")
                        print(f"      错误信息: {data['error']}")
                        return True
                    else:
                        print("   ❌ 应该返回错误但没有")
                        return False
                except json.JSONDecodeError:
                    print("   ❌ 错误响应格式异常")
                    return False
            else:
                print("   ❌ 未收到错误响应")
                return False
                
    except Exception as e:
        print(f"   ❌ 错误处理测试失败: {e}")
        return False


async def run_comprehensive_test():
    """运行综合测试"""
    print("🧪 开始 FastMCP 服务综合测试")
    print("=" * 60)
    
    tests = [
        ("服务器连接", test_server_connection),
        ("设备状态", test_device_status),
        ("资源访问", test_resource_access),
        ("图像分析", test_image_analysis),
        ("提示功能", test_prompt_functionality),
        ("错误处理", test_error_handling),
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            result = await test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name} 测试异常: {e}")
    
    end_time = time.time()
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
    
    print("-" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过数: {passed_tests}")
    print(f"失败数: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    print(f"总耗时: {end_time - start_time:.2f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过! FastMCP 服务运行正常")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，请检查相关功能")
    
    return passed_tests == total_tests


async def main():
    """主函数"""
    print("🎯 FastMCP 图像元素分析器服务测试")
    print("这个测试将验证 FastMCP 服务的各项功能")
    print()
    
    try:
        success = await run_comprehensive_test()
        exit_code = 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断测试")
        exit_code = 1
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    print(f"\n测试完成，退出码: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 