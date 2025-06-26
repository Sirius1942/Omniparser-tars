#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB MCP Driver 简单调用示例
演示独立方法调用
"""

import asyncio
from util.adb_mcp_driver import (
    test_mcp_connection,
    get_mcp_tools_list,
    execute_mcp_tool
)


async def simple_screenshot_example():
    """简单截图示例"""
    print("📸 简单截图示例")
    print("-" * 30)
    
    # 1. 测试连接
    print("1. 测试连接...")
    if not await test_mcp_connection():
        print("❌ 连接失败，退出")
        return
    
    # 2. 截图
    print("2. 执行截图...")
    result = await execute_mcp_tool("take_screenshot", {"compress": True})
    
    if result["success"]:
        print(f"✅ 截图成功: {result.get('saved_path', 'N/A')}")
    else:
        print(f"❌ 截图失败: {result.get('error', 'N/A')}")


async def simple_click_example():
    """简单点击示例"""
    print("\n🖱️ 简单点击示例")
    print("-" * 30)
    
    # 点击屏幕坐标
    x, y = 500, 1000
    print(f"点击坐标: ({x}, {y})")
    
    result = await execute_mcp_tool("click_screen", {"x": x, "y": y})
    
    if result["success"]:
        print("✅ 点击成功")
    else:
        print(f"❌ 点击失败: {result.get('error', 'N/A')}")


async def simple_input_example():
    """简单输入示例"""
    print("\n⌨️ 简单输入示例")
    print("-" * 30)
    
    text = "Hello MCP!"
    print(f"输入文本: {text}")
    
    result = await execute_mcp_tool("input_text", {"text": text})
    
    if result["success"]:
        print("✅ 文本输入成功")
    else:
        print(f"❌ 文本输入失败: {result.get('error', 'N/A')}")


async def simple_swipe_example():
    """简单滑动示例"""
    print("\n👆 简单滑动示例")
    print("-" * 30)
    
    # 从屏幕中下部向上滑动
    start_x, start_y = 500, 1200
    end_x, end_y = 500, 800
    duration = 1000  # 1秒
    
    print(f"滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y}), 持续 {duration}ms")
    
    result = await execute_mcp_tool("swipe_screen", {
        "start_x": start_x,
        "start_y": start_y,
        "end_x": end_x,
        "end_y": end_y,
        "duration": duration
    })
    
    if result["success"]:
        print("✅ 滑动成功")
    else:
        print(f"❌ 滑动失败: {result.get('error', 'N/A')}")


async def list_available_tools():
    """列出可用工具"""
    print("\n🔧 获取可用工具列表")
    print("-" * 30)
    
    tools = await get_mcp_tools_list()
    
    if tools:
        print(f"发现 {len(tools)} 个工具:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool}")
    else:
        print("❌ 无法获取工具列表")


async def run_single_command(tool_name: str, args: dict = None):
    """
    执行单个命令的通用函数
    
    Args:
        tool_name: 工具名称
        args: 工具参数
    """
    print(f"\n🚀 执行单个命令: {tool_name}")
    print(f"参数: {args}")
    print("-" * 40)
    
    result = await execute_mcp_tool(tool_name, args or {})
    
    if result["success"]:
        print(f"✅ {tool_name} 执行成功")
        if "saved_path" in result:
            print(f"📁 文件保存路径: {result['saved_path']}")
        return result
    else:
        print(f"❌ {tool_name} 执行失败: {result.get('error', 'N/A')}")
        return None


async def main():
    """主函数 - 演示独立方法调用"""
    print("=" * 50)
    print("🤖 ADB MCP Driver 简单调用示例")
    print("=" * 50)
    
    try:
        # 1. 列出工具
        await list_available_tools()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 2. 截图示例
        await simple_screenshot_example()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 3. 点击示例
        await simple_click_example()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 4. 输入示例
        await simple_input_example()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 5. 滑动示例
        await simple_swipe_example()
        
        print("\n" + "=" * 50)
        print("🎯 独立命令调用示例")
        print("=" * 50)
        
        # 独立调用示例
        await run_single_command("wake_screen")
        await asyncio.sleep(0.5)
        
        await run_single_command("go_home")
        await asyncio.sleep(0.5)
        
        await run_single_command("take_screenshot", {"compress": False})
        await asyncio.sleep(0.5)
        
        await run_single_command("press_back")
        
        print("\n✅ 所有示例执行完成！")
        
    except KeyboardInterrupt:
        print("\n👋 程序被中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 