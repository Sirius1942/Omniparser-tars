# Omniparser TARS - 智能图像解析工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Omniparser TARS 是一个强大的图像解析工具，集成了多种AI技术，包括OCR、目标检测和GPT-4视觉分析，为图像内容提供全面的智能解析能力。

## 🚀 主要特性

- **多模态AI解析**：结合OCR、YOLO目标检测和GPT-4视觉分析
- **多种服务模式**：支持MCP、FastMCP、HTTP API等多种服务方式
- **灵活的客户端**：提供命令行、HTTP、Gradio等多种客户端接口
- **丰富的示例**：包含完整的使用示例和演示代码
- **详细的文档**：提供API文档、使用指南和训练说明

## 📁 项目结构

```
├── src/                    # 核心源代码
│   ├── core/              # 核心功能模块
│   ├── server/            # 服务端实现
│   ├── client/            # 客户端实现
│   └── utils/             # 工具类和配置
├── examples/              # 示例代码
│   ├── basic/             # 基础示例
│   ├── mcp/               # MCP协议示例
│   ├── fastmcp/           # FastMCP服务示例
│   ├── http/              # HTTP API示例
│   └── gradio/            # Gradio界面示例
├── docs/                  # 文档
│   ├── api/               # API文档
│   ├── usage/             # 使用指南
│   └── training/          # 模型训练文档
├── results/               # 分析结果
├── weights/               # 模型权重
├── imgs/                  # 示例图片
└── screenshots/           # 截图示例
```

## 🛠️ 安装

### 环境要求

- Python 3.8+
- CUDA支持（可选，用于GPU加速）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. 复制配置文件模板：
```bash
cp config.example.json config.json
```

2. 编辑配置文件，填入你的API密钥：
```json
{
  "openai_api_key": "your-openai-api-key",
  "device": "cuda",  // 或 "cpu"
  "model_path": "./weights/"
}
```

## 🚀 快速开始

### 1. HTTP API 服务

启动HTTP服务：
```bash
python examples/http/standalone_image_analyzer.py
```

使用客户端：
```bash
python examples/http/standalone_client.py
```

### 2. MCP 服务

启动MCP服务：
```bash
python src/server/start_mcp_server.py
```

使用MCP客户端：
```bash
python examples/mcp/mcp_client_example.py
```

### 3. FastMCP 服务

启动FastMCP服务：
```bash
python examples/fastmcp/start_fastmcp_server.py
```

使用FastMCP客户端：
```bash
python examples/fastmcp/fastmcp_client_example.py
```

## 📖 使用示例

### 基础图像分析

```python
from src.utils.image_element_analyzer import ImageElementAnalyzer

# 初始化分析器
analyzer = ImageElementAnalyzer()

# 分析图像
results = analyzer.analyze_image("path/to/image.png")

# 获取分析结果
print(results)
```

### HTTP API 调用

```python
import requests

# 分析图像文件
with open("image.png", "rb") as f:
    response = requests.post(
        "http://localhost:8080/analyze_file",
        files={"file": f}
    )
    
results = response.json()
```

## 🔧 API 文档

### HTTP API 端点

- `GET /health` - 健康检查
- `POST /analyze_file` - 分析上传的图像文件
- `POST /analyze_base64` - 分析Base64编码的图像
- `GET /annotated_image/<filename>` - 获取标注后的图像
- `GET /results` - 获取分析结果列表

详细的API文档请参考：[docs/api/](docs/api/)

## 📚 文档

- [API文档](docs/api/) - 详细的API接口说明
- [使用指南](docs/usage/) - 完整的使用教程
- [模型训练](docs/training/) - 模型训练和评估指南

## 🧪 示例代码

在 `examples/` 目录下提供了丰富的示例：

- **基础示例** (`examples/basic/`) - 基本功能演示
- **MCP示例** (`examples/mcp/`) - MCP协议使用示例
- **FastMCP示例** (`examples/fastmcp/`) - FastMCP服务示例
- **HTTP示例** (`examples/http/`) - HTTP API使用示例

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 链接

- [GitHub仓库](https://github.com/Sirius1942/Omniparser-tars)
- [GitLab仓库](https://gitlab.casstime.net/a02267/tars-server)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

如果你觉得这个项目有用，请给我们一个⭐️！
