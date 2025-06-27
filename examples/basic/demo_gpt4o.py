#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-4o 图标识别演示脚本
基于 demo.ipynb 改写，使用 GPT-4o 替代 Florence-2
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import os
import sys
import time
import base64
import io
from PIL import Image
import torch
import pandas as pd

# 导入 OmniParser 相关模块
from src.utils.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
from src.utils.config import get_config

def main():
    print("🚀 OmniParser + GPT-4o 演示")
    print("=" * 50)
    
    # 1. 检查配置文件
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("❌ 配置文件不存在！请确保 config.json 已正确设置")
        return
    
    try:
        config = get_config(config_path)
        print("✅ 配置文件加载成功")
        print(f"   🔧 API端点: {config.get_openai_base_url()}")
        print(f"   🤖 使用模型: {config.get_openai_model()}")
        print(f"   📦 批处理大小: {config.get_batch_size()}")
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return
    
    # 2. 设置设备
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🖥️  使用设备: {device}")
    
    # 3. 加载YOLO模型
    model_path = 'weights/icon_detect/model.pt'
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return
    
    print("\n📥 加载YOLO图标检测模型...")
    som_model = get_yolo_model(model_path)
    som_model.to(device)
    print(f'✅ 模型已加载到 {device}')
    
    # 4. 配置GPT-4o图标描述模型
    print("\n🤖 配置GPT-4o图标描述模型...")
    caption_model_processor = get_caption_model_processor(
        model_name="gpt4o", 
        model_name_or_path=config.get_openai_model(),
        device=device
    )
    print("✅ GPT-4o模型配置完成")
    
    # 5. 处理测试图像
    test_images = [
        'imgs/word.png',
        'imgs/windows_home.png',
        'imgs/google_page.png'
    ]
    
    for image_path in test_images:
        if not os.path.exists(image_path):
            print(f"⚠️  跳过不存在的图像: {image_path}")
            continue
            
        print(f"\n🖼️  处理图像: {image_path}")
        print("-" * 40)
        
        # 加载图像
        image = Image.open(image_path)
        image_rgb = image.convert('RGB')
        print(f'📏 图像尺寸: {image.size}')
        
        # 配置边界框绘制参数
        box_overlay_ratio = max(image.size) / 3200
        draw_bbox_config = {
            'text_scale': 0.8 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
        }
        BOX_TRESHOLD = 0.05
        
        # 计时开始
        start_time = time.time()
        
        try:
            # OCR 检测
            print("🔍 进行OCR文本检测...")
            ocr_start = time.time()
            ocr_bbox_rslt, is_goal_filtered = check_ocr_box(
                image_path, 
                display_img=False, 
                output_bb_format='xyxy', 
                goal_filtering=None, 
                easyocr_args={'paragraph': False, 'text_threshold': 0.9}, 
                use_paddleocr=True
            )
            text, ocr_bbox = ocr_bbox_rslt
            ocr_time = time.time() - ocr_start
            print(f"   📝 OCR完成，检测到 {len(text)} 个文本区域 (耗时: {ocr_time:.2f}s)")
            
            # 图标检测和描述
            print("🎯 进行图标检测和GPT-4o描述...")
            caption_start = time.time()
            
            dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
                image_path, 
                som_model, 
                BOX_TRESHOLD=BOX_TRESHOLD, 
                output_coord_in_ratio=True, 
                ocr_bbox=ocr_bbox,
                draw_bbox_config=draw_bbox_config, 
                caption_model_processor=caption_model_processor, 
                ocr_text=text,
                use_local_semantics=True, 
                iou_threshold=0.7, 
                scale_img=False
                # batch_size 会从配置文件自动读取
            )
            
            caption_time = time.time() - caption_start
            total_time = time.time() - start_time
            
            print(f"   ✅ 图标识别完成 (耗时: {caption_time:.2f}s)")
            print(f"   🎯 总共检测到 {len(parsed_content_list)} 个元素")
            print(f"   ⏱️  总耗时: {total_time:.2f}s")
            
            # 保存标注图像
            output_path = f"output_gpt4o_{os.path.basename(image_path)}"
            image_data = base64.b64decode(dino_labled_img)
            output_image = Image.open(io.BytesIO(image_data))
            output_image.save(output_path)
            print(f"   💾 标注图像已保存: {output_path}")
            
            # 显示解析结果
            print(f"\n📋 解析结果详情:")
            print("=" * 60)
            
            # 创建DataFrame显示结果（类似notebook中的显示）
            df = pd.DataFrame(parsed_content_list)
            df['ID'] = range(len(df))
            
            # 按类型分组显示
            text_items = [item for item in parsed_content_list if item.get('type') == 'text']
            icon_items = [item for item in parsed_content_list if item.get('type') == 'icon']
            
            print(f"📝 文本元素 ({len(text_items)} 个):")
            for i, item in enumerate(text_items):
                content = item.get('content', 'N/A')
                bbox = item.get('bbox', [])
                print(f"   {i+1:2d}. {content}")
                if bbox:
                    print(f"       位置: ({bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f})")
            
            print(f"\n🎯 图标元素 ({len(icon_items)} 个) - GPT-4o描述:")
            for i, item in enumerate(icon_items):
                content = item.get('content', 'N/A')
                bbox = item.get('bbox', [])
                print(f"   {i+1:2d}. {content}")
                if bbox:
                    print(f"       位置: ({bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f})")
            
            # 保存详细结果到CSV
            csv_path = f"results_gpt4o_{os.path.basename(image_path).replace('.png', '.csv')}"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"\n💾 详细结果已保存到: {csv_path}")
            
        except Exception as e:
            print(f"❌ 处理图像时出错: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)

if __name__ == "__main__":
    main()
    print("\n🎉 演示完成！")
    print("查看生成的文件:")
    print("  - output_gpt4o_*.png: 标注图像")
    print("  - results_gpt4o_*.csv: 详细结果数据") 