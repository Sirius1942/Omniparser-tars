# src/ - 核心源代码

本目录包含了 Omniparser TARS 的核心源代码和功能模块。

## 📁 目录结构

```
src/
├── core/          # 核心功能模块
├── server/        # 服务端实现
├── client/        # 客户端实现
└── utils/         # 工具类和配置
```

## 🔧 core/ - 核心功能模块

包含项目的核心功能组件：

### gradio/
- Gradio Web界面相关代码
- 包含智能代理和执行器
- 提供用户友好的Web界面

### omnibox/
- 虚拟环境和容器相关功能
- Windows VM管理脚本
- Docker容器配置

### omniparserserver/
- 核心解析服务器实现
- 提供图像解析的核心服务

## 🖥️ server/ - 服务端实现

服务端相关的实现代码：

- `mcp_image_analyzer_server.py` - MCP协议服务器实现
- `start_mcp_server.py` - MCP服务启动脚本

### 功能特性
- 支持MCP（Model Context Protocol）协议
- 提供图像分析服务
- 支持多种工具调用

## 💻 client/ - 客户端实现

客户端相关的实现代码（目前主要在examples中）：

- 计划包含各种客户端实现
- 支持不同协议的客户端
- 提供统一的客户端接口

## 🛠️ utils/ - 工具类和配置

核心工具类和配置管理：

### 主要模块
- `image_element_analyzer.py` - 图像元素分析器核心类
- `omniparser.py` - 核心解析器实现
- `box_annotator.py` - 边框标注工具
- `config.py` - 配置管理模块
- `utils.py` - 通用工具函数

### 辅助工具
- `fix_config.py` - 配置修复工具
- `debug_image_analyzer.py` - 调试分析器

## 📋 主要功能

### 图像分析
- OCR文字识别
- 目标检测（YOLO）
- GPT-4视觉分析
- 结果整合和标注

### 服务协议支持
- MCP协议
- FastMCP协议  
- HTTP API
- WebSocket连接

### 配置管理
- 灵活的配置系统
- 支持多种AI模型
- 设备选择（CPU/GPU）

## 🚀 使用方法

### 导入核心模块

```python
from src.utils.image_element_analyzer import ImageElementAnalyzer
from src.utils.config import load_config
from src.utils.omniparser import OmniParser

# 初始化分析器
analyzer = ImageElementAnalyzer()

# 分析图像
results = analyzer.analyze_image("path/to/image.png")
```

### 启动服务器

```python
# 启动MCP服务器
python src/server/start_mcp_server.py

# 或者使用配置文件
python src/server/mcp_image_analyzer_server.py --config config.json
```

## 🔧 配置说明

### 配置文件格式 (config.json)

```json
{
  "openai_api_key": "your-api-key",
  "device": "cuda",
  "model_path": "./weights/",
  "server": {
    "host": "localhost",
    "port": 8080
  },
  "analysis": {
    "enable_ocr": true,
    "enable_detection": true,
    "enable_caption": true
  }
}
```

### 环境变量

- `OPENAI_API_KEY` - OpenAI API密钥
- `DEVICE` - 计算设备 (cpu/cuda)
- `MODEL_PATH` - 模型权重路径

## 🧪 测试

运行核心功能测试：

```bash
# 测试图像分析器
python -m pytest tests/test_image_analyzer.py

# 测试配置管理
python -m pytest tests/test_config.py

# 测试服务器
python -m pytest tests/test_server.py
```

## 📚 API文档

详细的API文档请参考：
- [图像分析器API](../docs/api/图像元素分析器API说明.md)
- [MCP服务API](../docs/api/MCP_服务使用说明.md)
- [工具方法API](../docs/api/MCP_工具方法API说明.md)

## 🔗 相关链接

- [项目主页](../README.md)
- [示例代码](../examples/)
- [完整文档](../docs/)
- [项目结构说明](../docs/PROJECT_STRUCTURE.md) 