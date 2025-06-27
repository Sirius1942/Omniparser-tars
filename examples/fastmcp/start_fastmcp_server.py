#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像元素分析器 FastMCP 服务器启动脚本
提供多种启动选项和环境检查
"""

import os
import sys
import argparse
from pathlib import Path

def check_requirements():
    """检查必要的文件和依赖"""
    errors = []
    warnings = []
    
    print("🔍 检查环境和依赖...")
    
    # 检查 FastMCP 依赖
    try:
        import fastmcp
        print(f"✅ FastMCP 已安装 (版本: {fastmcp.__version__ if hasattr(fastmcp, '__version__') else 'Unknown'})")
    except ImportError:
        errors.append("❌ FastMCP 未安装")
        errors.append("   请运行: pip install fastmcp")
    
    # 检查其他依赖
    required_modules = [
        ('torch', 'PyTorch'),
        ('PIL', 'Pillow'),
        ('transformers', 'Transformers'),
        ('ultralytics', 'Ultralytics'),
        ('easyocr', 'EasyOCR'),
        ('paddleocr', 'PaddleOCR')
    ]
    
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"✅ {name} 已安装")
        except ImportError:
            warnings.append(f"⚠️  {name} 未安装 - 某些功能可能不可用")
    
    # 检查核心文件
    core_files = [
        "util/image_element_analyzer.py",
        "image_element_analyzer_fastmcp_server.py"
    ]
    
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"✅ 核心文件存在: {file_path}")
        else:
            errors.append(f"❌ 核心文件缺失: {file_path}")
    
    # 检查可选文件
    optional_files = [
        ("weights/icon_detect/model.pt", "YOLO模型文件"),
        ("config.json", "配置文件")
    ]
    
    for file_path, description in optional_files:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
        else:
            if "config.json" in file_path and os.path.exists("config.example.json"):
                warnings.append(f"⚠️  {description}不存在，但发现示例文件")
                warnings.append(f"   请复制 config.example.json 为 config.json")
            else:
                warnings.append(f"⚠️  {description}不存在: {file_path}")
    
    # 检查输出目录
    results_dir = Path("results")
    if not results_dir.exists():
        results_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建输出目录: {results_dir}")
    else:
        print(f"✅ 输出目录存在: {results_dir}")
    
    return errors, warnings


def print_status(errors, warnings):
    """打印状态信息"""
    print("\n" + "="*60)
    
    if errors:
        print("❌ 发现错误:")
        for error in errors:
            print(f"   {error}")
        print()
        return False
    
    if warnings:
        print("⚠️  发现警告:")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    print("✅ 环境检查通过!")
    return True


def run_server(debug=False, host="127.0.0.1", port=None):
    """运行服务器"""
    print("\n" + "="*60)
    print("🚀 启动 FastMCP 服务器...")
    print("="*60)
    
    # 添加当前目录到 Python 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # 导入服务器模块
        from image_element_analyzer_fastmcp_server import mcp
        
        print(f"🌐 主机: {host}")
        if port:
            print(f"🔢 端口: {port}")
        if debug:
            print("🐛 调试模式: 开启")
        
        print("\n📋 服务器信息:")
        print(f"   • 名称: {mcp.name}")
        print(f"   • 工具数量: {len(mcp._tools) if hasattr(mcp, '_tools') else 'Unknown'}")
        print(f"   • 资源数量: {len(mcp._resources) if hasattr(mcp, '_resources') else 'Unknown'}")
        print(f"   • 提示数量: {len(mcp._prompts) if hasattr(mcp, '_prompts') else 'Unknown'}")
        
        print("\n💡 使用提示:")
        print("   • 通过 stdio 连接: python image_element_analyzer_fastmcp_server.py")
        print("   • 通过 HTTP 连接: 在浏览器中访问相应端口")
        print("   • 客户端示例: python fastmcp_client_example.py")
        print("   • 停止服务器: Ctrl+C")
        
        print("\n" + "="*60)
        
        # 运行服务器
        if port:
            # HTTP 模式
            mcp.run(transport="http", host=host, port=port)
        else:
            # stdio 模式（默认）
            mcp.run()
            
    except ImportError as e:
        print(f"❌ 导入服务器模块失败: {e}")
        print("   请确保 image_element_analyzer_fastmcp_server.py 文件存在且可访问")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  服务器已停止")
        return True
    except Exception as e:
        print(f"\n❌ 启动服务器时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_debug_mode():
    """运行调试模式"""
    print("\n🐛 启动调试模式...")
    print("这将打开 FastMCP 内置的调试工具")
    
    try:
        # 尝试启动调试器
        import subprocess
        script_path = "image_element_analyzer_fastmcp_server.py"
        
        # 使用 FastMCP 的调试命令
        cmd = ["python", "-m", "fastmcp", "dev", script_path]
        print(f"运行命令: {' '.join(cmd)}")
        
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ 启动调试模式失败: {e}")
        print("尝试手动运行: python -m fastmcp dev image_element_analyzer_fastmcp_server.py")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="图像元素分析器 FastMCP 服务器启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python start_fastmcp_server.py                    # 标准 stdio 模式
  python start_fastmcp_server.py --http --port 8000 # HTTP 模式
  python start_fastmcp_server.py --debug            # 调试模式
  python start_fastmcp_server.py --check-only       # 仅检查环境
        """
    )
    
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="仅检查环境，不启动服务器"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启动调试模式（使用 FastMCP 调试工具）"
    )
    
    parser.add_argument(
        "--http", 
        action="store_true", 
        help="使用 HTTP 传输模式而不是 stdio"
    )
    
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="HTTP 模式的主机地址 (默认: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        help="HTTP 模式的端口号 (默认: FastMCP 自动选择)"
    )
    
    args = parser.parse_args()
    
    print("🎯 图像元素分析器 FastMCP 服务器启动器")
    print("=" * 60)
    
    # 检查环境
    errors, warnings = check_requirements()
    status_ok = print_status(errors, warnings)
    
    if not status_ok:
        print("\n❌ 环境检查失败，无法启动服务器")
        sys.exit(1)
    
    if args.check_only:
        print("\n✅ 环境检查完成，退出")
        sys.exit(0)
    
    # 确定启动模式
    if args.debug:
        run_debug_mode()
    else:
        port = args.port if args.http else None
        success = run_server(
            debug=args.debug,
            host=args.host,
            port=port
        )
        
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main() 