#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像分析器调试脚本
用于诊断 'NoneType' object is not iterable 错误
"""

import os
import sys
import asyncio
import traceback
from PIL import Image

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.image_element_analyzer import ImageElementAnalyzer
from util.config import get_config


async def debug_image_analyzer():
    """调试图像分析器"""
    print("🔧 图像分析器调试工具")
    print("=" * 50)
    
    # 1. 检查配置
    print("1️⃣ 检查配置文件...")
    try:
        config = get_config()
        print(f"   ✅ 配置加载成功")
        print(f"   🔑 OpenAI Model: {config.config.get('openai', {}).get('model', 'N/A')}")
        print(f"   🔑 API Key: {'已设置' if config.config.get('openai', {}).get('api_key') else '未设置'}")
    except Exception as e:
        print(f"   ❌ 配置加载失败: {e}")
        return
    
    # 2. 检查模型文件
    print("\n2️⃣ 检查模型文件...")
    model_path = "weights/icon_detect/model.pt"
    if os.path.exists(model_path):
        model_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        print(f"   ✅ 模型文件存在: {model_path}")
        print(f"   📊 文件大小: {model_size:.1f} MB")
    else:
        print(f"   ❌ 模型文件不存在: {model_path}")
        print("   💡 请下载OmniParser模型文件")
        return
    
    # 3. 初始化分析器
    print("\n3️⃣ 初始化图像分析器...")
    try:
        analyzer = ImageElementAnalyzer()
        init_success = analyzer.initialize()
        
        if init_success:
            print("   ✅ 分析器初始化成功")
            print(f"   🖥️ 使用设备: {analyzer.device}")
        else:
            print("   ❌ 分析器初始化失败")
            return
    except Exception as e:
        print(f"   ❌ 初始化异常: {e}")
        traceback.print_exc()
        return
    
    # 4. 检查测试图像
    print("\n4️⃣ 检查测试图像...")
    test_images = []
    
    # 检查screenshots目录
    screenshots_dir = "screenshots"
    if os.path.exists(screenshots_dir):
        for filename in os.listdir(screenshots_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(screenshots_dir, filename)
                file_size = os.path.getsize(image_path)
                test_images.append((image_path, file_size))
    
    # 检查imgs目录
    imgs_dir = "imgs"
    if os.path.exists(imgs_dir):
        for filename in os.listdir(imgs_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(imgs_dir, filename)
                file_size = os.path.getsize(image_path)
                test_images.append((image_path, file_size))
    
    if not test_images:
        print("   ⚠️ 未找到测试图像")
        return
    
    # 排序，优先较大的文件（可能质量更好）
    test_images.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   📁 找到 {len(test_images)} 个测试图像")
    for i, (path, size) in enumerate(test_images[:5], 1):
        print(f"      {i}. {os.path.basename(path)} ({size/1024:.1f} KB)")
    
    # 5. 测试图像分析
    print("\n5️⃣ 测试图像分析...")
    
    for i, (image_path, file_size) in enumerate(test_images[:3], 1):  # 只测试前3个
        print(f"\n   测试图像 {i}: {os.path.basename(image_path)}")
        
        # 检查图像是否可以正常打开
        try:
            with Image.open(image_path) as img:
                print(f"      📏 图像尺寸: {img.size}")
                print(f"      🎨 图像模式: {img.mode}")
        except Exception as e:
            print(f"      ❌ 无法打开图像: {e}")
            continue
        
        # 执行分析
        try:
            print(f"      🔍 开始分析...")
            result = analyzer.analyze_image(
                image_path, 
                box_threshold=0.05,
                save_annotated=False,  # 不保存标注图像，加快速度
                verbose=False
            )
            
            if result and result.get("success"):
                elements = result.get("elements", [])
                element_count = result.get("element_count", {})
                processing_time = result.get("processing_time", {})
                
                print(f"      ✅ 分析成功!")
                print(f"      📊 检测元素: 总计{element_count.get('total', 0)} (文本:{element_count.get('text', 0)}, 图标:{element_count.get('icon', 0)})")
                print(f"      ⏱️ 处理时间: {processing_time.get('total', 0):.2f}s")
                
                # 显示前3个元素
                if elements:
                    print(f"      📋 前3个元素:")
                    for j, element in enumerate(elements[:3], 1):
                        content = element.get('content', 'N/A')[:30]
                        element_type = element.get('type', 'unknown')
                        print(f"         {j}. [{element_type}] {content}")
                
                print(f"      🎉 图像 {i} 测试通过!")
                break  # 找到一个可以正常工作的图像就停止
                
            else:
                error_msg = result.get('error', '未知错误') if result else '分析器返回空结果'
                print(f"      ❌ 分析失败: {error_msg}")
                
        except Exception as e:
            print(f"      ❌ 分析异常: {e}")
            print(f"      📝 详细错误:")
            traceback.print_exc()
    
    print("\n🎉 调试完成!")


async def test_with_latest_screenshot():
    """使用最新的截图测试"""
    print("\n🔬 使用最新截图进行详细测试")
    print("=" * 50)
    
    # 找到最新的截图
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ screenshots目录不存在")
        return
    
    screenshots = []
    for filename in os.listdir(screenshots_dir):
        if filename.lower().endswith('.png'):
            filepath = os.path.join(screenshots_dir, filename)
            mtime = os.path.getmtime(filepath)
            screenshots.append((filepath, mtime))
    
    if not screenshots:
        print("❌ 未找到截图文件")
        return
    
    # 按时间排序，获取最新的
    screenshots.sort(key=lambda x: x[1], reverse=True)
    latest_screenshot = screenshots[0][0]
    
    print(f"📸 最新截图: {os.path.basename(latest_screenshot)}")
    
    # 详细分析
    try:
        analyzer = ImageElementAnalyzer()
        if not analyzer.initialize():
            print("❌ 分析器初始化失败")
            return
        
        print("🔍 执行详细分析...")
        result = analyzer.analyze_image(
            latest_screenshot, 
            box_threshold=0.03,  # 降低阈值，检测更多元素
            save_annotated=True,
            output_dir="result",
            verbose=True  # 开启详细日志
        )
        
        if result and result.get("success"):
            print("✅ 分析成功!")
            
            # 保存结果到文件
            import json
            result_file = "debug_analysis_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                # 移除不能序列化的数据
                save_result = {
                    "success": result["success"],
                    "elements": result.get("elements", []),
                    "element_count": result.get("element_count", {}),
                    "processing_time": result.get("processing_time", {}),
                    "image_info": result.get("image_info", {})
                }
                json.dump(save_result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 分析结果已保存到: {result_file}")
            
        else:
            print("❌ 分析失败")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        traceback.print_exc()


async def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "latest":
        await test_with_latest_screenshot()
    else:
        await debug_image_analyzer()


if __name__ == "__main__":
    print("🔧 图像分析器调试工具")
    print("使用方法:")
    print("  python debug_image_analyzer.py        # 全面调试")
    print("  python debug_image_analyzer.py latest # 测试最新截图")
    print()
    
    asyncio.run(main()) 