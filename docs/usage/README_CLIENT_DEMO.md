# FastMCP 图像分析器客户端演示

本目录包含了 FastMCP 图像分析器的客户端演示代码，展示如何连接和调用服务器的各种功能。

## 文件说明

- `working_mcp_client.py` - 工作的 MCP 客户端演示（推荐）
- `demo_mcp_client.py` - 基础 MCP 客户端示例
- `simple_demo_client.py` - 简化的 HTTP 客户端示例
- `run_demo.py` - 自动启动脚本

## 运行演示

### 1. 确保服务器运行

首先确保 FastMCP 服务器正在运行：

```bash
# 检查服务器状态
lsof -i :8999

# 如果没有运行，启动服务器
python image_element_analyzer_fastmcp_server.py
```

### 2. 安装客户端依赖

```bash
# 安装 MCP 客户端库
pip install mcp httpx

# 如果要创建测试图片，还需要 PIL
pip install pillow
```

### 3. 运行客户端演示

```bash
# 运行工作的 MCP 客户端演示（推荐）
python working_mcp_client.py

# 或使用简化版本
python simple_demo_client.py
```

## 演示功能

客户端演示将展示以下功能：

1. **连接测试** - 验证与服务器的连接
2. **会话初始化** - 建立 MCP 会话
3. **工具列表** - 获取服务器提供的所有工具
4. **设备状态** - 查询服务器的设备信息（CPU/GPU）
5. **图像分析** - 分析图片文件或Base64编码的图像

## 可用工具

服务器提供以下工具：

- `analyze_image_file` - 分析本地图片文件
- `analyze_image_base64` - 分析Base64编码的图像
- `batch_analyze_images` - 批量分析多个图像
- `get_device_status` - 获取设备状态信息

## 自定义使用

您可以修改 `working_mcp_client.py` 中的代码来：

- 测试不同的图片文件
- 调整分析参数
- 添加新的工具调用
- 处理分析结果

## 故障排除

### 连接失败
- 确保服务器在端口 8999 上运行
- 检查防火墙设置
- 验证网络连接

### 缺少依赖
```bash
pip install mcp httpx pillow
```

### 服务器未响应
```bash
# 重启服务器
pkill -f fastmcp
python image_element_analyzer_fastmcp_server.py
```

## 示例输出

成功运行时，您将看到类似以下的输出：

```
🎯 启动 FastMCP 客户端演示...
==================================================
🚀 FastMCP 图像分析器客户端演示
==================================================
🔗 测试连接到: http://localhost:8999/sse
✅ 服务器响应状态: 404

🔗 正在建立 MCP 连接...
✅ MCP 会话建立成功!
✅ 会话初始化完成
   服务器信息: FastMCP Image Element Analyzer v1.0.0

📋 获取可用工具...
✅ 发现 4 个工具:
   • analyze_image_file: 分析本地图片文件中的UI元素
   • analyze_image_base64: 分析Base64编码图像中的UI元素
   • batch_analyze_images: 批量分析多个图像文件
   • get_device_status: 获取当前设备信息和状态
``` 