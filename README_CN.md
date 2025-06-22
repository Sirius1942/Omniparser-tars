# OmniParser: 纯视觉GUI智能体的屏幕解析工具

<p align="center">
  <img src="imgs/logo.png" alt="Logo">
</p>

[![arXiv](https://img.shields.io/badge/Paper-green)](https://arxiv.org/abs/2408.00203)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

📢 [[项目主页](https://microsoft.github.io/OmniParser/)] [[V2博客文章](https://www.microsoft.com/en-us/research/articles/omniparser-v2-turning-any-llm-into-a-computer-use-agent/)] [[V2模型](https://huggingface.co/microsoft/OmniParser-v2.0)] [[V1.5模型](https://huggingface.co/microsoft/OmniParser)] [[HuggingFace在线演示](https://huggingface.co/spaces/microsoft/OmniParser-v2)]

**OmniParser** 是一种综合性的方法，用于将用户界面截图解析为结构化且易于理解的元素，显著增强了GPT-4V生成能够准确定位到界面相应区域的操作的能力。

## 最新消息
- [2025/3] 我们支持本地轨迹日志记录，您可以使用OmniParser+OmniTool为您最喜欢的领域智能体构建训练数据管道。[文档制作中]
- [2025/3] 我们正在逐步添加多智能体编排功能，并改进OmniTool的用户界面以提供更好的体验。
- [2025/2] 我们发布了OmniParser V2 [检查点](https://huggingface.co/microsoft/OmniParser-v2.0)。[观看视频](https://1drv.ms/v/c/650b027c18d5a573/EWXbVESKWo9Buu6OYCwg06wBeoM97C6EOTG6RjvWLEN1Qg?e=alnHGC)
- [2025/2] 我们推出了OmniTool：使用OmniParser+您选择的视觉模型控制Windows 11虚拟机。OmniTool开箱即用支持以下大型语言模型 - OpenAI (4o/o1/o3-mini)、DeepSeek (R1)、Qwen (2.5VL) 或 Anthropic Computer Use。[观看视频](https://1drv.ms/v/c/650b027c18d5a573/EehZ7RzY69ZHn-MeQHrnnR4BCj3by-cLLpUVlxMjF4O65Q?e=8LxMgX)
- [2025/1] V2即将到来。我们在新的定位基准测试[Screen Spot Pro](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/tree/main)上使用OmniParser v2取得了39.5%的最新最佳结果（即将发布）！阅读更多详情[这里](https://github.com/microsoft/OmniParser/tree/master/docs/Evaluation.md)。
- [2024/11] 我们发布了更新版本OmniParser V1.5，具有：1）更细粒度/小图标检测，2）预测每个屏幕元素是否可交互。示例见demo.ipynb。
- [2024/10] OmniParser在huggingface模型中心成为#1热门模型（从2024年10月29日开始）。
- [2024/10] 欢迎查看我们在[huggingface space](https://huggingface.co/spaces/microsoft/OmniParser)上的演示！（敬请期待OmniParser + Claude Computer Use）
- [2024/10] 交互区域检测模型和图标功能描述模型都已发布！[Hugginface模型](https://huggingface.co/microsoft/OmniParser)
- [2024/09] OmniParser在[Windows Agent Arena](https://microsoft.github.io/WindowsAgentArena/)上取得最佳性能！

## 安装
首先克隆仓库，然后安装环境：
```bash
cd OmniParser
conda create -n "omni" python==3.12
conda activate omni
pip install -r requirements.txt
```

确保您已在weights文件夹中下载了V2权重（确保字幕权重文件夹名为icon_caption_florence）。如果没有，请用以下命令下载：
```bash
# 将模型检查点下载到本地目录 OmniParser/weights/
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights; done
mv weights/icon_caption weights/icon_caption_florence
```

## 示例
我们在demo.ipynb中整理了一些简单的示例。

## Gradio演示
要运行gradio演示，只需运行：
```bash
python gradio_demo.py
```

## 批量图片检测脚本

项目提供了一个便捷的批量检测脚本 `detect_images.py`，可以一次性处理imgs文件夹中的所有图片。

### 使用方法

1. **确保模型权重已下载**：
```bash
# 下载V2模型权重
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights; done
mv weights/icon_caption weights/icon_caption_florence
```

2. **将待检测图片放入imgs文件夹**：
```bash
# imgs文件夹中已包含一些示例图片
ls imgs/
# demo_image.jpg  excel.png  google_page.png  windows_home.png  ...
```

3. **运行批量检测脚本**：
```bash
python detect_images.py
```

### 输出结果

脚本会在 `detection_results/` 文件夹中生成以下文件：

- `{图片名}_labeled.png` - 带有检测框和标注的可视化图片
- `{图片名}_detection.json` - 详细的检测数据（JSON格式）
- `{图片名}_elements.csv` - 检测到的元素列表（CSV格式）

### 示例输出

```
=== OmniParser 批量图片检测脚本 ===
正在初始化模型...
使用设备: cuda
模型初始化完成!
找到 15 张图片:
  - imgs/demo_image.jpg
  - imgs/excel.png
  - imgs/google_page.png
  ...

是否继续处理这些图片? (y/n): y

--- 处理第 1/15 张图片 ---
正在处理: imgs/demo_image.jpg
图片尺寸: (1501, 843)
OCR检测完成，耗时: 1.23秒
检测完成，总耗时: 4.56秒，检测到 25 个元素
结果已保存: detection_results/demo_image_labeled.png, detection_results/demo_image_detection.json, detection_results/demo_image_elements.csv

=== 检测完成 ===
成功处理: 15/15 张图片
总检测元素数: 340
平均检测时间: 3.82秒
结果保存在: detection_results/ 文件夹
```

### 支持的图片格式

脚本支持以下图片格式：
- `.jpg`, `.jpeg`
- `.png`
- `.bmp`
- `.tiff`
- `.webp`

### 自定义配置

可以通过修改脚本中的参数来调整检测行为：

```python
# 在detect_image函数中调整检测阈值
result = detect_image(image_path, som_model, caption_model_processor, box_threshold=0.05)

# 调整批量处理大小（在get_som_labeled_img调用中）
batch_size=128  # 根据GPU内存调整
```

## 快速使用指南

### 1. 基本使用
```python
from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
from PIL import Image
import torch

# 设置设备
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 加载模型
som_model = get_yolo_model('weights/icon_detect/model.pt')
som_model.to(device)

# 加载字幕模型
caption_model_processor = get_caption_model_processor(
    model_name="florence2", 
    model_name_or_path="weights/icon_caption_florence", 
    device=device
)

# 处理图像
image_path = 'your_image.png'
image = Image.open(image_path)

# 执行解析
dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
    image_path, 
    som_model, 
    BOX_TRESHOLD=0.05,
    caption_model_processor=caption_model_processor,
    use_local_semantics=True
)
```

### 2. 批量处理图片
```bash
# 使用提供的批量检测脚本处理imgs文件夹中的所有图片
python detect_images.py

# 脚本会自动：
# 1. 检测imgs/文件夹中的所有图片
# 2. 对每张图片进行UI元素检测和描述生成
# 3. 保存带标注的图片和检测结果到detection_results/文件夹
```

## 项目结构

```
OmniParser/
├── README.md                     # 英文说明文档
├── README_CN.md                  # 中文说明文档
├── demo.ipynb                    # 演示笔记本
├── gradio_demo.py               # Gradio演示应用
├── detect_images.py             # 批量图片检测脚本
├── requirements.txt             # 依赖包列表
├── util/                        # 核心工具模块
│   ├── omniparser.py            # 主要解析类
│   ├── utils.py                 # 工具函数
│   └── box_annotator.py         # 边界框标注工具
├── weights/                     # 模型权重文件
│   ├── icon_detect/             # 图标检测模型
│   └── icon_caption_florence/   # Florence图标描述模型
├── imgs/                        # 示例图片
├── docs/                        # 文档
│   ├── Evaluation.md            # 评估文档
│   └── ModelTraining_CN.md      # 模型训练文档(中文)
├── eval/                        # 评估脚本
├── omnitool/                    # OmniTool工具集
│   ├── gradio/                  # Gradio应用
│   ├── omnibox/                 # OmniBox容器
│   └── omniparserserver/        # OmniParser服务器
└── LICENSE                      # 许可证文件
```

## 核心功能

### 1. UI元素检测
- 使用YOLO模型检测屏幕中的交互元素
- 支持细粒度的小图标检测
- 可预测元素是否可交互

### 2. OCR文本识别
- 支持EasyOCR和PaddleOCR两种OCR引擎
- 高精度的文本框检测和识别
- 多语言支持

### 3. 元素描述生成
- 使用Florence2或BLIP2模型生成元素描述
- 提供上下文相关的功能描述
- 支持批量处理优化性能

### 4. 结构化输出
- 生成带标注的可视化图像
- 提供坐标和描述的结构化数据
- 支持多种输出格式

## 支持的模型

### 图标检测模型
- **架构**: YOLOv8n
- **输入尺寸**: 1280x1280
- **输出**: 边界框坐标和置信度
- **许可证**: AGPL（继承自YOLO）

### 图标描述模型
- **Florence2**: 基于DaViT视觉编码器的多模态模型
- **BLIP2**: Salesforce的图像-文本理解模型
- **许可证**: MIT

## 性能指标

- **Screen Spot Pro基准测试**: 39.5%（V2版本）
- **Windows Agent Arena**: 最佳性能
- **处理速度**: 平均每张图片2-5秒（GPU）
- **内存使用**: 约4GB GPU内存（Florence2，batch_size=128）

## 高级配置

### 检测阈值调整
```python
# 低阈值检测更多元素
BOX_TRESHOLD = 0.01

# 高阈值检测更少但更准确的元素
BOX_TRESHOLD = 0.1
```

### 批处理大小优化
```python
# 根据GPU内存调整批处理大小
batch_size = 64   # 2GB GPU内存
batch_size = 128  # 4GB GPU内存
batch_size = 256  # 8GB GPU内存
```

## 常见问题

### Q: 如何提高检测精度？
A: 可以调整以下参数：
- 降低`BOX_TRESHOLD`检测更多元素
- 增加`iou_threshold`减少重复检测
- 使用更高分辨率的输入图像

### Q: 如何处理多语言界面？
A: 配置OCR引擎支持多语言：
```python
# PaddleOCR支持多语言
paddle_ocr = PaddleOCR(lang='ch')  # 中文
paddle_ocr = PaddleOCR(lang='en')  # 英文
```

### Q: 如何优化处理速度？
A: 
- 使用GPU加速
- 增加批处理大小
- 启用模型量化
- 使用较小的输入图像尺寸

## 模型权重许可证
对于huggingface模型中心的模型检查点，请注意icon_detect模型采用AGPL许可证，因为它是从原始yolo模型继承的许可证。icon_caption_blip2和icon_caption_florence采用MIT许可证。请参考每个模型文件夹中的LICENSE文件：https://huggingface.co/microsoft/OmniParser。

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. Fork这个仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 📚 引用
我们的技术报告可以在[这里](https://arxiv.org/abs/2408.00203)找到。
如果您发现我们的工作有用，请考虑引用我们的工作：
```
@misc{lu2024omniparserpurevisionbased,
      title={OmniParser for Pure Vision Based GUI Agent}, 
      author={Yadong Lu and Jianwei Yang and Yelong Shen and Ahmed Awadallah},
      year={2024},
      eprint={2408.00203},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2408.00203}, 
}
```

## 联系方式

- 项目主页: https://microsoft.github.io/OmniParser/
- 问题反馈: https://github.com/microsoft/OmniParser/issues
- 电子邮件: 通过GitHub Issues联系我们

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

注意：图标检测模型采用AGPL许可证，图标描述模型采用MIT许可证。 