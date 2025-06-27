# MCP工具方法API说明

## 概述

本文档说明了重构后的3个MCP工具方法，这些方法可以独立使用，供其他代码调用：

1. `test_mcp_connection()` - 测试MCP服务端连接
2. `get_mcp_tools_list()` - 获取MCP服务器工具列表
3. `execute_mcp_tool()` - 执行MCP工具命令

## 导入方式

```python
from util.adb_mcp_driver import test_mcp_connection, get_mcp_tools_list, execute_mcp_tool
```

## API详细说明

### 1. test_mcp_connection()

测试MCP服务端连接状态。

**函数签名：**
```python
async def test_mcp_connection(server_url: str = None, verbose: bool = True) -> bool
```

**参数说明：**
- `server_url` (str, 可选): MCP服务器URL，如果不提供则从配置文件读取
- `verbose` (bool, 默认True): 是否打印详细信息

**返回值：**
- `bool`: 连接是否成功

**使用示例：**
```python
# 使用默认配置测试连接
is_connected = await test_mcp_connection()

# 测试指定服务器连接（静默模式）
is_connected = await test_mcp_connection("http://localhost:8568/sse", verbose=False)
```

### 2. get_mcp_tools_list()

获取MCP服务器的可用工具列表。

**函数签名：**
```python
async def get_mcp_tools_list(server_url: str = None, verbose: bool = True) -> list
```

**参数说明：**
- `server_url` (str, 可选): MCP服务器URL，如果不提供则从配置文件读取
- `verbose` (bool, 默认True): 是否打印详细信息

**返回值：**
- `list`: 工具名称列表，如果失败返回空列表

**使用示例：**
```python
# 获取工具列表
tools = await get_mcp_tools_list()
print(f"可用工具: {tools}")

# 静默获取工具列表
tools = await get_mcp_tools_list(verbose=False)
```

### 3. execute_mcp_tool()

执行指定的MCP工具命令。

**函数签名：**
```python
async def execute_mcp_tool(tool_name: str, tool_args: dict = None, server_url: str = None, 
                          save_screenshots: bool = True, verbose: bool = True) -> dict
```

**参数说明：**
- `tool_name` (str, 必需): 工具名称
- `tool_args` (dict, 可选): 工具参数，默认为空字典
- `server_url` (str, 可选): MCP服务器URL，如果不提供则从配置文件读取
- `save_screenshots` (bool, 默认True): 是否自动保存截图（仅对截图工具有效）
- `verbose` (bool, 默认True): 是否打印详细信息

**返回值：**
- `dict`: 执行结果字典，包含以下字段：
  - `success` (bool): 执行是否成功
  - `result` (str/dict): 执行结果内容
  - `error` (str, 可选): 错误信息（仅失败时）
  - `tool_name` (str): 工具名称
  - `saved_path` (str, 可选): 截图保存路径（仅截图工具成功时）

**使用示例：**
```python
# 执行唤醒屏幕命令
result = await execute_mcp_tool("wake_screen")
if result["success"]:
    print("唤醒屏幕成功")

# 执行截图命令
result = await execute_mcp_tool("take_screenshot", {"compress": True})
if result["success"]:
    print(f"截图保存到: {result.get('saved_path')}")

# 执行点击操作
result = await execute_mcp_tool("click_screen", {"x": 500, "y": 300})

# 输入文本
result = await execute_mcp_tool("input_text", {"text": "Hello World"})
```

## 完整使用示例

### 基本工作流程

```python
import asyncio
from util.adb_mcp_driver import test_mcp_connection, get_mcp_tools_list, execute_mcp_tool

async def main():
    # 1. 测试连接
    if not await test_mcp_connection():
        print("连接失败")
        return
    
    # 2. 获取工具列表
    tools = await get_mcp_tools_list()
    if not tools:
        print("未获取到工具")
        return
    
    # 3. 执行工具
    if "take_screenshot" in tools:
        result = await execute_mcp_tool("take_screenshot", {"compress": True})
        if result["success"]:
            print(f"截图成功: {result.get('saved_path')}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 批量操作示例

```python
async def batch_operations():
    # 批量执行多个命令
    commands = [
        {"tool": "wake_screen", "args": {}},
        {"tool": "take_screenshot", "args": {"compress": True}},
        {"tool": "click_screen", "args": {"x": 200, "y": 400}},
        {"tool": "input_text", "args": {"text": "Hello World"}},
        {"tool": "go_home", "args": {}}
    ]
    
    results = []
    for cmd in commands:
        result = await execute_mcp_tool(cmd["tool"], cmd["args"])
        results.append(result)
        print(f"{cmd['tool']}: {'✅' if result['success'] else '❌'}")
    
    success_count = sum(1 for r in results if r["success"])
    print(f"成功率: {success_count}/{len(commands)}")
```

### 错误处理示例

```python
async def error_handling_example():
    # 测试不存在的工具
    result = await execute_mcp_tool("non_existent_tool")
    if not result["success"]:
        print(f"预期的错误: {result['error']}")
    
    # 测试错误参数
    result = await execute_mcp_tool("click_screen", {"invalid_param": "value"})
    if not result["success"]:
        print(f"参数错误: {result['error']}")
```

## 注意事项

1. **异步调用**：所有方法都是异步的，需要使用`await`关键字调用
2. **配置文件**：如果不指定`server_url`，会从`config.json`读取MCP服务器配置
3. **截图处理**：`take_screenshot`工具会自动保存截图到本地，路径在返回结果中
4. **错误处理**：所有方法都包含完善的错误处理，不会抛出未捕获的异常
5. **静默模式**：设置`verbose=False`可以禁用输出信息
6. **连接复用**：每次调用都会创建新的连接，适合独立使用场景

## 配置要求

确保`config.json`文件中包含MCP服务器配置：

```json
{
  "client": {
    "mcp_server_url": "http://127.0.0.1:8568/sse",
    "screenshot_dir": "screenshots"
  }
}
```

## 常见工具列表

根据MCP服务器实现，常见的工具包括：

- `wake_screen` - 唤醒设备屏幕
- `take_screenshot` - 截图
- `click_screen` - 点击屏幕指定位置
- `input_text` - 输入文本
- `go_home` - 返回主屏幕
- `swipe_screen` - 滑动屏幕
- `press_key` - 按键操作

具体可用工具请通过`get_mcp_tools_list()`获取。 