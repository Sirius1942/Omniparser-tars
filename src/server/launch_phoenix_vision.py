#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phoenix Vision MCP Server 启动脚本
🔥 启动凤凰视觉图像分析服务
"""

import asyncio
import os
import sys
from pathlib import Path

# 确保能导入 MCP 服务器
sys.path.append(str(Path(__file__).parent))

from phoenix_vision_mcp_server import main as start_phoenix_vision


def check_requirements():
    """检查必要的文件和依赖"""
    errors = []
    
    # 检查模型文件
    model_path = "weights/icon_detect/model.pt"
    if not os.path.exists(model_path):
        errors.append(f"❌ 模型文件不存在: {model_path}")
        errors.append("   请先下载模型权重文件")
    
    # 检查配置文件
    config_path = "config.json"
    if not os.path.exists(config_path):
        if os.path.exists("config.example.json"):
            errors.append(f"❌ 配置文件不存在: {config_path}")
            errors.append("   请复制 config.example.json 为 config.json 并配置")
        else:
            errors.append(f"❌ 配置文件和示例都不存在")
    
    # 检查必要的依赖
    try:
        import torch
        import fastapi
        import uvicorn
        import aiohttp
    except ImportError as e:
        errors.append(f"❌ 缺少依赖: {e}")
        errors.append("   请运行: pip install -r requirements.txt")
    
    return errors


async def main():
    """主函数"""
    print("🔥 Phoenix Vision MCP Server 启动器")
    print("🌌 与 Nebula Scout Client 完美配合的图像分析服务")
    print("=" * 50)
    
    # 检查依赖
    errors = check_requirements()
    if errors:
        print("⚠️ 启动前检查发现问题:")
        for error in errors:
            print(error)
        print("\n请解决上述问题后重新启动")
        return
    
    print("✅ 依赖检查通过")
    
    # 显示设备信息
    try:
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥️  检测到设备: {device}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🎮 GPU: {gpu_name}")
        else:
            print("💻 使用 CPU 模式")
    except Exception as e:
        print(f"⚠️ 无法检测设备信息: {e}")
    
    # 启动服务器
    print("\n🌐 启动 MCP 服务器...")
    print("📡 支持 SSE (Server-Sent Events) 流式通信")
    print("🔗 API 文档将在启动后可用: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        await start_mcp_server(
            model_path="weights/icon_detect/model.pt",
            config_path="config.json",
            port=8000
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 