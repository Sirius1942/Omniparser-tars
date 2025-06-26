#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB MCP Driver Demo 示例
演示如何通过文本命令调用和编排MCP工具
"""

import asyncio
import json
import sys
from typing import Dict, List, Any
from util.adb_mcp_driver import (
    test_mcp_connection,
    get_mcp_tools_list,
    execute_mcp_tool,
    load_client_config
)


class ADBMCPCommandParser:
    """ADB MCP 命令解析器"""
    
    def __init__(self):
        self.commands = {
            "connect": self.test_connection,
            "tools": self.list_tools,
            "wake": self.wake_screen,
            "screenshot": self.take_screenshot,
            "click": self.click_screen,
            "input": self.input_text,
            "home": self.go_home,
            "swipe": self.swipe_screen,
            "back": self.press_back,
            "help": self.show_help
        }
    
    def parse_command(self, command_line: str) -> Dict[str, Any]:
        """
        解析命令行文本
        
        例如：
        - "click 100 200" -> {"action": "click", "args": {"x": 100, "y": 200}}
        - "input hello world" -> {"action": "input", "args": {"text": "hello world"}}
        """
        parts = command_line.strip().split()
        if not parts:
            return {"action": "help", "args": {}}
        
        action = parts[0].lower()
        args = parts[1:]
        
        if action not in self.commands:
            return {"action": "help", "args": {}}
        
        # 根据不同命令解析参数
        parsed_args = {}
        
        if action == "click" and len(args) >= 2:
            try:
                parsed_args = {"x": int(args[0]), "y": int(args[1])}
            except ValueError:
                print("❌ 点击坐标必须是数字")
                return {"action": "help", "args": {}}
        
        elif action == "input" and args:
            parsed_args = {"text": " ".join(args)}
        
        elif action == "screenshot":
            # 支持压缩参数
            parsed_args = {"compress": "compress" in args or "c" in args}
        
        elif action == "swipe" and len(args) >= 4:
            try:
                parsed_args = {
                    "start_x": int(args[0]),
                    "start_y": int(args[1]),
                    "end_x": int(args[2]),
                    "end_y": int(args[3]),
                    "duration": int(args[4]) if len(args) > 4 else 500
                }
            except ValueError:
                print("❌ 滑动坐标必须是数字")
                return {"action": "help", "args": {}}
        
        return {"action": action, "args": parsed_args}
    
    async def execute_command(self, command_line: str) -> Dict[str, Any]:
        """执行解析后的命令"""
        parsed = self.parse_command(command_line)
        action = parsed["action"]
        args = parsed["args"]
        
        if action in self.commands:
            return await self.commands[action](args)
        else:
            return {"success": False, "error": f"未知命令: {action}"}
    
    async def test_connection(self, args: Dict) -> Dict[str, Any]:
        """测试连接"""
        print("🚀 测试MCP连接...")
        success = await test_mcp_connection()
        return {"success": success, "message": "连接测试完成"}
    
    async def list_tools(self, args: Dict) -> Dict[str, Any]:
        """获取工具列表"""
        print("📦 获取工具列表...")
        tools = await get_mcp_tools_list()
        return {"success": len(tools) > 0, "tools": tools}
    
    async def wake_screen(self, args: Dict) -> Dict[str, Any]:
        """唤醒屏幕"""
        return await execute_mcp_tool("wake_screen", args)
    
    async def take_screenshot(self, args: Dict) -> Dict[str, Any]:
        """截图"""
        return await execute_mcp_tool("take_screenshot", args)
    
    async def click_screen(self, args: Dict) -> Dict[str, Any]:
        """点击屏幕"""
        if "x" not in args or "y" not in args:
            return {"success": False, "error": "缺少坐标参数"}
        return await execute_mcp_tool("click_screen", args)
    
    async def input_text(self, args: Dict) -> Dict[str, Any]:
        """输入文本"""
        if "text" not in args:
            return {"success": False, "error": "缺少文本参数"}
        return await execute_mcp_tool("input_text", args)
    
    async def go_home(self, args: Dict) -> Dict[str, Any]:
        """回到主屏幕"""
        return await execute_mcp_tool("go_home", args)
    
    async def swipe_screen(self, args: Dict) -> Dict[str, Any]:
        """滑动屏幕"""
        required_keys = ["start_x", "start_y", "end_x", "end_y"]
        if not all(key in args for key in required_keys):
            return {"success": False, "error": "缺少滑动坐标参数"}
        return await execute_mcp_tool("swipe_screen", args)
    
    async def press_back(self, args: Dict) -> Dict[str, Any]:
        """按返回键"""
        return await execute_mcp_tool("press_back", args)
    
    async def show_help(self, args: Dict) -> Dict[str, Any]:
        """显示帮助信息"""
        help_text = """
📱 ADB MCP Demo 命令帮助:

基础命令:
  connect              - 测试MCP服务器连接
  tools                - 获取可用工具列表
  help                 - 显示此帮助信息

屏幕操作:
  wake                 - 唤醒屏幕
  screenshot [c]       - 截图 (c=压缩)
  click <x> <y>        - 点击屏幕坐标
  swipe <x1> <y1> <x2> <y2> [duration] - 滑动屏幕
  home                 - 回到主屏幕
  back                 - 按返回键

文本输入:
  input <text>         - 输入文本

示例:
  click 100 200        - 点击坐标(100, 200)
  input hello world    - 输入"hello world"
  screenshot c         - 压缩截图
  swipe 100 500 100 200 1000 - 从(100,500)滑动到(100,200)，持续1秒
        """
        print(help_text)
        return {"success": True, "message": "帮助信息已显示"}


class ADBMCPOrchestrator:
    """ADB MCP 命令编排器"""
    
    def __init__(self):
        self.parser = ADBMCPCommandParser()
        self.command_history = []
    
    async def run_command_sequence(self, commands: List[str], delay: float = 1.0) -> List[Dict]:
        """
        运行命令序列
        
        Args:
            commands: 命令列表
            delay: 命令间延迟（秒）
        
        Returns:
            执行结果列表
        """
        results = []
        
        print(f"🎯 开始执行 {len(commands)} 个命令序列...")
        
        for i, command in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] 执行命令: {command}")
            
            result = await self.parser.execute_command(command)
            results.append({
                "command": command,
                "result": result,
                "index": i
            })
            
            # 记录历史
            self.command_history.append({
                "command": command,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # 检查执行结果
            if not result.get("success", False):
                print(f"⚠️ 命令执行失败: {result.get('error', '未知错误')}")
            
            # 延迟
            if i < len(commands):
                print(f"⏱️ 等待 {delay} 秒...")
                await asyncio.sleep(delay)
        
        print(f"\n✅ 命令序列执行完成！")
        return results
    
    def save_results(self, results: List[Dict], filename: str = None):
        """保存执行结果"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"adb_mcp_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"📄 执行结果已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")


async def interactive_mode():
    """交互模式"""
    parser = ADBMCPCommandParser()
    print("🎮 进入交互模式，输入 'help' 查看帮助，输入 'quit' 退出")
    
    while True:
        try:
            command = input("\n>>> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not command:
                continue
            
            result = await parser.execute_command(command)
            
            if not result.get("success", False):
                print(f"❌ 执行失败: {result.get('error', '未知错误')}")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


async def demo_automation_scenario():
    """演示自动化场景"""
    orchestrator = ADBMCPOrchestrator()
    
    # 定义自动化命令序列
    automation_commands = [
        "connect",                    # 测试连接
        "tools",                      # 获取工具列表
        "wake",                       # 唤醒屏幕
        "screenshot c",               # 压缩截图
        "home",                       # 回到主屏幕
        "click 500 1000",             # 点击屏幕中央
        "input 自动化测试文本",          # 输入文本
        "swipe 500 1200 500 800 1000", # 向上滑动
        "back",                       # 返回
        "screenshot"                  # 最终截图
    ]
    
    # 执行命令序列
    results = await orchestrator.run_command_sequence(
        commands=automation_commands,
        delay=1.5  # 命令间隔1.5秒
    )
    
    # 保存结果
    orchestrator.save_results(results)
    
    # 统计信息
    successful_commands = sum(1 for r in results if r["result"].get("success", False))
    print(f"\n📊 执行统计:")
    print(f"   总命令数: {len(results)}")
    print(f"   成功执行: {successful_commands}")
    print(f"   失败执行: {len(results) - successful_commands}")
    
    return results


async def main():
    """主函数 - 命令编排演示"""
    print("=" * 60)
    print("🤖 ADB MCP Driver Demo")
    print("=" * 60)
    
    # 加载配置
    config = load_client_config()
    print(f"📁 截图保存目录: {config.get('client', {}).get('screenshot_dir', 'screenshots')}")
    
    print("\n请选择运行模式:")
    print("1. 交互模式 - 手动输入命令")
    print("2. 自动化演示 - 运行预定义场景")
    print("3. 快速测试 - 基础功能测试")
    print("4. 退出")
    
    try:
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "1":
            await interactive_mode()
        
        elif choice == "2":
            print("\n🎬 开始自动化演示...")
            await demo_automation_scenario()
        
        elif choice == "3":
            print("\n⚡ 快速测试...")
            orchestrator = ADBMCPOrchestrator()
            test_commands = ["connect", "tools", "screenshot c"]
            await orchestrator.run_command_sequence(test_commands, delay=0.5)
        
        elif choice == "4":
            print("👋 再见！")
        
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 