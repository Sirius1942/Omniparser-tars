#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像元素分析器
提供图像中文本和图标的检测、识别和描述功能
基于 OmniParser + GPT-4o 实现
"""

import os
import time
import base64
import io
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image
import torch
import pandas as pd

# 导入 OmniParser 相关模块
from src.utils.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
from src.utils.config import get_config


class ImageElementAnalyzer:
    """图像元素分析器类"""
    
    def __init__(self, model_path: str = 'weights/icon_detect/model.pt', config_path: str = "config.json"):
        """
        初始化分析器
        
        Args:
            model_path: YOLO模型路径
            config_path: 配置文件路径
        """
        self.model_path = model_path
        self.config_path = config_path
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.som_model = None
        self.caption_model_processor = None
        self.config = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        初始化模型和配置
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 加载配置
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            self.config = get_config(self.config_path)
            
            # 加载YOLO模型
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
            
            self.som_model = get_yolo_model(self.model_path)
            self.som_model.to(self.device)
            
            # 配置GPT-4o图标描述模型
            self.caption_model_processor = get_caption_model_processor(
                model_name="gpt4o", 
                model_name_or_path=self.config.get_openai_model(),
                device=self.device
            )
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def analyze_image(self, image_path: str, box_threshold: float = 0.05, 
                     save_annotated: bool = False, output_dir: str = ".", 
                     verbose: bool = True) -> Dict[str, Any]:
        """
        分析图像中的元素
        
        Args:
            image_path: 图像文件路径
            box_threshold: 检测框阈值
            save_annotated: 是否保存标注图像
            output_dir: 输出目录
            verbose: 是否显示详细信息
            
        Returns:
            dict: 分析结果，包含以下字段：
                - success: bool, 是否成功
                - elements: list, 检测到的元素列表
                - text_elements: list, 文本元素
                - icon_elements: list, 图标元素  
                - annotated_image_path: str, 标注图像路径（如果保存）
                - processing_time: dict, 各阶段耗时
                - image_info: dict, 图像基本信息
                - error: str, 错误信息（如果失败）
        """
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "error": "模型初始化失败"}
        
        if not os.path.exists(image_path):
            return {"success": False, "error": f"图像文件不存在: {image_path}"}
        
        try:
            start_time = time.time()
            
            # 加载图像
            image = Image.open(image_path)
            image_rgb = image.convert('RGB')
            image_info = {
                "path": image_path,
                "size": image.size,
                "mode": image.mode,
                "format": image.format
            }
            
            if verbose:
                print(f"🖼️  分析图像: {os.path.basename(image_path)}")
                print(f"📏 图像尺寸: {image.size}")
            
            # 配置边界框绘制参数
            box_overlay_ratio = max(image.size) / 3200
            draw_bbox_config = {
                'text_scale': 0.8 * box_overlay_ratio,
                'text_thickness': max(int(2 * box_overlay_ratio), 1),
                'text_padding': max(int(3 * box_overlay_ratio), 1),
                'thickness': max(int(3 * box_overlay_ratio), 1),
            }
            
            processing_time = {}
            
            # OCR 检测
            if verbose:
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
            processing_time['ocr'] = time.time() - ocr_start
            
            if verbose:
                print(f"   📝 OCR完成，检测到 {len(text)} 个文本区域 (耗时: {processing_time['ocr']:.2f}s)")
            
            # 图标检测和描述
            if verbose:
                print("🎯 进行图标检测和GPT-4o描述...")
            caption_start = time.time()
            
            dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
                image_path, 
                self.som_model, 
                BOX_TRESHOLD=box_threshold, 
                output_coord_in_ratio=True, 
                ocr_bbox=ocr_bbox,
                draw_bbox_config=draw_bbox_config, 
                caption_model_processor=self.caption_model_processor, 
                ocr_text=text,
                use_local_semantics=True, 
                iou_threshold=0.7, 
                scale_img=False
            )
            
            processing_time['caption'] = time.time() - caption_start
            processing_time['total'] = time.time() - start_time
            
            if verbose:
                print(f"   ✅ 图标识别完成 (耗时: {processing_time['caption']:.2f}s)")
                print(f"   🎯 总共检测到 {len(parsed_content_list)} 个元素")
                print(f"   ⏱️  总耗时: {processing_time['total']:.2f}s")
            
            # 分类元素
            text_elements = [item for item in parsed_content_list if item.get('type') == 'text']
            icon_elements = [item for item in parsed_content_list if item.get('type') == 'icon']
            
            # 保存标注图像（如果需要）
            annotated_image_path = None
            if save_annotated:
                output_filename = f"annotated_{os.path.basename(image_path)}"
                annotated_image_path = os.path.join(output_dir, output_filename)
                
                image_data = base64.b64decode(dino_labled_img)
                output_image = Image.open(io.BytesIO(image_data))
                output_image.save(annotated_image_path)
                
                if verbose:
                    print(f"   💾 标注图像已保存: {annotated_image_path}")
            
            return {
                "success": True,
                "elements": parsed_content_list,
                "text_elements": text_elements,
                "icon_elements": icon_elements,
                "annotated_image_path": annotated_image_path,
                "annotated_image_base64": dino_labled_img if not save_annotated else None,
                "label_coordinates": label_coordinates,
                "processing_time": processing_time,
                "image_info": image_info,
                "element_count": {
                    "total": len(parsed_content_list),
                    "text": len(text_elements),
                    "icon": len(icon_elements)
                }
            }
            
        except Exception as e:
            import traceback
            error_msg = f"分析图像时出错: {e}"
            if verbose:
                print(f"❌ {error_msg}")
                traceback.print_exc()
            
            return {
                "success": False,
                "error": error_msg,
                "traceback": traceback.format_exc()
            }
    
    def batch_analyze(self, image_paths: List[str], **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        批量分析多个图像
        
        Args:
            image_paths: 图像路径列表
            **kwargs: analyze_image方法的其他参数
            
        Returns:
            dict: 每个图像的分析结果，键为图像路径
        """
        results = {}
        verbose = kwargs.get('verbose', True)
        
        if verbose:
            print(f"🔄 开始批量分析 {len(image_paths)} 个图像...")
        
        for i, image_path in enumerate(image_paths, 1):
            if verbose:
                print(f"\n[{i}/{len(image_paths)}] 处理: {os.path.basename(image_path)}")
            
            result = self.analyze_image(image_path, **kwargs)
            results[image_path] = result
            
            if result["success"] and verbose:
                count = result["element_count"]
                print(f"✅ 完成 - 文本:{count['text']} 图标:{count['icon']}")
            elif not result["success"] and verbose:
                print(f"❌ 失败 - {result.get('error', 'Unknown error')}")
        
        return results


# 便捷函数
def analyze_single_image(image_path: str, model_path: str = 'weights/icon_detect/model.pt',
                        config_path: str = "config.json", **kwargs) -> Dict[str, Any]:
    """
    分析单个图像的便捷函数
    
    Args:
        image_path: 图像路径
        model_path: 模型路径
        config_path: 配置路径
        **kwargs: 其他分析参数
        
    Returns:
        dict: 分析结果
    """
    analyzer = ImageElementAnalyzer(model_path, config_path)
    return analyzer.analyze_image(image_path, **kwargs)


def get_element_descriptions(image_path: str, element_type: str = "all", 
                           model_path: str = 'weights/icon_detect/model.pt',
                           config_path: str = "config.json") -> List[Dict[str, Any]]:
    """
    获取图像元素描述的简化函数
    
    Args:
        image_path: 图像路径
        element_type: 元素类型 ("text", "icon", "all")
        model_path: 模型路径  
        config_path: 配置路径
        
    Returns:
        list: 元素描述列表，每个元素包含content和bbox信息
    """
    result = analyze_single_image(image_path, model_path, config_path, verbose=False)
    
    if not result["success"]:
        return []
    
    if element_type == "text":
        return result["text_elements"]
    elif element_type == "icon":
        return result["icon_elements"]
    else:  # "all"
        return result["elements"]


def get_coordinates_by_description(image_path: str, description: str, 
                                 model_path: str = 'weights/icon_detect/model.pt',
                                 config_path: str = "config.json") -> Optional[List[float]]:
    """
    根据描述查找元素坐标
    
    Args:
        image_path: 图像路径
        description: 元素描述
        model_path: 模型路径
        config_path: 配置路径
        
    Returns:
        list: 坐标 [x1, y1, x2, y2] 或 None
    """
    elements = get_element_descriptions(image_path, "all", model_path, config_path)
    
    # 简单的文本匹配查找
    description_lower = description.lower()
    for element in elements:
        content = element.get('content', '').lower()
        if description_lower in content or content in description_lower:
            return element.get('bbox')
    
    return None


if __name__ == "__main__":
    # 使用示例
    print("🚀 图像元素分析器使用示例")
    print("=" * 50)
    
    # 测试图像
    test_images = [
        'imgs/word.png',
        'imgs/windows_home.png', 
        'imgs/google_page.png'
    ]
    
    # 创建分析器
    analyzer = ImageElementAnalyzer()
    
    if not analyzer.initialize():
        print("❌ 分析器初始化失败")
        exit(1)
    
    # 分析单个图像
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n分析图像: {image_path}")
            result = analyzer.analyze_image(
                image_path, 
                save_annotated=True,
                output_dir="result"
            )
            
            if result["success"]:
                print(f"✅ 分析成功，检测到 {result['element_count']['total']} 个元素")
                
                # 显示前几个图标描述
                icons = result["icon_elements"][:3]  # 只显示前3个
                if icons:
                    print("🎯 图标描述示例:")
                    for i, icon in enumerate(icons, 1):
                        content = icon.get('content', 'N/A')
                        bbox = icon.get('bbox', [])
                        print(f"   {i}. {content}")
                        if bbox:
                            print(f"      坐标: [{bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f}]")
            else:
                print(f"❌ 分析失败: {result.get('error')}")
        else:
            print(f"⚠️ 跳过不存在的图像: {image_path}")
    
    print("\n🎉 示例完成！") 