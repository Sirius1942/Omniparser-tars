# 图像分析服务使用说明

## 概述

本项目提供了一个基于 HTTP API 的图像分析服务，能够分析图像中的文本和图标元素，并返回分析结果和标注图像。

## 功能特性

- ✅ 图像文件分析（支持本地路径）
- ✅ Base64 图像分析（支持在线传输）
- ✅ 文本和图标元素检测
- ✅ 自动生成标注图像
- ✅ OCR 文本识别
- ✅ GPT-4o 图标描述
- ✅ GPU/CPU 自动适配

## 快速开始

### 1. 启动服务器

```bash
python standalone_image_analyzer.py
```

服务器将在 `http://localhost:8080` 启动

### 2. 运行客户端测试

```bash
python standalone_client.py
```

## API 接口说明

### 健康检查
```
GET /health
```

响应示例：
```json
{
  "status": "healthy",
  "analyzer_ready": true,
  "device_info": {
    "device": "cpu",
    "cuda_available": false
  },
  "timestamp": 1234567890.123
}
```

### 分析图像文件
```
POST /analyze_file
Content-Type: application/json
```

请求参数：
```json
{
  "image_path": "path/to/image.png",
  "box_threshold": 0.05,
  "save_annotated": true,
  "output_dir": "./results"
}
```

响应示例：
```json
{
  "success": true,
  "elements": [...],
  "element_count": {
    "text": 10,
    "icon": 5,
    "total": 15
  },
  "processing_time": {
    "ocr": 2.35,
    "caption": 8.42,
    "total": 10.77
  },
  "annotated_image_path": "./results/annotated_image.png",
  "timestamp": 1234567890.123
}
```

### 分析 Base64 图像
```
POST /analyze_base64
Content-Type: application/json
```

请求参数：
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "box_threshold": 0.05,
  "save_annotated": true,
  "output_dir": "./results"
}
```

### 获取标注图像
```
GET /annotated_image/<filename>
```

直接返回图像文件（PNG 格式）

### 列出分析结果
```
GET /results
```

响应示例：
```json
{
  "success": true,
  "files": [
    {
      "name": "annotated_screenshot.png",
      "size": 2219841,
      "modified": "Wed Jun 26 21:58:30 2024"
    }
  ],
  "count": 1,
  "directory": "/path/to/results"
}
```

## 客户端使用示例

### Python 客户端

```python
from standalone_client import ImageAnalyzerClient

# 创建客户端
client = ImageAnalyzerClient("http://localhost:8080")

# 健康检查
health = client.health_check()
print(f"服务器状态: {health['status']}")

# 分析图像
result = client.analyze_image_file(
    "path/to/image.png",
    box_threshold=0.05,
    save_annotated=True,
    output_dir="./results"
)

if result["success"]:
    print(f"分析成功，检测到 {result['element_count']['total']} 个元素")
    print(f"标注图像: {result['annotated_image_path']}")
else:
    print(f"分析失败: {result['error']}")
```

### curl 命令示例

```bash
# 健康检查
curl http://localhost:8080/health

# 分析图像文件
curl -X POST http://localhost:8080/analyze_file \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "screenshots/screenshot.png",
    "box_threshold": 0.05,
    "save_annotated": true,
    "output_dir": "./results"
  }' \
  --max-time 180

# 获取标注图像
curl http://localhost:8080/annotated_image/annotated_screenshot.png \
  --output downloaded_annotated.png

# 列出分析结果
curl http://localhost:8080/results
```

## 配置参数说明

### box_threshold
- **说明**: 检测框置信度阈值
- **范围**: 0.01 - 1.0
- **默认值**: 0.05
- **建议值**:
  - 复杂图像（UI 界面）: 0.03-0.05
  - 简单图像（文档）: 0.05-0.1

### save_annotated
- **说明**: 是否保存标注后的图像
- **类型**: boolean
- **默认值**: true

### output_dir
- **说明**: 输出目录路径
- **类型**: string
- **默认值**: "./results"

## 性能优化建议

### GPU 加速
- 安装 CUDA 版本的 PyTorch 可大幅提升处理速度（3-5倍）
- GPU 内存建议 4GB 以上

### 图像尺寸
- 推荐分辨率: 800-3200px
- 过大图像会影响处理速度
- 过小图像可能影响识别精度

### 处理时间参考（CPU 模式）
- 1080p 图像: 约 10-30 秒
- 4K 图像: 约 30-60 秒
- 首次运行会较慢（模型加载）

## 错误处理

### 常见错误及解决方案

1. **端口占用**
   - 错误: `Address already in use`
   - 解决: 修改服务器端口或关闭占用程序

2. **模型文件不存在**
   - 错误: `模型文件不存在: weights/icon_detect/model.pt`
   - 解决: 确保模型文件路径正确

3. **配置文件缺失**
   - 错误: `配置文件不存在: config.json`
   - 解决: 创建或检查配置文件

4. **图像文件不存在**
   - 错误: `图像文件不存在: path/to/image.png`
   - 解决: 检查图像文件路径和权限

5. **请求超时**
   - 错误: `Read timed out`
   - 解决: 增加客户端超时时间或优化图像尺寸

## 文件结构

```
.
├── standalone_image_analyzer.py  # HTTP 服务端
├── standalone_client.py          # Python 客户端
├── util/
│   └── image_element_analyzer.py # 核心分析器
├── weights/
│   └── icon_detect/
│       └── model.pt              # YOLO 模型文件
├── config.json                   # 配置文件
├── results/                      # 输出目录
│   └── annotated_*.png          # 标注图像
└── screenshots/                  # 测试图像
    └── screenshot_*.png
```

## 系统要求

### 必需依赖
- Python 3.8+
- Flask
- requests
- PIL (Pillow)
- torch
- pandas
- transformers
- ultralytics
- easyocr
- paddleocr

### 可选依赖
- CUDA (GPU 加速)
- ccache (编译优化)

## 性能监控

### 实时监控
- 查看服务器控制台输出
- 监控 GPU/CPU 使用率
- 检查内存占用情况

### 日志分析
- OCR 处理时间
- 图标识别耗时
- 总体处理性能

## 部署建议

### 生产环境
- 使用 nginx 或 Apache 作为反向代理
- 配置 SSL/TLS 加密
- 设置适当的超时时间
- 监控服务器资源使用

### 容器化部署
- 支持 Docker 容器化
- 建议使用 GPU 容器镜像
- 配置持久化存储

## 技术架构

```
┌─────────────────┐    HTTP     ┌─────────────────┐
│   Client App    │ ────────► │  Flask Server   │
└─────────────────┘            └─────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ Image Analyzer  │
                               └─────────────────┘
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                    ┌─────────┐  ┌─────────────┐  ┌─────────┐
                    │   OCR   │  │ YOLO Model  │  │ GPT-4o  │
                    │ Engine  │  │ Detection   │  │Caption  │
                    └─────────┘  └─────────────┘  └─────────┘
```

## 更新日志

### v1.0.0 (当前版本)
- ✅ 基础图像分析功能
- ✅ HTTP API 接口
- ✅ 文本和图标检测
- ✅ 标注图像生成
- ✅ GPU/CPU 自适应

### 计划功能
- 🔲 批量图像处理
- 🔲 WebSocket 实时通信
- 🔲 图像预处理优化
- 🔲 结果缓存机制
- 🔲 API 认证授权 