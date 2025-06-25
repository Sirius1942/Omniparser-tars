import asyncio
from fastmcp import Client
from fastmcp.exceptions import ClientError, McpError
import time
import base64
import os
from datetime import datetime
import json
from pathlib import Path
from util.config import get_config

def load_client_config():
    """
    加载客户端配置
    
    Returns:
        配置字典
    """
    config_file = "config.json"
    default_config = {
        "client": {
            "screenshot_dir": "screenshots"
        }
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f) or {}
                # 合并默认配置
                if 'client' not in config:
                    config['client'] = {}
                config['client'] = {**default_config['client'], **config.get('client', {})}
                return config
        except Exception as e:
            print(f"⚠️ 读取配置文件失败，使用默认配置: {e}")
    
    return default_config


def save_screenshot(image_base64: str, filename: str = None, config: dict = None) -> str:
    """
    保存截图到本地
    
    Args:
        image_base64: base64编码的图片数据
        filename: 保存的文件名，如果不提供则自动生成
        config: 客户端配置
    
    Returns:
        保存的文件路径
    """
    if config is None:
        config = load_client_config()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    # 从配置中获取截图目录
    screenshots_dir = config.get('client', {}).get('screenshot_dir', 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # 完整的文件路径
    file_path = os.path.join(screenshots_dir, filename)
    
    try:
        # 解码base64数据并保存
        image_data = base64.b64decode(image_base64)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        file_size = len(image_data) / 1024  # KB
        print(f"✅ 截图已保存到: {file_path}")
        print(f"📊 文件大小: {file_size:.1f} KB")
        return file_path
    except Exception as e:
        print(f"❌ 保存截图失败: {e}")
        return None


async def test_mcp_connection(server_url: str = None, verbose: bool = True) -> bool:
    """
    测试MCP服务端连接
    
    Args:
        server_url: MCP服务器URL，如果不提供则从配置文件读取
        verbose: 是否打印详细信息
    
    Returns:
        bool: 连接是否成功
    """
    if not server_url:
        config = get_config()
        server_url = config.config['client']['mcp_server_url']
    
    if verbose:
        print("🚀 测试MCP服务器连接...")
    
    client = Client(server_url)
    
    try:
        async with client:
            # 测试连接
            await client.ping()
            if verbose:
                print("✅ MCP服务器连接成功!")
            return True
            
    except McpError as e:
        if verbose:
            print(f"❌ MCP 协议错误: {e}")
        return False
    except Exception as e:
        if verbose:
            print(f"❌ 连接错误: {e}")
        return False


async def get_mcp_tools_list(server_url: str = None, verbose: bool = True) -> list:
    """
    获取MCP服务器的工具列表
    
    Args:
        server_url: MCP服务器URL，如果不提供则从配置文件读取
        verbose: 是否打印详细信息
    
    Returns:
        list: 工具列表，如果失败返回空列表
    """
    if not server_url:
        config = get_config()
        server_url = config.config['client']['mcp_server_url']
    
    if verbose:
        print("📦 获取工具列表...")
    
    client = Client(server_url)
    
    try:
        async with client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            if verbose:
                print(f"✅ 获取到 {len(tool_names)} 个工具: {tool_names}")
            
            return tool_names
            
    except McpError as e:
        if verbose:
            print(f"❌ MCP 协议错误: {e}")
        return []
    except Exception as e:
        if verbose:
            print(f"❌ 获取工具列表失败: {e}")
        return []


async def execute_mcp_tool(tool_name: str, tool_args: dict = None, server_url: str = None, 
                          save_screenshots: bool = True, verbose: bool = True) -> dict:
    """
    执行MCP工具命令
    
    Args:
        tool_name: 工具名称
        tool_args: 工具参数
        server_url: MCP服务器URL，如果不提供则从配置文件读取
        save_screenshots: 是否自动保存截图
        verbose: 是否打印详细信息
    
    Returns:
        dict: 执行结果，包含success, result, error等字段
    """
    if tool_args is None:
        tool_args = {}
        
    if not server_url:
        config = get_config()
        server_url = config.config['client']['mcp_server_url']
    else:
        config = get_config()
    
    if verbose:
        print(f"🔧 执行工具: {tool_name}")
    
    client = Client(server_url)
    
    try:
        async with client:
            result = await client.call_tool(tool_name, tool_args)
            
            # 特殊处理截图工具
            if tool_name == 'take_screenshot' and save_screenshots:
                try:
                    response_data = json.loads(result[0].text)
                    if response_data.get('success') and response_data.get('image_base64'):
                        # 保存截图到本地 - 需要传递字典格式的配置
                        config_dict = {"client": config.config['client']}
                        saved_path = save_screenshot(response_data['image_base64'], config=config_dict)
                        if verbose:
                            print(f"✅ {tool_name}: 截图数据已接收并保存到 {saved_path}")
                        return {
                            "success": True,
                            "result": response_data,
                            "saved_path": saved_path,
                            "tool_name": tool_name
                        }
                    else:
                        error_msg = response_data.get('message', '截图失败')
                        if verbose:
                            print(f"❌ {tool_name}: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "tool_name": tool_name
                        }
                except json.JSONDecodeError as e:
                    if verbose:
                        print(f"❌ {tool_name}: JSON解析失败 - {e}")
                    return {
                        "success": False,
                        "error": f"JSON解析失败: {e}",
                        "result": result[0].text,
                        "tool_name": tool_name
                    }
            else:
                # 普通工具处理
                result_text = result[0].text
                if verbose:
                    print(f"✅ {tool_name}: {result_text}")
                return {
                    "success": True,
                    "result": result_text,
                    "tool_name": tool_name
                }
            
    except (ClientError, McpError) as e:
        error_msg = f"工具调用错误: {e}"
        if verbose:
            print(f"❌ {tool_name}: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "tool_name": tool_name
        }
    except Exception as e:
        error_msg = f"执行异常: {e}"
        if verbose:
            print(f"❌ {tool_name}: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "tool_name": tool_name
        }


async def sse_client():
    """SSE 客户端示例（保持向后兼容）"""
    print("🚀 SSE 客户端测试...")
    
    # 加载客户端配置
    config = get_config()
    print(f"📁 截图保存目录: {config.config['client']['screenshot_dir']}")
    
    # 1. 测试连接
    connection_ok = await test_mcp_connection()
    if not connection_ok:
        return
    
    # 2. 获取工具列表
    tools = await get_mcp_tools_list()
    if not tools:
        return
    
    # 3. 执行工具命令
    tool_calls = [
        {"name": "wake_screen", "args": {}},
        {"name": "take_screenshot", "args": {"compress": True}},
        {"name": "click_screen", "args": {"x": 100, "y": 200}},
        {"name": "click_screen", "args": {"x": 400, "y": 500}},
        {"name": "input_text", "args": {"text": "测试文本"}},
        {"name": "go_home", "args": {}}
    ]
    
    for tool_call in tool_calls:
        result = await execute_mcp_tool(
            tool_name=tool_call["name"], 
            tool_args=tool_call["args"]
        )
        
        if not result["success"]:
            print(f"⚠️ 工具 {tool_call['name']} 执行失败")
        
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(sse_client())