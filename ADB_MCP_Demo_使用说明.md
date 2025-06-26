# ADB MCP Driver Demo 使用说明

本项目提供了两个ADB MCP驱动的调用示例，演示如何通过文本命令调用和编排MCP工具。

## 文件说明

### 1. `adb_mcp_demo.py` - 功能完整的交互式Demo
- ✅ 文本命令解析器
- ✅ 交互式命令行界面
- ✅ 自动化场景编排
- ✅ 命令历史记录
- ✅ 结果保存功能

### 2. `adb_mcp_simple_demo.py` - 简化的独立调用示例
- ✅ 直接函数调用演示
- ✅ 基础功能测试
- ✅ 简单易懂的代码结构

## 支持的MCP工具

根据测试结果，当前MCP服务器支持以下15个工具：

| 工具名称 | 功能说明 | 状态 |
|---------|---------|------|
| `take_screenshot` | 截图 | ✅ 正常 |
| `click_screen` | 点击屏幕 | ✅ 正常 |
| `input_text` | 输入文本 | ✅ 正常 |
| `swipe_screen` | 滑动屏幕 | ⚠️ 参数格式问题 |
| `wake_screen` | 唤醒屏幕 | ✅ 正常 |
| `lock_screen` | 锁定屏幕 | 未测试 |
| `go_back` | 返回 | ✅ 正常 |
| `go_home` | 回到主屏幕 | ✅ 正常 |
| `show_recent_apps` | 显示最近应用 | 未测试 |
| `open_menu` | 打开菜单 | 未测试 |
| `get_screen_state` | 获取屏幕状态 | 未测试 |
| `get_device_info` | 获取设备信息 | 未测试 |
| `get_ui_elements` | 获取UI元素 | 未测试 |
| `execute_custom_command` | 执行自定义命令 | 未测试 |
| `get_connection_status` | 获取连接状态 | 未测试 |

## 使用方法

### 方法1：运行完整Demo

```bash
python adb_mcp_demo.py
```

运行后会看到菜单：
```
请选择运行模式:
1. 交互模式 - 手动输入命令
2. 自动化演示 - 运行预定义场景
3. 快速测试 - 基础功能测试
4. 退出
```

#### 交互模式命令示例：
```bash
>>> connect              # 测试连接
>>> tools                # 获取工具列表
>>> screenshot c         # 压缩截图
>>> click 100 200        # 点击坐标(100, 200)
>>> input hello world    # 输入文本
>>> home                 # 回到主屏幕
>>> help                 # 显示帮助
>>> quit                 # 退出
```

### 方法2：运行简化Demo

```bash
python adb_mcp_simple_demo.py
```

这个脚本会自动运行所有基础功能的测试示例。

## 独立方法调用示例

### 1. 基础连接和工具列表

```python
import asyncio
from util.adb_mcp_driver import test_mcp_connection, get_mcp_tools_list

async def basic_example():
    # 测试连接
    if await test_mcp_connection():
        print("连接成功")
        
        # 获取工具列表
        tools = await get_mcp_tools_list()
        print(f"可用工具: {tools}")

asyncio.run(basic_example())
```

### 2. 执行单个工具

```python
import asyncio
from util.adb_mcp_driver import execute_mcp_tool

async def single_tool_example():
    # 截图
    result = await execute_mcp_tool("take_screenshot", {"compress": True})
    if result["success"]:
        print(f"截图保存路径: {result.get('saved_path')}")
    
    # 点击
    result = await execute_mcp_tool("click_screen", {"x": 100, "y": 200})
    if result["success"]:
        print("点击成功")

asyncio.run(single_tool_example())
```

### 3. 命令序列编排

```python
import asyncio
from util.adb_mcp_driver import execute_mcp_tool

async def command_sequence():
    commands = [
        ("wake_screen", {}),
        ("take_screenshot", {"compress": True}),
        ("click_screen", {"x": 500, "y": 1000}),
        ("input_text", {"text": "Hello World"}),
        ("go_home", {})
    ]
    
    for tool_name, args in commands:
        result = await execute_mcp_tool(tool_name, args)
        print(f"{tool_name}: {'成功' if result['success'] else '失败'}")
        await asyncio.sleep(1)  # 等待1秒

asyncio.run(command_sequence())
```

## 文本命令格式

| 命令格式 | 说明 | 示例 |
|---------|-----|------|
| `connect` | 测试连接 | `connect` |
| `tools` | 获取工具列表 | `tools` |
| `screenshot [c]` | 截图，c表示压缩 | `screenshot` 或 `screenshot c` |
| `click <x> <y>` | 点击坐标 | `click 100 200` |
| `input <text>` | 输入文本 | `input hello world` |
| `home` | 回到主屏幕 | `home` |
| `wake` | 唤醒屏幕 | `wake` |
| `back` | 返回按钮 | `back` |
| `help` | 显示帮助 | `help` |

## 配置要求

确保您的 `config.json` 文件包含MCP服务器配置：

```json
{
  "client": {
    "mcp_server_url": "http://localhost:8000",
    "screenshot_dir": "screenshots"
  }
}
```

## 注意事项

1. **滑动工具参数问题**: 当前 `swipe_screen` 工具的参数格式与预期不符，需要进一步调试
2. **工具名称**: 某些工具名称可能与预期不符（如 `press_back` 应该是 `go_back`）
3. **异步调用**: 所有MCP工具调用都是异步的，需要使用 `await`
4. **错误处理**: 建议在实际使用中加强错误处理和重试机制

## 扩展功能

### 1. 添加新的文本命令

在 `ADBMCPCommandParser` 类中添加新的命令映射：

```python
self.commands["新命令"] = self.新方法
```

### 2. 自定义命令序列

修改 `demo_automation_scenario()` 函数中的命令列表来创建自定义自动化场景。

### 3. 结果保存

执行结果会自动保存为JSON文件，包含：
- 执行的命令
- 执行结果
- 时间戳
- 成功/失败状态

这些demo为您展示了如何：
- 通过文本命令调用MCP工具
- 编排和自动化命令序列
- 处理执行结果和错误
- 保存和记录操作历史 