#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phoenix Vision 服务启动脚本
🔥 直接启动 Phoenix Vision FastMCP 服务器
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动 Phoenix Vision FastMCP 服务器"""
    print("🔥 Phoenix Vision FastMCP 服务器启动器")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    server_script = project_root / "src/server/phoenix_vision_fastmcp_server.py"
    
    # 检查服务器脚本是否存在
    if not server_script.exists():
        print(f"❌ 服务器脚本不存在: {server_script}")
        sys.exit(1)
    
    print(f"📍 项目根目录: {project_root}")
    print(f"📍 服务器脚本: {server_script}")
    print(f"🌐 服务器地址: http://127.0.0.1:8923/sse/")
    print(f"💡 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    try:
        # 切换到项目根目录并启动服务器
        os.chdir(project_root)
        subprocess.run([sys.executable, str(server_script)], env=env, cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()