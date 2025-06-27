# 项目结构说明

本文档详细说明了 Omniparser TARS 项目的目录结构和文件组织方式。

## 📁 总体结构

```
Omniparser-tars/
├── src/                    # 核心源代码
├── examples/               # 示例代码
├── docs/                   # 文档
├── results/                # 分析结果
├── weights/                # 模型权重
├── imgs/                   # 示例图片
├── screenshots/            # 截图示例
├── eval/                   # 评估相关文件
├── requirements.txt        # Python依赖
├── config.example.json     # 配置文件模板
└── README.md              # 项目说明
```

## 🔧 src/ - 核心源代码

### src/core/ - 核心功能模块
- `gradio/` - Gradio Web界面相关代码
- `omnibox/` - 虚拟环境和容器相关
- `omniparserserver/` - 核心解析服务器

### src/server/ - 服务端实现
- `mcp_image_analyzer_server.py` - MCP协议服务器
- `start_mcp_server.py` - MCP服务启动脚本

### src/client/ - 客户端实现
目前为空，客户端代码在examples中

### src/utils/ - 工具类和配置
- `image_element_analyzer.py` - 图像元素分析器
- `omniparser.py` - 核心解析器
- `box_annotator.py` - 边框标注工具
- `config.py` - 配置管理
- `utils.py` - 通用工具函数
- `fix_config.py` - 配置修复工具
- `debug_image_analyzer.py` - 调试分析器

## 🧪 examples/ - 示例代码

### examples/basic/ - 基础示例
- `*demo*.py` - 各种基础演示脚本
- `test_*.py` - 测试脚本
- `apply_results.py` - 结果应用示例
- `coordinate_converter.py` - 坐标转换工具
- `detect_images.py` - 图像检测示例
- `image_analyzer_example.py` - 图像分析示例

### examples/mcp/ - MCP协议示例
- `mcp_client_example.py` - MCP客户端示例
- `*mcp*test*.py` - MCP测试脚本
- `working_mcp_client.py` - 工作中的MCP客户端

### examples/fastmcp/ - FastMCP服务示例
- `fastmcp_client_example.py` - FastMCP客户端示例
- `start_fastmcp_server.py` - FastMCP服务启动脚本
- `image_element_analyzer_fastmcp_server.py` - FastMCP服务器实现

### examples/http/ - HTTP API示例
- `standalone_client.py` - 独立HTTP客户端
- `standalone_image_analyzer.py` - 独立HTTP服务器

### examples/gradio/ - Gradio界面示例
目前为空，Gradio相关代码在src/core/gradio中

## 📚 docs/ - 文档

### docs/api/ - API文档
- `FastMCP_服务使用说明.md` - FastMCP服务API说明
- `MCP_服务使用说明.md` - MCP服务API说明
- `MCP_工具方法API说明.md` - MCP工具方法API说明
- `图像元素分析器API说明.md` - 图像分析器API说明
- `README_图像分析服务说明.md` - 图像分析服务说明
- `README_测试说明.md` - 测试说明

### docs/usage/ - 使用指南
- `README_CLIENT_DEMO.md` - 客户端演示说明
- `README_CN.md` - 中文使用说明
- `CLIENT_DEMO_SUMMARY.md` - 客户端演示总结
- `使用指南.md` - 详细使用指南

### docs/training/ - 模型训练文档
- `Evaluation.md` - 评估方法
- `ModelTraining.md` - 模型训练指南（英文）
- `ModelTraining_CN.md` - 模型训练指南（中文）
- `OutputFormat.md` - 输出格式说明
- `README.md` - 训练文档说明

## 📊 results/ - 分析结果

存储图像分析的结果文件：
- `*.png` - 标注后的图像文件
- `*.csv` - 分析结果数据
- `*.json` - JSON格式的分析结果

## 🏋️ weights/ - 模型权重

存储AI模型的权重文件：
- `icon_detect/` - 图标检测模型权重

## 🖼️ imgs/ - 示例图片

包含各种示例图片用于测试和演示：
- `demo_image.jpg` - 演示图片
- `*.png` - 各种格式的测试图片

## 📸 screenshots/ - 截图示例

存储屏幕截图示例文件，用于测试屏幕解析功能。

## 📋 eval/ - 评估相关

存储模型评估相关的脚本和结果：
- `*.py` - 评估脚本
- `*.json` - 评估结果

## 🔧 配置文件

- `requirements.txt` - Python依赖包列表
- `config.example.json` - 配置文件模板
- `config.json` - 实际配置文件（需要用户创建）

## 📝 文件命名规范

### Python文件
- `*_demo.py` - 演示脚本
- `*_example.py` - 示例代码
- `*_test.py` - 测试脚本
- `*_client.py` - 客户端代码
- `*_server.py` - 服务端代码

### 文档文件
- `README_*.md` - 说明文档
- `*_说明.md` - 中文说明文档
- `*API*.md` - API文档

### 结果文件
- `results_*.csv` - CSV格式结果
- `annotated_*.png` - 标注图像
- `output_*.png` - 输出图像

## 🚀 快速导航

- **开始使用**：查看 [README.md](../README.md)
- **API文档**：查看 [docs/api/](api/)
- **使用指南**：查看 [docs/usage/](usage/)
- **示例代码**：查看 [examples/](../examples/)
- **核心代码**：查看 [src/](../src/) 