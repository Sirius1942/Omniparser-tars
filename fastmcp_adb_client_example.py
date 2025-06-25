#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastMCP ADB客户端使用示例
演示如何使用重构后的3个工具方法：
1. test_mcp_connection - 测试服务端连接
2. get_mcp_tools_list - 获取工具列表  
3. execute_mcp_tool - 执行工具命令
"""

import asyncio
from util.adb_mcp_driver import test_mcp_connection, get_mcp_tools_list, execute_mcp_tool
from util.config import get_config

async def example_basic_usage():
    """基本使用示例"""
    print("=" * 50)
    print("🚀 FastMCP ADB客户端基本使用示例")
    print("=" * 50)
    
    # 1. 测试连接
    print("\n1️⃣ 测试MCP服务器连接...")
    is_connected = await test_mcp_connection()
    
    if not is_connected:
        print("❌ 无法连接到MCP服务器，请检查服务器是否启动")
        return
    
    # 2. 获取工具列表
    print("\n2️⃣ 获取可用工具列表...")
    tools = await get_mcp_tools_list()
    
    if not tools:
        print("❌ 未获取到任何工具")
        return
    
    print(f"✅ 共发现 {len(tools)} 个可用工具")
    
    # 3. 执行单个工具命令
    print("\n3️⃣ 执行工具命令示例...")
    
    # 示例1: 唤醒屏幕
    if "wake_screen" in tools:
        result = await execute_mcp_tool("wake_screen")
        print(f"wake_screen 执行结果: {result['success']}")
    
    # 示例2: 截图
    if "take_screenshot" in tools:
        result = await execute_mcp_tool("take_screenshot", {"compress": True})
        if result['success']:
            print(f"截图成功，保存到: {result.get('saved_path', 'N/A')}")
        else:
            print(f"截图失败: {result.get('error', 'Unknown error')}")
    
    # 示例3: 点击屏幕
    if "click_screen" in tools:
        result = await execute_mcp_tool("click_screen", {"x": 500, "y": 300})
        print(f"点击屏幕 (500,300): {result['success']}")


async def example_batch_operations():
    """批量操作示例"""
    print("=" * 50)
    print("🔄 批量操作示例")
    print("=" * 50)
    
    # 先测试连接
    if not await test_mcp_connection(verbose=False):
        print("❌ 连接失败")
        return
    
    # 批量执行多个命令
    commands = [
        {"tool": "wake_screen", "args": {}},
        {"tool": "take_screenshot", "args": {"compress": True}},
        {"tool": "click_screen", "args": {"x": 200, "y": 400}},
        {"tool": "input_text", "args": {"text": "Hello World"}},
        {"tool": "go_home", "args": {}}
    ]
    
    results = []
    for i, cmd in enumerate(commands, 1):
        print(f"\n执行命令 {i}/{len(commands)}: {cmd['tool']}")
        result = await execute_mcp_tool(
            tool_name=cmd["tool"], 
            tool_args=cmd["args"],
            verbose=False
        )
        results.append(result)
        
        if result["success"]:
            print(f"✅ 成功")
        else:
            print(f"❌ 失败: {result.get('error', 'Unknown error')}")
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    print(f"\n📊 批量操作完成: {success_count}/{len(commands)} 成功")


async def example_silent_mode():
    """静默模式示例"""
    print("=" * 50)
    print("🤫 静默模式示例")
    print("=" * 50)
    
    # 静默测试连接
    is_connected = await test_mcp_connection(verbose=False)
    print(f"连接状态: {'✅ 已连接' if is_connected else '❌ 未连接'}")
    
    if not is_connected:
        return
    
    # 静默获取工具列表
    tools = await get_mcp_tools_list(verbose=False)
    print(f"工具数量: {len(tools)}")
    print(f"工具列表: {', '.join(tools)}")
    
    # 静默执行命令
    if "take_screenshot" in tools:
        result = await execute_mcp_tool(
            "take_screenshot", 
            {"compress": True}, 
            verbose=False
        )
        if result["success"]:
            print(f"✅ 静默截图成功: {result.get('saved_path', 'N/A')}")
        else:
            print(f"❌ 静默截图失败: {result.get('error', 'N/A')}")


async def example_error_handling():
    """错误处理示例"""
    print("=" * 50)
    print("⚠️ 错误处理示例")
    print("=" * 50)
    
    # 测试不存在的工具
    result = await execute_mcp_tool("non_existent_tool", {})
    print(f"调用不存在工具的结果: {result}")
    
    # 测试错误参数
    result = await execute_mcp_tool("click_screen", {"invalid_param": "value"})
    print(f"使用错误参数的结果: {result}")
    
    # 测试连接到错误的服务器
    is_connected = await test_mcp_connection("http://localhost:9999", verbose=False)
    print(f"连接错误服务器: {'✅ 成功' if is_connected else '❌ 失败'}")


async def main():
    """主函数"""
    print("🎯 FastMCP ADB客户端工具方法使用示例")
    
    try:
        # 基本使用示例
        await example_basic_usage()
        
        print("\n" + "="*50)
        await asyncio.sleep(2)
        
        # 批量操作示例
        await example_batch_operations()
        
        print("\n" + "="*50)
        await asyncio.sleep(2)
        
        # 静默模式示例
        await example_silent_mode()
        
        print("\n" + "="*50)
        await asyncio.sleep(2)
        
        # 错误处理示例
        await example_error_handling()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断操作")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
    
    print("\n🎉 示例演示完成！")


if __name__ == "__main__":
    asyncio.run(main())