# 图像元素分析器 FastMCP 服务使用说明

## 📋 概述

图像元素分析器 FastMCP 服务基于 FastMCP 框架实现，提供强大的图像分析能力。与传统的 FastAPI 实现不同，FastMCP 是专门为 MCP (Model Context Protocol) 协议设计的框架，提供更原生的 MCP 支持和更好的集成体验。

## 🎯 主要功能

- 🖼️ **图像元素检测**: 检测图像中的文本和图标元素
- 🎯 **GPT-4o 描述**: 使用 GPT-4o 为图标生成详细描述
- 🖥️ **自动设备选择**: 自动选择 GPU 或 CPU 运行
- 📤 **多种输入方式**: 支持文件路径和 Base64 编码
- 🔄 **批量处理**: 支持批量分析多个图像
- 📊 **设备监控**: 实时监控GPU/CPU状态
- 📚 **资源访问**: 提供结果历史和设备状态资源
- 💡 **智能提示**: 内置调试和优化建议提示

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 FastMCP (必须)
pip install fastmcp

# 安装核心依赖
pip install torch pillow pandas transformers

# 安装图像分析依赖
pip install ultralytics easyocr paddleocr
```

### 2. 准备环境

```bash
# 检查环境（推荐）
python start_fastmcp_server.py --check-only

# 准备配置文件
cp config.example.json config.json
# 编辑 config.json，设置 OpenAI API 信息
```

### 3. 启动服务器

```bash
# 方式1: 使用启动脚本（推荐）
python start_fastmcp_server.py

# 方式2: 直接启动
python image_element_analyzer_fastmcp_server.py

# 方式3: HTTP 模式
python start_fastmcp_server.py --http --port 8000

# 方式4: 调试模式
python start_fastmcp_server.py --debug
```

## 🛠️ 服务器组件

### 📋 可用工具 (Tools)

#### 1. `analyze_image_file`
分析本地图像文件

**参数:**
- `image_path` (str): 图像文件路径
- `box_threshold` (float, 默认=0.05): 检测框置信度阈值
- `save_annotated` (bool, 默认=False): 是否保存标注图像
- `output_dir` (str, 默认="./results"): 输出目录

**示例:**
```python
await client.call_tool("analyze_image_file", {
    "image_path": "~/Desktop/screenshot.png",
    "box_threshold": 0.05,
    "save_annotated": True
})
```

#### 2. `analyze_image_base64`
分析 Base64 编码的图像

**参数:**
- `image_base64` (str): Base64 编码的图像数据
- `box_threshold` (float): 检测框置信度阈值
- `save_annotated` (bool): 是否保存标注图像
- `output_dir` (str): 输出目录

#### 3. `batch_analyze_images`
批量分析多个图像文件

**参数:**
- `image_paths` (List[str]): 图像文件路径列表
- `box_threshold` (float): 检测框置信度阈值
- `save_annotated` (bool): 是否保存标注图像
- `output_dir` (str): 输出目录

#### 4. `get_device_status`
获取当前设备状态信息

**返回:**
```json
{
  "success": true,
  "device_info": {
    "device": "cuda",
    "cuda_available": true,
    "gpu_name": "NVIDIA GeForce RTX 4090",
    "gpu_memory": {...}
  },
  "analyzer_status": {
    "initialized": true,
    "ready": true
  }
}
```

### 📚 可用资源 (Resources)

#### 1. `image://recent/{filename}`
获取最近分析的图像结果

**用法:**
```python
result = await client.read_resource("image://recent/demo_image")
```

#### 2. `device://status`
获取设备状态的文本描述

**用法:**
```python
status = await client.read_resource("device://status")
```

### 💡 可用提示 (Prompts)

#### 1. `debug_analysis_error`
生成调试图像分析错误的提示

**参数:**
- `error_message` (str): 错误信息
- `image_path` (str, 可选): 图像路径

#### 2. `optimize_analysis_settings`
生成优化分析设置的提示

**参数:**
- `image_type` (str): 图像类型 (screenshot, document, ui, mixed)
- `quality_priority` (str): 质量优先级 (speed, balanced, accuracy)

## 🖥️ 客户端使用

### FastMCP 客户端示例

```python
from fastmcp import Client
import asyncio

async def main():
    # 连接到 FastMCP 服务器
    async with Client("./image_element_analyzer_fastmcp_server.py") as client:
        # 分析图像
        result = await client.call_tool("analyze_image_file", {
            "image_path": "test.png",
            "save_annotated": True
        })
        print(result)
        
        # 获取设备状态
        status = await client.call_tool("get_device_status", {})
        print(status)
        
        # 访问资源
        device_info = await client.read_resource("device://status")
        print(device_info)

asyncio.run(main())
```

### 运行客户端演示

```bash
# 运行完整的客户端演示
python fastmcp_client_example.py
```

## ⚙️ 与 Claude Desktop 集成

### 1. 配置 Claude Desktop

编辑 Claude Desktop 配置文件:

**macOS/Linux:** `~/.config/claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "image-analyzer-fastmcp": {
      "command": "python",
      "args": [
        "/absolute/path/to/image_element_analyzer_fastmcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project"
      }
    }
  }
}
```

### 2. 重启 Claude Desktop

重启应用后，你会在工具栏看到 🔨 图标，表示 MCP 服务器已连接。

### 3. 使用示例

在 Claude 中直接说：
- "分析这个截图中的UI元素"
- "检测图片中的所有文本和图标"
- "获取当前GPU状态"

## 🔧 调试和监控

### 使用 FastMCP 调试器

```bash
# 启动调试模式
python start_fastmcp_server.py --debug

# 或者直接使用
python -m fastmcp dev image_element_analyzer_fastmcp_server.py
```

这会打开一个网页界面，你可以：
- 测试所有工具、资源和提示
- 查看参数和返回值
- 调试错误和异常

### 环境检查

```bash
# 检查环境和依赖
python start_fastmcp_server.py --check-only
```

### 日志监控

FastMCP 服务器会输出详细的执行日志，包括：
- 设备初始化状态
- 图像分析进度
- 错误和警告信息
- 性能统计

## 📊 性能优化

### GPU 优化

```python
# 检查 GPU 状态
await client.call_tool("get_device_status", {})

# 对于大图像，适当降低阈值
await client.call_tool("analyze_image_file", {
    "image_path": "large_image.png",
    "box_threshold": 0.1  # 提高阈值减少检测量
})
```

### 批量处理优化

```python
# 批量处理多个图像
await client.call_tool("batch_analyze_images", {
    "image_paths": ["img1.png", "img2.png", "img3.png"],
    "box_threshold": 0.05,
    "save_annotated": False  # 批量时建议关闭标注保存
})
```

## 🆚 FastMCP vs FastAPI 对比

| 特性 | FastMCP | FastAPI (原版本) |
|------|---------|------------------|
| **协议支持** | 原生 MCP 支持 | HTTP REST API |
| **连接方式** | stdio/HTTP | HTTP only |
| **客户端** | FastMCP Client | 自定义 HTTP 客户端 |
| **调试工具** | 内置调试器 | 需要外部工具 |
| **AI 集成** | 专为 AI 设计 | 通用 Web API |
| **传输模式** | stdio/HTTP/SSE | HTTP only |
| **协议复杂性** | 自动处理 | 手动实现 |
| **类型检查** | 自动生成 | 手动定义 |

## 🔍 故障排除

### 常见问题

1. **FastMCP 未安装**
   ```bash
   pip install fastmcp
   ```

2. **模型文件缺失**
   ```
   确保 weights/icon_detect/model.pt 存在
   ```

3. **配置文件问题**
   ```bash
   cp config.example.json config.json
   # 编辑配置文件设置 API 密钥
   ```

4. **GPU 内存不足**
   ```python
   # 降低检测阈值
   box_threshold = 0.1
   ```

5. **端口冲突 (HTTP 模式)**
   ```bash
   python start_fastmcp_server.py --http --port 8001
   ```

### 获取帮助

- 查看详细日志输出
- 使用调试模式测试
- 检查设备状态和资源
- 参考客户端示例代码

## 📚 扩展开发

### 添加新工具

```python
@mcp.tool()
def my_custom_tool(param: str) -> str:
    """自定义工具描述"""
    # 实现逻辑
    return "结果"
```

### 添加新资源

```python
@mcp.resource("custom://path/{param}")
def my_custom_resource(param: str) -> str:
    """自定义资源描述"""
    # 返回数据
    return "资源内容"
```

### 添加新提示

```python
@mcp.prompt()
def my_custom_prompt(context: str) -> List[Message]:
    """自定义提示描述"""
    return [Message(role="user", content=[TextContent(text=context)])]
```

FastMCP 提供了比传统 HTTP API 更强大、更专业的 MCP 服务器实现，特别适合AI应用集成！ 