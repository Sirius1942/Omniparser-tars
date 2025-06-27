# Examples - 示例代码

本目录包含了 Omniparser TARS 的各种使用示例和演示代码。

## 📁 目录结构

```
examples/
├── basic/         # 基础示例
├── mcp/          # MCP协议示例
├── fastmcp/      # FastMCP服务示例
├── http/         # HTTP API示例
└── gradio/       # Gradio界面示例
```

## 🚀 快速开始

### 基础示例 (basic/)
包含最基本的图像分析示例和各种演示脚本：

```bash
# 运行基础演示
python examples/basic/run_demo.py

# 图像分析示例
python examples/basic/image_analyzer_example.py

# GPT-4测试
python examples/basic/test_gpt4o_simple.py
```

### MCP协议示例 (mcp/)
展示如何使用MCP（Model Context Protocol）协议：

```bash
# 启动MCP服务器
python src/server/start_mcp_server.py

# 运行MCP客户端示例
python examples/mcp/mcp_client_example.py

# 测试MCP服务
python examples/mcp/test_mcp_service.py
```

### FastMCP服务示例 (fastmcp/)
展示FastMCP服务的使用方法：

```bash
# 启动FastMCP服务器
python examples/fastmcp/start_fastmcp_server.py

# 运行FastMCP客户端
python examples/fastmcp/fastmcp_client_example.py
```

### HTTP API示例 (http/)
展示HTTP API的使用方法：

```bash
# 启动HTTP服务器
python examples/http/standalone_image_analyzer.py

# 运行HTTP客户端
python examples/http/standalone_client.py
```

## 📋 示例列表

### 基础示例
- `run_demo.py` - 主要演示脚本
- `image_analyzer_example.py` - 图像分析器使用示例
- `test_gpt4o_simple.py` - GPT-4简单测试
- `test_gpt4o_real_selection.py` - GPT-4真实选择测试
- `apply_results.py` - 结果应用示例
- `coordinate_converter.py` - 坐标转换工具
- `detect_images.py` - 图像检测示例

### MCP示例
- `mcp_client_example.py` - MCP客户端基础示例
- `working_mcp_client.py` - 完整的MCP客户端实现
- `test_mcp_service.py` - MCP服务测试

### FastMCP示例
- `start_fastmcp_server.py` - FastMCP服务器启动脚本
- `fastmcp_client_example.py` - FastMCP客户端示例
- `image_element_analyzer_fastmcp_server.py` - FastMCP服务器实现

### HTTP示例
- `standalone_image_analyzer.py` - 独立的HTTP图像分析服务
- `standalone_client.py` - HTTP客户端示例

## 🔧 配置要求

运行示例前，请确保：

1. 已安装所有依赖：
```bash
pip install -r requirements.txt
```

2. 已配置API密钥：
```bash
cp config.example.json config.json
# 编辑config.json，填入你的OpenAI API密钥
```

3. 已下载模型权重（如果使用本地模型）

## 📖 使用说明

1. **选择示例**：根据你的需求选择合适的示例目录
2. **阅读代码**：每个示例都包含详细的注释
3. **运行测试**：按照说明运行示例代码
4. **修改配置**：根据需要调整配置参数

## 🐛 故障排除

### 常见问题

1. **模块导入错误**：确保在项目根目录运行脚本
2. **API密钥错误**：检查config.json中的API密钥配置
3. **网络连接问题**：确保网络连接正常，可以访问OpenAI API

### 获取帮助

如果遇到问题，请：
1. 查看相关的文档：[docs/](../docs/)
2. 检查配置文件是否正确
3. 查看日志输出获取错误信息
4. 在GitHub Issues中提问

## 🔗 相关链接

- [项目主页](../README.md)
- [API文档](../docs/api/)
- [使用指南](../docs/usage/)
- [项目结构说明](../docs/PROJECT_STRUCTURE.md) 