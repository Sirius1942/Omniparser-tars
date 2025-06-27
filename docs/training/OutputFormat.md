# OmniParser 输出结构化结果格式设计说明

## 概述

OmniParser是一个屏幕解析工具，能够将GUI界面转换为结构化的数据格式。本文档详细描述了OmniParser输出的数据结构和格式规范。

## 主要输出格式

OmniParser的核心函数 `get_som_labeled_img()` 返回三个主要组件：

```python
def get_som_labeled_img(...) -> Tuple[str, Dict, List[Dict]]:
    return encoded_image, label_coordinates, filtered_boxes_elem
```

### 1. 带标注的图像 (encoded_image)

**数据类型**: `str`  
**格式**: Base64编码的PNG图像  
**用途**: 可视化展示检测结果

```python
# 示例
encoded_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
```

**图像内容包含**:
- 原始GUI截图
- 检测到的边界框（带数字ID标签）
- 文本和图标区域的可视化标记
- 根据元素类型使用不同颜色的边框

### 2. 坐标映射 (label_coordinates)

**数据类型**: `Dict[str, List[float]]`  
**格式**: 字典，键为元素ID，值为边界框坐标  
**坐标系统**: 归一化坐标 (0-1范围)

```python
label_coordinates = {
    "0": [x, y, width, height],  # 归一化坐标
    "1": [x, y, width, height],
    "2": [x, y, width, height],
    ...
}
```

**实际示例**:
```python
{
    "0": [0.1500781625509262, 0.011121409013867378, 0.1771756261587143, 0.024096386507153511],
    "1": [0.034392911940813065, 0.04726598784327507, 0.020844191312789917, 0.025023165649250984],
    "2": [0.032580457627773285, 0.1255720555782318, 0.05744557827711105, 0.020826339721679688]
}
```

### 3. 结构化元素列表 (filtered_boxes_elem)

**数据类型**: `List[Dict]`  
**格式**: 元素字典列表，每个元素包含完整的属性信息

## 元素结构规范

### 基本字段定义

每个检测到的UI元素都包含以下标准字段：

| 字段名 | 数据类型 | 必填 | 描述 |
|--------|----------|------|------|
| `type` | `str` | ✅ | 元素类型：`'text'` 或 `'icon'` |
| `bbox` | `List[float]` | ✅ | 边界框坐标 `[x1, y1, x2, y2]` (归一化) |
| `interactivity` | `bool` | ✅ | 是否可交互：`True` 或 `False` |
| `content` | `str` | ✅ | 元素内容描述 |
| `source` | `str` | ✅ | 数据来源标识 |

### 元素类型详解

#### 文本元素 (type: 'text')

**特征**:
- 通过OCR技术检测和识别
- `interactivity` 通常为 `False`
- `content` 包含OCR识别的实际文字
- `source` 为 `'box_ocr_content_ocr'`

**示例**:
```python
{
    'type': 'text',
    'bbox': [0.1500781625509262, 0.011121409013867378, 0.3272537887096405, 0.03521779552102089],
    'interactivity': False,
    'content': 'Document 10.docx  General*  Last Modified: Just now',
    'source': 'box_ocr_content_ocr'
}
```

#### 图标元素 (type: 'icon')

**特征**:
- 通过YOLO模型检测位置
- 通过Florence2模型生成功能描述
- `interactivity` 通常为 `True`
- `content` 包含AI生成的图标功能描述
- `source` 为 `'box_yolo_content_yolo'`

**示例**:
```python
{
    'type': 'icon',
    'bbox': [0.032580457627773285, 0.1255720555782318, 0.09002603590488434, 0.1463983952999115],
    'interactivity': True,
    'content': 'Format Painter',
    'source': 'box_yolo_content_yolo'
}
```

### 坐标系统说明

#### 边界框格式
- **格式**: `[x1, y1, x2, y2]`
- **坐标系**: 左上角为原点 (0,0)
- **数值范围**: 0.0 - 1.0 (归一化坐标)
- **转换公式**: 
  ```python
  pixel_x = normalized_x * image_width
  pixel_y = normalized_y * image_height
  ```

#### 坐标示例
```python
# 归一化坐标
bbox = [0.1, 0.2, 0.3, 0.4]

# 对于1920x1080的图像，对应的像素坐标为:
# 左上角: (192, 216)
# 右下角: (576, 432)
# 宽度: 384像素
# 高度: 216像素
```

## 数据来源标识

### source 字段说明

| 值 | 描述 | 检测方法 | 内容生成 |
|----|------|----------|----------|
| `'box_ocr_content_ocr'` | OCR检测的文本元素 | EasyOCR/PaddleOCR | 直接OCR识别 |
| `'box_yolo_content_yolo'` | YOLO检测的图标元素 | YOLOv8模型 | Florence2描述生成 |

## 完整输出示例

### Microsoft Word界面解析结果

```python
[
    # 菜单文本
    {
        'type': 'text',
        'bbox': [0.034392911940813065, 0.04726598784327507, 0.05523710325360298, 0.07228915393352509],
        'interactivity': False,
        'content': 'Home',
        'source': 'box_ocr_content_ocr'
    },
    
    # 粘贴按钮
    {
        'type': 'icon',
        'bbox': [0.009730310179293156, 0.07482017576694489, 0.033241190016269684, 0.14442680776119232],
        'interactivity': True,
        'content': 'Paste',
        'source': 'box_yolo_content_yolo'
    },
    
    # 加粗按钮
    {
        'type': 'icon',
        'bbox': [0.1005261242389679, 0.11491625010967255, 0.11139624565839767, 0.1337515264749527],
        'interactivity': True,
        'content': 'Bold',
        'source': 'box_yolo_content_yolo'
    },
    
    # 文档标题
    {
        'type': 'text',
        'bbox': [0.1500781625509262, 0.011121409013867378, 0.3272537887096405, 0.03521779552102089],
        'interactivity': False,
        'content': 'Document 10.docx  General*  Last Modified: Just now',
        'source': 'box_ocr_content_ocr'
    }
]
```

## 性能指标

### 典型处理结果统计
- **总元素数量**: 通常50-200个元素
- **文本元素比例**: 约30-40%
- **图标元素比例**: 约60-70%
- **处理时间**: 
  - OCR检测: ~1-3秒
  - YOLO检测: ~0.1-0.5秒
  - Florence2描述: ~0.2-1秒

### 内存使用
- **Florence2批处理**: 默认batch_size=128，约4GB GPU内存
- **图标尺寸**: 统一resize到64x64像素
- **描述长度**: 最多20个token

## AI代理集成格式

### HTML格式转换

为便于AI模型理解，可将结构化数据转换为HTML格式：

```python
def reformat_messages(parsed_content_list):
    screen_info = ""
    for idx, element in enumerate(parsed_content_list):
        element['idx'] = idx
        if element['type'] == 'text':
            screen_info += f'<p id={idx} class="text" alt="{element["content"]}"> </p>\n'
        elif element['type'] == 'icon':
            screen_info += f'<img id={idx} class="icon" alt="{element["content"]}"> </img>\n'
    return screen_info
```

**输出示例**:
```html
<p id=0 class="text" alt="Home"> </p>
<p id=1 class="text" alt="Insert"> </p>
<img id=2 class="icon" alt="Paste"> </img>
<img id=3 class="icon" alt="Bold"> </img>
<img id=4 class="icon" alt="Format Painter"> </img>
```

## 应用场景

### 1. GUI自动化测试
```python
# 查找可点击的"保存"按钮
save_buttons = [elem for elem in parsed_content_list 
                if elem['type'] == 'icon' 
                and elem['interactivity'] 
                and 'save' in elem['content'].lower()]
```

### 2. 可访问性支持
```python
# 生成屏幕阅读器描述
def generate_accessibility_description(parsed_content_list):
    description = "Screen contains: "
    text_elements = [elem['content'] for elem in parsed_content_list if elem['type'] == 'text']
    icon_elements = [elem['content'] for elem in parsed_content_list if elem['type'] == 'icon']
    
    description += f"{len(text_elements)} text elements and {len(icon_elements)} interactive elements."
    return description
```

### 3. AI代理操作
```python
# AI代理任务执行
def find_element_by_description(parsed_content_list, target_description):
    for idx, element in enumerate(parsed_content_list):
        if target_description.lower() in element['content'].lower():
            return idx, element['bbox']
    return None, None
```

## 数据质量保证

### 置信度机制
- **OCR置信度**: 文本识别准确率通常>90%
- **YOLO检测**: 默认置信度阈值0.05
- **重叠去除**: IoU阈值0.7避免重复检测

### 错误处理
- 无效边界框自动过滤
- 空内容元素跳过处理
- 坐标范围验证 (0-1)

## 版本兼容性

### 当前版本: v2.0
- 支持Florence2和BLIP2模型
- 支持CPU和GPU推理
- 兼容transformers 4.36.2+

### 向后兼容
- v1.x格式可通过转换函数迁移
- 保持核心字段结构不变
- 新增字段采用可选方式

## 扩展性设计

### 自定义字段
结构支持添加自定义字段而不破坏现有功能：

```python
{
    'type': 'icon',
    'bbox': [...],
    'interactivity': True,
    'content': 'Save',
    'source': 'box_yolo_content_yolo',
    # 自定义字段
    'confidence': 0.95,
    'category': 'file_operation',
    'keyboard_shortcut': 'Ctrl+S'
}
```

### 插件机制
支持通过插件扩展内容生成器：
- 自定义OCR引擎
- 替代描述生成模型
- 特定领域的元素分类器

---

本设计说明确保了OmniParser输出格式的一致性、可扩展性和易用性，为各种GUI自动化应用提供了标准化的数据接口。 