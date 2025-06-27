#!/usr/bin/env python3
"""
批量检测imgs文件夹中图片的脚本
使用OmniParser后台方法检测图片中的UI元素
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import os
import time
import json
from pathlib import Path
from PIL import Image
import torch
import base64
import io
import pandas as pd

# 导入必要的模块
from src.utils.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model

def setup_models():
    """初始化模型"""
    print("正在初始化模型...")
    
    # 设置设备
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    # 加载SOM模型 (用于检测UI元素)
    som_model_path = 'weights/icon_detect/model.pt'
    if not os.path.exists(som_model_path):
        print(f"错误: 找不到模型文件 {som_model_path}")
        print("请确保已下载模型权重，参考README_CN.md中的安装说明")
        return None, None
    
    som_model = get_yolo_model(som_model_path)
    som_model.to(device)
    
    # 暂时跳过字幕模型，避免flash_attn依赖问题
    print("警告: 跳过字幕模型加载，避免flash_attn依赖问题")
    print("UI元素检测功能仍然可用，但不会生成元素描述")
    caption_model_processor = None
    
    # 原来的字幕模型加载代码（被注释掉）
    # caption_model_path = 'weights/icon_caption_florence'
    # if not os.path.exists(caption_model_path):
    #     print(f"错误: 找不到模型文件夹 {caption_model_path}")
    #     print("请确保已下载模型权重，参考README_CN.md中的安装说明")
    #     return None, None
    # 
    # caption_model_processor = get_caption_model_processor(
    #     model_name="florence2", 
    #     model_name_or_path=caption_model_path, 
    #     device=device
    # )
    
    print("模型初始化完成!")
    return som_model, caption_model_processor

def detect_image(image_path, som_model, caption_model_processor, box_threshold=0.05):
    """检测单张图片"""
    print(f"正在处理: {image_path}")
    
    # 加载图片
    try:
        image = Image.open(image_path).convert('RGB')
        print(f"图片尺寸: {image.size}")
    except Exception as e:
        print(f"无法加载图片 {image_path}: {e}")
        return None
    
    # 设置边界框绘制配置
    box_overlay_ratio = max(image.size) / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }
    
    start_time = time.time()
    
    # 执行OCR检测
    try:
        ocr_bbox_rslt, _ = check_ocr_box(
            image_path, 
            display_img=False, 
            output_bb_format='xyxy',
            easyocr_args={'paragraph': False, 'text_threshold': 0.8}, 
            use_paddleocr=True
        )
        text, ocr_bbox = ocr_bbox_rslt
        ocr_time = time.time() - start_time
        print(f"OCR检测完成，耗时: {ocr_time:.2f}秒")
    except Exception as e:
        print(f"OCR检测失败: {e}")
        text, ocr_bbox = [], []
    
    # 执行SOM检测和标注
    try:
        dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
            image_path, 
            som_model, 
            BOX_TRESHOLD=box_threshold, 
            output_coord_in_ratio=True, 
            ocr_bbox=ocr_bbox,
            draw_bbox_config=draw_bbox_config, 
            caption_model_processor=caption_model_processor, 
            ocr_text=text,
            use_local_semantics=True, 
            iou_threshold=0.7, 
            scale_img=False, 
            batch_size=128
        )
        
        total_time = time.time() - start_time
        print(f"检测完成，总耗时: {total_time:.2f}秒，检测到 {len(parsed_content_list)} 个元素")
        
        return {
            'image_path': image_path,
            'image_size': image.size,
            'detection_time': total_time,
            'labeled_image': dino_labeled_img,
            'coordinates': label_coordinates,
            'parsed_content': parsed_content_list,
            'element_count': len(parsed_content_list)
        }
        
    except Exception as e:
        print(f"SOM检测失败: {e}")
        return None

def save_results(results, output_dir="detection_results"):
    """保存检测结果"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # 保存带标注的图片
    for i, result in enumerate(results):
        if result is None:
            continue
            
        # 保存标注图片
        image_name = Path(result['image_path']).stem
        labeled_img_path = os.path.join(output_dir, f"{image_name}_labeled.png")
        
        # 将base64图片解码并保存
        image_data = base64.b64decode(result['labeled_image'])
        with open(labeled_img_path, 'wb') as f:
            f.write(image_data)
        
        # 保存检测结果为JSON
        json_path = os.path.join(output_dir, f"{image_name}_detection.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'image_path': result['image_path'],
                'image_size': result['image_size'],
                'detection_time': result['detection_time'],
                'element_count': result['element_count'],
                'parsed_content': result['parsed_content']
            }, f, ensure_ascii=False, indent=2)
        
        # 保存为CSV (方便查看)
        if result['parsed_content']:
            df = pd.DataFrame(result['parsed_content'])
            df['ID'] = range(len(df))
            csv_path = os.path.join(output_dir, f"{image_name}_elements.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            print(f"结果已保存: {labeled_img_path}, {json_path}, {csv_path}")
        else:
            print(f"结果已保存: {labeled_img_path}, {json_path} (无检测到的元素)")

def main():
    """主函数"""
    print("=== OmniParser 批量图片检测脚本 ===")
    
    # 初始化模型
    som_model, caption_model_processor = setup_models()
    if som_model is None:
        print("模型初始化失败，退出程序")
        print("请确保:")
        print("1. 已安装所有依赖: pip install -r requirements.txt")
        print("2. 已下载模型权重到weights/文件夹")
        print("3. GPU驱动和CUDA环境配置正确")
        return
    
    # 获取imgs文件夹中的所有图片
    imgs_dir = "imgs"
    if not os.path.exists(imgs_dir):
        print(f"错误: 找不到 {imgs_dir} 文件夹")
        return
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for file in os.listdir(imgs_dir):
        if Path(file).suffix.lower() in image_extensions:
            image_files.append(os.path.join(imgs_dir, file))
    
    if not image_files:
        print(f"在 {imgs_dir} 文件夹中没有找到支持的图片文件")
        print(f"支持的格式: {', '.join(image_extensions)}")
        return
    
    print(f"找到 {len(image_files)} 张图片:")
    for img_file in image_files:
        print(f"  - {img_file}")
    
    # 询问用户是否继续
    response = input("\n是否继续处理这些图片? (y/n): ").lower().strip()
    if response not in ['y', 'yes', '是']:
        print("取消处理")
        return
    
    # 批量处理图片
    results = []
    failed_images = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n--- 处理第 {i}/{len(image_files)} 张图片 ---")
        try:
            result = detect_image(image_path, som_model, caption_model_processor)
            if result is not None:
                results.append(result)
            else:
                failed_images.append(image_path)
        except Exception as e:
            print(f"处理图片 {image_path} 时发生错误: {e}")
            failed_images.append(image_path)
            continue
    
    # 保存结果
    print("\n=== 保存检测结果 ===")
    if results:
        save_results(results)
    
    # 打印统计信息
    successful_detections = len(results)
    print(f"\n=== 检测完成 ===")
    print(f"成功处理: {successful_detections}/{len(image_files)} 张图片")
    
    if failed_images:
        print(f"失败的图片:")
        for failed_img in failed_images:
            print(f"  - {failed_img}")
    
    if results:
        total_elements = sum(r['element_count'] for r in results)
        avg_time = sum(r['detection_time'] for r in results) / len(results)
        print(f"总检测元素数: {total_elements}")
        print(f"平均检测时间: {avg_time:.2f}秒")
        print(f"结果保存在: detection_results/ 文件夹")
        
        # 显示检测结果摘要
        print(f"\n=== 检测结果摘要 ===")
        for result in results:
            image_name = Path(result['image_path']).name
            print(f"{image_name}: {result['element_count']} 个元素, {result['detection_time']:.2f}秒")

if __name__ == "__main__":
    main() 