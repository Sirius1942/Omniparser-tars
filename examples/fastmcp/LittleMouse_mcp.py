#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LittleMouse MCP Server - 通过SSE通信的最简单示例
🐭 LittleMouse - 小巧而强大的MCP服务
"""

from mcp.server.fastmcp import FastMCP

# 创建 LittleMouse 服务器
mcp = FastMCP("LittleMouse")

@mcp.tool()
def say_hello(name: str = "世界") -> str:
    """向指定的名字问好"""
    return f"🐭 LittleMouse 说：你好，{name}！"

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """计算两个数字的和"""
    return a + b

@mcp.tool()
def get_mouse_info() -> dict:
    """获取小鼠信息"""
    return {
        "name": "LittleMouse",
        "species": "数字小鼠",
        "superpower": "MCP通信",
        "mood": "开心",
        "version": "1.0.0"
    }

@mcp.resource("mouse://status")
def get_status() -> str:
    """获取小鼠状态"""
    return "🐭 LittleMouse 状态：运行正常，准备为您服务！"

@mcp.resource("mouse://config")
def get_config() -> str:
    """获取小鼠配置"""
    return """
🐭 LittleMouse 配置信息:
- 通信协议: MCP over SSE
- 支持工具: 3个
- 支持资源: 2个
- 运行模式: 开发模式
"""

@mcp.prompt()
def chat_with_mouse(message: str) -> str:
    """与小鼠聊天的提示模板"""
    return f"请以一只友好的数字小鼠的身份回应这条消息：{message}"

if __name__ == "__main__":
    print("🐭 启动 LittleMouse SSE 服务器...")
    print("📡 通过 SSE 提供服务")
    print("🔗 默认访问地址: http://localhost:3000/sse")
    print("=" * 50)
    
    # 使用 SSE 传输协议运行服务器 - 不传递host和port参数
    mcp.run(transport="sse")