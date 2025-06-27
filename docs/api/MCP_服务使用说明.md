# 图像元素分析器 MCP 服务使用说明

## 📋 概述

图像元素分析器 MCP 服务基于 FastAPI 和 Server-Sent Events (SSE) 技术，提供强大的图像分析能力。服务支持自动 GPU/CPU 选择，并通过流式通信实时反馈分析进度。

## 🎯 主要功能

- 🖼️ **图像元素检测**: 检测图像中的文本和图标元素
- 🎯 **GPT-4o 描述**: 使用 GPT-4o 为图标生成详细描述
- 📡 **SSE 流式通信**: 实时获取分析进度和结果
- 🖥️ **自动设备选择**: 自动选择 GPU 或 CPU 运行
- 📤 **多种上传方式**: 支持文件上传和 Base64 编码
- 🔄 **异步处理**: 支持并发分析多个图像

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装额外的 MCP 服务依赖
pip install fastapi uvicorn aiohttp
```

### 2. 准备配置文件

```bash
# 复制配置示例文件
cp config.example.json config.json

# 编辑配置文件，设置 OpenAI API 信息
vim config.json
```

### 3. 启动服务器

```bash
# 方式1: 使用启动脚本（推荐）
python start_mcp_server.py

# 方式2: 直接启动 MCP 服务器
python image_element_analyzer_mcp_server.py

# 方式3: 自定义参数启动
python image_element_analyzer_mcp_server.py --port 8080 --model-path weights/icon_detect/model.pt
```

### 4. 验证服务状态

访问 http://localhost:8000 查看服务信息，或者访问 http://localhost:8000/docs 查看 API 文档。

## 🛠️ API 接口

### 📍 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务器信息和状态 |
| `/health` | GET | 健康检查 |
| `/analyze` | POST | 异步分析图像（JSON） |
| `/analyze/upload` | POST | 同步分析上传的图像文件 |
| `/analyze/stream/{task_id}` | GET | SSE 流式获取分析进度 |
| `/status/{task_id}` | GET | 获取特定任务状态 |
| `/status` | GET | 获取所有任务状态 |

### 📡 SSE 流式通信详解

SSE (Server-Sent Events) 允许客户端实时接收服务器推送的数据流：

```javascript
// JavaScript 客户端示例
const eventSource = new EventSource(`/analyze/stream/${taskId}`);

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(`进度: ${data.progress}% - ${data.message}`);
    
    if (data.status === 'completed') {
        console.log('分析完成！', data.result);
        eventSource.close();
    }
};
```

### 📝 请求示例

#### 1. 文件上传方式（同步）

```python
import requests

# 上传图像文件进行分析
with open('test_image.png', 'rb') as f:
    files = {'file': f}
    data = {
        'box_threshold': 0.05,
        'save_annotated': True,
        'output_dir': './results'
    }
    response = requests.post('http://localhost:8000/analyze/upload', 
                           files=files, data=data)
    result = response.json()
```

#### 2. Base64 编码方式（异步 + SSE）

```python
import base64
import requests
import json

# 编码图像为 Base64
with open('test_image.png', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# 提交分析任务
response = requests.post('http://localhost:8000/analyze', json={
    'image_base64': image_data,
    'box_threshold': 0.05,
    'save_annotated': False,
    'verbose': True
})

task_id = response.json()['task_id']
print(f"任务ID: {task_id}")

# 使用 SSE 监听进度（需要使用支持 SSE 的客户端）
```

## 🐍 Python 客户端使用

### 安装客户端依赖

```bash
pip install aiohttp
```

### 基本使用示例

```python
import asyncio
from mcp_client_example import ImageAnalyzerMCPClient

async def analyze_image():
    async with ImageAnalyzerMCPClient("http://localhost:8000") as client:
        # 检查服务器状态
        health = await client.check_health()
        print(f"服务器状态: {health['status']}")
        
        # 分析图像（带进度显示）
        result = await client.analyze_with_progress("test_image.png")
        
        if result.get('success'):
            print(f"检测到 {result['element_count']['total']} 个元素")
        else:
            print(f"分析失败: {result.get('error')}")

# 运行示例
asyncio.run(analyze_image())
```

### 批量分析示例

```python
async def batch_analyze():
    images = ["img1.png", "img2.png", "img3.png"]
    
    async with ImageAnalyzerMCPClient() as client:
        for image_path in images:
            result = await client.analyze_with_progress(
                image_path, 
                show_progress=False  # 批量处理时可关闭进度显示
            )
            print(f"{image_path}: {result['element_count']['total']} 个元素")

asyncio.run(batch_analyze())
```

## 🔧 高级配置

### 服务器配置选项

```python
# 自定义启动参数
await start_mcp_server(
    model_path="weights/icon_detect/model.pt",
    config_path="config.json",
    port=8000
)
```

### 分析参数说明

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `box_threshold` | float | 0.05 | 检测框置信度阈值 (0.01-1.0) |
| `save_annotated` | bool | false | 是否保存标注后的图像 |
| `output_dir` | string | "./results" | 输出目录路径 |
| `verbose` | bool | true | 是否显示详细日志信息 |

### GPU/CPU 自动选择

服务会自动检测并选择最佳的计算设备：

```python
# 在服务器初始化时自动检测
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 可以通过 /health 端点查看当前使用的设备
health_info = await client.check_health()
print(health_info['device'])
```

## 📊 响应格式

### 成功响应示例

```json
{
  "success": true,
  "elements": [
    {
      "type": "text",
      "content": "文档标题",
      "bbox": [0.1, 0.2, 0.3, 0.25]
    },
    {
      "type": "icon", 
      "content": "一个保存按钮图标，显示软盘符号",
      "bbox": [0.8, 0.1, 0.85, 0.15]
    }
  ],
  "text_elements": [...],
  "icon_elements": [...],
  "element_count": {
    "total": 15,
    "text": 8,
    "icon": 7
  },
  "processing_time": {
    "ocr": 1.2,
    "caption": 3.8,
    "total": 5.1
  },
  "image_info": {
    "size": [1920, 1080],
    "mode": "RGB"
  }
}
```

### SSE 流式响应示例

```
data: {"task_id": "task_1234567890", "status": "starting", "progress": 0, "message": "任务开始"}

data: {"task_id": "task_1234567890", "status": "processing", "progress": 10, "message": "解码图像数据"}

data: {"task_id": "task_1234567890", "status": "processing", "progress": 30, "message": "开始图像分析"}

data: {"task_id": "task_1234567890", "status": "completed", "progress": 100, "message": "分析完成", "result": {...}}
```

## 🔍 故障排除

### 常见问题

1. **模型文件不存在**
   ```bash
   # 下载模型权重
   huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/model.pt" --local-dir weights
   ```

2. **配置文件错误**
   ```bash
   # 检查 config.json 格式和 OpenAI API 配置
   python -c "import json; print(json.load(open('config.json')))"
   ```

3. **GPU 内存不足**
   - 尝试减小 `batch_size` 设置
   - 或强制使用 CPU 模式

4. **端口占用**
   ```bash
   # 使用不同端口启动
   python start_mcp_server.py --port 8080
   ```

### 调试模式

```bash
# 启用详细日志
export PYTHONPATH=.
python image_element_analyzer_mcp_server.py --verbose
```

## 🌐 部署建议

### 生产环境部署

```bash
# 使用 Gunicorn 部署
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker image_element_analyzer_mcp_server:app --bind 0.0.0.0:8000
```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_mcp_server.py"]
```

## 📚 扩展功能

### 自定义回调处理

```python
async def custom_progress_callback(status):
    """自定义进度回调函数"""
    if status.get('status') == 'processing':
        # 发送到其他系统或保存到数据库
        await save_progress_to_db(status)

# 使用自定义回调
result = await client.stream_analysis_progress(task_id, custom_progress_callback)
```

### 与其他服务集成

MCP 服务可以轻松与其他系统集成：

- **Web 应用**: 使用 JavaScript 的 EventSource API
- **移动应用**: 使用 HTTP 长连接或 WebSocket
- **微服务架构**: 作为独立的分析服务
- **工作流引擎**: 集成到自动化流程中

## 📞 技术支持

如果遇到问题，请检查：

1. 📋 服务器日志输出
2. 🔍 `/health` 端点状态
3. 📡 网络连接状况
4. 🖥️ 系统资源使用情况

---

**注意**: 此服务依赖 OpenAI GPT-4o API 进行图标描述，请确保已正确配置 API 密钥和网络访问权限。 