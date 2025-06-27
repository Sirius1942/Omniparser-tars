# 图像元素分析器API说明

## 概述

`ImageElementAnalyzer` 是一个强大的图像分析工具，基于 OmniParser + GPT-4o 实现，可以：

- 🔍 **OCR文本检测** - 检测图像中的文本内容
- 🎯 **图标识别** - 使用YOLO模型检测图标
- 🤖 **智能描述** - 使用GPT-4o生成图标功能描述
- 📍 **坐标定位** - 返回所有元素的精确位置坐标
- 🖼️ **可视化标注** - 生成带标注的图像

## 文件结构

- `util/image_element_analyzer.py` - 主要工具类和函数
- `image_analyzer_example.py` - 使用示例
- `util/demo_gpt4o.py` - 原始演示脚本（已重构）

## 导入方式

```python
from util.image_element_analyzer import (
    ImageElementAnalyzer,           # 主要分析器类
    analyze_single_image,          # 便捷函数
    get_element_descriptions,      # 获取元素描述
    get_coordinates_by_description # 根据描述查找坐标
)
```

## 主要类和方法

### 1. ImageElementAnalyzer 类

#### 初始化

```python
analyzer = ImageElementAnalyzer(
    model_path='weights/icon_detect/model.pt',  # YOLO模型路径
    config_path='config.json'                   # 配置文件路径
)

# 初始化模型
success = analyzer.initialize()
```

#### 分析单个图像

```python
result = analyzer.analyze_image(
    image_path="imgs/word.png",        # 图像路径
    box_threshold=0.05,                # 检测框阈值
    save_annotated=True,               # 是否保存标注图像
    output_dir="result",               # 输出目录
    verbose=True                       # 是否显示详细信息
)
```

**返回值结构：**
```python
{
    "success": bool,                    # 是否成功
    "elements": list,                   # 所有检测到的元素
    "text_elements": list,              # 文本元素
    "icon_elements": list,              # 图标元素
    "annotated_image_path": str,        # 标注图像路径
    "annotated_image_base64": str,      # 标注图像base64
    "label_coordinates": list,          # 标签坐标
    "processing_time": {                # 处理耗时
        "ocr": float,
        "caption": float,
        "total": float
    },
    "image_info": {                     # 图像信息
        "path": str,
        "size": tuple,
        "mode": str,
        "format": str
    },
    "element_count": {                  # 元素统计
        "total": int,
        "text": int,
        "icon": int
    }
}
```

#### 批量分析

```python
results = analyzer.batch_analyze(
    image_paths=["img1.png", "img2.png"],  # 图像路径列表
    box_threshold=0.05,                     # 其他参数同analyze_image
    save_annotated=True,
    output_dir="result"
)

# 返回: {image_path: result_dict, ...}
```

### 2. 便捷函数

#### analyze_single_image()

```python
result = analyze_single_image(
    image_path="imgs/word.png",
    model_path="weights/icon_detect/model.pt",
    config_path="config.json",
    save_annotated=True,
    output_dir="result"
)
```

#### get_element_descriptions()

```python
# 获取所有元素
all_elements = get_element_descriptions("imgs/word.png", "all")

# 只获取图标
icons = get_element_descriptions("imgs/word.png", "icon")

# 只获取文本
texts = get_element_descriptions("imgs/word.png", "text")
```

每个元素包含：
```python
{
    "type": "icon" | "text",           # 元素类型
    "content": str,                    # 描述内容
    "bbox": [x1, y1, x2, y2],         # 边界框坐标 (相对比例)
    # 其他属性...
}
```

#### get_coordinates_by_description()

```python
# 根据描述查找坐标
coords = get_coordinates_by_description(
    image_path="imgs/word.png",
    description="文件"  # 搜索包含"文件"的元素
)

# 返回: [x1, y1, x2, y2] 或 None
```

## 使用示例

### 基本使用

```python
from util.image_element_analyzer import analyze_single_image

# 分析图像
result = analyze_single_image("imgs/word.png", save_annotated=True)

if result["success"]:
    print(f"检测到 {result['element_count']['total']} 个元素")
    
    # 显示图标描述
    for icon in result["icon_elements"]:
        content = icon.get('content')
        bbox = icon.get('bbox')
        print(f"图标: {content}")
        print(f"坐标: {bbox}")
```

### 类实例使用

```python
from util.image_element_analyzer import ImageElementAnalyzer

# 创建分析器
analyzer = ImageElementAnalyzer()
analyzer.initialize()

# 分析多个图像
images = ["img1.png", "img2.png", "img3.png"]
for img in images:
    result = analyzer.analyze_image(img, verbose=False)
    if result["success"]:
        count = result["element_count"]
        print(f"{img}: 文本:{count['text']} 图标:{count['icon']}")
```

### 批量处理

```python
# 批量分析
results = analyzer.batch_analyze(
    ["img1.png", "img2.png"],
    save_annotated=True,
    output_dir="output"
)

# 统计结果
success_count = sum(1 for r in results.values() if r["success"])
print(f"成功处理: {success_count}/{len(results)}")
```

### 查找特定元素

```python
from util.image_element_analyzer import get_coordinates_by_description

# 查找包含"设置"的元素坐标
coords = get_coordinates_by_description("screenshot.png", "设置")
if coords:
    x1, y1, x2, y2 = coords
    print(f"设置按钮位置: ({x1:.3f}, {y1:.3f}, {x2:.3f}, {y2:.3f})")
```

## 配置要求

### config.json 示例

```json
{
    "openai": {
        "api_key": "your-api-key",
        "base_url": "http://your-api-endpoint/v1/",
        "model": "Qwen3-32B",
        "max_tokens": 50,
        "temperature": 0.1,
        "batch_size": 3
    },
    "caption": {
        "default_prompt": "请简洁地描述这个图标的功能..."
    }
}
```

### 模型文件

- YOLO模型: `weights/icon_detect/model.pt`
- 确保模型文件存在且可访问

## 输出说明

### 坐标格式

- 所有坐标都是相对比例 (0.0-1.0)
- 格式: `[x1, y1, x2, y2]` (左上角, 右下角)
- 转换为像素坐标: `pixel_x = relative_x * image_width`

### 元素类型

- **text**: OCR检测到的文本
  - content: 文本内容
  - bbox: 文本区域坐标

- **icon**: YOLO检测到的图标
  - content: GPT-4o生成的功能描述
  - bbox: 图标区域坐标

### 标注图像

- 保存为 `annotated_原文件名.png`
- 包含边界框和标签
- 不同类型元素使用不同颜色标注

## 性能优化

### 批量处理建议

```python
# 推荐: 使用类实例处理多图像
analyzer = ImageElementAnalyzer()
analyzer.initialize()  # 只初始化一次

for image in image_list:
    result = analyzer.analyze_image(image, verbose=False)
    # 处理结果...
```

### 参数调优

- `box_threshold`: 降低值检测更多元素，提高值减少误检
- `batch_size`: 在config.json中调整GPT-4o批处理大小
- `verbose=False`: 大批量处理时关闭详细输出

## 错误处理

```python
result = analyze_single_image("image.png")

if not result["success"]:
    error_msg = result.get("error", "Unknown error")
    print(f"分析失败: {error_msg}")
    
    # 可选：查看详细错误
    if "traceback" in result:
        print(result["traceback"])
```

## 注意事项

1. **模型依赖**: 需要YOLO模型文件和GPT-4o API访问
2. **内存使用**: 大图像可能消耗较多内存
3. **处理时间**: 包含OCR、图标检测、GPT-4o调用，耗时较长
4. **坐标精度**: 返回的是相对坐标，需要根据图像尺寸转换
5. **API限制**: 注意GPT-4o API的调用限制和费用

## 扩展功能

可以基于现有API开发更多功能：

- 自动UI测试（结合坐标点击）
- 界面布局分析
- 可访问性检查
- 多语言OCR支持
- 自定义图标分类器 