#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastMCP 图像分析器演示启动脚本
自动检查服务器状态并运行客户端演示
"""

import subprocess
import time
import requests
import os
import sys
from pathlib import Path


def check_server_running(port: int = 8999) -> bool:
    """检查服务器是否正在运行"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=3)
        return True
    except:
        return False


def start_server():
    """启动服务器"""
    print("🚀 启动 FastMCP 服务器...")
    
    # 检查服务器文件是否存在
    server_file = "image_element_analyzer_fastmcp_server.py"
    if not os.path.exists(server_file):
        print(f"❌ 服务器文件不存在: {server_file}")
        return None
    
    try:
        # 启动服务器进程
        process = subprocess.Popen([
            sys.executable, server_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        for i in range(15):  # 最多等待15秒
            if check_server_running():
                print("✅ 服务器启动成功!")
                return process
            time.sleep(1)
            print(f"   等待中... ({i+1}/15)")
        
        print("❌ 服务器启动超时")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return None


def run_client_demo():
    """运行客户端演示"""
    print("\n🎯 启动客户端演示...")
    
    client_file = "demo_mcp_client.py"
    if not os.path.exists(client_file):
        print(f"❌ 客户端文件不存在: {client_file}")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, client_file
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 运行客户端演示失败: {e}")
        return False


def main():
    """主函数"""
    print("🎬 FastMCP 图像分析器完整演示")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("image_element_analyzer_fastmcp_server.py"):
        print("❌ 请在项目根目录运行此脚本")
        return
    
    server_process = None
    
    try:
        # 1. 检查服务器是否已经运行
        if check_server_running():
            print("✅ 检测到服务器已在运行")
            user_input = input("是否使用现有服务器? (y/n) [默认: y]: ").strip().lower()
            if user_input in ['n', 'no']:
                print("⚠️ 请先停止现有服务器，然后重新运行此脚本")
                return
        else:
            # 2. 启动服务器
            server_process = start_server()
            if not server_process:
                print("❌ 无法启动服务器，演示终止")
                return
        
        # 3. 运行客户端演示
        success = run_client_demo()
        
        if success:
            print("\n🎉 演示完成!")
        else:
            print("\n❌ 演示过程中出现问题")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
    
    finally:
        # 清理：停止服务器进程
        if server_process:
            print("\n🛑 正在停止服务器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                server_process.kill()
                print("🔪 强制停止服务器")


if __name__ == "__main__":
    main() 