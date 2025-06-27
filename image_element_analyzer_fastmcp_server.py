#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像元素分析器 FastMCP 服务器
基于 FastMCP 框架实现图片分析服务
支持 GPU/CPU 自动选择
"""

import os
import time
import base64
import io
import traceback
from typing import Dict, Any, Optional, List
from PIL import Image
import torch
from pathlib import Path

# FastMCP 相关导入 - 兼容性修复版
try:
    from fastmcp import FastMCP
    
    # 尝试多种方式导入 Message 和 TextContent
    Message = None
    TextContent = None
    
    # 方式1: 从 mcp.types 导入
    try:
        from mcp.types import Message, TextContent
    except ImportError:
        # 方式2: 从 fastmcp 直接导入
        try:
            from fastmcp import Message, TextContent
        except ImportError:
            # 方式3: 从 mcp 导入
            try:
                from mcp import Message, TextContent
            except ImportError:
                # 方式4: 使用后备类定义
                class Message:
                    """消息类 - 兼容 MCP 协议"""
                    def __init__(self, role: str, content: list):
                        self.role = role
                        self.content = content
                
                class TextContent:
                    """文本内容类 - 兼容 MCP 协议"""
                    def __init__(self, text: str):
                        self.text = text
                        
                print("⚠️ 使用内置的 Message 和 TextContent 类")
    
except ImportError:
    print("❌ FastMCP 未安装，请运行: pip install fastmcp")
    print("   或者尝试: pip install fastmcp mcp")
    exit(1)

# 导入图像分析器
from util.image_element_analyzer import ImageElementAnalyzer


# 创建 FastMCP 服务器实例
mcp = FastMCP(
    name="图像元素分析器",
    dependencies=["torch", "PIL", "pandas", "transformers", "ultralytics", "easyocr", "paddleocr"]
)

# 全局变量存储分析器实例
analyzer: Optional[ImageElementAnalyzer] = None
device_info: Dict[str, Any] = {}


def get_device_info() -> Dict[str, Any]:
    """获取设备信息"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    info = {
        "device": device,
        "cuda_available": torch.cuda.is_available(),
    }
    
    if torch.cuda.is_available():
        info.update({
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
    
    return info


def initialize_analyzer() -> bool:
    """初始化分析器"""
    global analyzer, device_info
    
    if analyzer is not None:
        return True
    
    try:
        device_info = get_device_info()
        print(f"🚀 正在初始化图像分析器...")
        print(f"🖥️  设备信息: {device_info['device']}")
        if device_info['cuda_available']:
            print(f"🎮 GPU: {device_info.get('gpu_name', 'Unknown')}")
        
        # 检查模型和配置文件
        model_path = 'weights/icon_detect/model.pt'
        config_path = "config.json"
        
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return False
            
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        analyzer = ImageElementAnalyzer(model_path, config_path)
        success = analyzer.initialize()
        
        if success:
            print("✅ 分析器初始化成功")
            return True
        else:
            print("❌ 分析器初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 初始化分析器时出错: {e}")
        return False


@mcp.tool()
def analyze_image_file(
    image_path: str,
    box_threshold: float = 0.05,
    save_annotated: bool = False,
    output_dir: str = "./results"
) -> Dict[str, Any]:
    """
    分析图像文件中的文本和图标元素
    
    Args:
        image_path: 图像文件路径
        box_threshold: 检测框置信度阈值 (0.01-1.0)
        save_annotated: 是否保存标注后的图像
        output_dir: 输出目录路径
        
    Returns:
        包含分析结果的字典
    """
    # 确保分析器已初始化
    if not initialize_analyzer():
        return {
            "success": False,
            "error": "分析器初始化失败",
            "device_info": device_info
        }
    
    try:
        # 展开路径中的波浪号
        expanded_path = os.path.expanduser(image_path)
        
        if not os.path.exists(expanded_path):
            return {
                "success": False,
                "error": f"图像文件不存在: {expanded_path}"
            }
        
        print(f"🖼️  分析图像: {os.path.basename(expanded_path)}")
        
        # 执行分析
        result = analyzer.analyze_image(
            expanded_path,
            box_threshold=box_threshold,
            save_annotated=save_annotated,
            output_dir=output_dir,
            verbose=True
        )
        
        # 添加设备信息
        result["device_info"] = device_info
        
        return result
        
    except Exception as e:
        error_msg = f"分析图像时出错: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "traceback": traceback.format_exc(),
            "device_info": device_info
        }


@mcp.tool()
def analyze_image_base64(
    image_base64: str,
    box_threshold: float = 0.05,
    save_annotated: bool = False,
    output_dir: str = "./results"
) -> Dict[str, Any]:
    """
    分析 Base64 编码的图像
    
    Args:
        image_base64: Base64 编码的图片数据
        box_threshold: 检测框置信度阈值 (0.01-1.0)
        save_annotated: 是否保存标注后的图像
        output_dir: 输出目录路径
        
    Returns:
        包含分析结果的字典
    """
    # 确保分析器已初始化
    if not initialize_analyzer():
        return {
            "success": False,
            "error": "分析器初始化失败",
            "device_info": device_info
        }
    
    try:
        # 移除可能的前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # 解码图像
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 保存临时文件
        temp_path = f"temp_fastmcp_{int(time.time()*1000)}.png"
        image.save(temp_path)
        
        try:
            print(f"🖼️  分析 Base64 图像 (大小: {image.size})")
            
            # 执行分析
            result = analyzer.analyze_image(
                temp_path,
                box_threshold=box_threshold,
                save_annotated=save_annotated,
                output_dir=output_dir,
                verbose=True
            )
            
            # 添加设备信息
            result["device_info"] = device_info
            
            return result
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        error_msg = f"分析 Base64 图像时出错: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "traceback": traceback.format_exc(),
            "device_info": device_info
        }


@mcp.tool()
def batch_analyze_images(
    image_paths: List[str],
    box_threshold: float = 0.05,
    save_annotated: bool = False,
    output_dir: str = "./results"
) -> Dict[str, Any]:
    """
    批量分析多个图像文件
    
    Args:
        image_paths: 图像文件路径列表
        box_threshold: 检测框置信度阈值 (0.01-1.0)
        save_annotated: 是否保存标注后的图像
        output_dir: 输出目录路径
        
    Returns:
        包含批量分析结果的字典
    """
    # 确保分析器已初始化
    if not initialize_analyzer():
        return {
            "success": False,
            "error": "分析器初始化失败",
            "device_info": device_info
        }
    
    try:
        print(f"🔄 开始批量分析 {len(image_paths)} 个图像...")
        
        results = {}
        success_count = 0
        
        for i, image_path in enumerate(image_paths, 1):
            expanded_path = os.path.expanduser(image_path)
            print(f"\n[{i}/{len(image_paths)}] 处理: {os.path.basename(expanded_path)}")
            
            if not os.path.exists(expanded_path):
                results[image_path] = {
                    "success": False,
                    "error": f"文件不存在: {expanded_path}"
                }
                continue
            
            try:
                result = analyzer.analyze_image(
                    expanded_path,
                    box_threshold=box_threshold,
                    save_annotated=save_annotated,
                    output_dir=output_dir,
                    verbose=False
                )
                
                results[image_path] = result
                
                if result.get("success", False):
                    success_count += 1
                    count = result.get("element_count", {})
                    print(f"✅ 完成 - 文本:{count.get('text', 0)} 图标:{count.get('icon', 0)}")
                else:
                    print(f"❌ 失败 - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_msg = f"分析失败: {str(e)}"
                results[image_path] = {
                    "success": False,
                    "error": error_msg
                }
                print(f"❌ 失败 - {error_msg}")
        
        return {
            "success": True,
            "total_images": len(image_paths),
            "success_count": success_count,
            "failed_count": len(image_paths) - success_count,
            "results": results,
            "device_info": device_info
        }
        
    except Exception as e:
        error_msg = f"批量分析出错: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "traceback": traceback.format_exc(),
            "device_info": device_info
        }


@mcp.tool()
def get_device_status() -> Dict[str, Any]:
    """
    获取当前设备状态信息
    
    Returns:
        包含设备信息的字典
    """
    try:
        current_info = get_device_info()
        
        # 如果有 CUDA，更新内存信息
        if current_info['cuda_available']:
            current_info['gpu_memory'] = {
                "total": torch.cuda.get_device_properties(0).total_memory,
                "allocated": torch.cuda.memory_allocated(0),
                "cached": torch.cuda.memory_reserved(0),
                "free": torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
            }
        
        # 检查分析器状态
        analyzer_status = {
            "initialized": analyzer is not None,
            "ready": analyzer is not None and analyzer._initialized if analyzer else False
        }
        
        return {
            "success": True,
            "device_info": current_info,
            "analyzer_status": analyzer_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取设备状态失败: {str(e)}",
            "timestamp": time.time()
        }


@mcp.resource("image://recent/{filename}")
def get_recent_image_analysis(filename: str) -> str:
    """
    获取最近分析的图像结果
    
    Args:
        filename: 图像文件名
        
    Returns:
        图像分析结果的文本描述
    """
    try:
        # 在结果目录中查找相关文件
        results_dir = Path("./results")
        if not results_dir.exists():
            return f"结果目录不存在: {results_dir}"
        
        # 查找可能的结果文件
        possible_files = list(results_dir.glob(f"*{filename}*"))
        
        if not possible_files:
            return f"未找到与 '{filename}' 相关的分析结果"
        
        # 返回找到的文件信息
        file_info = []
        for file_path in possible_files:
            stat = file_path.stat()
            file_info.append(f"文件: {file_path.name}, 大小: {stat.st_size} 字节, 修改时间: {time.ctime(stat.st_mtime)}")
        
        return f"找到 {len(possible_files)} 个相关结果文件:\n" + "\n".join(file_info)
        
    except Exception as e:
        return f"获取最近分析结果时出错: {str(e)}"


@mcp.resource("device://status")
def get_device_resource() -> str:
    """
    作为资源提供设备状态信息
    
    Returns:
        设备状态的文本描述
    """
    try:
        info = get_device_info()
        
        status_text = f"设备类型: {info['device']}\n"
        status_text += f"CUDA 可用: {info['cuda_available']}\n"
        
        if info['cuda_available']:
            status_text += f"CUDA 版本: {info.get('cuda_version', 'Unknown')}\n"
            status_text += f"GPU 数量: {info.get('gpu_count', 0)}\n"
            status_text += f"当前 GPU: {info.get('gpu_name', 'Unknown')}\n"
            
            gpu_memory = info.get('gpu_memory', {})
            if gpu_memory:
                total_gb = gpu_memory.get('total', 0) / (1024**3)
                allocated_gb = gpu_memory.get('allocated', 0) / (1024**3)
                status_text += f"GPU 内存: {allocated_gb:.2f}GB / {total_gb:.2f}GB"
        
        analyzer_ready = analyzer is not None and analyzer._initialized if analyzer else False
        status_text += f"\n分析器状态: {'就绪' if analyzer_ready else '未初始化'}"
        
        return status_text
        
    except Exception as e:
        return f"获取设备状态时出错: {str(e)}"


@mcp.prompt()
def debug_analysis_error(error_message: str, image_path: str = "") -> List[Message]:
    """
    生成调试图像分析错误的提示
    
    Args:
        error_message: 错误信息
        image_path: 可选的图像路径
        
    Returns:
        调试提示消息列表
    """
    prompt_text = f"""我在使用图像元素分析器时遇到了错误：

错误信息: {error_message}
"""
    
    if image_path:
        prompt_text += f"图像路径: {image_path}\n"
    
    prompt_text += """
请帮我分析可能的原因并提供解决方案。常见问题包括：

1. 文件路径问题（文件不存在、权限问题）
2. 图像格式不支持
3. 模型文件缺失或损坏
4. 配置文件问题
5. GPU/CPU 内存不足
6. 依赖库版本冲突

请提供具体的排查步骤和解决建议。
"""
    
    return [
        Message(
            role="user",
            content=[
                TextContent(text=prompt_text)
            ]
        )
    ]


@mcp.prompt()
def optimize_analysis_settings(
    image_type: str = "screenshot",
    quality_priority: str = "balanced"
) -> List[Message]:
    """
    生成优化分析设置的提示
    
    Args:
        image_type: 图像类型 (screenshot, document, ui, mixed)
        quality_priority: 质量优先级 (speed, balanced, accuracy)
        
    Returns:
        优化建议消息列表
    """
    prompt_text = f"""请为我的图像分析任务推荐最佳参数设置：

图像类型: {image_type}
质量优先级: {quality_priority}

可调整的参数包括：
- box_threshold: 检测框置信度阈值 (0.01-1.0)
- save_annotated: 是否保存标注图像
- output_dir: 输出目录设置

请根据我的需求推荐具体的参数值，并解释选择这些值的原因。
"""
    
    return [
        Message(
            role="user",
            content=[
                TextContent(text=prompt_text)
            ]
        )
    ]


if __name__ == "__main__":
    # 配置服务器端口
    port_number = 8999
    
    print("🎯 图像元素分析器 FastMCP 服务器")
    print("=" * 50)
    
    # 显示设备信息
    device_info = get_device_info()
    print(f"🖥️  设备: {device_info['device']}")
    if device_info['cuda_available']:
        print(f"🎮 GPU: {device_info.get('gpu_name', 'Unknown')}")
    else:
        print("💻 使用 CPU 模式")
    
    print(f"\n🌐 服务端口: {port_number}")
    print("\n🚀 启动 FastMCP 服务器...")
    print("📋 可用工具:")
    print("   • analyze_image_file - 分析图像文件")
    print("   • analyze_image_base64 - 分析 Base64 图像")
    print("   • batch_analyze_images - 批量分析图像")
    print("   • get_device_status - 获取设备状态")
    print("\n📚 可用资源:")
    print("   • image://recent/{filename} - 最近分析结果")
    print("   • device://status - 设备状态")
    print("\n💡 可用提示:")
    print("   • debug_analysis_error - 调试分析错误")
    print("   • optimize_analysis_settings - 优化分析设置")
    print("\n" + "=" * 50)
    
    # 运行服务器
    mcp.run(transport="sse", host="0.0.0.0", port=port_number) 