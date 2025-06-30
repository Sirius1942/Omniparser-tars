#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-4o 图标识别演示脚本
基于 demo.ipynb 改写，使用 GPT-4o 替代 Florence-2

功能描述:
- 使用 YOLO 模型进行图标检测
- 使用 GPT-4o 进行图标描述和分析
- 使用 PaddleOCR 进行文本识别
- 生成标注图像和详细结果数据

使用方法:
1. 从项目根目录运行:
   python examples/basic/demo_gpt4o.py

2. 从当前目录运行:
   cd examples/basic && python demo_gpt4o.py

依赖要求:
- 已安装所有依赖: pip install -r requirements.txt
- 配置文件: config.json (包含 OpenAI API 密钥)
- 模型权重: weights/icon_detect/model.pt
- 测试图像: imgs/word.png, imgs/windows_home.png, imgs/google_page.png

输出文件:
- output_gpt4o_*.png: 带标注的图像文件
- results_gpt4o_*.csv: 详细的检测结果数据

示例命令:
# 基础运行
python examples/basic/demo_gpt4o.py

# 查看帮助信息
python examples/basic/demo_gpt4o.py --help

注意事项:
- 确保 config.json 中配置了有效的 OpenAI API 密钥
- 首次运行可能需要下载模型权重
- CPU 模式下处理速度较慢，建议使用 GPU
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
import time
import base64
import io
from PIL import Image
import torch
import pandas as pd

# 导入 OmniParser 相关模块
from src.utils.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
from src.utils.config import get_config

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="GPT-4o 图标识别演示脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基础运行 (处理默认图像)
  python examples/basic/demo_gpt4o.py
  
  # 处理单个图像
  python examples/basic/demo_gpt4o.py --image imgs/word.png
  
  # 处理多个图像
  python examples/basic/demo_gpt4o.py --image imgs/word.png imgs/windows_home.png
  
  # 启用 GPU 加速
  python examples/basic/demo_gpt4o.py --device cuda
  
  # 调整检测阈值
  python examples/basic/demo_gpt4o.py --threshold 0.1
  
  # 启用详细输出
  python examples/basic/demo_gpt4o.py --verbose

输出文件:
  - output_gpt4o_*.png: 带标注的图像文件
  - results_gpt4o_*.csv: 详细的检测结果数据
  
注意事项:
  - 确保 config.json 中配置了有效的 OpenAI API 密钥
  - 确保模型权重文件存在: weights/icon_detect/model.pt
  - CPU 模式下处理速度较慢，建议使用 GPU
        """
    )
    
    parser.add_argument(
        '--image', '-i',
        type=str,
        nargs='*',
        help='要处理的图像文件路径 (可指定多个)'
    )
    
    parser.add_argument(
        '--device', '-d',
        type=str,
        choices=['auto', 'cpu', 'cuda'],
        default='auto',
        help='指定计算设备 (默认: auto)'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=0.05,
        help='检测阈值 (默认: 0.05)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='配置文件路径 (默认: config.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细输出'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='.',
        help='输出目录 (默认: 当前目录)'
    )
    
    return parser.parse_args()

def main(args=None):
    """主函数"""
    if args is None:
        args = parse_arguments()
    
    print("🚀 OmniParser + GPT-4o 演示")
    print("=" * 50)
    
    if args.verbose:
        print(f"📋 参数配置:")
        print(f"   设备: {args.device}")
        print(f"   阈值: {args.threshold}")
        print(f"   输出目录: {args.output_dir}")
        if args.image:
            print(f"   指定图像: {args.image}")
    
    # 1. 检查配置文件
    config_path = args.config if args.config else os.path.join(project_root, "config.json")
    if not os.path.exists(config_path):
        print("❌ 配置文件不存在！请确保 config.json 已正确设置")
        print(f"   期望路径: {config_path}")
        return
    
    try:
        config = get_config(config_path)
        print("✅ 配置文件加载成功")
        if args.verbose:
            print(f"   🔧 API端点: {config.get_openai_base_url()}")
            print(f"   🤖 使用模型: {config.get_openai_model()}")
            print(f"   📦 批处理大小: {config.get_batch_size()}")
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return
    
    # 2. 设置设备
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device
        if device == 'cuda' and not torch.cuda.is_available():
            print("⚠️  CUDA 不可用，切换到 CPU")
            device = 'cpu'
    
    print(f"🖥️  使用设备: {device}")
    
    # 3. 检查输出目录
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"📁 创建输出目录: {args.output_dir}")
    
    # 4. 加载YOLO模型
    model_path = os.path.join(project_root, 'weights/icon_detect/model.pt')
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        print("   请确保已下载模型权重文件")
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
    
    # 6. 确定要处理的图像
    if args.image:
        test_images = args.image
    else:
        # 默认图像
        test_images = [
            os.path.join(project_root, 'imgs/word.png'),
            os.path.join(project_root, 'imgs/windows_home.png'),
            os.path.join(project_root, 'imgs/google_page.png')
        ]
    
    print(f"📸 将处理 {len(test_images)} 个图像")
    
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
        BOX_TRESHOLD = args.threshold
        
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
            output_path = os.path.join(args.output_dir, f"output_gpt4o_{os.path.basename(image_path)}")
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
            csv_path = os.path.join(args.output_dir, f"results_gpt4o_{os.path.basename(image_path).replace('.png', '.csv')}")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"\n💾 详细结果已保存到: {csv_path}")
            
        except Exception as e:
            print(f"❌ 处理图像时出错: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)

if __name__ == "__main__":
    args = parse_arguments()
    try:
        main(args)
        print("\n🎉 演示完成！")
        print("查看生成的文件:")
        print(f"  - {args.output_dir}/output_gpt4o_*.png: 标注图像")
        print(f"  - {args.output_dir}/results_gpt4o_*.csv: 详细结果数据")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了处理过程")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc() 