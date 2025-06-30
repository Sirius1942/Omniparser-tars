#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phoenix Vision FastMCP Server - 凤凰视觉FastMCP服务端
基于 FastMCP 的智能图像元素分析服务
🔥 Phoenix Vision - 涅槃重生的图像识别能力
"""

import os
import sys
import json
import time
import base64
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastmcp import FastMCP

# 尝试导入图像分析器
try:
    from src.utils.image_element_analyzer import ImageElementAnalyzer
    analyzer_available = True
except ImportError as e:
    print(f"⚠️ 无法导入图像分析器: {e}")
    analyzer_available = False

# 创建 Phoenix Vision 服务器
mcp = FastMCP("phoenix-vision")

# 全局分析器实例
analyzer: Optional[ImageElementAnalyzer] = None

def initialize_analyzer() -> bool:
    """初始化图像分析器"""
    global analyzer
    
    if not analyzer_available:
        print("❌ 图像分析器不可用")
        return False
    
    if analyzer is not None:
        return True
    
    try:
        print("🚀 正在初始化图像分析器...")
        
        # 检查模型和配置文件 - 使用绝对路径
        model_path = os.path.join(project_root, 'weights/icon_detect/model.pt')
        config_path = os.path.join(project_root, "config.json")
        
        print(f"📍 项目根目录: {project_root}")
        print(f"📍 模型路径: {model_path}")
        print(f"📍 配置路径: {config_path}")
        
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return False
            
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        # 切换到项目根目录
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            analyzer = ImageElementAnalyzer(model_path, config_path)
            success = analyzer.initialize()
        finally:
            # 恢复原工作目录
            os.chdir(original_cwd)
        
        if success:
            print("✅ 分析器初始化成功")
            return True
        else:
            print("❌ 分析器初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 初始化分析器时出错: {e}")
        traceback.print_exc()
        return False

@mcp.tool()
def analyze_image_file(
    image_path: str,
    box_threshold: float = 0.05,
    save_annotated: bool = True,
    output_dir: str = "./results"
) -> dict:
    """分析图像文件中的文本和图标元素"""
    
    # 确保分析器已初始化
    if not initialize_analyzer():
        return {
            "success": False,
            "error": "分析器初始化失败",
            "timestamp": time.time()
        }
    
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"图像文件不存在: {image_path}",
                "timestamp": time.time()
            }
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🖼️  分析图像: {os.path.basename(image_path)}")
        
        # 执行分析
        result = analyzer.analyze_image(
            image_path,
            box_threshold=box_threshold,
            save_annotated=save_annotated,
            output_dir=output_dir,
            verbose=True
        )
        
        # 添加时间戳
        result["timestamp"] = time.time()
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"分析图像时出错: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()
def analyze_image_base64(
    image_base64: str,
    box_threshold: float = 0.05,
    save_annotated: bool = True,
    output_dir: str = "./results"
) -> dict:
    """分析 Base64 编码的图像"""
    
    # 确保分析器已初始化
    if not initialize_analyzer():
        return {
            "success": False,
            "error": "分析器初始化失败",
            "timestamp": time.time()
        }
    
    try:
        # 移除可能的前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # 解码图像
        from PIL import Image
        import io
        
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 保存临时文件
        timestamp = int(time.time() * 1000)
        temp_path = f"temp_fastmcp_{timestamp}.png"
        image.save(temp_path)
        
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🖼️  分析 Base64 图像 (大小: {image.size})")
            
            # 执行分析
            result = analyzer.analyze_image(
                temp_path,
                box_threshold=box_threshold,
                save_annotated=save_annotated,
                output_dir=output_dir,
                verbose=True
            )
            
            # 添加时间戳
            result["timestamp"] = time.time()
            
            return result
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return {
            "success": False,
            "error": f"分析 Base64 图像时出错: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()
def get_device_status() -> dict:
    """获取设备和分析器状态信息"""
    try:
        import torch
        
        # 获取设备信息
        device_info = {
            "device": 'cuda' if torch.cuda.is_available() else 'cpu',
            "cuda_available": torch.cuda.is_available(),
        }
        
        if torch.cuda.is_available():
            device_info.update({
                "cuda_version": torch.version.cuda,
                "gpu_count": torch.cuda.device_count(),
                "current_gpu": torch.cuda.current_device(),
                "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None,
                "gpu_memory": {
                    "total": torch.cuda.get_device_properties(0).total_memory if torch.cuda.device_count() > 0 else 0,
                    "allocated": torch.cuda.memory_allocated(0) if torch.cuda.device_count() > 0 else 0,
                    "cached": torch.cuda.memory_reserved(0) if torch.cuda.device_count() > 0 else 0
                }
            })
        
        # 检查分析器状态
        analyzer_status = {
            "initialized": analyzer is not None,
            "ready": analyzer is not None and analyzer._initialized if analyzer else False
        }
        
        result = {
            "success": True,
            "device_info": device_info,
            "analyzer_status": analyzer_status,
            "timestamp": time.time()
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取设备状态失败: {str(e)}",
            "timestamp": time.time()
        }

@mcp.resource("phoenix://results")
def get_results_directory() -> str:
    """获取分析结果目录信息"""
    try:
        results_dir = Path(os.path.join(project_root, "results"))
        
        if not results_dir.exists():
            return json.dumps({
                "directory": str(results_dir.absolute()),
                "files": [],
                "count": 0,
                "message": "结果目录不存在"
            }, ensure_ascii=False, indent=2)
        
        files = []
        for file_path in results_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "size": stat.st_size,
                    "modified": time.ctime(stat.st_mtime)
                })
        
        return json.dumps({
            "directory": str(results_dir.absolute()),
            "files": files,
            "count": len(files)
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"获取结果目录失败: {str(e)}",
            "timestamp": time.time()
        }, ensure_ascii=False, indent=2)

@mcp.resource("phoenix://config")
def get_analyzer_config() -> str:
    """获取分析器配置信息"""
    try:
        config_info = {
            "initialized": analyzer is not None,
            "ready": analyzer is not None and analyzer._initialized if analyzer else False,
            "model_path": os.path.join(project_root, "weights/icon_detect/model.pt"),
            "config_path": os.path.join(project_root, "config.json"),
            "analyzer_available": analyzer_available
        }
        
        if analyzer:
            config_info.update({
                "device": analyzer.device,
                "model_loaded": analyzer.som_model is not None,
                "caption_model_loaded": analyzer.caption_model_processor is not None
            })
        
        return json.dumps(config_info, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"获取配置信息失败: {str(e)}",
            "timestamp": time.time()
        }, ensure_ascii=False, indent=2)

@mcp.prompt()
def analyze_image_tips(image_type: str = "general") -> str:
    """图像分析使用提示和最佳实践"""
    return f"""
# 🔥 Phoenix Vision 图像分析使用提示

## 图像类型: {image_type}

### 🎯 最佳实践:
1. **图像质量**: 确保图像清晰，分辨率适中 (推荐 800-3200px)
2. **检测阈值**: 
   - 复杂图像: box_threshold = 0.03-0.05
   - 简单图像: box_threshold = 0.05-0.1
3. **输出目录**: 使用绝对路径或确保目录存在
4. **文件格式**: 支持 PNG, JPG, JPEG, BMP

### 📊 参数建议:
- **截图分析**: box_threshold=0.05, save_annotated=true
- **文档分析**: box_threshold=0.03, save_annotated=true  
- **UI界面**: box_threshold=0.05, save_annotated=true

### ⚠️ 注意事项:
- 首次运行需要初始化模型，可能需要较长时间
- GPU 模式比 CPU 模式快 3-5 倍
- 大图像 (>5MB) 处理时间较长

### 🚀 快速开始:
```python
# 分析图像文件
result = await mcp_client.call_tool("analyze_image_file", {{
    "image_path": "your_image.png",
    "box_threshold": 0.05,
    "save_annotated": True
}})
```
"""

if __name__ == "__main__":
    print("🔥 Phoenix Vision FastMCP 服务器")
    print("=" * 50)
    
    # 显示设备信息
    try:
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥️  设备: {device}")
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("💻 使用 CPU 模式")
    except ImportError:
        print("⚠️ PyTorch 未安装")
    
    print(f"\n📍 项目根目录: {project_root}")
    print(f"📋 分析器可用: {'✅' if analyzer_available else '❌'}")
    
    print("\n🔧 可用工具:")
    print("   • analyze_image_file - 分析图像文件")
    print("   • analyze_image_base64 - 分析 Base64 图像") 
    print("   • get_device_status - 获取设备状态")
    print("\n📚 可用资源:")
    print("   • phoenix://results - 分析结果目录")
    print("   • phoenix://config - 分析器配置")
    print("\n💡 可用提示:")
    print("   • analyze_image_tips - 使用提示")
    print("\n🚀 启动 FastMCP 服务器...")
    print("=" * 50)
    
    # 使用 stdio 传输协议运行服务器
    mcp.run(transport="sse", host="0.0.0.0", port=8923) 