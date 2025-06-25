#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像元素分析器使用示例
展示如何使用重构后的工具方法分析图像中的文本和图标元素
"""

import os
from util.image_element_analyzer import (
    ImageElementAnalyzer,
    analyze_single_image,
    get_element_descriptions,
    get_coordinates_by_description
)


def example_basic_usage():
    """基本使用示例"""
    print("=" * 50)
    print("🚀 图像元素分析器基本使用示例")
    print("=" * 50)
    
    image_path = "screenshots/screenshot_20250625_074204.png"
    
    if not os.path.exists(image_path):
        print(f"❌ 测试图像不存在: {image_path}")
        return
    
    # 使用便捷函数分析单个图像
    print(f"\n📷 分析图像: {image_path}")
    result = analyze_single_image(
        image_path,
        save_annotated=True,
        output_dir="result"
    )
    
    if result["success"]:
        print(f"✅ 分析成功!")
        print(f"   📊 总元素数: {result['element_count']['total']}")
        print(f"   📝 文本元素: {result['element_count']['text']}")
        print(f"   🎯 图标元素: {result['element_count']['icon']}")
        print(f"   ⏱️  总耗时: {result['processing_time']['total']:.2f}s")
        
        if result["annotated_image_path"]:
            print(f"   💾 标注图像: {result['annotated_image_path']}")
        
        # 显示前3个图标描述
        icons = result["icon_elements"][:3]
        if icons:
            print(f"\n🎯 图标描述示例:")
            for i, icon in enumerate(icons, 1):
                content = icon.get('content', 'N/A')
                bbox = icon.get('bbox', [])
                print(f"   {i}. {content}")
                if bbox:
                    print(f"      坐标: [{bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f}]")
    else:
        print(f"❌ 分析失败: {result.get('error')}")


def example_class_usage():
    """使用类实例进行分析"""
    print("=" * 50)
    print("🔧 使用分析器类实例")
    print("=" * 50)
    
    # 创建分析器实例
    analyzer = ImageElementAnalyzer()
    
    # 初始化
    if not analyzer.initialize():
        print("❌ 分析器初始化失败")
        return
    
    print("✅ 分析器初始化成功")
    
    # 分析多个图像
    test_images = [
        "imgs/word.png",
        "imgs/windows_home.png",
        "imgs/google_page.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n📷 分析: {os.path.basename(image_path)}")
            
            result = analyzer.analyze_image(
                image_path,
                box_threshold=0.05,
                save_annotated=False,  # 不保存标注图像
                verbose=False  # 静默模式
            )
            
            if result["success"]:
                count = result["element_count"]
                time_info = result["processing_time"]
                print(f"✅ 成功 - 文本:{count['text']} 图标:{count['icon']} (耗时:{time_info['total']:.1f}s)")
            else:
                print(f"❌ 失败: {result.get('error')}")
        else:
            print(f"⚠️ 跳过不存在的图像: {image_path}")


def example_batch_analysis():
    """批量分析示例"""
    print("=" * 50)
    print("📦 批量分析示例")
    print("=" * 50)
    
    # 获取所有测试图像
    test_images = []
    for img_name in ["word.png", "windows_home.png", "google_page.png"]:
        img_path = f"imgs/{img_name}"
        if os.path.exists(img_path):
            test_images.append(img_path)
    
    if not test_images:
        print("❌ 未找到测试图像")
        return
    
    # 创建分析器并批量处理
    analyzer = ImageElementAnalyzer()
    
    if not analyzer.initialize():
        print("❌ 分析器初始化失败")
        return
    
    # 批量分析
    results = analyzer.batch_analyze(
        test_images,
        box_threshold=0.05,
        save_annotated=True,
        output_dir="result",
        verbose=False
    )
    
    # 统计结果
    total_success = sum(1 for r in results.values() if r["success"])
    total_elements = sum(r["element_count"]["total"] for r in results.values() if r["success"])
    total_time = sum(r["processing_time"]["total"] for r in results.values() if r["success"])
    
    print(f"\n📊 批量分析结果:")
    print(f"   ✅ 成功: {total_success}/{len(test_images)}")
    print(f"   🎯 总元素数: {total_elements}")
    print(f"   ⏱️  总耗时: {total_time:.2f}s")
    print(f"   📈 平均每图: {total_time/total_success:.2f}s")


def example_utility_functions():
    """工具函数使用示例"""
    print("=" * 50)
    print("🛠️ 工具函数使用示例")
    print("=" * 50)
    
    image_path = "imgs/word.png"
    
    if not os.path.exists(image_path):
        print(f"❌ 测试图像不存在: {image_path}")
        return
    
    # 1. 获取所有元素描述
    print("1️⃣ 获取所有元素描述:")
    elements = get_element_descriptions(image_path, "all")
    print(f"   总共找到 {len(elements)} 个元素")
    
    # 2. 只获取图标描述
    print("\n2️⃣ 获取图标描述:")
    icons = get_element_descriptions(image_path, "icon")
    print(f"   找到 {len(icons)} 个图标")
    for i, icon in enumerate(icons[:3], 1):  # 显示前3个
        print(f"   {i}. {icon.get('content', 'N/A')}")
    
    # 3. 只获取文本元素
    print("\n3️⃣ 获取文本元素:")
    texts = get_element_descriptions(image_path, "text")
    print(f"   找到 {len(texts)} 个文本元素")
    for i, text in enumerate(texts[:3], 1):  # 显示前3个
        print(f"   {i}. {text.get('content', 'N/A')}")
    
    # 4. 根据描述查找坐标
    print("\n4️⃣ 根据描述查找坐标:")
    if icons:
        # 使用第一个图标的部分描述进行搜索
        first_icon_content = icons[0].get('content', '')
        if first_icon_content:
            # 取描述的前几个字符进行模糊匹配
            search_term = first_icon_content.split()[0] if first_icon_content.split() else first_icon_content[:5]
            coords = get_coordinates_by_description(image_path, search_term)
            
            if coords:
                print(f"   搜索'{search_term}' -> 找到坐标: [{coords[0]:.3f}, {coords[1]:.3f}, {coords[2]:.3f}, {coords[3]:.3f}]")
            else:
                print(f"   搜索'{search_term}' -> 未找到匹配项")


def example_custom_parameters():
    """自定义参数示例"""
    print("=" * 50)
    print("⚙️ 自定义参数示例")
    print("=" * 50)
    
    image_path = "imgs/google_page.png"
    
    if not os.path.exists(image_path):
        print(f"❌ 测试图像不存在: {image_path}")
        return
    
    # 使用不同的检测阈值
    thresholds = [0.03, 0.05, 0.08]
    
    for threshold in thresholds:
        print(f"\n🎯 使用检测阈值: {threshold}")
        
        result = analyze_single_image(
            image_path,
            box_threshold=threshold,
            save_annotated=False,
            verbose=False
        )
        
        if result["success"]:
            count = result["element_count"]
            print(f"   检测到 {count['total']} 个元素 (文本:{count['text']}, 图标:{count['icon']})")
        else:
            print(f"   ❌ 分析失败: {result.get('error')}")


def main():
    """主函数"""
    print("🎯 图像元素分析器使用示例集合")
    
    try:
        # 确保输出目录存在
        os.makedirs("result", exist_ok=True)
        
        # 运行各种示例
        example_basic_usage()
        
        print("\n" + "="*60)
        example_class_usage()
        
        print("\n" + "="*60)  
        example_batch_analysis()
        
        print("\n" + "="*60)
        example_utility_functions()
        
        print("\n" + "="*60)
        example_custom_parameters()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断操作")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 所有示例演示完成！")
    print("💾 查看 result/ 目录中的输出文件")


if __name__ == "__main__":
    main() 