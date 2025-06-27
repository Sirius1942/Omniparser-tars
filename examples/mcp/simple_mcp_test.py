#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的 MCP 图像分析测试
验证标准 MCP 协议的基本功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import asyncio
import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 创建服务端
server = Server("simple-image-analyzer")

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="test_tool",
            description="测试工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "测试消息"}
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """调用工具"""
    if name == "test_tool":
        message = arguments.get("message", "默认消息")
        result = {
            "success": True,
            "message": f"收到消息: {message}",
            "server": "simple-image-analyzer"
        }
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    else:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"未知工具: {name}"
            }, ensure_ascii=False, indent=2)
        )]

async def main():
    """启动服务器"""
    print("🎯 简单 MCP 测试服务器")
    print("启动中...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main()) 