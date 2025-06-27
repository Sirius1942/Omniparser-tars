#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
标准 MCP 协议图像分析服务端
符合 Model Context Protocol 标准规范
"""

import asyncio
import json
import os
import base64
import time
import tempfile
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, Prompt, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, GetPromptRequest, GetResourceRequest, ListResourcesRequest,
    ListToolsRequest, ListPromptsRequest
)

# 导入图像分析器
from src.utils.image_element_analyzer import ImageElementAnalyzer

# 全局分析器实例
analyzer: Optional[ImageElementAnalyzer] = None
server = Server("image-analyzer")

def initialize_analyzer() -> bool:
    """初始化图像分析器"""
    global analyzer
    
    if analyzer is not None:
        return True
    
    try:
        print("🚀 正在初始化图像分析器...")
        
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


@server.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="analyze_image_file",
            description="分析图像文件中的文本和图标元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "图像文件路径"
                    },
                    "box_threshold": {
                        "type": "number",
                        "description": "检测框置信度阈值 (0.01-1.0)",
                        "default": 0.05,
                        "minimum": 0.01,
                        "maximum": 1.0
                    },
                    "save_annotated": {
                        "type": "boolean",
                        "description": "是否保存标注后的图像",
                        "default": True
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录路径",
                        "default": "./results"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="analyze_image_base64",
            description="分析 Base64 编码的图像",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_base64": {
                        "type": "string",
                        "description": "Base64 编码的图片数据"
                    },
                    "box_threshold": {
                        "type": "number",
                        "description": "检测框置信度阈值 (0.01-1.0)",
                        "default": 0.05,
                        "minimum": 0.01,
                        "maximum": 1.0
                    },
                    "save_annotated": {
                        "type": "boolean",
                        "description": "是否保存标注后的图像",
                        "default": True
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录路径",
                        "default": "./results"
                    }
                },
                "required": ["image_base64"]
            }
        ),
        Tool(
            name="get_device_status",
            description="获取设备和分析器状态信息",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """调用工具"""
    
    # 确保分析器已初始化
    if not initialize_analyzer():
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "分析器初始化失败"
            }, ensure_ascii=False, indent=2)
        )]
    
    if name == "analyze_image_file":
        return await _analyze_image_file(arguments)
    elif name == "analyze_image_base64":
        return await _analyze_image_base64(arguments)
    elif name == "get_device_status":
        return await _get_device_status(arguments)
    else:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"未知工具: {name}"
            }, ensure_ascii=False, indent=2)
        )]


async def _analyze_image_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """分析图像文件"""
    try:
        image_path = arguments.get("image_path")
        box_threshold = arguments.get("box_threshold", 0.05)
        save_annotated = arguments.get("save_annotated", True)
        output_dir = arguments.get("output_dir", "./results")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }, ensure_ascii=False, indent=2)
            )]
        
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
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"分析图像时出错: {str(e)}",
                "timestamp": time.time()
            }, ensure_ascii=False, indent=2)
        )]


async def _analyze_image_base64(arguments: Dict[str, Any]) -> List[TextContent]:
    """分析 Base64 编码的图像"""
    try:
        image_base64 = arguments.get("image_base64")
        box_threshold = arguments.get("box_threshold", 0.05)
        save_annotated = arguments.get("save_annotated", True)
        output_dir = arguments.get("output_dir", "./results")
        
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
        temp_path = f"temp_mcp_{timestamp}.png"
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"分析 Base64 图像时出错: {str(e)}",
                "timestamp": time.time()
            }, ensure_ascii=False, indent=2)
        )]


async def _get_device_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """获取设备状态"""
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
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"获取设备状态失败: {str(e)}",
                "timestamp": time.time()
            }, ensure_ascii=False, indent=2)
        )]


@server.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用资源"""
    return [
        Resource(
            uri="file://results/",
            name="分析结果目录",
            description="图像分析结果和标注图像的存储目录",
            mimeType="application/x-directory"
        ),
        Resource(
            uri="config://analyzer",
            name="分析器配置",
            description="当前分析器的配置和状态信息",
            mimeType="application/json"
        )
    ]


@server.get_resource()
async def get_resource(uri: str) -> str:
    """获取资源内容"""
    if uri == "file://results/":
        # 列出结果目录中的文件
        results_dir = Path("./results")
        if not results_dir.exists():
            return "结果目录不存在"
        
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
    
    elif uri == "config://analyzer":
        # 返回分析器配置信息
        config_info = {
            "initialized": analyzer is not None,
            "ready": analyzer is not None and analyzer._initialized if analyzer else False,
            "model_path": "weights/icon_detect/model.pt",
            "config_path": "config.json"
        }
        
        if analyzer:
            config_info.update({
                "device": analyzer.device,
                "model_loaded": analyzer.som_model is not None,
                "caption_model_loaded": analyzer.caption_model_processor is not None
            })
        
        return json.dumps(config_info, ensure_ascii=False, indent=2)
    
    else:
        return f"未知资源: {uri}"


@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """列出可用提示"""
    return [
        Prompt(
            name="analyze_image_tips",
            description="图像分析使用提示和最佳实践",
            arguments=[
                {
                    "name": "image_type",
                    "description": "图像类型 (screenshot, document, ui, photo)",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="troubleshoot_analysis",
            description="图像分析问题排查指南",
            arguments=[
                {
                    "name": "error_type",
                    "description": "错误类型",
                    "required": False
                }
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> str:
    """获取提示内容"""
    if name == "analyze_image_tips":
        image_type = arguments.get("image_type", "general")
        
        tips = f"""
# 图像分析使用提示

## 图像类型: {image_type}

### 最佳实践:
1. **图像质量**: 确保图像清晰，分辨率适中 (推荐 800-3200px)
2. **检测阈值**: 
   - 复杂图像: box_threshold = 0.03-0.05
   - 简单图像: box_threshold = 0.05-0.1
3. **输出目录**: 使用绝对路径或确保目录存在
4. **文件格式**: 支持 PNG, JPG, JPEG, BMP

### 参数建议:
- **截图分析**: box_threshold=0.05, save_annotated=true
- **文档分析**: box_threshold=0.03, save_annotated=true  
- **UI界面**: box_threshold=0.05, save_annotated=true

### 注意事项:
- 首次运行需要初始化模型，可能需要较长时间
- GPU 模式比 CPU 模式快 3-5 倍
- 大图像 (>5MB) 处理时间较长
"""
        return tips
    
    elif name == "troubleshoot_analysis":
        error_type = arguments.get("error_type", "general")
        
        guide = f"""
# 图像分析问题排查指南

## 错误类型: {error_type}

### 常见问题及解决方案:

1. **模型初始化失败**
   - 检查 weights/icon_detect/model.pt 是否存在
   - 检查 config.json 配置文件
   - 确认 PyTorch 和相关依赖已安装

2. **图像文件不存在**
   - 验证文件路径是否正确
   - 检查文件权限
   - 支持的格式: PNG, JPG, JPEG, BMP

3. **GPU 内存不足**
   - 减小图像尺寸
   - 调整 batch size
   - 使用 CPU 模式

4. **分析结果质量差**
   - 调整 box_threshold 参数
   - 检查图像质量和清晰度
   - 确认图像类型适合分析

5. **处理速度慢**
   - 使用 GPU 加速
   - 减小图像尺寸
   - 关闭详细输出 (verbose=False)

### 日志分析:
- 查看控制台输出的详细信息
- 检查 OCR 和图标检测的耗时
- 监控内存和 GPU 使用情况
"""
        return guide
    
    else:
        return f"未知提示: {name}"


async def main():
    """启动 MCP 服务器"""
    print("🎯 标准 MCP 协议图像分析服务器")
    print("=" * 50)
    
    # 显示设备信息
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🖥️  设备: {device}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("💻 使用 CPU 模式")
    
    print("\n📋 可用功能:")
    print("   • analyze_image_file - 分析图像文件")
    print("   • analyze_image_base64 - 分析 Base64 图像") 
    print("   • get_device_status - 获取设备状态")
    print("\n📚 可用资源:")
    print("   • file://results/ - 分析结果目录")
    print("   • config://analyzer - 分析器配置")
    print("\n💡 可用提示:")
    print("   • analyze_image_tips - 使用提示")
    print("   • troubleshoot_analysis - 问题排查")
    print("\n🚀 启动 MCP 服务器...")
    print("=" * 50)
    
    # 运行 stdio 服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main()) 